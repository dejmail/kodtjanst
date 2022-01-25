from pdb import set_trace
import requests
import re

from django import forms
from django.conf import settings
from django.contrib import admin
from django.core.validators import URLValidator
from django.forms import ModelChoiceField, ValidationError
from django.forms.models import BaseInlineFormSet

from django.contrib.admin.options import *

from django.shortcuts import render
from django.template import response
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.forms import Textarea

from simple_history.admin import SimpleHistoryAdmin

from .custom_filters import DuplicateKodtextFilter, DuplicatKodverkFilter, SwedishLettersinKodFilter
from .forms import KodverkAdminForm, MultiMappingForm, KommentarAdminForm, ArbetsKommentarForm
#ExternaKodtextForm
from .models import *
from .models import Kodtext, Kodverk, ArbetsKommentar

admin.site.site_header = "KOLLI Admin"
admin.site.site_title = "KOLLI Admin Portal"
admin.site.index_title = "Välkommen till KOLLI Portalen"

class KodtextManager(SimpleHistoryAdmin):

    list_display = ('id',
                    'kod',
                    'kodtext', 
                    'kodverk_grupp',
                    'definition',
                    'annan_kodtext',
                    'extra_data'
                    )

    list_filter = ('status', DuplicateKodtextFilter, SwedishLettersinKodFilter)

    fieldsets = [
        ['Main', {
        'fields': ['kodverk',
            ('kodtext', 'annan_kodtext')],
        }],
        [None, {
        'fields': [('kod', 'status')],
        }],
        ["Extra attribut", {
        'classes': ('collapse',),
        'fields' : ['definition',
                    'kommentar',
                    ('extra_data', 'position'),
                    ]
        }]
    ]

    def kodverk_grupp(self, obj):
        display_text = ", ".join([
            "<a href={}>{}</a>".format(
                reverse('admin:{}_{}_change'.format(obj._meta.app_label, 'kodverk'),
                args=(obj.kodverk.id,)),
                obj.kodverk.titel_på_kodverk)
            #for kodv in obj.kodverk
        ])
        
        if display_text:
            return mark_safe(display_text)
        return "-"
    
    kodverk_grupp.short_description = 'Kodverk'

    search_fields = ('kodverk__titel_på_kodverk', 'kodtext')

    def save_model(self, request, obj, form, change):
        
        obj.ändrad_av_id = request.user.id
        super().save_model(request, obj, form, change)


from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.core.paginator import EmptyPage, InvalidPage, Paginator


class InlineChangeList(object):
    can_show_all = True
    multi_page = True
    get_query_string = ChangeList.__dict__['get_query_string']

    def __init__(self, request, page_num, paginator):
        self.show_all = 'all' in request.GET
        self.page_num = page_num
        self.paginator = paginator
        self.result_count = paginator.count
        self.params = dict(request.GET.items())

class PaginationInline(admin.TabularInline):
    
    template = 'admin/edit_inline/pagination_inline.html'
    per_page = 20

    def get_formset(self, request, obj=None, **kwargs):
        formset_class = super(PaginationInline, self).get_formset(
            request, obj, **kwargs)

        class PaginationFormSet(formset_class):
            def __init__(self, *args, **kwargs):
                super(PaginationFormSet, self).__init__(*args, **kwargs)

                qs = self.queryset
                paginator = Paginator(qs, self.per_page)
                try:
                    page_num = int(request.GET.get('page', '0'))
                except ValueError:
                    page_num = 0

                try:
                    page = paginator.page(page_num + 1)
                except (EmptyPage, InvalidPage):
                    page = paginator.page(paginator.num_pages)
                
                self.cl = InlineChangeList(request, page_num, paginator)
                
                self.paginator = paginator

                if self.cl.show_all:
                    self._queryset = qs
                else:
                    self._queryset = page.object_list

        PaginationFormSet.per_page = self.per_page
        PaginationFormSet.has_next = True
        
        return PaginationFormSet

class KodtextInline(PaginationInline):
    
    model = Kodtext
    extra = 1

    fieldsets = [
    [None, {
    'fields': [('kod', 'kodtext', 'annan_kodtext', 'position')],
    }
    ]]

    def has_changed(self):
        """Returns True for new instances, calls super() for ones that exist in db.
        Prevents forms with defaults being recognized as empty/unchanged."""
        return not self.instance.pk or super().has_changed()

class NyckelOrdInline(admin.TabularInline):
    model = Nyckelord
    extra = 1

    fieldsets = [
    [None, {
    'fields': [('nyckelord')],
    }
    ]]

class ArbetsKommentarInline(admin.TabularInline):
    model = ArbetsKommentar
    form = ArbetsKommentarForm
    extra = 1

    fieldsets = [
    [None, {
    'fields':[('kommentar',)],
    }
    ]]

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':10, 'cols':40})}
    }



class NyckelordManager(admin.ModelAdmin):

    list_display = ('nyckelord', 'kodverk_grupp')
    search_fields = ('nyckelord',)

    def kodverk_grupp(self, obj):
        
        display_text = ", ".join([
            "<a href={}>{}</a>".format(
                reverse('admin:{}_{}_change'.format(obj._meta.app_label, 'kodverk'),
                args=(obj.kodverk_from_id,)),
                obj.kodverk_from.titel_på_kodverk)
            #for kodv in obj.kodverk
        ])
        
        if display_text:
            return mark_safe(display_text)
        return "-"


def make_aktiv(modeladmin, request, queryset):
    
    queryset.update(status='Aktiv')
make_aktiv.short_description = "Markera kodverk som Aktiv"

def make_inaktiv(modeladmin, request, queryset):
    
    queryset.update(status='Inaktiv')
make_inaktiv.short_description = "Markera kodverk som Inaktiv"


class CodeableConceptFormSet(BaseInlineFormSet):

    def clean(self):
        super(CodeableConceptFormSet, self).clean()
        for form in self.forms:
            if ('källa' in form.cleaned_data.keys()) and (form.cleaned_data.get('källa') is not None):
                
                if 'http' in form.cleaned_data.get('källa'):

                    try:
                        split_text = re.split(r'\blänk=\b|\bklartext=\b', form.cleaned_data.get('källa'))
                        clean_list = list(filter(None, split_text))
                        if len(clean_list) != 2:
                            form.add_error('källa', 'Skriv länken så länk=http://www.länk.se klartext=rubrik')
                            return form.cleaned_data                                               
                        else:
                            http_link, link_text = clean_list
                    except ValueError as e:
                        form.add_error('källa', 'Skriv länken så länk=http://www.länk.se klartext=rubrik')
                        raise
                                    
                    validate = URLValidator()
                    try:
                        validate(http_link.strip())
                    except ValidationError:
                        form.add_error('källa', 'Skriv länken så länk=http://www.länk.se klartext=rubrik')
                        raise
                    try:
                        requests.get(http_link)
                    except requests.exceptions.ConnectionError:
                        form.add_error('källa', 'HTTP länken är inte nåbar, kolla tillgänglighet och stavning')
                    
            if ('version_av_källa' in form.cleaned_data.keys()) and (form.cleaned_data.get('version_av_källa') is not None):
                
                if any(substring in form.cleaned_data.get('version_av_källa') for substring in ['http://', 'https://']):
                    form.add_error('version_av_källa', 'Skriv inte länkar - skriv versionen från Källan')                
        return form.cleaned_data

class CodeableConceptInline(admin.TabularInline):

    class Media:

        css = {'all' : ('https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css',)}

    model = CodeableConceptAttributes
    formset = CodeableConceptFormSet

    extra = 1

    fieldsets = [
    [None, {
    'fields':[('ägare_till_kodverk','källa', 'version_av_källa', 'ansvarig_förvaltare')],
    }
    ]]
    
class ExternaKodtextInline(admin.TabularInline):

    model = ExternaKodtext
    extra = 1
    fieldsets = [
    [None, {
    'fields':[('mappad_id', 'mappad_text', 'resolving_url', 'kommentar')]
    }
    ]]
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':10, 'cols':40})}
    }


class CodeableConceptManager(SimpleHistoryAdmin):

    list_display = ('kodverk_from', 'källa', 'version_av_källa', 'ansvarig_förvaltare')


class KodverkManager(SimpleHistoryAdmin):

    class Media:
    
        css = {
            'all': ('https://use.fontawesome.com/releases/v5.8.2/css/all.css',
                    f'{settings.STATIC_URL}css/custom_icon.css',
                    f'{settings.STATIC_URL}css/main.css',)
            }   

    change_form_template = 'change_form_autocomplete.html'
    form = KodverkAdminForm    
    save_on_top = True
    list_display = ('id', 
                    'titel_på_kodverk',
                    'safe_syfte',
                    'status',
                    'kodverk_variant',
                    'version',
                    'clean_ägare',
                    'ansvarig_fullname',
                    'clean_källa',
                    'datum_skapat',
                    'has_underlag')
    list_display_links = ('titel_på_kodverk',)
    exclude = ['ändrad_av',]
    actions = [make_aktiv, make_inaktiv]
    list_filter = ('kodverk_variant', DuplicatKodverkFilter, 'status')
    search_fields = ('titel_på_kodverk',)
    history_list_display = ['changed_fields']
    fieldsets = [
        ['Main', {
        'fields': [('titel_på_kodverk', 'kodverk_variant'),
        ('syfte'),
        ('beskrivning_av_innehållet'),
        ('identifierare', 'uppdateringsintervall', 'användning_av_kodverk'),
        ('status', 'version'), 
        ('giltig_från', 'giltig_tom'),
        ('ansvarig'),
        ('underlag', 'länk'),
        ]}],
        ['Extra', {
        'fields': [('extra_data')],
        }],
    ]

    def get_inlines(self, request, obj):
        #set_trace()
        if obj is None:
            return [NyckelOrdInline, CodeableConceptInline, KodtextInline, ArbetsKommentarInline]
        elif ExternaKodtext.objects.filter(kodverk__titel_på_kodverk=obj.titel_på_kodverk) is None:
            return [NyckelOrdInline, CodeableConceptInline, KodtextInline, ArbetsKommentarInline]
        elif obj.kodverk_variant == 'VGR codeable concept':
            return [NyckelOrdInline, CodeableConceptInline, ExternaKodtextInline, ArbetsKommentarInline]

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return_text = ""
            for field in delta.changed_fields:
                return_text += f"""från --> <span class="text_highlight_yellow">{getattr(delta.old_record, field)}</span></br></br>
                till --> <span class="text_highlight_green">{getattr(delta.new_record, field)}</span></br>"""
            return mark_safe(return_text)
        return None

    def clean_ägare(self, obj):
        
        return ', '.join([i.get("ägare_till_kodverk") for i in obj.codeableconceptattributes_set.values() if i.get("ägare_till_kodverk") is not None])

    clean_ägare.short_description = "Ägare"


    def clean_källa(self, obj):
        return_string = ''
        
        for i in obj.codeableconceptattributes_set.values():
        
            if i.get("källa") is not None:
                        
                if all(substring in i.get('källa') for substring in ['länk', 'klartext']):
                    
                    http_link, link_text = list(filter(None, re.split(r'\blänk=\b|\bklartext=\b', i.get("källa"))))
                    format_link = f'<a href="{http_link.strip()}" target="_blank">{link_text}</a>'
                    safe_link = format_html(format_link)
                    if return_string == '':
                        return_string += safe_link
                    else:
                        return_string += ', ' + safe_link
                else:
                    return i.get('källa')    
        return mark_safe(return_string)

    clean_källa.short_description = "Källa"

    def safe_syfte(self, obj):

        return mark_safe(obj.syfte)

    safe_syfte.short_description = "Syfte"
    
    def ansvarig_fullname(self, obj):
        if obj.ansvarig:
            return obj.ansvarig.get_full_name()
        else:
            return ''

    def has_underlag(self, obj):

        #if obj.titel_på_kodverk == "VGRKV_StatusKliniskProcess": set_trace()
        if (obj.underlag != None) and (obj.underlag.name != ''):
            return format_html(f'''<a href={obj.underlag}>
                                    <i class="fas fa-file-download">
                                    </i>
                                    </a>''')
        else:
             return format_html(f'''
                                    <i class="fas fa-exclamation-triangle"  style="color:red">
                                    </i>
                                    ''')
    has_underlag.short_description = "Underlag fil"

    def save_model(self, request, obj, form, change):
        
        obj.ändrad_av_id = request.user.id
        super().save_model(request, obj, form, change)

class ArbetsKommentarManager(admin.ModelAdmin):

    form = ArbetsKommentarForm

    def save_model(self, request, obj, form, change):
        #set_trace()
        super(ArbetsKommentarManager, self).save_model(request, obj, form, change)

    # def get_formsets_with_inlines(self, request, obj):
    #     #set_trace()
    #     return super().get_formsets_with_inlines(request, obj=obj)

    def get_inline_formsets(self, request, formsets, inline_instances, obj):
        #set_trace()
        return super().get_inline_formsets(request, formsets, inline_instances, obj=obj)

    # def save_new_objects(self, commit=True):
    #     saved_instances = super(ArbetsKommentarForm, self).save_new_objects(commit)
    #     if commit:
    #         # create book for press
    #     return saved_instances

    # def save_existing_objects(self, commit=True):
    #     saved_instances = super(ArbetsKommentarForm, self).save_existing_objects(commit)
    #     if commit:
    #         # update book for press
    #     return saved_instances

class KodtextIdandTextField(forms.ModelChoiceField):

     def label_from_instance(self, obj):
         return f"{obj.id} - {obj.kodtext}"

from django.contrib.admin import helpers, widgets

class ExternaKodtextManager(admin.ModelAdmin):

    list_display = ('mappad_id',
                    'mappad_text',
                    'clickable_url',                    
                    'kommentar',
                    'kodverk')

    def clickable_url(self, obj):
        return format_html("<a href='{url}' target='_blank' rel='noopener noreferrer'>{url}</a>", url=obj.resolving_url)

    clickable_url.short_description = "URL"

class CommentedKodverkManager(admin.ModelAdmin):
    
    model = CommentedKodverk
    form = KommentarAdminForm
    extra = 1
    readonly_fields = ('kodverk_link',)
    exclude = ('kodverk',)
    list_filter = ('status',)

    fieldsets = [
    ['Main', {
    'fields': [('kodverk_link', 'status',),
        ('namn', 'epost', 'kontakt'),
    ('kommentar',),
    ('handläggnings_kommentar', 'handläggare',),

    ]}],
    ]    

    list_display = ('datum_skapat','kodverk_link','namn','epost','kontakt', 'kommentar', 'handläggare','status',) 

    def kodverk_link(self, instance):
        
        link = f'admin:{instance._meta.app_label}_kodverk_change'
        url = reverse(link, args=(instance.kodverk.pk,))
        return format_html(f'<a href="{url}">{instance.kodverk.titel_på_kodverk}</a>')

    kodverk_link.short_description = 'Kodverk'


from django.forms import SelectMultiple


class MultiKodtextMappingManager(admin.ModelAdmin):

    formfield_overrides = { models.ManyToManyField: {'widget': SelectMultiple(attrs={'size':'30'})}, }


    change_form_template = 'admin/mapping_template.html'

    class Media:
        js = (f'{settings.STATIC_URL}js/admin_multimap_loadkodtext.js',)
        css = {
            'all': (f'{settings.STATIC_URL}css/hide_plus_sign.css',)
            }            

    form = MultiMappingForm

    list_display = ('id', 'text_description',
                    'kodverk_map_from',
                    'kodtext_map_from',
                    'kodverk_map_to',
                    'kodtext_map_to')

    def kodverk_map_from(self, obj):
        return Kodverk.objects.filter(id=obj.kodtext_from.prefetch_related()[0].kodverk_id).values()[0].get('titel_på_kodverk')

    def kodtext_map_from(self, obj):
        
        return_list = '<div style="color:dodgerblue";>-|-</div>'.join([k.kodtext for k in obj.kodtext_from.all() if k.kodtext is not None])
        
        if return_list is not None:
            return format_html(return_list)
        else:
            return ""

    kodtext_map_from.short_description = 'Kodtext från'

    def kodverk_map_to(self, obj):
        return Kodverk.objects.filter(id=obj.kodtext_to.prefetch_related()[0].kodverk_id).values()[0].get('titel_på_kodverk')
        
    def kodtext_map_to(self, obj):
        
        return_list = '<div style="color:lightcoral";>-|-</div>'.join([k.kodtext for k in obj.kodtext_to.all() if k.kodtext is not None])
        
        if return_list is not None:
            return format_html(return_list)
        else:
            return ""
    
    kodtext_map_to.short_description = 'Kodtext till'

admin.site.register(Kodverk, KodverkManager)
admin.site.register(Kodtext, KodtextManager)
admin.site.register(ExternaKodtext, ExternaKodtextManager)
#admin.site.register(ExternaKodverk)
admin.site.register(Nyckelord, NyckelordManager)
admin.site.register(ArbetsKommentar, ArbetsKommentarManager)
admin.site.register(CommentedKodverk, CommentedKodverkManager)
admin.site.register(MultiKodtextMapping, MultiKodtextMappingManager)
admin.site.register(CodeableConceptAttributes, CodeableConceptManager)

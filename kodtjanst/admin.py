from pdb import set_trace

from django import forms
from django.conf import settings
from django.contrib import admin
from django.forms import ModelChoiceField, ValidationError
from django.forms.models import BaseInlineFormSet

from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .custom_filters import DuplicateKodtextFilter, DuplicatKodverkFilter
from .forms import ExternaKodtextForm, KodverkAdminForm, MultiMappingForm
from .models import *
from .models import Kodtext, Kodverk

admin.site.site_header = "KOLLI Admin"
admin.site.site_title = "KOLLI Admin Portal"
admin.site.index_title = "Välkommen till KOLLI Portalen"

class KodtextManager(admin.ModelAdmin):

    list_display = ('id',
                    'kodtext', 
                    'kodverk_grupp',
                    'definition',
                    'annan_kodtext',
                    'extra_data'
                    )

    list_filter = ('status', DuplicateKodtextFilter,)

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



class ValidatedByInline(admin.TabularInline):
    model = ValidatedBy
    extra = 1

    fieldsets = [
    [None, {
    'fields':[('domän_stream','domän_epost','domän_telefon','domän_kontext')],
    }
    ]]

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
            if ('http://' in form.cleaned_data.get('källa')) and ("a href" not in form.cleaned_data.get('källa')):
                form.add_error('källa', 'Skriv länken så - Exempel - <a href="http://www.google.com" target="_blank">Google</a>')
            if 'http://' in form.cleaned_data.get('version_av_källa'):
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
    

class CodeableConceptManager(admin.ModelAdmin):

    list_display = ('kodverk_from', 'källa', 'version_av_källa', 'ansvarig_förvaltare')


class KodverkManager(admin.ModelAdmin):

    class Media:
    
        css = {
            'all': ('https://use.fontawesome.com/releases/v5.8.2/css/all.css',
                    f'{settings.STATIC_URL}css/custom_icon.css',)
            }   

    change_form_template = 'change_form_autocomplete.html'
    form = KodverkAdminForm

    inlines = [NyckelOrdInline, CodeableConceptInline, KodtextInline, ValidatedByInline]
    
    save_on_top = True

    list_display = ('titel_på_kodverk',
                    'syfte',
                    'status',
                    'version',
                    'clean_ägare',
                    'ansvarig',
                    'kategori',
                    'datum_skapat',
                    'has_underlag')

    exclude = ['ändrad_av',]

    actions = [make_aktiv, make_inaktiv]

    list_filter = ('kodverk_variant', DuplicatKodverkFilter, 'status')

    search_fields = ('titel_på_kodverk','kategori')

    fieldsets = [
        ['Main', {
        'fields': [('titel_på_kodverk'),
        ('syfte'),
        ('beskrivning_av_informationsbehov'),
        ('identifier', 'uppdateringsintervall', 'användning_av_kodverk'),
        ('status', 'version'), 
        ('giltig_från', 'giltig_tom'),
        ('ansvarig'),
        ('underlag', 'länk_till_underlag'),
        ]}],
        ['Extra', {
        'fields': [('extra_data')],
        }],
    ]

    def clean_ägare(self, obj):
        
        return ', '.join([i.get("ägare_till_kodverk") for i in obj.codeableconceptattributes_set.values() if i.get("ägare_till_kodverk") is not None])

    clean_ägare.short_description = "Ägare"
        
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



class KodtextIdandTextField(forms.ModelChoiceField):

     def label_from_instance(self, obj):
         return f"{obj.id} - {obj.kodtext}"

class ExternaKodtextManager(admin.ModelAdmin):

    form = ExternaKodtextForm

    
    list_display = ('get_kodtext',
                    'mappad_id',
                    'mappad_text',
                    'clickable_url',                    
                    'kommentar',
                    'kodverk_grupp')
    
    def get_kodtext(self, obj):
        
        return obj.kodtext

    get_kodtext.short_description = 'Kodtext'


    def clickable_url(self, obj):
        return format_html("<a href='{url}' target='_blank' rel='noopener noreferrer'>{url}</a>", url=obj.resolving_url)

    clickable_url.short_description = "URL"
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):    

        if db_field.name == "kodtext":
            kwargs["queryset"] = Kodtext.objects.all()
            return KodtextIdandTextField(queryset=Kodtext.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ExternaKodtextManager, self).get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields['kodverk'].initial = Kodverk.objects.all()
            form.base_fields['kodtext'].initial = Kodtext.objects.none()
        else:
            
            form.base_fields['kodverk'].initial =  Kodverk.objects.filter(titel_på_kodverk=obj.kodtext.kodverk.titel_på_kodverk).values()[0].get('titel_på_kodverk')
        return form
    
    def save(self, commit=True):
        extra_field = self.cleaned_data.get('kodverk', None)
        return super(form, self).save(commit=commit)

    def save_model(self, request, obj, form, change):

        #remove the extra field from the form
        del form.fields['kodverk']
        super(ExternaKodtextManager, self).save_model(request, obj, form, change)
    
    def kodverk_grupp(self, obj):
        
        
        display_text = ", ".join([
            "<a href={}>{}</a>".format(
                reverse('admin:{}_{}_change'.format(obj._meta.app_label, 'kodverk'),
                args=(obj.kodtext.id,)),
                obj.kodtext.kodverk.titel_på_kodverk)
           
        ]).replace(' ' ,'_')
            
    kodverk_grupp.short_description = 'Kodverk'

class CommentedKodverkManager(admin.ModelAdmin):
    
    model = CommentedKodverk
    extra = 1

    list_display = ('kodverk_id','comment_name','comment_epost','comment_telefon', 'comment_kontext') 


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
admin.site.register(ValidatedBy)
admin.site.register(CommentedKodverk, CommentedKodverkManager)
admin.site.register(MultiKodtextMapping, MultiKodtextMappingManager)
admin.site.register(CodeableConceptAttributes, CodeableConceptManager)

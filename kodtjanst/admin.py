from django.contrib import admin

from .models import Kodverk, Kodtext
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse
from django import forms
from django.forms import ModelChoiceField
from django.conf import settings
from .models import *
from .forms import ExternaKodtextForm, MultiMappingForm, KodverkAdminForm
from .custom_filters import DuplicatKodverkFilter, DuplicateKodtextFilter
from django.utils.html import format_html


from pdb import set_trace

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


def make_unpublished(modeladmin, request, queryset):
    
    queryset.update(status='Publicera ej')
make_unpublished.short_description = "Markera kodverk som Publicera ej"

class KodverkManager(admin.ModelAdmin):  

    form = KodverkAdminForm

    inlines = [KodtextInline, NyckelOrdInline, ValidatedByInline]
    
    save_on_top = True

    list_display = ('id',
                    'titel_på_kodverk',
                    'status',
                    'kodverk_variant',
                    'urval_referens',
                    'syfte',
                    'version',
                    'ägare_till_kodverk',
                    'ansvarig',
                    'kategori')

    exclude = ['ändrad_av',]

    actions = [make_unpublished]

    list_filter = ('ägare_till_kodverk','kodverk_variant', DuplicatKodverkFilter, 'status')

    search_fields = ('id','titel_på_kodverk','kategori')

    fieldsets = [
        ['Main', {
        'fields': [('titel_på_kodverk', 'status', 'kodverk_variant', 'urval_referens','identifier'),
        ('underlag', 'länk_till_underlag')]}],
        ['Extra', {
        'fields': [('syfte'),
        ('beskrivning_av_informationsbehov'),
        ('giltig_från', 'giltig_tom'),
        ('kategori', 'ägare_till_kodverk', 'ansvarig_förvaltare'),
        ('källa', 'version_av_källa'),
        ('version', 'uppdateringsintervall'),
        'användning_av_kodverk',
        'extra_data'],
        }],
    ]

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

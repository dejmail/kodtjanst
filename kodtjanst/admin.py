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
from .forms import ExternaKodtextForm, MultiMappingForm
from .custom_filters import DuplicatKodverkFilter, DuplicateKodtextFilter

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


class KodtextInline(admin.TabularInline):
    
    model = Kodtext
    extra = 1

    fieldsets = [
    [None, {
    'fields': [('kod', 'kodtext', 'annan_kodtext', 'status')],
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




def make_unpublished(modeladmin, request, queryset):
    
    queryset.update(status='Publicera ej')
make_unpublished.short_description = "Markera kodverk som Publicera ej"

class KodverkManager(admin.ModelAdmin):  

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
        'fields': [('titel_på_kodverk', 'status', 'kodverk_variant', 'urval_referens'),
        ('identifier', 'instruktion_för_kodverket')]}],
        [None, {
        'fields': [('syfte'),
        ('beskrivning_av_informationsbehov'),
        ('giltig_från', 'giltig_tom'),
        ('kategori', 'ägare_till_kodverk', 'ansvarig_förvaltare'),
        ('hämtnings_källa', 'version_av_källa'),
        ('version', 'uppdateringsintervall', 'mappning_för_rapportering'),
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
                    'resolving_url',                    
                    'kommentar',
                    'kodverk_grupp')
    
    def get_kodtext(self, obj):
        
        return obj.kodtext
    
    get_kodtext.short_description = 'Kodtext'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):    
        #set_trace()
        if db_field.name == "kodtext":
            kwargs["queryset"] = Kodtext.objects.all()
            return KodtextIdandTextField(queryset=Kodtext.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ExternaKodtextManager, self).get_form(request, obj, **kwargs)
        if obj is None:
            set_trace()
            form.base_fields['kodverk'].initial = Kodverk.objects.all()
            form.base_fields['kodtext'].initial = Kodtext.objects.none()
        else:
            form.base_fields['kodverk'].initial =  Kodverk.objects.filter(titel_på_kodverk=obj.kodtext.kodverk.titel_på_kodverk).values()[0].get('titel_på_kodverk')
        return form
    
    def save(self, commit=True):
        extra_field = self.cleaned_data.get('kodverk', None)
        set_trace()
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


		
class MultiKodtextMappingManager(admin.ModelAdmin):

    class Media:
        js = (f'{settings.STATIC_URL}js/admin_multimap_loadkodtext.js',)
            

    #model = MultiKodtextMapping
    form = MultiMappingForm


    # def save_related(self, request, form, formsets, change):
        
    #     super(MultiKodtextMappingManager, self).save_related(request, form, formsets, change)
    #     set_trace()

    # def formfield_for_dbfield(self, db_field, request, **kwargs):
    #     set_trace()
    #     return None

    # def get_form(self, request, obj=None, change=False, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     #set_trace()
    #     return form

    # def get_form(self, request, obj=None, **kwargs):
    #     form = super().get_form(request, obj, **kwargs)
    #     if obj is None:
    #         pass
    #     else:
    #         form.base_fields['kodtext_from'].initial = 'Välja kodverk först'
            #set_trace()
            #form.get_initial_for_field(self, 'kodverk_from') = 'Välja kodverk'
            #form.base_fields['kodverk_to'].initial = 'Välja kodverk'

admin.site.register(Kodverk, KodverkManager)
admin.site.register(Kodtext, KodtextManager)
admin.site.register(ExternaKodtext, ExternaKodtextManager)
#admin.site.register(ExternaKodverk)
admin.site.register(Nyckelord)
admin.site.register(ValidatedBy)
admin.site.register(CommentedKodverk, CommentedKodverkManager)
admin.site.register(MultiKodtextMapping, MultiKodtextMappingManager)

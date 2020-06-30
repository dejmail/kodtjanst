from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Kodverk, Kodtext
from django.urls import reverse
from django.utils.safestring import mark_safe


from .models import Kodverk, Kodtext, ExternaKodverk, MappadTillKodtext, Nyckelord
from .forms import MappadTillKodtextForm
from import_export import resources

from pdb import set_trace

admin.site.site_header = "KOLLI Admin"
admin.site.site_title = "KOLLI Admin Portal"
admin.site.index_title = "Välkommen till KOLLI Portalen"

class KodtextInline(admin.TabularInline):
    model = Kodtext
    extra = 1

    fieldsets = [
    [None, {
    'fields': [('kodtext', 'annan_kodtext', 'kod', 'status')],
    }]
    # [None, {
    # 'fields': [('kod', 'status')],
    # }],
    # [None, {
    # 'classes': ['collapse'],
    # 'fields' : ['definition',
    #             'kommentar',
    #             ('extra_data', 'position'),
    #             ]
    # }]
    ]   

    # fieldsets = [
    # [None, {
    # 'fields': [('kodtext', 'annan_kodtext')],
    # }],
    # [None, {
    # 'fields': [('kod', 'status')],
    # }],
    # [None, {
    # 'classes': ['collapse'],
    # 'fields' : ['definition',
    #             'kommentar',
    #             ('extra_data', 'position'),
    #             ]
    # }]
    # ]   

    def has_changed(self):
        """Returns True for new instances, calls super() for ones that exist in db.
        Prevents forms with defaults being recognized as empty/unchanged."""
        return not self.instance.pk or super().has_changed()

class KodtextManager(admin.ModelAdmin):

    list_display = ('kodtext', 
                    'kodverk_grupp',
                    'definition',
                    'annan_kodtext',
                    'extra_data'
                    )

    list_filter = ('status',)

    fieldsets = [
        ['Main', {
        'fields': [('kodtext', 'annan_kodtext')],
        }],
        [None, {
        'fields': [('kod', 'status')],
        }],
        [None, {
        'classes': ['collapse'],
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
                obj.kodverk.rubrik_på_kodverk)
            #for kodv in obj.kodverk
        ])
        
        if display_text:
            return mark_safe(display_text)
        return "-"
    
    kodverk_grupp.short_description = 'Kodverk'

    search_fields = ('kodverk__rubrik_på_kodverk', 'kodtext')

    def save_model(self, request, obj, form, change):
            if not obj.pk:
                # Only set added_by during the first save.
                obj.added_by = request.user
            super().save_model(request, obj, form, change)

class KodverkResource(resources.ModelResource):

    class Meta:
        model = Kodverk

class KodverkManager(ImportExportModelAdmin):  

    inlines = [KodtextInline]

    save_on_top = True

    list_display = ('rubrik_på_kodverk',
                    'status',
                    'kodverk_variant',
                    'urval_referens',
                    'syfte',
                    'kort_beskrivning',
                    'version',
                    'ägare_av_kodverk',
                    'ansvarig',
                    'kategori')

    exclude = ['ändrad_av',]

    list_filter = ('ägare_av_kodverk','kodverk_variant')

    search_fields = ('rubrik_på_kodverk','kategori')

    fieldsets = [
        ['Main', {
        'fields': [('rubrik_på_kodverk', 'status', 'kodverk_variant', 'urval_referens'),
        ('identifier', 'kodschema','instruktion_för_kodverket')]}],
        [None, {
        'fields': [('syfte', 'kort_beskrivning'),
        ('beskrivning_av_informationsbehov', 'kommentar'),
        ('giltig_från', 'giltig_tom'),
        ('kategori', 'nyckelord', 'språk'),
        ('källa', 'version_av_källa', 'system_som_använderkodverket'),
        ('ägare_av_kodverk', 'version', 'uppdateringsintervall', 'mappning_för_rapportering'),
        'extra_data'],
        }],
    ]

    def get_inline(self, request, obj=None):
        return [inline(self.model, self.admin_site) for inline in self.inlines]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.added_by = request.user
        super().save_model(request, obj, form, change)

class MappadtillKodtextManager(admin.ModelAdmin):

    form = MappadTillKodtextForm

    list_display = ('get_kodtext',
                    'mappad_id',
                    'mappad_text',
                    'resolving_url',                    
                    'kommentar',
                    'kodverk_grupp')
    
    def get_kodtext(self, obj):
        return obj.kodtext.kodtext
    
    get_kodtext.short_description = 'Kodtext'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        
        if db_field.name == "kodtext":
            kwargs["queryset"] = Kodtext.objects.all()
        return super(MappadtillKodtextManager, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(MappadtillKodtextManager, self).get_form(request, obj, **kwargs)
        form.base_fields['kodverk'].initial =  Kodverk.objects.filter(rubrik_på_kodverk=obj.kodtext.kodverk.rubrik_på_kodverk).values()[0].get('rubrik_på_kodverk')
        return form
    
    def save(self, commit=True):
        extra_field = self.cleaned_data.get('kodverk', None)
        # ...do something with extra_field here...
        return super(form, self).save(commit=commit)
    
    def kodverk_grupp(self, obj):
        
        display_text = ", ".join([
            "<a href={}>{}</a>".format(
                reverse('admin:{}_{}_change'.format(obj._meta.app_label, 'kodverk'),
                args=(obj.kodtext.kodverk.id,)),
                obj.kodtext.kodverk.rubrik_på_kodverk)
           
        ]).replace(' ' ,'_')
        print(display_text)
    
    kodverk_grupp.short_description = 'Kodverk'

# class MyInvoiceAdminForm(forms.ModelForm):
#     kodtext = CustomMappadKodtextField(queryset=Kodtext.objects.all()) 
#     class Meta:
#           model = Invoice

# class CustomMappadKodtextField(forms.ModelChoiceField):
#      def label_from_instance(self, obj):
#          return "%s" % (obj.kodtext)

admin.site.register(Kodverk, KodverkManager)
admin.site.register(Kodtext, KodtextManager)
#admin.site.register(ExternaKodverk)
admin.site.register(MappadTillKodtext, MappadtillKodtextManager)
admin.site.register(Nyckelord)

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Kodverk, Kodtext
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse


from .models import Kodverk, Kodtext, ExternaKodverk, MappadTillKodtext, Nyckelord
from .forms import MappadTillKodtextForm
from import_export import resources
from import_export.formats import base_formats

from .file_import_functions import main_import_function

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

class KodtextResource(resources.ModelResource):

    class Meta:
        model = Kodtext

class KodverkResource(resources.ModelResource):

    class Meta:
        model = Kodverk

    def before_import(self, dataset, dry_run):
        print('trying to catch the file post POST')
        set_trace()

class ImportMixin(object):
    
    formats = (base_formats.XLS,
               base_formats.XLSX)


class KodverkManager(ImportExportModelAdmin):  

    inlines = [KodtextInline]

    resource_class = KodverkResource

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

    def get_import_formats(self):
            """
            Returns available import formats.
            """
            formats = (
                  base_formats.CSV,
                  base_formats.XLS,
                  base_formats.XLSX,
            )
            return [f for f in formats if f().can_import()]  
    
    def import_action(self, request, *args, **kwargs):

        if not self.has_import_permission(request):
            raise PermissionDenied

        context = self.get_import_context_data()

        import_formats = self.get_import_formats()
        form_type = self.get_import_form()
        form_kwargs = self.get_form_kwargs(form_type, *args, **kwargs)
        form = form_type(import_formats,
                    request.POST or None,
                    request.FILES or None,
                    **form_kwargs)

        if request.POST and form.is_valid():
            print("received uploaded file")
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            tmp_storage = self.write_to_tmp_storage(import_file, input_format)

            # then read the file, using the proper format-specific mode
            # warning, big files may exceed memory
            try:
                data = tmp_storage.read(input_format.get_read_mode())
                if not input_format.is_binary() and self.from_encoding:
                    data = force_str(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
            except UnicodeDecodeError as e:
                return HttpResponse(_(u"<h1>Imported file has a wrong encoding: %s</h1>" % e))
            except Exception as e:
                return HttpResponse(_(u"<h1>%s encountered while trying to read file: %s</h1>" % (type(e).__name__, import_file.name)))
            
                        # prepare kwargs for import data, if needed
            res_kwargs = self.get_import_resource_kwargs(request, form=form, *args, **kwargs)
            resource = self.get_import_resource_class()(**res_kwargs)

            # prepare additional kwargs for import_data, if needed
            imp_kwargs = self.get_import_data_kwargs(request, form=form, *args, **kwargs)
            result = resource.import_data(dataset, dry_run=True,
                                          raise_errors=False,
                                          file_name=import_file.name,
                                          user=request.user,
                                          **imp_kwargs)

            context['result'] = result

            if not result.has_errors() and not result.has_validation_errors():
                initial = {
                    'import_file_name': tmp_storage.name,
                    'original_file_name': import_file.name,
                    'input_format': form.cleaned_data['input_format'],
                }
                confirm_form = self.get_confirm_import_form()
                initial = self.get_form_kwargs(form=form, **initial)
                context['confirm_form'] = confirm_form(initial=initial)

        else:
            res_kwargs = self.get_import_resource_kwargs(request, form=form, *args, **kwargs)
            resource = self.get_import_resource_class()(**res_kwargs)

        context['title'] = _("Import")
        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in resource.get_user_visible_fields()]
        
        request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.import_template_name], context)

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

admin.site.register(Kodverk, KodverkManager)
admin.site.register(Kodtext, KodtextManager)
#admin.site.register(ExternaKodverk)
admin.site.register(MappadTillKodtext, MappadtillKodtextManager)
admin.site.register(Nyckelord)

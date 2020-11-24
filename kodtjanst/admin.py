from django.contrib import admin

from .models import Kodverk, Kodtext
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse
from django import forms
from django.forms import ModelChoiceField

from .models import *
from .forms import MappadTillKodtextForm
from .custom_filters import DuplicatKodverkFilter, DuplicateKodtextFilter

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
    }
    ]]

    # def has_changed(self):
    #     """Returns True for new instances, calls super() for ones that exist in db.
    #     Prevents forms with defaults being recognized as empty/unchanged."""
    #     return not self.instance.pk or super().has_changed()

class NyckelOrdInline(admin.TabularInline):
    model = Nyckelord
    extra = 1

    fieldsets = [
    [None, {
    'fields': [('nyckelord')],
    }
    ]]

class ÄmneInline(admin.TabularInline):
    model = Ämne
    extra = 1

    fieldsets = [
    [None, {
    'fields': [('domän_namn', 'domän_kontext')],
    }
    ]]

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
                obj.kodverk.titel_på_kodverk)
            #for kodv in obj.kodverk
        ])
        
        if display_text:
            return mark_safe(display_text)
        return "-"
    
    kodverk_grupp.short_description = 'Kodverk'

    search_fields = ('kodverk__titel_på_kodverk', 'kodtext')

    def save_model(self, request, obj, form, change):
            if not obj.pk:
                # Only set added_by during the first save.
                obj.added_by = request.user
            super().save_model(request, obj, form, change)


def make_unpublished(modeladmin, request, queryset):
    
    queryset.update(status='Publicera ej')
make_unpublished.short_description = "Markera kodverk som Publicera ej"

class KodverkManager(admin.ModelAdmin):  


    inlines = [KodtextInline, NyckelOrdInline, ÄmneInline]

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
        ('kategori', 'ägare_till_kodverk'),
        ('hämtnings_källa', 'version_av_källa'),
        ('version', 'uppdateringsintervall', 'mappning_för_rapportering'),
        'extra_data'],
        }],
    ]

    def save_model(self, request, obj, form, change):
        
        obj.ändrad_av_id = request.user.id
        super().save_model(request, obj, form, change)

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
                return HttpResponse(_(f"<h1>Imported file has a wrong encoding: {e}</h1>"))
            except Exception as e:
                return HttpResponse(_(f"<h1>{type(e).__name__} encountered while trying to read file: {import_file.name}</h1>"))
            
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


class KodtextIdandTextField(forms.ModelChoiceField):

     def label_from_instance(self, obj):
         return f"{obj.id} - {obj.kodtext}"

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
        #set_trace()
        if db_field.name == "kodtext":
            kwargs["queryset"] = Kodtext.objects.all()
            return KodtextIdandTextField(queryset=Kodtext.objects.all())
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

        # return super(MappadtillKodtextManager, self).formfield_for_foreignkey(db_field, request, **kwargs)
        

    def get_form(self, request, obj=None, **kwargs):
        form = super(MappadtillKodtextManager, self).get_form(request, obj, **kwargs)
        form.base_fields['kodverk'].initial =  Kodverk.objects.filter(titel_på_kodverk=obj.kodtext.kodverk.titel_på_kodverk).values()[0].get('titel_på_kodverk')
        #set_trace()
        #form.base_fields['kodtext_text'] =  Kodtext.objects.filter(kodtext=obj.kodtext.kodtext)
        return form

    # def get_fieldsets(self, request, obj=None):
    #     fieldsets = super(MappadtillKodtextManager, self).get_fieldsets(request, obj)
    #     set_trace()
    #     form = self.get_formset(request).form
    #     set_trace()
    #     return fieldsets

    # def get_form(self, request, obj=None, **kwargs):
    #     set_trace()
    #     form = super(InvoiceAdmin, self).get_form(request, obj, **kwargs)
    #     form.base_fields['person'].label_from_instance = lambda obj: "{} {}".format(obj.id, obj.first_name)
    #     return form
    
    def save(self, commit=True):
        extra_field = self.cleaned_data.get('kodverk', None)
        # ...do something with extra_field here...
        return super(form, self).save(commit=commit)
    
    def kodverk_grupp(self, obj):
        
        display_text = ", ".join([
            "<a href={}>{}</a>".format(
                reverse('admin:{}_{}_change'.format(obj._meta.app_label, 'kodverk'),
                args=(obj.kodtext.kodverk.id,)),
                obj.kodtext.kodverk.titel_på_kodverk)
           
        ]).replace(' ' ,'_')
        print(display_text)
    
    kodverk_grupp.short_description = 'Kodverk'

admin.site.register(Kodverk, KodverkManager)
admin.site.register(Kodtext, KodtextManager)
#admin.site.register(ExternaKodverk)
admin.site.register(MappadTillKodtext, MappadtillKodtextManager)
admin.site.register(Nyckelord)
admin.site.register(Ämne)

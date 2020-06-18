from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Kodverk, Kodtext

from .models import Kodverk, Kodtext, ExternaKodverk, MappadTillKodtext, Nyckelord
from import_export import resources

admin.site.site_header = "OLLI Kodtjänst Admin"
admin.site.site_title = "OLLI Kodtjänst Admin Portal"
admin.site.index_title = "Välkommen till OLLI Kodtjänst Portalen"

class KodtextManager(admin.ModelAdmin):

    list_display = ('kodtext', 
                    'definition',
                    'andra_definition',
                    'kodverk',)

class KodverkResource(resources.ModelResource):

    class Meta:
        model = Kodverk

class KodverkManager(ImportExportModelAdmin):  

    list_display = ('kodverk_variant',
                    'urval_referens',
                    'syfte',
                    'rubrik_på_kodverk',
                    'kort_beskrivning',
                    'giltig_från',
                    'giltig_tom',
                    'kodschema',
                    'identifier',
                    'version',
                    'källa',
                    'kodverk_variant',
                    'instruktion_för_kodverket',
                    'ändrad_av',
                    'ägare_av_kodverk',
                    'ansvarig',
                    'mappning_för_rapportering',
                    'språk',
                    'uppdateringsintervall',
                    'version_av_källa',
                    'system_som_använderkodverket',
                    'kategori',
                    'beskrivning_av_informationsbehov')
    
admin.site.register(Kodverk, KodverkManager)
admin.site.register(Kodtext, KodtextManager)
admin.site.register(ExternaKodverk)
admin.site.register(MappadTillKodtext)
admin.site.register(Nyckelord)


from django.contrib import admin
from .models import Kodverk, Kodtext, ExternaKodverk, MappadTillKodtext

admin.site.site_header = "OLLI Kodtjänst Admin"
admin.site.site_title = "OLLI Kodtjänst Admin Portal"
admin.site.index_title = "Välkommen till OLLI Kodtjänst Portalen"

class KodtextManager(admin.ModelAdmin):

    list_display = ('kodtext', 
                    'definition',
                    'andra_definition',
                    'kodverk',)

admin.site.register(Kodverk)
admin.site.register(Kodtext,KodtextManager)
admin.site.register(ExternaKodverk)
admin.site.register(MappadTillKodtext)


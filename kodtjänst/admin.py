from django.contrib import admin
from .models import Kodverk, Kodtext, ExternaKodverk, MappadTillKodtext

class KodtextManager(admin.ModelAdmin):

    list_display = ('kodtext', 
                    'definition',
                    'andra_definition',
                    'kodverk',)

admin.site.register(Kodverk)
admin.site.register(Kodtext,KodtextManager)
admin.site.register(ExternaKodverk)
admin.site.register(MappadTillKodtext)


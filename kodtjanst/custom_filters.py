from django.contrib.admin import SimpleListFilter
from django.db.models import Count

from pdb import set_trace
from .models import Kodtext

class DuplicatKodverkFilter(SimpleListFilter):
    """
        This filter is being used in django admin panel.
        """
    title = 'Duplicates'
    parameter_name = 'id'

    def lookups(self, request, model_admin):
            return (
                ('duplicates', 'Duplicates'),
            )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value().lower() == 'duplicates':
            #set_trace()
            return queryset.filter().exclude(titel_på_kodverk__in=[element_id.get('titel_på_kodverk)') for element_id in queryset.values("titel_på_kodverk").distinct()])

class DuplicateKodtextFilter(SimpleListFilter):
    """
        This filter is being used in django admin panel.
    """
    
    title = 'Kodtext dubbletter'
    parameter_name = 'kodtext'

    def lookups(self, request, model_admin):

        return (('dubbletter', 'Dubbletter'),)

    def queryset(self, request, queryset):
        
        if not self.value():
            return queryset
        if self.value().lower() == 'dubbletter':
            duplicate_names = Kodtext.objects.values('kodtext').annotate(Count('kodtext')).order_by().filter(kodtext__count__gt=1)
            
            # You can then retrieve all these duplicate objects using this query:
            
            duplicate_objects = Kodtext.objects.filter(kodtext__in=[item['kodtext'] for item in duplicate_names]).order_by('kodtext','kodverk')

            return duplicate_objects


class SwedishLettersinKodFilter(SimpleListFilter):

    title = "Svenska bokstäver i kod"
    parameter_name = 'q'


    def lookups(self, request, model_admin):
        return (
            ('ÄäÅåÖö', 'ÄäÅåÖö'),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        
        queryset = Kodtext.objects.all()

        for letter in ['ÄÅÖ']:
            queryset.filter(kod__icontains=letter)
        return queryset
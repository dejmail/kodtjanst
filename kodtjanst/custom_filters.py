from django.contrib.admin import SimpleListFilter
from pdb import set_trace

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
    title = 'Duplicates'
    parameter_name = 'kodtext'

    def lookups(self, request, model_admin):
            return (
                ('duplicates', 'Duplicates'),
            )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value().lower() == 'duplicates':
            #set_trace()
            return queryset.filter().exclude(kodtext__in=[element_id.get('kodtext') for element_id in queryset.values("kodtext").distinct()])
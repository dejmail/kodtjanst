from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Kodverk, Kodtext
from pdb import set_trace

class SenasteKodverkFlöde(Feed):
    title = "VGR IS - Nya kodverk"
    link = "/nyakodverk/"
    description = "Nya publicerade kodverk."

    def items(self):
        return Kodverk.objects.filter(status='Aktiv').order_by('-datum_skapat')[:5]

    def item_title(self, item):
        return item.titel_på_kodverk

    def item_description(self, item):
        return item.beskrivning_av_innehållet

class ÄndringariKodverkFlöde(Feed):
    title = "VGR IS - Kodverk förändringar"
    link = "/ändradkodverk/"
    description = "Ändringar och tillägg till kodverk och kodtexter."
    description_template = "feeds/kodverk_feed.html"
    
    def item_title(self, item):
        return item.titel_på_kodverk

    def get_context_data(self, **kwargs):
        context = super(ÄndringariKodverkFlöde, self).get_context_data(**kwargs)
        
        context['history'] = self.item_history_delta(context.get('obj').id)
        return context

    def item_link(self, item):
        return reverse('show_kodverk_history', args=[item.pk])
        
    def items(self):
        history = []
        for entry in Kodverk.objects.filter(status="Aktiv"):
            if entry.history.exists():
                history.append(entry.id)
        return Kodverk.objects.filter(id__in=history)

    def item_history_delta(self, id):
    
        history_qs = Kodtext.history.filter(kodverk__id=id)
        list_of_changes = []
        for history in history_qs:
            if history.prev_record:
                list_of_changes.append([history.history_date, history.diff_against(history.prev_record)])
        return list_of_changes
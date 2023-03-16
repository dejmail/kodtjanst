from django.db import models

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import JSONField
from django.urls import reverse

from pdb import set_trace
import datetime
import os
from kodtjanst.utils import make_string_html_safe

from simple_history.models import HistoricalRecords

statuser = [("Publicera ej","Publicera ej"),
            ("Beslutad", "Beslutad"),
            ("Utkast", "Utkast"),
            ("Okänt", "Okänt")]


class Kodtext(models.Model):

    class Meta:
        verbose_name_plural = "Kodtexter"
    
    annan_kodtext = models.CharField(max_length=255, null=True, blank=True)
    datum_skapat = models.DateField(auto_now_add=True)
    definition = models.TextField(max_length=500, null=True, blank=True)
    extra_data = JSONField(
        null=True, 
        blank=True, 
        help_text='Data behöver vara i JSON format dvs {"nyckel" : "värde"}`\
          <br> t.ex {"Alternativ kod": 22897599} och kan ha flera, hierarkiska nivåer',
        verbose_name="ExtraInfo")

    kod = models.CharField(max_length=255, null=True,blank=True)
    kodtext = models.CharField(max_length=255, null=True)
    kodverk = models.ForeignKey(to='Kodverk', to_field='id', on_delete=models.CASCADE)
    kommentar = models.TextField(null=True, blank=True)
    position = models.PositiveIntegerField(null=True,blank=True)
    senaste_ändring = models.DateField(auto_now=True, blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True, choices=statuser)
    ändrad_av = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)

    history = HistoricalRecords(excluded_fields=['datum_skapat'])

    def __str__(self):
        return str(self.id)

class ExternaKodtext(models.Model):

    class Meta:
        verbose_name_plural = "Externa Kodtexter"
        verbose_name = "Extern Kodtext"
    
    #kodtext = models.ForeignKey(to='Kodtext', to_field='id', on_delete=models.CASCADE)
    kodverk = models.ForeignKey(to='Kodverk', to_field='id', on_delete=models.CASCADE)
    mappad_id = models.CharField(max_length=255)
    mappad_text = models.CharField(max_length=255)
    resolving_url = models.URLField()
    kommentar = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.mappad_text

class ExternaKodverk(models.Model):

    class Meta:
        verbose_name_plural = "Externa Kodverk"

    namn = models.CharField(max_length=255)
    url = models.URLField()
    kodterm_url = models.URLField(null=True)    




# class KodverkVariations(models.Model):

#     class Meta:
#         verbose_name_plural = "Kodverk varianter"

#     kodverk_typ = models.CharField(choices=[('VGR kodverk', 'VGR kodverk'), 
#                    ('Externt kodverk hänvisning', 'Externt kodverk hänvisning'),
#                    ('VGR codeable concept','VGR codeable concept')], max_length=30)

class Kodverk(models.Model):

    class Meta:
        verbose_name_plural = "Kodverk"

    kodverk_typer = [('Inget','Inget'),
                     ('Administrativ','Administrativ'),
                     ('Klinisk','Klinisk')]

    intervall = [('Årligen','Årligen'),
                 ('Halvårsvis' ,'Halvårsvis'),
                 ('Vid behov', 'Vid behov')]

    statuser = [("Publicera ej","Publicera ej"),
                ("Aktiv", "Aktiv"),
                ('Inaktiv', 'Inaktiv')]

    kodverk_typ = [('VGR kodverk', 'VGR kodverk'), 
                   ('Externt kodverk hänvisning', 'Externt kodverk hänvisning'),
                   ('VGR codeable concept','VGR codeable concept')]

    syfte = models.TextField(max_length=1000, null=True)
    beskrivning_av_innehållet = models.TextField(null=True,blank=True, verbose_name='Beskrivning av innehållet')
    identifierare = models.CharField(max_length=255,null=True, blank=True)
    titel_på_kodverk = models.CharField(max_length=255, null=True, verbose_name="Namn")
    version = models.FloatField(validators=[MinValueValidator(0.01)], null=True, default=None)
    
    kategori = models.CharField(max_length=255,null=True)
    länk = models.URLField(null=True,blank=True)
    kodverk_variant = models.CharField(max_length=26, null=True, blank=True, choices=kodverk_typ, help_text='Kodtext fält kommer ändras efter sparande, beroende på valet.')
    status = models.CharField(max_length=25, blank=True, null=True, choices=statuser)
    uppdateringsintervall =  models.CharField(max_length=20, null=True, choices=intervall, blank=True)
        
    datum_skapat = models.DateField(auto_now_add=True)
    senaste_ändring = models.DateField(auto_now=True, blank=True, null=True)
    giltig_från = models.DateField(null=True, blank=True)
    giltig_tom = models.DateField(default= datetime.date(2099, 12, 31), null=True, blank=True)
    ändrad_av = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ändrad_av_person')

    extra_data = JSONField(null=True, blank=True, help_text='Data behöver vara i JSON format dvs {"nyckel" : "värde"} <br> t.ex {"millenium_code_value": 22897599} och kan ha hierarkiska nivåer')
    
    ansvarig =  models.ForeignKey(User, on_delete=models.PROTECT, related_name='ansvarig_person', null=True, blank=True, verbose_name='Ansvarig person')
    urval_referens = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, help_text='Välja kodverket som är huvud kodverket')
    användning_av_kodverk = models.CharField(max_length=255, null=True, blank=True)

    #mall = models.ForeignKey(KodverkVariations, on_delete=models.PROTECT, related_name='mall')

    history = HistoricalRecords(excluded_fields=['datum_skapat'])

    def __str__(self):
        return self.titel_på_kodverk

    def get_absolute_url(self):
        return reverse('kodverk_komplett_metadata', kwargs={'kodverk_id' : str(self.id)})

    @property
    def beskrivning_av_innehållet_html(self):
        return make_string_html_safe(self.beskrivning_av_innehållet)

class CodeableConceptAttributes(models.Model):

    class Meta:
        verbose_name_plural = 'Attribut som kan ha flera värde'

    kodverk_from = models.ForeignKey(to='Kodverk', to_field='id', on_delete=models.CASCADE)
    källa = models.CharField(max_length=255,null=True, blank=True)
    version_av_källa = models.CharField(max_length=50, null=True, blank=True)
    ansvarig_förvaltare =  models.CharField(max_length=255, null=True)
    ägare_till_kodverk = models.CharField(max_length=255,null=True)

    history = HistoricalRecords()

    def __str__(self):
        
        return self.kodverk_from.titel_på_kodverk + " flera värde attribut"

class Nyckelord(models.Model):
    
    class Meta:
        verbose_name_plural = "Sökord"

    kodverk_from = models.ForeignKey(to='Kodverk', to_field='id', on_delete=models.CASCADE)
    nyckelord = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nyckelord

class MultiKodtextMapping(models.Model):

    text_description = models.CharField(max_length=255, blank=True, null=True)
    kodtext_from = models.ManyToManyField('Kodtext', related_name="field_from")
    kodtext_to = models.ManyToManyField('Kodtext', related_name="field_to")
    order_dictionary = JSONField(null=True, blank=True, help_text='Ordning av attributer som mappas')

    def __str__(self):
        return str(self.id)

    
class ArbetsKommentar(models.Model):
    class Meta:     
        verbose_name_plural = "Arbets Kommentar"

    id = models.AutoField(primary_key=True)
    kodverk = models.ForeignKey("Kodverk", to_field="id", on_delete=models.CASCADE, blank=True, null=True)
    angivet_av =  models.ForeignKey(User, on_delete=models.PROTECT, related_name='angivet_av', null=True, blank=True, verbose_name='Angivet av person')
    kommentar = models.TextField(max_length=5000, null=True, blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.kommentar

class CommentedKodverk(models.Model):
    class Meta:
        verbose_name_plural = "Kommenterade kodverk"
    
    id = models.AutoField(primary_key=True)
    kodverk = models.ForeignKey("kodverk", to_field="id", on_delete=models.CASCADE, blank=True, null=True)
    handläggare = models.ForeignKey(User, on_delete=models.PROTECT, related_name='kommentar_handläggare', null=True)
    datum_skapat = models.DateTimeField(auto_now_add=True)
    namn = models.CharField(max_length=255, null=True)
    epost = models.EmailField(null=True)
    kontakt = models.CharField(max_length=255, null=True)
    kommentar = models.TextField(max_length=2000, null=True)
    handläggnings_kommentar = models.TextField(max_length=2000, null=True)
    status = models.CharField(choices=[('Pågår','Pågår'),('Klart','Klart'),('Nytt', 'Nytt')], max_length=5, null=True)

    def __str__(self):
        return self.namn

class ValidatedBy(models.Model):
    class Meta:     
        verbose_name_plural = "Verifierad av"

    id = models.AutoField(primary_key=True)
    kodverk = models.ForeignKey("Kodverk", to_field="id", on_delete=models.CASCADE, blank=True, null=True)
    domän_kontext = models.TextField(max_length=2000, null=True, blank=True)
    domän_stream = models.CharField(max_length=255, null=True)
    domän_epost = models.EmailField(null=True)
    domän_telefon = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        if self.domän_stream is None:
            return '' 
        else:
            return self.domän_stream


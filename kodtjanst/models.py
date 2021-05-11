from django.db import models

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import JSONField
from pdb import set_trace
import datetime
import os

from django.db.models import signals
from django.db.models.signals import pre_save
from kodtjanst.custom_signals import has_uploaded_file_been_deleted

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
    extra_data = JSONField(null=True, blank=True, help_text='Data behöver vara i JSON format dvs {"nyckel" : "värde"} <br> t.ex {"millenium_code_value": 22897599} och kan ha hierarkiska nivåer')
    kod = models.CharField(max_length=255, null=True,blank=True)
    kodtext = models.CharField(max_length=255, null=True)
    kodverk = models.ForeignKey(to='Kodverk', to_field='id', on_delete=models.CASCADE)
    kommentar = models.TextField(null=True, blank=True)
    position = models.PositiveIntegerField(null=True,blank=True)
    senaste_ändring = models.DateField(auto_now=True)
    status = models.CharField(max_length=50, blank=True, null=True, choices=statuser)
    ändrad_av = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return str(self.id)

class ExternaKodtext(models.Model):

    class Meta:
        verbose_name_plural = "Externa Kodtext"

    kodtext = models.ForeignKey(to='Kodtext', to_field='id', on_delete=models.CASCADE)
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

    kodverk_typ = [('kodverk','kodverk'), 
                   ('codeable concept','codeable concept'),
                   ('code set','code set'), 
                   ('alpha response','alpha response'), 
                   ('urval','urval')]

    syfte = models.TextField(max_length=1000, null=True)
    beskrivning_av_innehållet = models.TextField(null=True,blank=True, verbose_name='Beskrivning av innehållet')
    identifier = models.CharField(max_length=255,null=True, blank=True)
    titel_på_kodverk = models.CharField(max_length=255, null=True)
    version = models.FloatField(validators=[MinValueValidator(0.01)], null=True, default=None)
    
    kategori = models.CharField(max_length=255,null=True)
    underlag = models.FileField(null=True,blank=True, upload_to='')
    länk_till_underlag = models.URLField(null=True,blank=True)
    kodverk_variant = models.CharField(max_length=17, null=True, blank=True, choices=kodverk_typ)
    status = models.CharField(max_length=25, blank=True, null=True, choices=statuser)
    uppdateringsintervall =  models.CharField(max_length=20, null=True, choices=intervall, blank=True)
        
    datum_skapat = models.DateField(auto_now_add=True)
    senaste_ändring = models.DateField(auto_now=True, blank=True, null=True)
    giltig_från = models.DateField(null=True)
    giltig_tom = models.DateField(default= datetime.date(2099, 12, 31), null=True)
    ändrad_av = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ändrad_av_person')

    extra_data = JSONField(null=True, blank=True, help_text='Data behöver vara i JSON format dvs {"nyckel" : "värde"} <br> t.ex {"millenium_code_value": 22897599} och kan ha hierarkiska nivåer')
    
    ansvarig =  models.ForeignKey(User, on_delete=models.PROTECT, related_name='ansvarig_person', null=True, blank=True, verbose_name='Ansvarig person')
    urval_referens = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, help_text='Välja kodverket som är huvud kodverket')
    användning_av_kodverk = models.CharField(max_length=255, null=True, blank=True)    

    def __str__(self):
        return self.titel_på_kodverk

pre_save.connect(has_uploaded_file_been_deleted, sender=Kodverk)


class CodeableConceptAttributes(models.Model):

    class Meta:
        verbose_name_plural = 'Attribut som kan ha flera värde'

    kodverk_from = models.ForeignKey(to='Kodverk', to_field='id', on_delete=models.CASCADE)
    källa = models.CharField(max_length=255,null=True, blank=True)
    version_av_källa = models.CharField(max_length=50, null=True, blank=True)
    ansvarig_förvaltare =  models.CharField(max_length=255, null=True)
    ägare_till_kodverk = models.CharField(max_length=255,null=True)

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
    kodtext_from = models.ManyToManyField('Kodtext', related_name="field_from")#, on_delete=models.PROTECT)
    kodtext_to = models.ManyToManyField('Kodtext', related_name="field_to")#, on_delete=models.PROTECT)
    order_dictionary = JSONField(null=True, blank=True, help_text='Ordning av attributer som mappas')

    def __str__(self):
        return str(self.id)

    
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

class CommentedKodverk(models.Model):
    class Meta:
        verbose_name_plural = "Kommenterade kodverk"
    
    id = models.AutoField(primary_key=True)
    kodverk = models.ForeignKey("kodverk", to_field="id", on_delete=models.CASCADE, blank=True, null=True)
    comment_datum = models.DateTimeField(auto_now_add=True)
    comment_name = models.CharField(max_length=255, null=True)
    comment_epost = models.EmailField(null=True)
    comment_telefon = models.CharField(max_length=255, null=True)
    comment_kontext = models.TextField(max_length=2000, null=True)
    comment_status = models.CharField(choices=[('Pågår','Pågår'),('Klart','Klart'),('Nytt', 'Nytt')], max_length=5, null=True)

    def __str__(self):
        return self.comment_name
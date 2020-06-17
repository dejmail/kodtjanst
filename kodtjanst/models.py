from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
#from .fields import JSONField
from django_mysql.models import JSONField, Model


class Kodtext(models.Model):

    class Meta:
        verbose_name_plural = "Kodtexter"
    
    andra_definition = models.TextField(max_length=500, null=True, blank=True)
    definition = models.TextField(max_length=500, null=True, blank=True)
    extra_data = JSONField(null=True)
    kod = models.CharField(max_length=255, null=True)
    kodtext = models.CharField(max_length=255)
    kodverk = models.ForeignKey(to='Kodverk', to_field='id', on_delete=models.PROTECT, default=11)
    kommentar = models.TextField(null=True)
    position = models.PositiveIntegerField(null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    ändrad_av = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.kodtext

class MappadTillKodtext(models.Model):

    class Meta:
        verbose_name_plural = "Mappad Kodtexter"

    kodtext = models.ForeignKey(to='Kodtext', to_field='id', on_delete=models.PROTECT)
    mappad_id = models.CharField(max_length=255, null=True)
    mappad_text = models.CharField(max_length=255, null=True)
    resolving_url = models.URLField()
    kommentar = models.TextField(null=True)

class ExternaKodverk(models.Model):

    class Meta:
        verbose_name_plural = "Externa Kodverk"

    namn = models.CharField(max_length=255)
    url = models.URLField()
    kodterm_url = models.URLField(null=True)    

class Kodverk(models.Model):

    class Meta:
        verbose_name_plural = "Kodverk"

    SPRÅK_CHOICES = [('svenska','svenska'),
                     ('engelska','engelska')]

    kodverk_typer = [('Inget','Inget'),
                     ('Administrativ','Administrativ'),
                     ('Klinisk','Klinisk')]

    kodverk_ägare = [('Inera','Inera'),
                     ('Socialstyrelsen','Socialstyrelsen'),
                     ('Västra Götalandsregionen','Västra Götalandsregionen')]

    intervall = [('Årligen','Årligen'), 
                 ('Månadsvis','Månadsvis'), 
                 ('Veckovis','Veckovis'),
                 ('Dagligen','Dagligen'),
                 ('Vid behov', 'Vid behov'),
                 ('Ej aktuellt', 'Ej aktuellt')]

    kodverk_typ = [('Kodverk','Kodverk'), 
                   ('Kodset','Kodset'), 
                   ('Alfa respons','Alfa respons'), 
                   ('Urval','Urval')]

    ansvarig =  models.ForeignKey(User, on_delete=models.PROTECT, related_name='ansvarig_person', null=True, blank=True)
    beskrivning_av_informationsbehov = models.TextField(null=True)
    giltig_från = models.DateField(null=True)
    giltig_tom = models.DateField(null=True)
    kommentar = models.TextField(null=True)
    identifier = models.CharField(max_length=255,null=True)
    instruktion_för_kodverket = models.CharField(max_length=255,null=True)
    extra_data = JSONField(null=True)
    kategori = models.CharField(max_length=255,null=True)
    kodschema = models.CharField(max_length=255,null=True)
    kodverk_variant = models.CharField(max_length=12, choices=kodverk_typ, null=True, blank=True)
    kort_beskrivning = models.TextField(max_length=1000, null=True)
    källa = models.CharField(max_length=255,null=True)
    mappning_för_rapportering = models.BooleanField(null=True)
    nyckelord = models.CharField(max_length=255, null=True, blank=True)
    rubrik_på_kodverk = models.CharField(max_length=255, null=True)
    senaste_ändring = models.DateField(blank=True, null=True)
    språk = models.CharField(max_length=25, choices=SPRÅK_CHOICES, default='svenska',null=True)
    status = models.CharField(max_length=25, blank=True ,null=True)
    syfte = models.TextField(max_length=1000, null=True)
    system_som_använderkodverket = models.CharField(max_length=255,null=True)
    uppdateringsintervall =  models.CharField(max_length=20, null=True, choices=intervall)
    urval_referens = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    version = models.FloatField(validators=[MinValueValidator(0.01)], null=True)
    version_av_källa = models.CharField(max_length=50,null=True)
    ägare_av_kodverk = models.CharField(max_length=255,null=True, choices=kodverk_ägare)
    #ämnesområde = models.CharField(max_length=255,null=True)
    ändrad_av = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ändrad_av_person')

    def __str__(self):
        return self.rubrik_på_kodverk

class Nyckelord(models.Model):
    
    class Meta:
        verbose_name_plural = "Nyckelord"

    kodverk_id = models.ForeignKey(to='Kodtext', to_field='id', on_delete=models.PROTECT)
    nyckelord = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nyckelord

class Ämne(models.Model):
    class Meta:     
        verbose_name_plural = "Ämnesområde"

    kodverk = models.ForeignKey("Kodverk", to_field="id", on_delete=models.PROTECT, blank=True, null=True)
    domän_id = models.AutoField(primary_key=True)
    domän_kontext = models.TextField(null=True)
    domän_namn = models.CharField(max_length=255)       

    def __str__(self):
        return self.domän_namn
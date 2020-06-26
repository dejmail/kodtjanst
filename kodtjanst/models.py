from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
#from .fields import JSONField
from django_mysql.models import JSONField, Model
from pdb import set_trace

statuser = [("Design","Design"),
            ("Bygg", "Bygg"),
            ("Beslutad", "Beslutad"),
            ("Utjast", "Utkast"),
            ("Okänt", "Okänt")]


class Kodtext(models.Model):

    class Meta:
        verbose_name_plural = "Kodtexter"
    
    annan_kodtext = models.CharField(max_length=255, null=True, blank=True)
    definition = models.TextField(max_length=500, null=True, blank=True)
    extra_data = JSONField(null=True)
    kod = models.CharField(max_length=255, null=True,blank=True)
    kodtext = models.CharField(max_length=255, null=True)
    kodverk = models.ForeignKey(to='Kodverk', to_field='id', on_delete=models.PROTECT, default=11)
    kommentar = models.TextField(null=True)
    position = models.PositiveIntegerField(null=True)
    status = models.CharField(max_length=50, blank=True, null=True, choices=statuser)
    ändrad_av = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return str(self.id)

class MappadTillKodtext(models.Model):

    class Meta:
        verbose_name_plural = "Mappad Kodtexter"

    kodtext = models.ForeignKey(to='Kodtext', to_field='id', on_delete=models.PROTECT)
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

    SPRÅK_CHOICES = [('svenska','svenska'),
                     ('engelska','engelska')]

    kodverk_typer = [('Inget','Inget'),
                     ('Administrativ','Administrativ'),
                     ('Klinisk','Klinisk')]

    #kodverk_ägare = [('Inera','Inera'),
    #                 ('Socialstyrelsen','Socialstyrelsen'),
    #                 ('Västra Götalandsregionen','Västra Götalandsregionen')]

    intervall = [('Årligen','Årligen'), 
                 ('Månadsvis','Månadsvis'), 
                 ('Veckovis','Veckovis'),
                 ('Dagligen','Dagligen'),
                 ('Vid behov', 'Vid behov'),
                 ('Ej aktuellt', 'Ej aktuellt')]

    statuser = [("Design","Design"),
                ("Bygg", "Bygg"),
                ("Beslutad", "Beslutad"),
                ("Utjast", "Utkast"),
                ("Okänt", "Okänt")]

    kodverk_typ = [('kodverk','kodverk'), 
                   ('code set','code set'), 
                   ('alpha response','alpha response'), 
                   ('urval','urval')]

    ansvarig =  models.ForeignKey(User, on_delete=models.PROTECT, related_name='ansvarig_person', null=True, blank=True)
    beskrivning_av_informationsbehov = models.TextField(null=True,blank=True)
    giltig_från = models.DateField(null=True, blank=True)
    giltig_tom = models.DateField(null=True, blank=True)
    kommentar = models.TextField(null=True,blank=True)
    identifier = models.CharField(max_length=255,null=True, blank=True)
    instruktion_för_kodverket = models.CharField(max_length=255,null=True,blank=True)
    extra_data = JSONField(null=True, help_text='Data behöver vara i JSON format dvs {"nyckel" : "värde"} <br> t.ex {"millenium_code_value": 22897599} och kan kan hierarkiska nivåer', blank=True)
    kategori = models.CharField(max_length=255,null=True)
    kodschema = models.CharField(max_length=255,null=True, blank=True)
    kodverk_variant = models.CharField(max_length=14, null=True, blank=True, choices=kodverk_typ)
    kort_beskrivning = models.TextField(max_length=1000, null=True, blank=True)
    källa = models.CharField(max_length=255,null=True, blank=True)
    mappning_för_rapportering = models.BooleanField(null=True)
    nyckelord = models.CharField(max_length=255, null=True, blank=True)
    rubrik_på_kodverk = models.CharField(max_length=255, null=True)
    senaste_ändring = models.DateField(blank=True, null=True)
    språk = models.CharField(max_length=25, choices=SPRÅK_CHOICES, default='svenska',null=True)
    status = models.CharField(max_length=25, blank=True, null=True, choices=statuser)
    syfte = models.TextField(max_length=1000, null=True,blank=True)
    system_som_använderkodverket = models.CharField(max_length=255,null=True,blank=True)
    uppdateringsintervall =  models.CharField(max_length=20, null=True, choices=intervall, blank=True)
    urval_referens = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, help_text='Välja kodverket som är huvud kodverket')
    version = models.FloatField(validators=[MinValueValidator(0.01)], null=True, blank=True)
    version_av_källa = models.CharField(max_length=50,null=True, blank=True)
    ägare_av_kodverk = models.CharField(max_length=255,null=True)#, choices=kodverk_ägare)
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
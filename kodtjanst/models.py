from django.db import models

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import JSONField
from pdb import set_trace
import datetime

statuser = [('Publicera ej','Publicera ej'),
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

    # SPRÅK_CHOICES = [('svenska','svenska'),
    #                  ('engelska','engelska')]

    kodverk_typer = [('Inget','Inget'),
                     ('Administrativ','Administrativ'),
                     ('Klinisk','Klinisk')]

    kodverk_ägare = [('Informatik','Informatik'),
                    ('Inera','Inera'),
                    ('Socialstyrelsen','Socialstyrelsen'),
                    ('Västra Götalandsregionen','Västra Götalandsregionen'),
                    ('Skatteverket','Skatteverket'),
                    ('Snomed International','Snomed International')]

    intervall = [('Årligen','Årligen'), 
                 ('Månadsvis','Månadsvis'), 
                 ('Veckovis','Veckovis'),
                 ('Dagligen','Dagligen'),
                 ('Vid behov', 'Vid behov'),
                 ('Ej aktuellt', 'Ej aktuellt')]

    statuser = [("Publicera ej","Publicera ej"),
                ("Beslutad", "Beslutad")]

    kodverk_typ = [('kodverk','kodverk'), 
                   ('code set','code set'), 
                   ('alpha response','alpha response'), 
                   ('urval','urval')]

    syfte = models.TextField(max_length=1000, null=True)
    beskrivning_av_informationsbehov = models.TextField(null=True,blank=True)
    identifier = models.CharField(max_length=255,null=True, blank=True)
    titel_på_kodverk = models.CharField(max_length=255, null=True)
    ägare_till_kodverk = models.CharField(max_length=255,null=True, choices=kodverk_ägare)
    version = models.FloatField(validators=[MinValueValidator(0.01)], null=True, default=None)
    hämtnings_källa = models.CharField(max_length=255,null=True, blank=True)

    version_av_källa = models.CharField(max_length=50, null=True, blank=True)
    kategori = models.CharField(max_length=255,null=True)
    instruktion_för_kodverket = models.CharField(max_length=255,null=True,blank=True)
    kodverk_variant = models.CharField(max_length=14, null=True, blank=True, choices=kodverk_typ)
    status = models.CharField(max_length=25, blank=True, null=True, choices=statuser)
    uppdateringsintervall =  models.CharField(max_length=20, null=True, choices=intervall, blank=True)
    mappning_för_rapportering = models.BooleanField(null=True)

    
    ansvarig_förvaltare =  models.CharField(max_length=255, null=True)
    datum_skapat = models.DateField(auto_now_add=True)
    senaste_ändring = models.DateField(auto_now=True, blank=True, null=True)
    giltig_från = models.DateField(null=True)
    giltig_tom = models.DateField(default= datetime.date(2099, 12, 31), null=True)
    ändrad_av = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ändrad_av_person')

    extra_data = JSONField(null=True, blank=True, help_text='Data behöver vara i JSON format dvs {"nyckel" : "värde"} <br> t.ex {"millenium_code_value": 22897599} och kan ha hierarkiska nivåer')
    
    ansvarig =  models.ForeignKey(User, on_delete=models.PROTECT, related_name='ansvarig_person', null=True, blank=True)
    urval_referens = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, help_text='Välja kodverket som är huvud kodverket')
    användning_av_kodverk = models.CharField(max_length=255, null=True, blank=True)
    
    #kommentar = models.TextField(null=True, blank=True)    
    #kodschema = models.CharField(max_length=255,null=True, blank=True)    
    #kort_beskrivning = models.TextField(max_length=1000, null=True, blank=True)    
    #ägare_till_kodverk = models.CharField(max_length=255, null=True, blank=True)    
    #språk = models.CharField(max_length=25, choices=SPRÅK_CHOICES, default='svenska',null=True)    
    
    
    
    
#    ämnesområde = models.CharField(max_length=255,null=True, blank=True)
    

    def __str__(self):
        return self.titel_på_kodverk

class Nyckelord(models.Model):
    
    class Meta:
        verbose_name_plural = "Nyckelord"

    kodverk_id = models.ForeignKey(to='Kodverk', to_field='id', on_delete=models.CASCADE)
    nyckelord = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nyckelord

class Ämne(models.Model):
    class Meta:     
        verbose_name_plural = "Ämnesområde"

    id = models.AutoField(primary_key=True)
    kodverk = models.ForeignKey("Kodverk", to_field="id", on_delete=models.CASCADE, blank=True, null=True)
    domän_kontext = models.TextField(null=True, blank=True)
    domän_namn = models.CharField(max_length=255)       

    def __str__(self):
        return self.domän_namn
from django.db import models
from django.contrib.auth.models import User


class Kodtext(models.Model):
    
    kodtext = models.CharField(max_length=255)
    kod = models.CharField(max_length=255)
    definition = models.TextField(max_length=500, null=True)
    andra_definition = models.TextField(max_length=500, null=True)
    kodverk = models.ForeignKey(to='Kodverk', to_field='id', on_delete=models.PROTECT, default=11)
    position = models.IntegerField()

    def __str__(self):
        return self.code_text

class MappadTillKodtext(models.Model):

    code = models.ForeignKey(to='Kodtext', to_field='id', on_delete=models.PROTECT)
    mappad_id = models.CharField(max_length=255)
    mappad_kodverk = models.URLField()

class ExternaKodverk(models.Model):

    namn = models.CharField(max_length=255)
    url = models.URLField()
    kodterm_url = models.URLField(null=True)    

class Kodverk(models.Model):

    SPRÅK_CHOICES = [('svenska','svenska'),
                     ('engelska','engelska')]

    är_ett_urval = models.BooleanField(null=True)
    syfte = models.TextField(max_length=1000, null=True)
    rubrik_på_kodverk = models.CharField(max_length=255, null=True)
    kort_beskrivning = models.TextField(max_length=1000, null=True)
    giltig_från = models.DateField(null=True)
    giltig_tom = models.DateField(null=True)
    kodschema = models.CharField(max_length=255,null=True)
    identifier = models.CharField(max_length=255,null=True)
    version = models.FloatField(null=True)
    källa = models.CharField(max_length=255,null=True)
    typ_av_kodverk = models.CharField(max_length=255,null=True)
    ämnesområde = models.CharField(max_length=255,null=True)
    #Länk till Kodverk - det blir url
    instruktion_för_kodverket = models.CharField(max_length=255,null=True)
    ändrad_av = models.ForeignKey(User, on_delete=models.PROTECT)
    ägare = models.CharField(max_length=255,null=True)
    ansvarig = models.CharField(max_length=255,null=True)
    mappning_för_rapportering = models.BooleanField(null=True)
    #Sökord
    språk = models.CharField(max_length=25, choices=SPRÅK_CHOICES, default='svenska',null=True)
    uppdateringsintervall =  models.DurationField(null=True)
    version_av_källa = models.CharField(max_length=50,null=True)
    system_som_använderkodverket = models.CharField(max_length=255,null=True)
    kategori = models.CharField(max_length=255,null=True)
    #antal koder i kodverket
    beskrivning_av_informationsbehov = models.TextField(null=True)

    def __str__(self):
        return self.rubrik_på_kodverk
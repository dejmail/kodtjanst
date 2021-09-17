from django.test import TestCase

from kodtjanst.models import Kodverk
from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404
import datetime

class KodverkModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        User.objects.create(username='vgrinfor')
        user = get_object_or_404(User, username='vgrinfor')
        Kodverk.objects.create(titel_på_kodverk='test_kodverk', 
        syfte='syfte for the test', 
        version='1', 
        datum_skapat=datetime.datetime.now(),
        ändrad_av=user)
    
    def test_beskrivning_av_innehållet(self):
        kodverk = Kodverk.objects.get(id=1)
        field_label = kodverk._meta.get_field('beskrivning_av_innehållet').verbose_name
        self.assertEqual(field_label, 'Beskrivning av innehållet')
    
    
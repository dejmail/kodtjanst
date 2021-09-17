from django.test import TestCase, Client
from django.urls import reverse

from kodtjanst.models import Kodverk

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from random import randint
from pdb import set_trace

from datetime import datetime

class KodverkListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create 10 kodverk for tests
        number_of_kodverk = 10

        User.objects.create(username='vgrinfor')
        user = get_object_or_404(User, username='vgrinfor')

        for kodverk_id in range(number_of_kodverk):
            Kodverk.objects.create(titel_på_kodverk=f'test_kodverk-{kodverk_id}', 
                                   syfte=f'syfte for the test-{kodverk_id}', 
                                   version='1', 
                                   datum_skapat=datetime.now(),
                                   ändrad_av=user)

    def test_view_url_exists_at_desired_location(self):
        
        response = self.client.get(f'/kodverk/metadata-och-kodtext/{randint(1,10)}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('kodverk_komplett_metadata', kwargs={'kodverk_id' : randint(1,10)}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('kodverk_komplett_metadata', args=[randint(1,10),]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kodverk_komplett_metadata.html')
    
    def test_return_all_aktiv_kodverk(self):

        queryset = Kodverk.objects.filter(status='Aktiv')

        test_client = Client()
        response = test_client.get('/q=?*all')
        set_trace()
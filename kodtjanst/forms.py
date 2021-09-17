from django import forms
from django.forms import ModelChoiceField
from django.forms.fields import ChoiceField
from .models import Kodtext, Kodverk, MultiKodtextMapping, CommentedKodverk, ArbetsKommentar
from django.contrib.auth import (
    authenticate,
    get_user_model

)

from pdb import set_trace

from .models import ExternaKodtext, Kodverk


class UserModelChoiceField(ModelChoiceField):
    ''' 
    A ModelChoiceField to represent User 
    select boxes in the Auto Admin 
    '''
    def label_from_instance(self, obj):

        return f"{obj.get_full_name()}"

kodverk_ägare = [('Informatik','Informatik'),
                ('Inera','Inera'),
                ('Socialstyrelsen','Socialstyrelsen'),
                ('Västra Götalandsregionen','Västra Götalandsregionen'),
                ('Skatteverket','Skatteverket'),
                ('Snomed International','Snomed International'),
                ('Equalis','Equalis')]

User = get_user_model()

class UserLoginForm(forms.Form):
    
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('This user does not exist')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect password')
            if not user.is_active:
                raise forms.ValidationError('This user is not active')
        return super(UserLoginForm, self).clean(*args, **kwargs)

class KodverkAdminForm(forms.ModelForm):

    ansvarig = UserModelChoiceField(User.objects.filter(first_name__isnull=False).exclude(first_name__exact='').order_by('first_name', 'last_name'), required=False)

    def __init__(self, *args, **kwargs):
        super(KodverkAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Kodverk
        fields = '__all__'

class ArbetsKommentarForm(forms.ModelForm):

    class Meta:
        model = ArbetsKommentar
        fields = ('kommentar',)

    kodverk = ModelChoiceField(Kodverk.objects.filter(status='Aktiv').order_by('titel_på_kodverk'), help_text="Bara kodverk med 'Aktiv' status visas")

    def __init__(self, *args, **kwargs):
        super(ArbetsKommentarForm, self).__init__(*args, **kwargs)

class KommentarAdminForm(forms.ModelForm):

    class Meta:
        model = CommentedKodverk
        fields = ('kodverk', 'handläggare', 'namn', 'epost', 'kontakt', 'kommentar', 'kommentar', 'handläggnings_kommentar', 'status',)
        exclude = ('kodverk_id',)

    handläggare = UserModelChoiceField(User.objects.filter(first_name__isnull=False).exclude(first_name__exact='').order_by('first_name', 'last_name'))

    def __init__(self, *args, **kwargs):
        super(KommentarAdminForm, self).__init__(*args, **kwargs)


class ExternaKodtextForm(forms.ModelForm):

    kodverk = forms.CharField(disabled=True)

    class Meta:
        model = ExternaKodtext
        fields = '__all__'
        
def beslutad_kodtext_choices():
    beslutad_kodtext = Kodtext.objects.filter(kodverk__status='Beslutad').all().values('id','kod','kodtext')
    return_list = []
    for index, choice in enumerate(beslutad_kodtext):
        try:
            built_choice = []
            if choice.get('kod') is not None:
                return_list.append((choice.get('id',''), choice.get('kod','')+' | ' + choice.get('kodtext','')))
            else:
                return_list.append((choice.get('id',''), 'Ingen kod' + ' | ' + choice.get('kodtext','')))
        except TypeError as e:
            print(e)            
    return tuple(return_list)

def beslutad_kodverk_choices():

    beslutad_kodverk_choices = [(i.get('id'), i.get('titel_på_kodverk')) for i in Kodverk.objects.filter(status='Beslutad').values('id','titel_på_kodverk')]
    beslutad_kodverk_choices.insert(0,('', 'Välja kodverk'))
    return tuple(beslutad_kodverk_choices)

class MultiMappingForm(forms.ModelForm):
    
    kodverk_from = forms.ChoiceField(choices=beslutad_kodverk_choices)
    kodtext_from = forms.MultipleChoiceField(choices=beslutad_kodtext_choices)

    kodverk_to = forms.ChoiceField(choices=beslutad_kodverk_choices)
    kodtext_to = forms.MultipleChoiceField(choices=beslutad_kodtext_choices)
    
    class Meta:
        model = MultiKodtextMapping
        fields = ('kodverk_from', 'kodtext_from', 'kodverk_to', 'kodtext_to','order_dictionary')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['kodtext_from'].help_text = 'Välja ett kodverk först'
        self.fields['kodtext_to'].help_text = 'Välja ett kodverk först'

    def clean_kodtext_from(self):
        data = self.cleaned_data['kodtext_from']
        return data

    def clean_order_dictionary(self):
        
        if self.cleaned_data['order_dictionary'] is None:
            return {"kodtext_från" : self.cleaned_data['kodtext_from'], 
            "kodtext_till" : self.cleaned_data['kodtext_to']}
        else:
            return self.cleaned_data['order_dictionary']

class KommenteraKodverk(forms.Form):

    namn = forms.CharField()
    epost = forms.EmailField()
    kontakt = forms.CharField(max_length=30, label="Kontakt", widget=forms.TextInput(attrs={'placeholder': "Teams namn eller telefon"}))
    kommentar = forms.CharField(widget=forms.Textarea, max_length=2000, label='Kommentar')
    kodverk = forms.CharField(widget=forms.HiddenInput())  

class VerifyKodverk(forms.Form):

    kodverk = forms.CharField(widget=forms.HiddenInput())  
    stream = forms.CharField(label='Vem är du? ex. soki/ws/organisation', required=True)
    epost = forms.EmailField()
    telefon = forms.CharField(max_length=30, label="Kontakt", widget=forms.TextInput(attrs={'placeholder': "Skypenamn eller telefon"}))
    kontext = forms.CharField(widget=forms.Textarea, max_length=2000, label='Specificera hur ni använder det')
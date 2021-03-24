from django import forms
from .models import Kodtext
from .models import Kodtext, Kodverk, MultiKodtextMapping
from django.contrib.auth import (
    authenticate,
    get_user_model

)

from pdb import set_trace

from .models import ExternaKodtext, Kodverk

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

    def __init__(self, *args, **kwargs):
        super(KodverkAdminForm, self).__init__(*args, **kwargs)
        # in case this comes in as csv string in which case it must be converted to a list
        self.initial['ägare_till_kodverk'] = [i.strip() for i in self.instance.ägare_till_kodverk.split(',')]
        
    ägare_till_kodverk = forms.MultipleChoiceField(choices = kodverk_ägare)

    class Meta:
        model = Kodverk
        fields = '__all__'

    def clean(self):
        # must be saved as a csv string in the db, otherwise we see a list structure
        self.cleaned_data['ägare_till_kodverk'] = ', '.join([i for i in self.cleaned_data['ägare_till_kodverk']])


class ExternaKodtextForm(forms.ModelForm):

    kodverk = forms.CharField(disabled=True)

    class Meta:
        model = ExternaKodtext
        fields = '__all__'

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'id':
    #         return KodtextIdandTextField(queryset=Kodtext.objects.all())
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)
        
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
    telefon = forms.CharField(max_length=30, label="Kontakt", widget=forms.TextInput(attrs={'placeholder': "Skypenamn eller telefon"}))
    kommentar_kontext = forms.CharField(widget=forms.Textarea, max_length=2000, label='Kommentar')
    kodverk = forms.CharField(widget=forms.HiddenInput())  

class VerifyKodverk(forms.Form):

    kodverk = forms.CharField(widget=forms.HiddenInput())  
    stream = forms.CharField(label='Vem är du? ex. soki/ws/organisation', required=True)
    epost = forms.EmailField()
    telefon = forms.CharField(max_length=30, label="Kontakt", widget=forms.TextInput(attrs={'placeholder': "Skypenamn eller telefon"}))
    kontext = forms.CharField(widget=forms.Textarea, max_length=2000, label='Specificera hur ni använder det')

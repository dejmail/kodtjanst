from django import forms
from .models import Kodtext, MultiKodtextMapping
from django.contrib.auth import (
    authenticate,
    get_user_model

)

from .models import ExternaKodtext

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

class ExternaKodtextForm(forms.ModelForm):

    kodverk = forms.CharField(disabled=True)

    class Meta:
        model = ExternaKodtext
        fields = '__all__'

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == 'id':
    #         return KodtextIdandTextField(queryset=Kodtext.objects.all())
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)
        

class MultiMappingForm(forms.ModelForm):

    kodverk_to = forms.CharField()
    kodverk_from = forms.CharField()

    class Meta:
        model = MultiKodtextMapping
        fields = ('kodverk_from', 'kodtext_from', 'kodtext_to','kodtext_to', 'order_dictionary')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_trace()
        self.fields['kodtext_from'].queryset = Kodtext.objects.none()
        self.fields['kodtext_to'].queryset = Kodtext.objects.none()


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

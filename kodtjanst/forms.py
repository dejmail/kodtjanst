from django import forms
from django.contrib.auth import (
    authenticate,
    get_user_model

)

from .models import MappadTillKodtext

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

class MappadTillKodtextForm(forms.ModelForm):

    kodverk = forms.CharField(disabled=True)

    class Meta:
        model = MappadTillKodtext
        fields = '__all__'



class KommenteraKodverk(forms.Form):

    namn = forms.CharField()
    epost = forms.EmailField()
    telefon = forms.CharField(max_length=30, label="Kontakt", widget=forms.TextInput(attrs={'placeholder': "Skypenamn eller telefon"}))
    kommentar = forms.CharField(widget=forms.Textarea, max_length=2000, label='Kommentar')
    kodverk = forms.CharField(widget=forms.HiddenInput())  

class VerifyKodverk(forms.Form):

    kodverk = forms.CharField(widget=forms.HiddenInput())  
    epost = forms.EmailField()
    telefon = forms.CharField(max_length=30, label="Kontakt", widget=forms.TextInput(attrs={'placeholder': "Skypenamn eller telefon"}))
    kontext = forms.CharField(label='Specificera var begreppet används')

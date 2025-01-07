

from django import forms
from pageprincipale.models import Person,Classiq_User,Professionnel,Adress,Quality
class LoginForm(forms.Form):
    email=forms.EmailField(label='Courriel')
    password=forms.CharField(label='Mot de passe',widget=forms.PasswordInput)

    def clean(self):
        cleaned_data= super (LoginForm,self).clean()
        email =cleaned_data.get('email')
        password=cleaned_data.get('password')

        if email and password:
            result=Person.objects.filter(password=password,email=email)
            if len(result) != 1:
                raise forms.ValidationError("Adresse de courriel ou mot de passe erroné(e)")


class AdressForm(forms.ModelForm):
    class Meta:
        model = Adress
        fields = '__all__'  # Inclut tous les champs du modèle


class UserNormalProfileForm(forms.ModelForm):
    class Meta:
        model = Classiq_User
        exclude = ['adress']  # Exclure le champ 'adresse'

class ProForm(forms.ModelForm):
    class Meta:
        model = Professionnel
        exclude = ['quality']  # Exclure le champ 'adresse'

class QualityForm(forms.ModelForm):
    class Meta:
        model = Quality
        fields = '__all__'  # Inclut tous les champs du modèle
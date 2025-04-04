from django import forms
from pageprincipale.models import Utilisateur, Plante, Adresse, Demande_plante, Message, Commentaire,MessageImage
import re


class LoginForm(forms.Form):
    pseudo = forms.CharField(label='Pseudo')
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        pseudo = cleaned_data.get('pseudo')
        password = cleaned_data.get('password')

        if pseudo and password:
            try:
                user = Utilisateur.objects.get(pseudo=pseudo)

                if not user.check_password(password):
                    raise forms.ValidationError("Pseudo ou mot de passe incorrect.")

            except Utilisateur.DoesNotExist:
                raise forms.ValidationError("Pseudo ou mot de passe incorrect.")

        return cleaned_data


class AdressForm(forms.ModelForm):
    class Meta:
        model = Adresse
        fields = '__all__'  # Inclut tous les champs du modèle


import re
from django import forms
from .models import Utilisateur  # Assure-toi que ton modèle est bien importé

class UserNormalProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        exclude = ['adresse', 'longitude', 'latitude']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        password_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[#?!@$%^&*-]).{12,}$"

        if not password:
            raise forms.ValidationError("Le mot de passe est requis.")

        if not re.match(password_pattern, password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins : "
                                        "8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial.")

        return password



class PlanteForm(forms.ModelForm):
    class Meta:
        model = Plante
        fields = ['nom_plante', 'photo_plante']
        widgets = {
            'nom_plante': forms.TextInput(attrs={'class': 'form-control'}),
            'photo_plante': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class DemandeForm(forms.ModelForm):
    class Meta:
        model = Demande_plante
        fields = ['plante', 'message']  # Plante et message sont les champs du formulaire

    def __init__(self, *args, **kwargs):
        logged_user = kwargs.pop('logged_user', None)  # Récupérer l'utilisateur passé en argument
        super().__init__(*args, **kwargs)

        if logged_user:
            # Filtrer les plantes de l'utilisateur connecté
            self.fields['plante'].queryset = Plante.objects.filter(utilisateur=logged_user)

class DemandeAideForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text', 'photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget = forms.Textarea(attrs={'rows': 4, 'placeholder': 'Entrez votre message'})

class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ['text']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['text'].widget = forms.Textarea(attrs={'rows': 4, 'placeholder': 'Entrez votre commentaire'})

class GardeForm(forms.ModelForm):
    class Meta:
        model = MessageImage
        fields = ['photo','text']
from django import forms
from pageprincipale.models import Utilisateur, Plante, Adresse, Demande_plante, Message, Commentaire,MessageImage


class LoginForm(forms.Form):
    pseudo=forms.CharField(label='Pseudo')
    password=forms.CharField(label='Mot de passe',widget=forms.PasswordInput)

    def clean(self):
        cleaned_data= super (LoginForm,self).clean()
        pseudo =cleaned_data.get('pseudo')
        password=cleaned_data.get('password')

        if pseudo and password:
            result=Utilisateur.objects.filter(password=password,pseudo=pseudo)
            if len(result) != 1:
                raise forms.ValidationError("Adresse de courriel ou mot de passe erroné(e)")


class AdressForm(forms.ModelForm):
    class Meta:
        model = Adresse
        fields = '__all__'  # Inclut tous les champs du modèle


class UserNormalProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        exclude = ['adresse','longitude','latitude']  # Exclure le champ 'adresse'




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
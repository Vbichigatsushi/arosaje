from sys import prefix

from django.shortcuts import render, redirect
from pageprincipale.forms import LoginForm,UserNormalProfileForm,AdressForm,ProForm, QualityForm
# Create your views here.
def index(request):
    return render(request, 'pageprincipale.html')

def login(request):
    if len(request.POST)>0:
        form= LoginForm(request.POST)
        if form.is_valid():
            return redirect('index')
        else:
            return render(request,'login.html',{'form':form})
    else :
        form =LoginForm()
        return render(request,'login.html',{'form':form})



from django.shortcuts import render, redirect
from .forms import UserNormalProfileForm


def register(request):
    profile_type = None  # Valeur par défaut pour éviter les erreurs
    if request.method == 'POST' and 'profileType' in request.POST:
        profile_type = request.POST['profileType']

        # Formulaires
        userclassique_form = UserNormalProfileForm(request.POST, prefix="uc")
        pro_form = ProForm(request.POST, prefix="pr")
        adresse_form = AdressForm(request.POST)
        quality_form = QualityForm(request.POST)

        if profile_type == 'Classiq_User':  # Si utilisateur classique
            if userclassique_form.is_valid() and adresse_form.is_valid():
                adresse = adresse_form.save()
                user = userclassique_form.save(commit=False)
                user.adresse = adresse  # Associer l'adresse à l'utilisateur
                user.save()  # Sauvegarder l'utilisateur

                return redirect('login')  # Rediriger après l'enregistrement
            else:
                # Si le formulaire est invalide, afficher les erreurs
                return render(request, 'register.html', {
                    'userclassique_form': userclassique_form,
                    'adresse_form': adresse_form,
                    'profileType': profile_type  # Ajouter profileType au contexte
                })

        elif profile_type == 'Professionnel':  # Si professionnel
            if pro_form.is_valid() and quality_form.is_valid():
                quality = quality_form.save()
                user = pro_form.save(commit=False)
                user.quality = quality  # Associer la qualité à l'utilisateur
                user.save()  # Sauvegarder l'utilisateur

                return redirect('login')  # Rediriger après l'enregistrement
            else:
                # Si le formulaire est invalide, afficher les erreurs
                return render(request, 'register.html', {
                    'pro_form': pro_form,
                    'quality_form': quality_form,
                    'profileType': profile_type  # Ajouter profileType au contexte
                })
    else:
        # Si c'est une requête GET, initialiser les formulaires et définir profileType à None
        userclassique_form = UserNormalProfileForm(prefix="uc")
        pro_form = ProForm(prefix="pr")
        adresse_form = AdressForm()
        quality_form = QualityForm()

        return render(request, 'register.html', {
            'userclassique_form': userclassique_form,
            'pro_form': pro_form,
            'adresse_form': adresse_form,
            'quality_form': quality_form,
            'profileType': profile_type  # Assurez-vous d'inclure profileType ici
        })

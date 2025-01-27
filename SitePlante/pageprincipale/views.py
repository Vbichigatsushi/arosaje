from sys import prefix

from django.shortcuts import render, redirect
from pageprincipale.forms import LoginForm,UserNormalProfileForm,AdressForm,PlanteForm,DemandeForm
from .models import Utilisateur, Plante, Demande_plante


def get_logged_form_request(request):
    if 'logged_user_id' in request.session:
        logged_user_id = request.session['logged_user_id']
        try:
            # Assurez-vous que vous utilisez l'ID, pas le nom d'utilisateur
            return Utilisateur.objects.get(id_utilisateur=logged_user_id)
        except Utilisateur.DoesNotExist:
            return None
    return None
# Create your views here.
def profil(request):
    logged_user = get_logged_form_request(request)
    plantes_utilisateur = Plante.objects.filter(utilisateur=logged_user)
    if logged_user:
        # Passe l'utilisateur connecté au template
        return render(request, 'profil.html', {'logged_user': logged_user,'plantes_utilisateur': plantes_utilisateur})

    else:
        # Redirige vers la page de connexion si non connecté
        return redirect('login')
def index(request):
    logged_user = get_logged_form_request(request)
    if logged_user :
        return render(request,'pageprincipale.html',{'logged_user':logged_user})
    else:
        return redirect('login')

def login(request):
    if len(request.POST)>0:
        form= LoginForm(request.POST)
        if form.is_valid():
            user_pseudo = form.cleaned_data['pseudo']
            logged_user= Utilisateur.objects.get(pseudo=user_pseudo)
            request.session['logged_user_id']=logged_user.id_utilisateur
            return redirect('index')
        else:
            return render(request,'login.html',{'form':form})
    else :
        form =LoginForm()
        return render(request,'login.html',{'form':form})



from django.shortcuts import render, redirect
from .forms import UserNormalProfileForm


def creer_plante(request):
    logged_user = get_logged_form_request(request)
    if logged_user:
        if request.method == 'POST':
            form = PlanteForm(request.POST, request.FILES)
            if form.is_valid():
                plante = form.save(commit=False)
                plante.utilisateur = logged_user  # Associer l'utilisateur connecté
                plante.save()
                return redirect('profil')  # Rediriger vers la page profil ou autre page
        else:
            form = PlanteForm()

        return render(request, 'creer_plante.html', {'form': form})
    else:
        # Redirige vers la page de connexion si non connecté
        return redirect('login')
def register(request):
    profile_type = None  # Valeur par défaut pour éviter les erreurs
    if request.method == 'POST' and 'profileType' in request.POST:
        profile_type = request.POST['profileType']

        # Formulaires
        userclassique_form = UserNormalProfileForm(request.POST, prefix="uc")
        adresse_form = AdressForm(request.POST)

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
    else:
        # Si c'est une requête GET, initialiser les formulaires et définir profileType à None
        userclassique_form = UserNormalProfileForm(prefix="uc")
        adresse_form = AdressForm()

        return render(request, 'register.html', {
            'userclassique_form': userclassique_form,
            'adresse_form': adresse_form,
            'profileType': profile_type  # Assurez-vous d'inclure profileType ici
        })


def demandes(request):

    demandes = Demande_plante.objects.filter(statut='en attente', utilisateur_receveur__isnull=True)

    return render(request, 'demandes_en_attente.html', {'demandes': demandes})


def faire_demande(request):
    logged_user = get_logged_form_request(request)  # Récupérer l'utilisateur connecté
    if logged_user:
        if request.method == 'POST':
            form = DemandeForm(request.POST, logged_user=logged_user)  # Passer l'utilisateur au formulaire

            if form.is_valid():
                plante = form.cleaned_data['plante']  # Récupérer l'objet Plante
                plante_id = plante.id_plante  # Extraire l'ID de la plante

                # Vérifier si la plante appartient à l'utilisateur
                try:
                    plante = Plante.objects.get(id_plante=plante_id, utilisateur=logged_user)
                except Plante.DoesNotExist:
                    return render(request, 'faire_demande.html', {'form': form, 'error': "Plante invalide."})

                # Créer la demande avec l'utilisateur actuel
                demande = form.save(commit=False)
                demande.utilisateur_demandeur = logged_user
                demande.save()

                # Rediriger vers une page de confirmation après l'enregistrement de la demande
                return redirect('profil')  # Rediriger vers une page de confirmation
        else:
            form = DemandeForm(logged_user=logged_user)  # Passer l'utilisateur connecté au formulaire

        return render(request, 'faire_demande.html', {'form': form})

    else:
        # Rediriger vers la page de connexion si l'utilisateur n'est pas connecté
        return redirect('login')
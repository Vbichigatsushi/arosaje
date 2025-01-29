from sys import prefix
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from pageprincipale.forms import LoginForm,UserNormalProfileForm,AdressForm,PlanteForm,DemandeForm
from .models import Utilisateur, Plante, Demande_plante
from django.core.serializers.json import DjangoJSONEncoder
import json
from .forms import UserNormalProfileForm
import urllib.parse

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


def geocode_address(address):
    address_encoded = urllib.parse.quote(address)
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={address_encoded}"

    
    headers = {
        'User-Agent': 'SitePlante/1.0 (mailto:SitePlante@test.com)'  
    }
    
    
    response = requests.get(url, headers=headers)
    
    
    if response.status_code == 200:
        try:
            
            data = response.json()
            if data:
                lat_str = data[0].get('lat')
                lon_str = data[0].get('lon')
                if lat_str and lon_str:
                    lat = float(lat_str)
                    lon = float(lon_str)
                    return lat, lon
            return None, None
        except ValueError:
            print("Erreur lors du décodage JSON.")
            return None, None
    else:
        print(f"Erreur de l'API: {response.status_code}")
        return None, None


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
    profile_type = None 
    if request.method == 'POST' and 'profileType' in request.POST:
        profile_type = request.POST['profileType']

        userclassique_form = UserNormalProfileForm(request.POST, prefix="uc")
        adresse_form = AdressForm(request.POST)

        if profile_type == 'Classiq_User':  # Si utilisateur classique
            if userclassique_form.is_valid() and adresse_form.is_valid():
                adresse = adresse_form.save()
                address = f"{adresse.numero} {adresse.voie}, {adresse.ville}, France"
                lat, lon = geocode_address(address)
                
                if lat is not None and lon is not None:
                    user = userclassique_form.save(commit=False)
                    user.adresse = adresse
                    user.latitude = lat
                    user.longitude = lon
                    user.save()
                    
                    return redirect('login')
                
                else:
                    adresse_form.add_error(None, "Erreur de géocodage.")
                    return render(request, 'register.html', {
                      'userclassique_form': userclassique_form,
                      'adresse_form': adresse_form,
                      'profileType': profile_type  # 
                })
              
            else:
                return render(request, 'register.html', {
                    'userclassique_form': userclassique_form,
                    'adresse_form': adresse_form,
                    'profileType': profile_type  
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
    
def interactiv_map(request):
    logged_user = get_logged_form_request(request)
    if logged_user:
        demandes = Demande_plante.objects.select_related('utilisateur_demandeur__adresse').all()
        markers = []
        for demande in demandes:
            adresse = demande.utilisateur_demandeur.adresse
            full_address = f"{adresse.numero} {adresse.voie}, {adresse.ville}, France"
            plante_nom = demande.plante.nom_plante if demande.plante else "Nom de la plante non disponible"
            lat = demande.utilisateur_demandeur.latitude
            lon = demande.utilisateur_demandeur.longitude
            markers.append({
                'id': demande.id,
                'adresse': full_address,
                'pseudo': demande.utilisateur_demandeur.pseudo,
                'nom': plante_nom,
                'latitude': lat,
                'longitude':lon
                
            })
        markers_json = json.dumps(markers)  # Sérialisation en JSON
        return render(request, 'interactiv-map.html', {
            'logged_user': logged_user, 
            'markers_json': markers_json  
        })
    else:
        
        return redirect('login')
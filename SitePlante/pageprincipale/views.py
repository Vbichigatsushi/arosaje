from sys import prefix
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from pageprincipale.forms import LoginForm, UserNormalProfileForm, AdressForm, PlanteForm, DemandeForm, DemandeAideForm, \
    CommentaireForm, GardeForm,CommentaireForm,MessageImage
from .models import Utilisateur, Plante, Demande_plante, Message, Commentaire
import json
from .forms import UserNormalProfileForm
import urllib.parse
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import PlanteForm
from .utils.model_loader import load_model
from .utils.image_predictor import predict_image
import os
from .models import Plante
from PIL import Image
from io import BytesIO
from django.contrib.auth import authenticate, login as auth_login, logout
from django.shortcuts import render, redirect
from .forms import LoginForm
model_path = os.path.join(os.path.dirname(__file__), 'models', 'mon_modele.h5')
model = load_model(model_path)
from haversine import haversine, Unit



def profil(request):
    logged_user = request.user
    plantes_utilisateur = Plante.objects.filter(utilisateur=logged_user)
    Demande_demander=Demande_plante.objects.filter(utilisateur_demandeur=logged_user)
    Demande_receveur = Demande_plante.objects.filter(utilisateur_receveur=logged_user)
    if logged_user:
        # Passe l'utilisateur connecté au template
        return render(request, 'profil.html', {'Demande_demandeur':Demande_demander,'logged_user': logged_user,'plantes_utilisateur': plantes_utilisateur,'Demande_receveur': Demande_receveur})

    else:
        # Redirige vers la page de connexion si non connecté
        return redirect('login')

def index(request):
    logged_user = request.user
    dernieres_demandes = (
        Demande_plante.objects.values('plante').order_by('-date_demande')[:3]
    )
    dernieres_plantes = Plante.objects.filter(
        id_plante__in=[demande['plante'] for demande in dernieres_demandes]
    )
    if logged_user :
        return render(request,'pageprincipale.html',{'logged_user':logged_user,'dernieres_plantes':dernieres_plantes})
    else:
        return redirect('login')

def login(request):
    logout(request)

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['pseudo']
            password = form.cleaned_data['password']  # Adapté à ton champ de formulaire

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)  # Connexion sécurisée

                return redirect('index')
            else:
                form.add_error(None, 'Identifiants invalides')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def geocode_address(address):
    address_encoded = urllib.parse.quote(address)
    url = f"https://api-adresse.data.gouv.fr/search/?q={address_encoded}&limit=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('features'):
            geometry = data['features'][0]['geometry']
            lon, lat = geometry['coordinates']
            return lat, lon
    print(f"Erreur de l'API: {response.status_code}")
    return None, None


def creer_plante(request):
    logged_user = request.user

    if not logged_user:
        return redirect('login')  # Rediriger si non connecté

    if request.method == 'POST':
        form = PlanteForm(request.POST, request.FILES)
        if form.is_valid():
            plante = form.save(commit=False)
            plante.utilisateur = logged_user

            # Récupérer l'objet ImageFieldFile
            image_file = request.FILES['photo_plante']

            # Vérifier si l'image est une plante
            image = Image.open(BytesIO(image_file.read()))
            target_size = (64, 64)  # Remplacez par la taille d'entrée de votre modèle
            predictions = predict_image(model, image, target_size)
            is_plant = predictions[0][0] > 0.5

            if is_plant:
                plante.save()
                return redirect('profil')  # Rediriger vers le profil
            else:
                form.add_error('photo_plante', 'L\'image téléchargée n\'est pas une plante.')
                return render(request, 'creer_plante.html', {'form': form})
    else:
        form = PlanteForm()

    return render(request, 'creer_plante.html', {'form': form})


def register(request):
    if request.method == 'POST':
        userclassique_form = UserNormalProfileForm(request.POST, prefix="uc")
        adresse_form = AdressForm(request.POST)

        if userclassique_form.is_valid() and adresse_form.is_valid():
            adresse = adresse_form.save()
            address = f"{adresse.numero} {adresse.voie} {adresse.ville}"
            lat, lon = geocode_address(address)

            if lat is not None and lon is not None:
                user = userclassique_form.save(commit=False)
                user.adresse = adresse
                user.latitude = lat
                user.longitude = lon
                user.set_password(user.password)
                user.save()
                
                return redirect('login')

            else:
                adresse_form.add_error(None, "Erreur de géocodage.")
                return render(request, 'register.html', {
                  'userclassique_form': userclassique_form,
                  'adresse_form': adresse_form
                })

    else:
        userclassique_form = UserNormalProfileForm(prefix="uc")
        adresse_form = AdressForm()

    return render(request, 'register.html', {
        'userclassique_form': userclassique_form,
        'adresse_form': adresse_form,
    })


def demandes(request):

    demandes = Demande_plante.objects.filter(statut='en attente', utilisateur_receveur__isnull=True)

    return render(request, 'demandes_en_attente.html', {'demandes': demandes})


def faire_demande(request):
    logged_user = request.user
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


def get_demandes_with_marker_info(logged_user, filter_by_receiver=False, only_accepted=False):
    demandes = Demande_plante.objects.select_related('utilisateur_demandeur')

    if filter_by_receiver:
        demandes = demandes.filter(utilisateur_receveur=logged_user)

    if only_accepted:
        demandes = demandes.filter(statut="acceptée")

    markers = []
    user_coords = (logged_user.latitude, logged_user.longitude)
    if not all(user_coords):
        return markers

    for demande in demandes:
        adresse = demande.utilisateur_demandeur.adresse
        adresse_coords = (demande.utilisateur_demandeur.latitude, demande.utilisateur_demandeur.longitude)

        if all(adresse_coords):
            distance = haversine(user_coords, adresse_coords, unit=Unit.METERS)
            if distance <= 500:
                full_address = f"{adresse.numero} {adresse.voie}, {adresse.ville}, France" if adresse else "Adresse non disponible"
                plante_nom = demande.plante.nom_plante if demande.plante else "Nom de la plante non disponible"
                lat = demande.utilisateur_demandeur.latitude
                lon = demande.utilisateur_demandeur.longitude

                markers.append({
                    'id': demande.id,
                    'adresse': full_address,
                    'pseudo': demande.utilisateur_demandeur.username,
                    'nom': plante_nom,
                    'latitude': lat,
                    'longitude': lon,
                    'distance': distance,
                    'statut': demande.statut, 
                    
                    
                })
    
    return markers

def filtered_garde_liste(request):
    logged_user = request.user
    if logged_user:
        markers = get_demandes_with_marker_info(logged_user)
        if not markers:
            return render(request, 'filtered-garde-liste.html', {'message': 'Aucune demande dans les environs.'})
        
        markers_json = json.dumps(markers)
        return render(request, 'filtered-garde-liste.html', {'markers_json': markers_json})
    else:
        return redirect('login')

def interactiv_map(request):
    logged_user = request.user
    if logged_user:
        markers = get_demandes_with_marker_info(
            logged_user, 
            filter_by_receiver=True, 
            only_accepted=True
        )
        markers_json = json.dumps(markers)
        
        return render(request, 'interactiv-map.html', {
            'logged_user': logged_user,
            'markers_json': markers_json
        })
    else:
        return redirect('login')

def research_pro(request):
    logged_user = request.user
    search_query = request.GET.get('q', '')
    utilisateurs_pro = Utilisateur.objects.filter(is_pro=True)
    if logged_user:
        if search_query:
            utilisateurs_pro = utilisateurs_pro.filter(pseudo__icontains=search_query)
        # Passe l'utilisateur connecté au template
        return render(request, 'research_pro.html', {'logged_user': logged_user,'user_pro': utilisateurs_pro,'search_query':search_query})

    else:
        # Redirige vers la page de connexion si non connecté
        return redirect('login')


def demande(request):
    logged_user = request.user
    if logged_user:
        if request.method == 'POST':
            form = DemandeAideForm(request.POST, request.FILES)
            if form.is_valid():
                Demande = form.save(commit=False)
                Demande.User= logged_user  # Associer l'utilisateur connecté
                Demande.save()
                return redirect('demande')
        else:
            form = DemandeAideForm()
        messages = Message.objects.order_by('-date_demande')
        return render(request, 'demande.html',
                      {'logged_user': logged_user, 'messages': messages,'form':form})
    else:
        # Redirige vers la page de connexion si non connecté
        return redirect('login')


def demande_aide(request,id):
    logged_user = request.user
    if logged_user:
        if request.method == 'POST':
            form = CommentaireForm(request.POST)
            if form.is_valid():
                Com = form.save(commit=False)
                Com.User= logged_user  # Associer l'utilisateur connecté
                Com.demande=Message.objects.get(id_message=id)
                Com.save()
                return redirect('demande_aide', id=id)

        else:
            form = CommentaireForm()
        message = Message.objects.get(id_message=id)
        reponses = message.commentaires.all().order_by('-date_creation')
        return render(request, 'demande_aide.html',
                      {'logged_user': logged_user, 'message': message, 'reponses': reponses,'form':form})
    else:
        # Redirige vers la page de connexion si non connecté
        return redirect('login')

def all_demande_garde(request):
    logged_user = request.user
    if logged_user:
        if request.method == "POST":
            demande_id = request.POST.get("demande_id")
            demande=Demande_plante.objects.get(id=demande_id)
            if demande.utilisateur_receveur is None:

                demande.utilisateur_receveur = logged_user
                demande.statut = "acceptée"
                demande.save()
        Demandes = Demande_plante.objects.order_by('-date_demande')
        return render(request, 'all_demande_garde.html',
                      {'logged_user': logged_user, 'Demandes': Demandes})
    else:
        return redirect('login')

def garde(request,id):
    logged_user = request.user
    form= GardeForm(request.POST)
    if logged_user:
        if request.method == 'POST':
            form = GardeForm(request.POST, request.FILES)
            if form.is_valid():
                messagephoto = form.save(commit=False)
                messagephoto.Demande = Demande_plante.objects.get(id=id)
                messagephoto.utilisateur=logged_user
                messagephoto.save()
                message_images = MessageImage.objects.filter(Demande=Demande_plante.objects.get(id=id))
                return render(request, 'garde.html',
                              {'logged_user': logged_user, 'form': form, 'message_images':message_images,'id':id})
        else :
            form = GardeForm()
            Demande = Demande_plante.objects.get(id=id)
            message_images = MessageImage.objects.filter(Demande=Demande)
            return render(request, 'garde.html',
                      {'logged_user': logged_user, 'Demande': Demande,'form':form,'message_images':message_images})
    else:
        # Redirige vers la page de connexion si non connecté
        return redirect('login')


def supprimer_plante(request, id_plante):
    plante = get_object_or_404(Plante, id_plante=id_plante)
    if request.method == 'POST':
        plante.delete()
    return redirect('profil')

def supprimer_demande(request, demande_id):
    demande = get_object_or_404(Demande_plante, id=demande_id)
    if request.method == 'POST':
        demande.delete()
    return redirect('profil')

def rgpd(request):
    return render(request, 'rgpd.html',
                  {})

def suppression(request):
    logged_user = request.user
    if logged_user:


        return render(request, 'suppression.html', {})
    else:
        # Redirige vers la page de connexion si non connecté
        return redirect('login')

def supprimer(request):
    user = get_object_or_404(Utilisateur, id=request.session['logged_user_id'])

    user.delete()
    logout(request)
    return redirect('login')

def liste_plantes(request):
    plantes = Plante.objects.all().values()  # Récupère toutes les plantes sous forme de dictionnaire
    return JsonResponse(list(plantes), safe=False)

def changer_adresse(request):

        user=request.user
        if request.method == 'POST':
            adresse_form = AdressForm(request.POST)

            if  adresse_form.is_valid():
                adresse = adresse_form.save()
                address = f"{adresse.numero} {adresse.voie} {adresse.ville}"
                lat, lon = geocode_address(address)

                if lat is not None and lon is not None:

                    user.adresse = adresse
                    user.latitude = lat
                    user.longitude = lon
                    user.save()

                    return redirect('profil')

                else:
                    adresse_form.add_error(None, "Erreur de géocodage.")
                    return render(request, 'changement_des_donnees.html', {
                        'adresse_form': adresse_form
                    })

        else:
            adresse_form = AdressForm()

        return render(request, 'changement_des_donnees.html', {
            'adresse_form': adresse_form,
        })


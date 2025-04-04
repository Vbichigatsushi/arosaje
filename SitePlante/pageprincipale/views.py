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

model_path = os.path.join(os.path.dirname(__file__), 'models', 'mon_modele.h5')
model = load_model(model_path)
def get_logged_form_request(request):
    if 'logged_user_id' in request.session:
        logged_user_id = request.session['logged_user_id']
        try:
            # Assurez-vous que vous utilisez l'ID, pas le nom d'utilisateur
            return Utilisateur.objects.get(id_utilisateur=logged_user_id)
        except Utilisateur.DoesNotExist:
            return None
    return None

def profil(request):
    logged_user = get_logged_form_request(request)
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
    logged_user = get_logged_form_request(request)
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
            user_pseudo = form.cleaned_data['pseudo']
            user = Utilisateur.objects.get(pseudo=user_pseudo)

            request.session['logged_user_id'] = user.id_utilisateur
            return redirect('index')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


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

    if not logged_user:
        return redirect('login')  # Rediriger si non connecté

    if request.method == 'POST':
        form = PlanteForm(request.POST, request.FILES)
        if form.is_valid():
            plante = form.save(commit=False)
            plante.utilisateur = logged_user  # Associer l'utilisateur connecté

            # Récupérer l'objet ImageFieldFile
            image_file = request.FILES['photo_plante']

            # Vérifier si l'image est une plante
            image = Image.open(BytesIO(image_file.read()))
            target_size = (64, 64)  # Remplacez par la taille d'entrée de votre modèle
            predictions = predict_image(model, image, target_size)
            is_plant = predictions[0][0] > 0.5  # Remplacez par la logique de votre modèle

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
            user = userclassique_form.save(commit=False)
            user.adresse = adresse

            # 🔐 Hachage du mot de passe
            user.set_password(user.password)
            user.save()

            return redirect('login')  # Redirige vers la page de connexion

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

def research_pro(request):
    logged_user = get_logged_form_request(request)
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
    logged_user = get_logged_form_request(request)
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
    logged_user = get_logged_form_request(request)
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
    logged_user = get_logged_form_request(request)
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
    logged_user = get_logged_form_request(request)
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
    logged_user = get_logged_form_request(request)
    if logged_user:


        return render(request, 'suppression.html', {})
    else:
        # Redirige vers la page de connexion si non connecté
        return redirect('login')

def supprimer(request):
    user = get_object_or_404(Utilisateur, id_utilisateur=request.session['logged_user_id'])

    user.delete()
    logout(request)
    return redirect('login')

def liste_plantes(request):
    plantes = Plante.objects.all().values()  # Récupère toutes les plantes sous forme de dictionnaire
    return JsonResponse(list(plantes), safe=False)
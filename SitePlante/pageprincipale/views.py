from sys import prefix
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from pageprincipale.forms import LoginForm, UserNormalProfileForm, AdressForm, PlanteForm, DemandeForm, DemandeAideForm, \
    CommentaireForm, GardeForm,CommentaireForm,MessageImage,FormChangPseudo
from .models import Utilisateur, Plante, Demande_plante, Message, Commentaire
import json
from .forms import UserNormalProfileForm
import urllib.parse


from django.contrib.auth import logout
from django.shortcuts import render, redirect

import os
import json
import urllib.parse
from io import BytesIO
from PIL import Image

import requests
from haversine import haversine, Unit
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required

from pageprincipale.forms import (
    LoginForm, UserNormalProfileForm, AdressForm, PlanteForm,
    DemandeForm, DemandeAideForm, CommentaireForm,
    GardeForm, MessageImage
)
from .models import Utilisateur, Plante, Demande_plante, Message, Commentaire
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
from django.db.models import Q
from django.contrib.auth.decorators import login_required
@login_required(login_url='login')
def profil(request):
    logged_user = request.user
    plantes_utilisateur = Plante.objects.filter(utilisateur=logged_user)
    Demande_demander=Demande_plante.objects.filter(utilisateur_demandeur=logged_user)
    Demande_receveur = Demande_plante.objects.filter(utilisateur_receveur=logged_user)
    if logged_user:
        # Passe l'utilisateur connecté au template
        return render(request, 'profil.html', {'Demande_demandeur':Demande_demander,'logged_user': logged_user,'plantes_utilisateur': plantes_utilisateur,'Demande_receveur': Demande_receveur})

    else:
        return redirect('login')
@login_required(login_url='login')
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
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)

                return redirect('index')
            else:
                form.add_error(None, 'Identifiants invalides')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})



def geocode_address(address, expected_city=None, expected_postal_code=None, expected_street=None):
    address_encoded = urllib.parse.quote(address)
    url = f"https://api-adresse.data.gouv.fr/search/?q={address_encoded}&limit=1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get('features'):
            feature = data['features'][0]
            properties = feature['properties']
            geometry = feature['geometry']
            lon, lat = geometry['coordinates']

            city_ok = expected_city and properties.get('city', '').lower() == expected_city.lower()
            postcode_ok = expected_postal_code and str(properties.get('postcode', '')) == str(expected_postal_code)
            street_ok = expected_street and expected_street.lower() in properties.get('name', '').lower()

            if city_ok and postcode_ok and street_ok:
                return lat, lon

            print("Adresse incohérente :", properties)
    return None, None

@login_required(login_url='login')
def creer_plante(request):
    logged_user = request.user

    if not logged_user:
        return redirect('login')  # Rediriger si non connecté

    if request.method == 'POST':
        form = PlanteForm(request.POST, request.FILES)
        if form.is_valid():
            plante = form.save(commit=False)
            plante.utilisateur = logged_user

            image_file = request.FILES['photo_plante']


            image = Image.open(BytesIO(image_file.read()))
            target_size = (64, 64)
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


def accepter_demande(request):
    logged_user = request.user
    if logged_user.is_authenticated:
        demande_id = request.POST.get("demande_id")
        demande = get_object_or_404(Demande_plante, id=demande_id)
        if demande.utilisateur_receveur is None:
            demande.utilisateur_receveur = logged_user
            demande.statut = "acceptée"
            demande.save()
    return redirect('filtered-garde-liste')

def register(request):
    if request.method == 'POST':
        userclassique_form = UserNormalProfileForm(request.POST, prefix="uc")
        adresse_form = AdressForm(request.POST)

        if userclassique_form.is_valid() and adresse_form.is_valid():
            adresse = adresse_form.save()
            address = f"{adresse.numero} {adresse.voie} {adresse.code_postale} {adresse.ville}"
            lat, lon = geocode_address(
                address,
                expected_city=adresse.ville,
                expected_postal_code=adresse.code_postale,
                expected_street=adresse.voie
            )

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

@login_required(login_url='login')
def demandes(request):

    demandes = Demande_plante.objects.filter(statut='en attente', utilisateur_receveur__isnull=True)

    return render(request, 'demandes_en_attente.html', {'demandes': demandes})

@login_required(login_url='login')
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
@login_required(login_url='login')
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
@login_required(login_url='login')
def interactiv_map(request):
    logged_user = request.user
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

@login_required(login_url='login')
def research_pro(request):
    logged_user = request.user
    search_query = request.GET.get('q', '')

    llm_reponse = None  # valeur par défaut

    if search_query:
        embeddings = torch.tensor(
            np.stack(text_chunks_and_embedding_df_load["embedding"].to_list(), axis=0),
            dtype=torch.float32
        ).to(device)
        try:
            llm_reponse = rag_with_mistral(search_query, embeddings)
        except Exception as e:
            print(f"[ERREUR] rag_with_mistral : {e}")
            llm_reponse = "Une erreur est survenue lors de la recherche."

    # Toujours retourner une réponse
    return render(request, 'research_pro.html', {
        'logged_user': logged_user,
        'search_query': search_query,
        'llm_reponse': llm_reponse  # corrigé : pas d’espace dans la clé
    })
@login_required(login_url='login')
def demande(request):
    logged_user = request.user
    if not logged_user:
        return redirect('login')

    search_query = request.GET.get('q', '')
    form = DemandeAideForm()


    messages = Message.objects.all()

    if search_query:
        messages = messages.filter(
            Q(text__icontains=search_query) |
            Q(User__username__icontains=search_query)
        )

    if request.method == 'POST':
        form = DemandeAideForm(request.POST, request.FILES)
        if form.is_valid():
            demande = form.save(commit=False)
            demande.User = logged_user
            demande.save()
            return redirect('demande')

    messages = messages.order_by('-date_demande')

    return render(request, 'demande.html', {
        'logged_user': logged_user,
        'messages': messages,
        'form': form,
        'search_query': search_query
    })


@login_required(login_url='login')
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
        return redirect('login')
@login_required(login_url='login')
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
@login_required(login_url='login')
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

@login_required(login_url='login')
def supprimer_plante(request, id_plante):
    plante = get_object_or_404(Plante, id_plante=id_plante)
    if request.method == 'POST':
        plante.delete()
    return redirect('profil')
@login_required(login_url='login')
def supprimer_demande(request, demande_id):
    demande = get_object_or_404(Demande_plante, id=demande_id)
    if request.method == 'POST':
        demande.delete()
    return redirect('profil')
@login_required(login_url='login')
def rgpd(request):
    return render(request, 'rgpd.html',
                  {})
@login_required(login_url='login')
def suppression(request):
    logged_user = request.user
    if logged_user:


        return render(request, 'suppression.html', {})
    else:
        # Redirige vers la page de connexion si non connecté
        return redirect('login')
@login_required(login_url='login')
def supprimer(request):
    user = get_object_or_404(Utilisateur, id=request.session['logged_user_id'])

    user.delete()
    logout(request)
    return redirect('login')
@login_required(login_url='login')
def liste_plantes(request):
    plantes = Plante.objects.all().values()  # Récupère toutes les plantes sous forme de dictionnaire
    return JsonResponse(list(plantes), safe=False)

def changer_adresse(request):

        user=request.user
        if request.method == 'POST':
            adresse_form = AdressForm(request.POST)

            if  adresse_form.is_valid():
                adresse = adresse_form.save()
                address = f"{adresse.numero} {adresse.voie} {adresse.code_postale} {adresse.ville}"
                lat, lon = geocode_address(
                    address,
                    expected_city=adresse.ville,
                    expected_postal_code=adresse.code_postale,
                    expected_street=adresse.voie
                )

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

@login_required(login_url='login')
def changer_nom(request):
    user = request.user
    if request.method == 'POST':
        nom_form = FormChangPseudo(request.POST)
        if nom_form.is_valid():
            user.username = nom_form.cleaned_data['username']
            user.save()
            return redirect('profil')
        else:
            nom_form.add_error(None, "Erreur dans le pseudo.")
    else:
        nom_form = FormChangPseudo(initial={'username': user.username})

    return render(request, 'changement_de_nom.html', {
        'nom_form': nom_form,
    })

def supprimer_message(request, message_id):
    message = get_object_or_404(Message,  id_message=message_id)
    message.delete()
    return redirect('demande')
def suppression_message(request,message_id):
    logged_user = request.user
    if logged_user:


        return render(request, 'suppression_message.html', {'message_id':message_id})
    else:

        return redirect('login')
def supprimer_message_image(request, message_image_id):
    message = get_object_or_404(MessageImage, id=message_image_id)
    if request.method == 'POST':
        message.delete()
    return redirect('profil')

def supprimer_commentaire(request, message_id,commentaire_id):
    commentaire = get_object_or_404(Commentaire,  id=commentaire_id)
    commentaire.delete()
    return redirect('demande_aide', id=message_id)
def suppression_commentaire(request,message_id,commentaire_id):
    logged_user = request.user
    if logged_user:


        return render(request, 'suppression_commentaire.html', {'commentaire_id':commentaire_id,'message_id':message_id})
    else:

        return redirect('login')

import os
import pandas as pd
from django.conf import settings

BASE_DIR = settings.BASE_DIR
import random
import torch
import numpy as np
from sentence_transformers import util,SentenceTransformer
from timeit import default_timer as timer
csv_path = os.path.join(BASE_DIR, "pageprincipale/static/data/text_chunks_and_embedding_df.csv")
text_chunks_and_embedding_df_load = pd.read_csv(csv_path)
device = "cuda" if torch.cuda.is_available() else "cpu"
text_chunks_and_embedding_df_load["embedding"]=text_chunks_and_embedding_df_load["embedding"].apply(lambda x: np.fromstring(x.strip("[]"),sep=" "))
embeddings=torch.tensor(np.stack(text_chunks_and_embedding_df_load["embedding"].to_list(),axis=0),dtype=torch.float32 ).to(device)
pages_and_chuncks = text_chunks_and_embedding_df_load.to_dict(orient="records")

embedding_model = SentenceTransformer(model_name_or_path="all-mpnet-base-v2",device=device)
def retrieve_relevant_resources(query: str, embeddings: torch.tensor, model: SentenceTransformer = embedding_model,
                                n_resources_to_return: int = 5, print_time: bool = True):

    query_embedding = model.encode(query, convert_to_tensor=True)


    if query_embedding.dtype != embeddings.dtype:
        query_embedding = query_embedding.to(dtype=embeddings.dtype)

    start_time = timer()
    dot_scores = util.dot_score(query_embedding, embeddings)[0]
    end_time = timer()

    if print_time:
        print(f"[INFO] Temps pris pour les embeddings pour {len(embeddings)} embeddings : {end_time - start_time:.5f} second")
    scores, indices = torch.topk(input=dot_scores, k=n_resources_to_return)
    return scores, indices
def print_top_results_and_scores(query:str,
                                 embeddings:torch.tensor,
                                 pages_and_chunks:list[dict]=pages_and_chuncks,
                                 n_ressources_to_return: int=5):
    score,indices = retrieve_relevant_resources(query=query,embeddings=embeddings,n_resources_to_return=n_ressources_to_return)

    for score,idx in zip(score,indices):
        print(f"score:{score:.4f}")
        print(f"Text:{pages_and_chuncks[idx]['sentence_chunck']}")
        print(f"Page :{pages_and_chuncks[idx]['page_number']}")
        print("\n")
def text_top_results_and_scores(query:str,
                                 embeddings:torch.tensor,
                                 pages_and_chunks:list[dict]=pages_and_chuncks,
                                 n_ressources_to_return: int=5):
    score,indices = retrieve_relevant_resources(query=query,embeddings=embeddings,n_resources_to_return=n_ressources_to_return)
    text_final="Voici les 5 phrases les plus proches dans mon document avec la base vectorielle : "
    for score,idx in zip(score,indices):
        text_final=text_final +"     " +pages_and_chuncks[idx]['sentence_chunck']
    return text_final
from mistralai import Mistral


def rag_with_mistral(query: str, embeddings: dict) -> str:


    os.environ["MISTRAL_API_KEY"] = "VwEcL08P6LMpj6wk1GqKxyIkW7IIFOZs"
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)

    text_embedding = text_top_results_and_scores(query=query, embeddings=embeddings)

    query_final = f"{text_embedding}    '''{query}'''"

    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu es un jardinier professionnel qui donne des conseils très précis. "
                    "Si la question n'a aucun rapport avec les plantes, dire 'Je ne suis expert qu'en plante veiller reposez une question' "
                    "et ne rien répondre d'autre. "
                    "Tu ne réponds à la query entre triple simple quote qu'avec les 5 informations données par le RAG si les informations sont présentes "
                    "et vérifie que ce soit bien la bonne plante. "
                    "Si l'information demandée n'est pas dans la liste, dire seulement 'désolé je ne sais pas' et ne continue pas. "
                    "Sinon, fais 2 petits paragraphes."
                )
            },
            {
                "role": "user",
                "content": query_final,
            },
        ]
    )

    return chat_response.choices[0].message.content


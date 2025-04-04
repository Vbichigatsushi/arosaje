import os
import django
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from PIL import Image

# Charger Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SitePlante.settings")
django.setup()

# Importer la fonction après l'initialisation de Django
from forms import preprocess_image  # Suppression de "SitePlante." qui pose problème

# Définir le chemin du modèle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Récupère le dossier du script
MODEL_PATH = os.path.join(BASE_DIR, "mon_modele.h5")

# Charger le modèle
model = load_model(MODEL_PATH)

# Charger et prétraiter l'image
image_path = os.path.join(BASE_DIR, "test.jpg")  # Vérifie que l'image est bien là

if os.path.exists(image_path):  # Vérifie si le fichier existe
    test_image = Image.open(image_path)
    test_image = preprocess_image(test_image)  # Appliquer le prétraitement

    # Faire une prédiction
    prediction = model.predict(test_image)
    print("Résultat du modèle :", prediction)
else:
    print(f"Erreur : Image {image_path} introuvable.")

from django.db import models


from django.db import models
from django.conf import settings
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

from django.core.exceptions import ValidationError

class TypeDemande(models.Model):
    id_type_demande = models.AutoField(primary_key=True)  # ID du type de demande
    nom_type_demande = models.CharField(max_length=255)  # Nom du type de demande

    def __str__(self):
        return self.nom_type_demande


class Adresse(models.Model):
    id_addresse = models.AutoField(primary_key=True)  # ID de l'adresse
    numero = models.IntegerField()  # Numéro de la voie
    voie = models.CharField(max_length=255)  # Nom de la voie
    complement = models.CharField(max_length=255, null=True, blank=True)  # Complément d'adresse
    ville = models.CharField(max_length=255)  # Ville
    code_postale = models.IntegerField()  # Code postal

    def __str__(self):
        return f"{self.numero} {self.voie}, {self.ville} ({self.code_postale})"


class Utilisateur(models.Model):
    id_utilisateur = models.AutoField(primary_key=True)
    is_pro = models.BooleanField(default=False)
    pseudo = models.CharField(max_length=255, unique=True)  # Ajout de unique=True pour éviter les doublons
    password = models.CharField(max_length=255)  # Stocke un mot de passe haché
    adresse = models.ForeignKey("Adresse", on_delete=models.CASCADE)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    rgpd_accepted = models.BooleanField(default=False)

    def set_password(self, raw_password):

        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        
        return check_password(raw_password, self.password)

    def clean(self):
        if not self.rgpd_accepted:
            raise ValidationError('Vous devez accepter les conditions RGPD.')
    def __str__(self):
        return self.pseudo

class Plante(models.Model):
    id_plante = models.AutoField(primary_key=True)
    nom_plante = models.CharField(max_length=255)
    photo_plante = models.ImageField(upload_to='photos_plantes/', blank=True, null=True)
    utilisateur = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name='plantes', null=True
    )

    def __str__(self):
        return self.nom_plante

class Demande_plante(models.Model):
    plante = models.ForeignKey('Plante', on_delete=models.CASCADE)
    utilisateur_demandeur = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name='demandes_envoyees'
    )
    utilisateur_receveur = models.ForeignKey(
        Utilisateur, on_delete=models.SET_NULL, related_name='demandes_recues', null=True, blank=True

    )  # Par défaut, aucun receveur
    statut = models.CharField(
        max_length=20,
        choices=[('en attente', 'En attente'), ('acceptée', 'Acceptée'), ('refusée', 'Refusée')],
        default='en attente'
    )
    message=models.CharField(max_length=255,null=True)
    date_demande = models.DateTimeField(auto_now_add=True)
    date_reponse = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Demande pour {self.plante.nom_plante} par {self.utilisateur_demandeur.pseudo}"

class Message(models.Model):
    id_message=models.AutoField(primary_key=True)
    User = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    text=models.CharField(max_length=500)
    date_demande = models.DateTimeField(auto_now_add=True)
    photo= models.ImageField(upload_to='photos_plantes/', blank=True, null=True)

class Commentaire(models.Model):
    demande = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='commentaires')
    User = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    text = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

class MessageImage(models.Model):
    Demande = models.ForeignKey('Demande_plante',on_delete=models.CASCADE)
    text=text=models.CharField(max_length=250, blank=True, null=True)
    photo = models.ImageField(upload_to='photos_plantes/', blank=True, null=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE,null=True, blank=True)
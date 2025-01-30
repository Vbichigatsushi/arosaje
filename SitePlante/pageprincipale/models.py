from django.db import models


from django.db import models
from django.conf import settings



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
    id_utilisateur = models.AutoField(primary_key=True)  # ID de l'utilisateur
    is_pro = models.BooleanField(default=False)  # Si l'utilisateur est professionnel
    pseudo = models.CharField(max_length=255)  # Pseudo
    password = models.CharField(max_length=255)  # Mot de passe
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE)  # Clé étrangère vers Adresse
    REQUIRED_FIELDS = ['password']
    USERNAME_FIELD = 'pseudo'
    def __str__(self):
        return self.pseudo

class Plante(models.Model):
    id_plante = models.AutoField(primary_key=True)  # ID de la plante
    nom_plante = models.CharField(max_length=255)  # Nom de la plante
    photo_plante = models.ImageField(upload_to='photos_plantes/', blank=True, null=True)
    utilisateur = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name='plantes', null=True
    )

    def __str__(self):
        return self.nom_plante
class Demande(models.Model):
    plante = models.ForeignKey(Plante, on_delete=models.CASCADE)  # Clé étrangère vers Plante
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)  # Clé étrangère vers Utilisateur
    type_demande = models.ForeignKey(TypeDemande, on_delete=models.CASCADE)  # Clé étrangère vers TypeDemande
    date_demande = models.DateTimeField()  # Date de la demande

    class Meta:
        unique_together = (("plante", "utilisateur", "type_demande"))  # Clé primaire composite

    def __str__(self):
        return f"Demande de {self.utilisateur} pour {self.plante}"


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
    photo_plante1 = models.ImageField(upload_to='photos_plantes/', blank=True, null=True)
    photo_plante2 = models.ImageField(upload_to='photos_plantes/', blank=True, null=True)
    photo_plante3 = models.ImageField(upload_to='photos_plantes/', blank=True, null=True)

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
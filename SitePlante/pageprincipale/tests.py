from django.test import TestCase
from django.utils import timezone
from pageprincipale.models import TypeDemande, Adresse, Utilisateur, Plante, Demande, Demande_plante, Message, Commentaire, MessageImage

# Create your tests here.

class ModelsTestCase(TestCase):
  # Test la création d'un type demande + vérifie que le nom est correctement enregistré
    def test_create_type_demande(self):
        type_demande = TypeDemande.objects.create(nom_type_demande="Consultation")
        self.assertEqual(TypeDemande.objects.count(), 1)
        self.assertEqual(type_demande.nom_type_demande, "Consultation")

    # Test la création d'une adresse + vérifie que sa représentation est la bonne string
    def test_create_adresse(self):
        adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
        self.assertEqual(Adresse.objects.count(), 1)
        self.assertEqual(str(adresse), "1 Place du Maréchal Leclerc, Auxerre (89000)")

    # Test la création d'un utilisateur + que le pseudo est bien enregistré
    def test_create_utilisateur(self):
        adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
        utilisateur = Utilisateur.objects.create(pseudo="User1", password="test", adresse=adresse)
        self.assertEqual(Utilisateur.objects.count(), 1)
        self.assertEqual(utilisateur.pseudo, "User1")

    # Test la création d'une plante + vérifie qu'elle est bien associée à un utilisateur
    def test_create_plante(self):
        adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
        utilisateur = Utilisateur.objects.create(pseudo="User1", password="test", adresse=adresse)
        plante = Plante.objects.create(nom_plante="Rosier", utilisateur=utilisateur)
        self.assertEqual(Plante.objects.count(), 1)
        self.assertEqual(plante.nom_plante, "Rosier")
        self.assertEqual(plante.utilisateur.pseudo, "User1")
    
    # Test la création d'une demande + vérifie sa relation avec une plante, un utilisateur et un type de demande
    def test_create_demande(self):
        adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
        utilisateur = Utilisateur.objects.create(pseudo="User1", password="test", adresse=adresse)
        plante = Plante.objects.create(nom_plante="Tulipe", utilisateur=utilisateur)
        type_demande = TypeDemande.objects.create(nom_type_demande="Echange")
        demande = Demande.objects.create(plante=plante, utilisateur=utilisateur, type_demande=type_demande, date_demande=timezone.now())
        self.assertEqual(Demande.objects.count(), 1)
        self.assertEqual(str(demande), f"Demande de {utilisateur} pour {plante}")
    
    
    # Test la création d'un message + vérifie que son texte est correctement enregistré
    def test_create_message(self):
        adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
        utilisateur = Utilisateur.objects.create(pseudo="Messager", password="secret", adresse=adresse)
        message = Message.objects.create(User=utilisateur, text="Test Message")
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.text, "Test Message")
    
    # Test la création d'un commentaire + vérifie qu'il est bien associé à un message et un utilisateur
    def test_create_commentaire(self):
        adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
        utilisateur = Utilisateur.objects.create(pseudo="User1", password="test", adresse=adresse)
        message = Message.objects.create(User=utilisateur, text="Test Message")
        commentaire = Commentaire.objects.create(demande=message, User=utilisateur, text="Test Message")
        self.assertEqual(Commentaire.objects.count(), 1)
        self.assertEqual(commentaire.text, "Test Message")
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from pageprincipale.models import TypeDemande, Adresse, Utilisateur, Plante, Demande_plante, Message, Commentaire, MessageImage
import os
from PIL import Image
from io import BytesIO
class ModelsTestCase(TestCase):
    def test_create_type_demande(self):
        type_demande = TypeDemande.objects.create(nom_type_demande="Consultation")
        self.assertEqual(TypeDemande.objects.count(), 1)
        self.assertEqual(type_demande.nom_type_demande, "Consultation")

    def test_create_adresse(self):
        adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
        self.assertEqual(Adresse.objects.count(), 1)
        self.assertEqual(str(adresse), "1 Place du Maréchal Leclerc, Auxerre (89000)")

    def test_create_utilisateur(self):
        adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
        utilisateur = Utilisateur.objects.create(pseudo="User1", adresse=adresse)
        utilisateur.set_password("test")
        utilisateur.save()
        self.assertEqual(Utilisateur.objects.count(), 1)
        self.assertEqual(utilisateur.pseudo, "User1")

    def test_create_plante(self):
        adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
        utilisateur = Utilisateur.objects.create(pseudo="User1", adresse=adresse)
        utilisateur.set_password("test")
        utilisateur.save()
        plante = Plante.objects.create(nom_plante="Rosier", utilisateur=utilisateur)
        self.assertEqual(Plante.objects.count(), 1)
        self.assertEqual(plante.nom_plante, "Rosier")
        self.assertEqual(plante.utilisateur.pseudo, "User1")

    def test_create_demande_plante(self):
        adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
        utilisateur_demandeur = Utilisateur.objects.create(pseudo="User1", adresse=adresse)
        utilisateur_demandeur.set_password("test")
        utilisateur_demandeur.save()
        utilisateur_receveur = Utilisateur.objects.create(pseudo="User2", adresse=adresse)
        utilisateur_receveur.set_password("test")
        utilisateur_receveur.save()
        plante = Plante.objects.create(nom_plante="Tulipe", utilisateur=utilisateur_demandeur)

        demande = Demande_plante.objects.create(
            plante=plante,
            utilisateur_demandeur=utilisateur_demandeur,
            utilisateur_receveur=utilisateur_receveur,
            statut='en attente',
            message="Je souhaite échanger cette plante."
        )

        self.assertEqual(Demande_plante.objects.count(), 1)
        self.assertEqual(str(demande), f"Demande pour {plante.nom_plante} par {utilisateur_demandeur.pseudo}")

    def test_create_message(self):
        adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
        utilisateur = Utilisateur.objects.create(pseudo="Messager", adresse=adresse)
        utilisateur.set_password("secret")
        utilisateur.save()
        message = Message.objects.create(User=utilisateur, text="Test Message")
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.text, "Test Message")

    def test_create_commentaire(self):
        adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
        utilisateur = Utilisateur.objects.create(pseudo="User1", adresse=adresse)
        utilisateur.set_password("test")
        utilisateur.save()
        message = Message.objects.create(User=utilisateur, text="Test Message")
        commentaire = Commentaire.objects.create(demande=message, User=utilisateur, text="Test Comment")
        self.assertEqual(Commentaire.objects.count(), 1)
        self.assertEqual(commentaire.text, "Test Comment")

class ViewsModelsFormsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.adresse = Adresse.objects.create(
            numero=10,
            voie='rue Jules Ferry',
            ville='Auxerre',
            code_postale=89000
        )
        self.utilisateur = Utilisateur.objects.create(
            pseudo='testuser',
            adresse=self.adresse,
            rgpd_accepted=True
        )
        self.utilisateur.set_password('Password123!')
        self.utilisateur.save()
        self.plante = Plante.objects.create(
            nom_plante='Test Plante',
            utilisateur=self.utilisateur
        )
        self.demande_plante = Demande_plante.objects.create(
            plante=self.plante,
            utilisateur_demandeur=self.utilisateur,
            statut='en attente'
        )

    def login_user(self):
        self.client.post(reverse('login'), {'pseudo': 'testuser', 'password': 'Password123!'})

    def test_login_view_post(self):
        response = self.client.post(reverse('login'), {'pseudo': 'testuser', 'password': 'Password123!'})
        self.assertRedirects(response, reverse('index'))

    def test_creer_plante_view_post(self):
        self.login_user()

        # Chemin vers l'image réelle de la plante dans le même répertoire que tests.py
        image_path = os.path.join(os.path.dirname(__file__), 'plante.png')

        # Ouvrir l'image réelle et créer un SimpleUploadedFile
        with open(image_path, 'rb') as f:
            image = SimpleUploadedFile(f.name, f.read(), content_type='image/png')

        # Convertir l'image en RGB et redimensionner si nécessaire
        image_pil = Image.open(image).convert('RGB')
        image_pil = image_pil.resize((64, 64))

        # Sauvegarder l'image redimensionnée dans un BytesIO
        image_io = BytesIO()
        image_pil.save(image_io, format='PNG')
        image_io.seek(0)

        # Créer un SimpleUploadedFile à partir de l'image redimensionnée
        image_file = SimpleUploadedFile(image.name, image_io.read(), content_type='image/png')

        # Ajoutez l'image aux données du formulaire
        form_data = {
            'nom_plante': 'Nouvelle Plante',
            'photo_plante': image_file
        }

        response = self.client.post(reverse('creer_plante'), data=form_data)
        self.assertRedirects(response, reverse('profil'))

    def test_register_view_post(self):
        form_data = {
            'uc-pseudo': 'newuser',
            'uc-password': 'Newpassword123!',
            'uc-rgpd_accepted':True,
            'numero': 10,
            'voie': 'Rue Jules Ferry',
            'ville': 'Auxerre',
            'code_postale': 89000
        }
        response = self.client.post(reverse('register'), data=form_data)

        # Vérifiez que l'utilisateur a été créé
        self.assertTrue(Utilisateur.objects.filter(pseudo='newuser').exists())

        # Vérifiez la redirection
        self.assertRedirects(response, reverse('login'))
    def test_faire_demande_view_post(self):
        self.login_user()
        form_data = {'plante': self.plante.id_plante, 'message': 'Test message'}
        response = self.client.post(reverse('faire_demande'), data=form_data)
        self.assertRedirects(response, reverse('profil'))

    def test_demande_view_post(self):
        self.login_user()
        form_data = {'text': 'Test message'}
        response = self.client.post(reverse('demande'), data=form_data)
        self.assertRedirects(response, reverse('demande'))

    def test_demande_aide_view_post(self):
        self.login_user()
        message = Message.objects.create(User=self.utilisateur, text='Test message')
        form_data = {'text': 'Test commentaire'}
        response = self.client.post(reverse('demande_aide', args=[message.id_message]), data=form_data)
        self.assertRedirects(response, reverse('demande_aide', args=[message.id_message]))

    def test_all_demande_garde_view_post(self):
        self.login_user()
        demande = Demande_plante.objects.create(
            plante=self.plante,
            utilisateur_demandeur=self.utilisateur,
            statut='en attente'
        )
        form_data = {'demande_id': demande.id}
        response = self.client.post(reverse('all_demande_garde'), data=form_data)
        self.assertIn('logged_user', response.context)
        self.assertIn('Demandes', response.context)

    def test_garde_view_post(self):
        self.login_user()
        demande = Demande_plante.objects.create(
            plante=self.plante,
            utilisateur_demandeur=self.utilisateur,
            statut='en attente'
        )
        form_data = {'photo': '', 'text': 'Test garde'}
        response = self.client.post(reverse('garde', args=[demande.id]), data=form_data)
        self.assertIn('logged_user', response.context)
        self.assertIn('form', response.context)
        self.assertIn('message_images', response.context)

    def test_interactiv_map_view(self):
        self.login_user()
        response = self.client.get(reverse('interactiv-map'))
        self.assertIn('logged_user', response.context)
        self.assertIn('markers_json', response.context)

    def test_research_pro_view(self):
        self.login_user()
        response = self.client.get(reverse('pro'))
        self.assertIn('logged_user', response.context)
        self.assertIn('user_pro', response.context)

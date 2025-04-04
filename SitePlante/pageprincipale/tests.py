from django.test import TestCase, Client
from django.utils import timezone
from pageprincipale.models import TypeDemande, Adresse, Utilisateur, Plante, Demande_plante, Message, Commentaire, MessageImage
from django.urls import reverse



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




def test_create_demande_plante(self):
    adresse = Adresse.objects.create(numero=1, voie="Place du Maréchal Leclerc", ville="Auxerre", code_postale=89000)
    utilisateur_demandeur = Utilisateur.objects.create(pseudo="User1", password="test", adresse=adresse)
    utilisateur_receveur = Utilisateur.objects.create(pseudo="User2", password="test", adresse=adresse)
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


class ViewsModelsFormsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.adresse = Adresse.objects.create(
            numero=123,
            voie='Rue de Test',
            ville='Testville',
            code_postale=12345
        )
        self.utilisateur = Utilisateur.objects.create(
            pseudo='testuser',
            password='password123',
            adresse=self.adresse
        )
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
        self.client.post(reverse('login'), {'pseudo': 'testuser', 'password': 'password123'})

    def test_login_view_post(self):
        response = self.client.post(reverse('login'), {'pseudo': 'testuser', 'password': 'password123'})
        self.assertIn(reverse('index'), response.headers.get('Location', ''))

    def test_creer_plante_view_post(self):
        self.login_user()
        form_data = {'nom_plante': 'Nouvelle Plante'}
        response = self.client.post(reverse('creer_plante'), data=form_data)
        self.assertIn(reverse('profil'), response.headers.get('Location', ''))

    def test_register_view_post(self):
        form_data = {
            'uc-pseudo': 'newuser',
            'uc-password': 'newpassword123',
            'numero': 456,
            'voie': 'Rue de Exemple',
            'ville': 'Exempleville',
            'code_postale': 67890
        }
        response = self.client.post(reverse('register'), data=form_data)


    def test_faire_demande_view_post(self):
        self.login_user()
        form_data = {'plante': self.plante.id_plante, 'message': 'Test message'}
        response = self.client.post(reverse('faire_demande'), data=form_data)
        self.assertIn(reverse('profil'), response.headers.get('Location', ''))

    def test_demande_view_post(self):
        self.login_user()
        form_data = {'text': 'Test message'}
        response = self.client.post(reverse('demande'), data=form_data)
        self.assertIn('demande', response.headers.get('Location', ''))

    def test_demande_aide_view_post(self):
        self.login_user()
        message = Message.objects.create(User=self.utilisateur, text='Test message')
        form_data = {'text': 'Test commentaire'}
        response = self.client.post(reverse('demande_aide', args=[message.id_message]), data=form_data)
        self.assertIn('demande_aide', response.headers.get('Location', ''))

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
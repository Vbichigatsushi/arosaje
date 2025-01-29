from django.test import TestCase, Client
from django.urls import reverse
from .models import Utilisateur, Plante, Demande_plante, Message

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Utilisateur.objects.create(id_utilisateur=1, pseudo="TestUser")
        self.client.session['logged_user_id'] = self.user.id_utilisateur
        self.client.session.save()
        self.plante = Plante.objects.create(id_plante=1, nom="Rose", utilisateur=self.user)
        self.demande = Demande_plante.objects.create(id=1, plante=self.plante, utilisateur_demandeur=self.user)
        self.message = Message.objects.create(id_message=1, texte="Test Message")

    def test_profil_view(self):
        response = self.client.get(reverse('profil'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profil.html')

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pageprincipale.html')

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_view_post(self):
        response = self.client.post(reverse('login'), {'pseudo': 'TestUser'})
        self.assertRedirects(response, reverse('index'))

    def test_creer_plante_view(self):
        response = self.client.get(reverse('creer_plante'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'creer_plante.html')

    def test_demandes_view(self):
        response = self.client.get(reverse('demandes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'demandes_en_attente.html')

    def test_faire_demande_view(self):
        response = self.client.get(reverse('faire_demande'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'faire_demande.html')

    def test_research_pro_view(self):
        response = self.client.get(reverse('research_pro'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'research_pro.html')

    def test_demande_view(self):
        response = self.client.get(reverse('demande'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'demande.html')

    def test_demande_aide_view(self):
        response = self.client.get(reverse('demande_aide', args=[self.message.id_message]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'demande_aide.html')

    def test_all_demande_garde_view(self):
        response = self.client.get(reverse('all_demande_garde'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'all_demande_garde.html')

    def test_garde_view(self):
        response = self.client.get(reverse('garde', args=[self.demande.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'garde.html')

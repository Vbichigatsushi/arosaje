from django.contrib import admin
from pageprincipale.models import Utilisateur, Plante, Adresse,Demande_plante,Demande

admin.site.register(Utilisateur)
admin.site.register(Plante)
admin.site.register(Adresse)
admin.site.register(Demande_plante)
admin.site.register(Demande)
from django.contrib import admin
from pageprincipale.models import Utilisateur, Plante, Adresse,Demande_plante,Demande,Message,Commentaire

admin.site.register(Utilisateur)
admin.site.register(Plante)
admin.site.register(Adresse)
admin.site.register(Demande_plante)
admin.site.register(Demande)
admin.site.register(Message)
admin.site.register(Commentaire)

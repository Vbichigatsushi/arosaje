from django.contrib import admin
from pageprincipale.models import Utilisateur, Plante, Adresse,Demande_plante,Message,Commentaire,MessageImage

admin.site.register(Utilisateur)
admin.site.register(Plante)
admin.site.register(Adresse)
admin.site.register(Demande_plante)

admin.site.register(Message)
admin.site.register(Commentaire)
admin.site.register(MessageImage)
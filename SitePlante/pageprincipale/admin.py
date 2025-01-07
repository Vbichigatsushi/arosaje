from django.contrib import admin
from pageprincipale.models import Person, Plante, Adress, Quality, Professionnel, Classiq_User

admin.site.register(Person)
admin.site.register(Plante)
admin.site.register(Quality)
admin.site.register(Adress)
admin.site.register(Professionnel)
admin.site.register(Classiq_User)
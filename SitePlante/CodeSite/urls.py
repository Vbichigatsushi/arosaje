"""
URL configuration for CodeSite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from pageprincipale.views import (
    index, login, register, profil, creer_plante, research_pro,
    faire_demande, demande_aide, demande, interactiv_map,
    filtered_garde_liste, all_demande_garde, garde, rgpd,
    suppression, supprimer, accepter_demande,
    supprimer_plante, supprimer_demande, changer_adresse,
    liste_plantes,
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('register/',register,name="register"),
    path('profil/', profil, name='profil'),
    path('contact_pro/', research_pro, name='pro'),
    path('creer_plante/', creer_plante, name='creer_plante'),
    path('faire_demande/',faire_demande,name='faire_demande'),
    path('demande/',demande,name='demande'),
    path('demande_aide/<int:id>/',demande_aide,name='demande_aide'),
    path('interactiv-map/', interactiv_map, name='interactiv-map'),
    path('filtered-garde-liste/', filtered_garde_liste, name='filtered-garde-liste'),
    path('all_demande_garde/', all_demande_garde, name='all_demande_garde'),
    path('accepter_demande/', accepter_demande, name='accepter_demande'),
    path('garde/<int:id>/',garde,name='garde'),
    path('supprimer_plante/<int:id_plante>/', supprimer_plante, name='supprimer_plante'),
    path('supprimer_demande/<int:demande_id>/', supprimer_demande, name='supprimer_demande'),
    path('rgpd',rgpd, name='rgpd'),
    path('suppression',suppression, name='suppression'),
    path('supprimer', supprimer, name='supprimer'),
    path('plantes/', liste_plantes),
    path('changer_adresse/', changer_adresse,name='changer_adresse'),
    
  
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

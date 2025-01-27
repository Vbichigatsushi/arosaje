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
from django.contrib.auth import login
from django.urls import path
from pageprincipale.views import index, faire_demande
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path
from pageprincipale.views import index
from django.contrib import admin
from django.urls import path
from pageprincipale.views import index,login,register,profil,creer_plante,demandes
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('register/',register,name="register"),
    path('profil/', profil, name='profil'),
path('demande/', demandes, name='demandes'),
path('creer_plante/', creer_plante, name='creer_plante'),
path('faire_demande/',faire_demande,name='faire_demande'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

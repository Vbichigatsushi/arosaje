from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from django.utils.timezone import now
import threading
from pytz import timezone

scheduler_lock = threading.Lock()
scheduler_started = False

class PageprincipaleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pageprincipale'

    def ready(self):
        
        global scheduler_started

        with scheduler_lock:
            if scheduler_started:
                return
            scheduler_started = True
        
        from .models import Utilisateur, Adresse
        
        
        def check_users_auth_date():
            today = now().date()
            one_year_ago = today - timedelta(days = 365)
            
            adresse_fictive, _ = Adresse.objects.get_or_create(
                numero=0,
                voie='Adresse supprimée',
                code_postale=0,
                ville='Inconnue',
                complement=''
            )
            
            
            utilisateurs = Utilisateur.objects.all()
            
            for user in utilisateurs:
                if user.date_auth and user.date_auth <= one_year_ago:
                    user.pseudo = "(Profil supprimé)"
                    user.password = ""
                    user.adresse = adresse_fictive
                    user.latitude = None
                    user.longitude = None
                    user.save()

                                    
                   
        scheduler = BackgroundScheduler()
        scheduler.add_job(
        check_users_auth_date,
        trigger=CronTrigger(hour=0, minute=0, timezone=timezone('Europe/Paris')),
        id="delete_users_informations",
        replace_existing=True,
        )

        scheduler.start()

        print("Démarrage de APScheduler")

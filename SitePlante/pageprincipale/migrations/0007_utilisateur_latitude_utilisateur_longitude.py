# Generated by Django 5.1.5 on 2025-01-29 06:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pageprincipale', '0006_alter_demande_plante_utilisateur_demandeur_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisateur',
            name='latitude',
            field=models.FloatField(default=3.570579),
        ),
        migrations.AddField(
            model_name='utilisateur',
            name='longitude',
            field=models.FloatField(default=47.7961287),
        ),
    ]

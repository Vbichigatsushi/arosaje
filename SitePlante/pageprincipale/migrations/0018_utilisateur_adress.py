# Generated by Django 5.1.5 on 2025-01-30 21:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pageprincipale', '0017_remove_utilisateur_adresse_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisateur',
            name='adress',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pageprincipale.adresse'),
        ),
    ]

# Generated by Django 5.1.7 on 2025-04-03 20:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Adresse',
            fields=[
                ('id_addresse', models.AutoField(primary_key=True, serialize=False)),
                ('numero', models.IntegerField()),
                ('voie', models.CharField(max_length=255)),
                ('complement', models.CharField(blank=True, max_length=255, null=True)),
                ('ville', models.CharField(max_length=255)),
                ('code_postale', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Plante',
            fields=[
                ('id_plante', models.AutoField(primary_key=True, serialize=False)),
                ('nom_plante', models.CharField(max_length=255)),
                ('photo_plante', models.ImageField(blank=True, null=True, upload_to='photos_plantes/')),
            ],
        ),
        migrations.CreateModel(
            name='TypeDemande',
            fields=[
                ('id_type_demande', models.AutoField(primary_key=True, serialize=False)),
                ('nom_type_demande', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Demande_plante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statut', models.CharField(choices=[('en attente', 'En attente'), ('acceptée', 'Acceptée'), ('refusée', 'Refusée')], default='en attente', max_length=20)),
                ('message', models.CharField(max_length=255, null=True)),
                ('date_demande', models.DateTimeField(auto_now_add=True)),
                ('date_reponse', models.DateTimeField(blank=True, null=True)),
                ('plante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pageprincipale.plante')),
            ],
        ),
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id_utilisateur', models.AutoField(primary_key=True, serialize=False)),
                ('is_pro', models.BooleanField(default=False)),
                ('pseudo', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('rgpd_accepted', models.BooleanField(default=False)),
                ('adresse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pageprincipale.adresse')),
            ],
        ),
        migrations.AddField(
            model_name='plante',
            name='utilisateur',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='plantes', to='pageprincipale.utilisateur'),
        ),
        migrations.CreateModel(
            name='MessageImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(blank=True, max_length=250, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='photos_plantes/')),
                ('Demande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pageprincipale.demande_plante')),
                ('utilisateur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pageprincipale.utilisateur')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id_message', models.AutoField(primary_key=True, serialize=False)),
                ('text', models.CharField(max_length=500)),
                ('date_demande', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='photos_plantes/')),
                ('User', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pageprincipale.utilisateur')),
            ],
        ),
        migrations.AddField(
            model_name='demande_plante',
            name='utilisateur_demandeur',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demandes_envoyees', to='pageprincipale.utilisateur'),
        ),
        migrations.AddField(
            model_name='demande_plante',
            name='utilisateur_receveur',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='demandes_recues', to='pageprincipale.utilisateur'),
        ),
        migrations.CreateModel(
            name='Commentaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('demande', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commentaires', to='pageprincipale.message')),
                ('User', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pageprincipale.utilisateur')),
            ],
        ),
    ]

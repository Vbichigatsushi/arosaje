# Generated by Django 5.1.5 on 2025-01-26 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pageprincipale', '0004_demande_plante'),
    ]

    operations = [
        migrations.AddField(
            model_name='demande_plante',
            name='message',
            field=models.CharField(max_length=255, null=True),
        ),
    ]

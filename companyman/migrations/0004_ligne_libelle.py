# Generated by Django 4.1.7 on 2023-05-12 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companyman', '0003_rename_id_user_utilisateur_nom_utilisateur'),
    ]

    operations = [
        migrations.AddField(
            model_name='ligne',
            name='libelle',
            field=models.CharField(max_length=40, null=True),
        ),
    ]
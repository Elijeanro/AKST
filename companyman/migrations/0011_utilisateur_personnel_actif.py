# Generated by Django 4.2.1 on 2023-05-31 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companyman', '0010_infoligne_date_arr'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisateur',
            name='personnel_actif',
            field=models.BooleanField(default=True),
        ),
    ]
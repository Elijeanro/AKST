# Generated by Django 4.1.7 on 2023-05-24 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companyman', '0007_infoligne_compagnie_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='infoligne',
            name='compagnie_id',
        ),
        migrations.AddField(
            model_name='ligne',
            name='duree_trajet',
            field=models.DurationField(null=True),
        ),
    ]

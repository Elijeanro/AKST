# Generated by Django 4.1.7 on 2023-05-05 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0008_etatbillet'),
    ]

    operations = [
        migrations.AddField(
            model_name='billet',
            name='etat_billet',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='client.etatbillet'),
        ),
    ]

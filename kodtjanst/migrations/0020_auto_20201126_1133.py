# Generated by Django 3.1.2 on 2020-11-26 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0019_kodverk_användning_av_kodverk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kodverk',
            name='ägare_till_kodverk',
            field=models.CharField(choices=[('Informatik', 'Informatik'), ('Inera', 'Inera'), ('Socialstyrelsen', 'Socialstyrelsen'), ('Västra Götalandsregionen', 'Västra Götalandsregionen'), ('Skatteverket', 'Skatteverket')], max_length=255, null=True),
        ),
    ]

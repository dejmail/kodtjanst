# Generated by Django 3.1.2 on 2020-10-28 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0008_auto_20200714_1354'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kodtext',
            name='extra_data',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='kodverk',
            name='extra_data',
            field=models.JSONField(blank=True, help_text='Data behöver vara i JSON format dvs {"nyckel" : "värde"} <br> t.ex {"millenium_code_value": 22897599} och kan kan hierarkiska nivåer', null=True),
        ),
    ]

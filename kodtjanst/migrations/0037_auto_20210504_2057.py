# Generated by Django 3.1.2 on 2021-05-04 18:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0036_auto_20210428_1114'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kodverk',
            old_name='beskrivning_av_informationsbehov',
            new_name='beskrivning_av_innehållet',
        ),
    ]

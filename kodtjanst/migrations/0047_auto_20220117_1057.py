# Generated by Django 3.1.2 on 2022-01-17 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0046_auto_20220117_1016'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalkodverk',
            old_name='länk_till_underlag',
            new_name='länk',
        ),
        migrations.RenameField(
            model_name='kodverk',
            old_name='länk_till_underlag',
            new_name='länk',
        ),
    ]

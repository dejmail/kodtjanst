# Generated by Django 3.1.2 on 2021-05-27 08:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0040_auto_20210519_0809'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kodverk',
            old_name='identifier',
            new_name='identifierare',
        ),
    ]

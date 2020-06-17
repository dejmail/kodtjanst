# Generated by Django 3.0.3 on 2020-05-26 13:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0005_auto_20200526_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kodverk',
            name='version',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.01)]),
        ),
    ]
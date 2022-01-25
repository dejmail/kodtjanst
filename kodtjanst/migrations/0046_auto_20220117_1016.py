# Generated by Django 3.1.2 on 2022-01-17 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0045_auto_20210920_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalkodverk',
            name='kodverk_variant',
            field=models.CharField(blank=True, choices=[('VGR kodverk', 'VGR kodverk'), ('Externt kodverk hänvisning', 'Externt kodverk hänvisning'), ('VGR codeable concept', 'VGR codeable concept')], max_length=26, null=True),
        ),
        migrations.AlterField(
            model_name='kodverk',
            name='kodverk_variant',
            field=models.CharField(blank=True, choices=[('VGR kodverk', 'VGR kodverk'), ('Externt kodverk hänvisning', 'Externt kodverk hänvisning'), ('VGR codeable concept', 'VGR codeable concept')], max_length=26, null=True),
        ),
    ]
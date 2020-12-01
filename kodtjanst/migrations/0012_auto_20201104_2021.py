# Generated by Django 3.1.2 on 2020-11-04 19:21

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0011_auto_20201030_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='kodtext',
            name='datum_skapat',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='kodtext',
            name='senaste_ändring',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='kodverk',
            name='datum_skapat',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='kodverk',
            name='senaste_ändring',
            field=models.DateField(auto_now=True, null=True),
        ),
    ]
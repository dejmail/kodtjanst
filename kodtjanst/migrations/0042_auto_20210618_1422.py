# Generated by Django 3.1.2 on 2021-06-18 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0041_auto_20210527_1021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kodverk',
            name='kodverk_variant',
            field=models.CharField(blank=True, choices=[('kodverk', 'kodverk'), ('codeable concept', 'codeable concept'), ('paraply', 'paraply'), ('code set', 'code set'), ('alpha response', 'alpha response'), ('urval', 'urval')], max_length=17, null=True),
        ),
    ]

# Generated by Django 3.1.2 on 2021-02-12 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0029_auto_20210202_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kodverk',
            name='mappning_för_rapportering',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
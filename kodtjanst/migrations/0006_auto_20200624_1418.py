# Generated by Django 3.0.6 on 2020-06-24 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0005_auto_20200624_1103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mappadtillkodtext',
            name='mappad_id',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='mappadtillkodtext',
            name='mappad_text',
            field=models.CharField(max_length=255),
        ),
    ]

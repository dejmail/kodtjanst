# Generated by Django 3.0.6 on 2020-06-19 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kodtext',
            old_name='andra_definition',
            new_name='annan_kodtext',
        ),
        migrations.AlterField(
            model_name='kodtext',
            name='kodtext',
            field=models.CharField(max_length=255, null=True),
        ),
    ]

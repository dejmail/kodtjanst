# Generated by Django 3.1.2 on 2020-11-24 19:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0016_auto_20201124_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nyckelord',
            name='kodverk_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='kodtjanst.kodverk'),
        ),
    ]

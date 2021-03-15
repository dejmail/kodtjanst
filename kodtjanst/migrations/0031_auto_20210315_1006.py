# Generated by Django 3.1.2 on 2021-03-15 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kodtjanst', '0030_auto_20210212_1118'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kodverk',
            old_name='hämtnings_källa',
            new_name='källa',
        ),
        migrations.RemoveField(
            model_name='kodverk',
            name='instruktion_för_kodverket',
        ),
        migrations.RemoveField(
            model_name='kodverk',
            name='mappning_för_rapportering',
        ),
        migrations.AddField(
            model_name='kodverk',
            name='länk_till_underlag',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='kodverk',
            name='underlag',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
    ]

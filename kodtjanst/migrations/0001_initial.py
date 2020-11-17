# Generated by Django 3.0.6 on 2020-06-17 18:11

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternaKodverk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('namn', models.CharField(max_length=255)),
                ('url', models.URLField()),
                ('kodterm_url', models.URLField(null=True)),
            ],
            options={
                'verbose_name_plural': 'Externa Kodverk',
            },
        ),
        migrations.CreateModel(
            name='Kodtext',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('andra_definition', models.TextField(blank=True, max_length=500, null=True)),
                ('definition', models.TextField(blank=True, max_length=500, null=True)),
                ('extra_data', models.JSONField(default=dict, null=True)),
                ('kod', models.CharField(max_length=255, null=True)),
                ('kodtext', models.CharField(max_length=255)),
                ('kommentar', models.TextField(null=True)),
                ('position', models.PositiveIntegerField(null=True)),
                ('status', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'verbose_name_plural': 'Kodtexter',
            },
        ),
        migrations.CreateModel(
            name='Kodverk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('beskrivning_av_informationsbehov', models.TextField(null=True)),
                ('giltig_från', models.DateField(null=True)),
                ('giltig_tom', models.DateField(null=True)),
                ('kommentar', models.TextField(null=True)),
                ('identifier', models.CharField(max_length=255, null=True)),
                ('instruktion_för_kodverket', models.CharField(max_length=255, null=True)),
                ('extra_data', models.JSONField(default=dict, null=True)),
                ('kategori', models.CharField(max_length=255, null=True)),
                ('kodschema', models.CharField(max_length=255, null=True)),
                ('kodverk_variant', models.CharField(blank=True, choices=[('Kodverk', 'Kodverk'), ('Kodset', 'Kodset'), ('Alfa respons', 'Alfa respons'), ('Urval', 'Urval')], max_length=12, null=True)),
                ('kort_beskrivning', models.TextField(max_length=1000, null=True)),
                ('källa', models.CharField(max_length=255, null=True)),
                ('mappning_för_rapportering', models.BooleanField(null=True)),
                ('rubrik_på_kodverk', models.CharField(max_length=255, null=True)),
                ('senaste_ändring', models.DateField(blank=True, null=True)),
                ('språk', models.CharField(choices=[('svenska', 'svenska'), ('engelska', 'engelska')], default='svenska', max_length=25, null=True)),
                ('status', models.CharField(blank=True, max_length=25, null=True)),
                ('syfte', models.TextField(max_length=1000, null=True)),
                ('system_som_använderkodverket', models.CharField(max_length=255, null=True)),
                ('uppdateringsintervall', models.CharField(choices=[('Årligen', 'Årligen'), ('Månadsvis', 'Månadsvis'), ('Veckovis', 'Veckovis'), ('Dagligen', 'Dagligen'), ('Vid behov', 'Vid behov'), ('Ej aktuellt', 'Ej aktuellt')], max_length=20, null=True)),
                ('version', models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('version_av_källa', models.CharField(max_length=50, null=True)),
                ('ägare_av_kodverk', models.CharField(choices=[('Inera', 'Inera'), ('Socialstyrelsen', 'Socialstyrelsen'), ('Västra Götalandsregionen', 'Västra Götalandsregionen')], max_length=255, null=True)),
                ('ansvarig', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ansvarig_person', to=settings.AUTH_USER_MODEL)),
                ('urval_referens', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='kodtjanst.Kodverk')),
                ('ändrad_av', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ändrad_av_person', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Kodverk',
            },
        ),
        migrations.CreateModel(
            name='Ämne',
            fields=[
                ('domän_id', models.AutoField(primary_key=True, serialize=False)),
                ('domän_kontext', models.TextField(null=True)),
                ('domän_namn', models.CharField(max_length=255)),
                ('kodverk', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='kodtjanst.Kodverk')),
            ],
            options={
                'verbose_name_plural': 'Ämnesområde',
            },
        ),
        migrations.CreateModel(
            name='Nyckelord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nyckelord', models.CharField(blank=True, max_length=255, null=True)),
                ('kodverk_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='kodtjanst.Kodtext')),
            ],
            options={
                'verbose_name_plural': 'Nyckelord',
            },
        ),
        migrations.CreateModel(
            name='MappadTillKodtext',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mappad_id', models.CharField(max_length=255, null=True)),
                ('mappad_text', models.CharField(max_length=255, null=True)),
                ('resolving_url', models.URLField()),
                ('kommentar', models.TextField(null=True)),
                ('kodtext', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='kodtjanst.Kodtext')),
            ],
            options={
                'verbose_name_plural': 'Mappad Kodtexter',
            },
        ),
        migrations.AddField(
            model_name='kodtext',
            name='kodverk',
            field=models.ForeignKey(default=11, on_delete=django.db.models.deletion.PROTECT, to='kodtjanst.Kodverk'),
        ),
        migrations.AddField(
            model_name='kodtext',
            name='ändrad_av',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]

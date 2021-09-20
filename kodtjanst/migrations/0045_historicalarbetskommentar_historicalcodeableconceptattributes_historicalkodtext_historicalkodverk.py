# Generated by Django 3.1.2 on 2021-09-14 08:20

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kodtjanst', '0044_validatedby'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalKodverk',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('syfte', models.TextField(max_length=1000, null=True)),
                ('beskrivning_av_innehållet', models.TextField(blank=True, null=True, verbose_name='Beskrivning av innehållet')),
                ('identifierare', models.CharField(blank=True, max_length=255, null=True)),
                ('titel_på_kodverk', models.CharField(max_length=255, null=True)),
                ('version', models.FloatField(default=None, null=True, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('kategori', models.CharField(max_length=255, null=True)),
                ('underlag', models.TextField(blank=True, max_length=100, null=True)),
                ('länk_till_underlag', models.URLField(blank=True, null=True)),
                ('kodverk_variant', models.CharField(blank=True, choices=[('kodverk', 'kodverk'), ('codeable concept', 'codeable concept'), ('code set', 'code set'), ('alpha response', 'alpha response'), ('urval', 'urval')], max_length=17, null=True)),
                ('status', models.CharField(blank=True, choices=[('Publicera ej', 'Publicera ej'), ('Aktiv', 'Aktiv'), ('Inaktiv', 'Inaktiv')], max_length=25, null=True)),
                ('uppdateringsintervall', models.CharField(blank=True, choices=[('Årligen', 'Årligen'), ('Halvårsvis', 'Halvårsvis'), ('Vid behov', 'Vid behov')], max_length=20, null=True)),
                ('datum_skapat', models.DateField(blank=True, editable=False)),
                ('senaste_ändring', models.DateField(blank=True, editable=False, null=True)),
                ('giltig_från', models.DateField(null=True)),
                ('giltig_tom', models.DateField(default=datetime.date(2099, 12, 31), null=True)),
                ('extra_data', models.JSONField(blank=True, help_text='Data behöver vara i JSON format dvs {"nyckel" : "värde"} <br> t.ex {"millenium_code_value": 22897599} och kan ha hierarkiska nivåer', null=True)),
                ('användning_av_kodverk', models.CharField(blank=True, max_length=255, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('ansvarig', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Ansvarig person')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('urval_referens', models.ForeignKey(blank=True, db_constraint=False, help_text='Välja kodverket som är huvud kodverket', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='kodtjanst.kodverk')),
                ('ändrad_av', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical kodverk',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalKodtext',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('annan_kodtext', models.CharField(blank=True, max_length=255, null=True)),
                ('datum_skapat', models.DateField(blank=True, editable=False)),
                ('definition', models.TextField(blank=True, max_length=500, null=True)),
                ('extra_data', models.JSONField(blank=True, help_text='Data behöver vara i JSON format dvs {"nyckel" : "värde"} <br> t.ex {"millenium_code_value": 22897599} och kan ha hierarkiska nivåer', null=True)),
                ('kod', models.CharField(blank=True, max_length=255, null=True)),
                ('kodtext', models.CharField(max_length=255, null=True)),
                ('kommentar', models.TextField(blank=True, null=True)),
                ('position', models.PositiveIntegerField(blank=True, null=True)),
                ('senaste_ändring', models.DateField(blank=True, editable=False)),
                ('status', models.CharField(blank=True, choices=[('Publicera ej', 'Publicera ej'), ('Beslutad', 'Beslutad'), ('Utkast', 'Utkast'), ('Okänt', 'Okänt')], max_length=50, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('kodverk', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='kodtjanst.kodverk')),
                ('ändrad_av', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical kodtext',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalCodeableConceptAttributes',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('källa', models.CharField(blank=True, max_length=255, null=True)),
                ('version_av_källa', models.CharField(blank=True, max_length=50, null=True)),
                ('ansvarig_förvaltare', models.CharField(max_length=255, null=True)),
                ('ägare_till_kodverk', models.CharField(max_length=255, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('kodverk_from', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='kodtjanst.kodverk')),
            ],
            options={
                'verbose_name': 'historical codeable concept attributes',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalArbetsKommentar',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('kommentar', models.TextField(blank=True, max_length=5000, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('angivet_av', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Angivet av person')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('kodverk', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='kodtjanst.kodverk')),
            ],
            options={
                'verbose_name': 'historical arbets kommentar',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
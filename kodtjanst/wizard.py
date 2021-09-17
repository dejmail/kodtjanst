import data_wizard
from rest_framework import serializers
from django.db.models.fields import TextField

from kodtjanst.models import Kodverk, Kodtext
from pdb import set_trace

from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from django.core.exceptions import ObjectDoesNotExist

kodverk_header_map = {'urval_reference': 'Värde från KV - finns det koppling till ett regionalt KV?',
                        'syfte': 'Syfte',
                        'json-codeset_nummer': 'Code set-nummer',
                        'titel_på_kodverk': 'Tillhör codeset / DTA - obligatoriskt om det är från Millennium',
                        'giltig_från': 'Datum - obligatorisk',
                        'version': 'Version',
                        'ämnesområde': 'Konsumenter - obligatorisk',
                        'kommentar': 'Kommentar',
                        'ägare_till_kodverk':     'Ägare - obligatorisk',
                        'ansvarig_id': 'Inlagt i filen av - obligatoriskt med kontaktperson',
                        'urval_referens': 'Kodverksrelation - vid koppling till ett regionalt utvecklat kodverk',
                        'system_som_använderkodverket': 'System/modul - obligatorisk',
                        'json-dcw': 'Tillhör DCW - obligatoriskt om det är från Millennium',
                        'status': 'Status',
                        'nyckelord': 'Förslag på sökord/ägare_till_kodverk till databasen - fyll i detta så gott ni kan!'}

kodverk_excel_db_map = {value:key for key,value in kodverk_header_map.items()}


def clean_data_dictionary(model, data_dictionary, json_field):

    fields_notin_model = [i.lower() for i in data_dictionary.keys() if i.lower() not in dir(model)]
    new_dictionary = {key.lower():value for key,value in data_dictionary.items() if key in dir(model)}
    temp_dict = {json_field:''}
    for extra_data in fields_notin_model:
        
        temp_dict[json_field] = temp_dict[json_field] + f'"{extra_data}" : "{data_dictionary.get(json_field)}", '
    new_dictionary.update(temp_dict)
    return new_dictionary, fields_notin_model

class KodverkSerializer(serializers.ModelSerializer):

    syfte = serializers.CharField(source="Syfte")#, style={'base_template': 'textarea.html'})
    titel_på_kodverk = serializers.CharField(source='Tillhör codeset / DTA - obligatoriskt om det är från Millennium')
    giltig_från = serializers.DateField(source='Datum - obligatorisk')
    version = serializers.FloatField(source='Version', required=False, allow_null=True)
    ämnesområde = serializers.CharField(source='Konsumenter - obligatorisk', allow_blank=True, allow_null=True, required=False)
    kommentar = serializers.CharField(source='Kommentar', style={'base_template': 'textarea.html'}, allow_blank=True, allow_null=True, required=False)
    ägare_till_kodverk = serializers.CharField(source='Ägare - obligatorisk')
    ansvarig_id = serializers.CharField(source='Inlagt i filen av - obligatoriskt med kontaktperson', allow_null=True, required=False)
    ändrad_av = serializers.CharField(required=False)
    urval_referens = serializers.CharField(source='Kodverksrelation - vid koppling till ett regionalt utvecklat kodverk', allow_blank=True, allow_null=True, required=False)
    system_som_använderkodverket = serializers.CharField(source='System/modul - obligatorisk', allow_blank=True, allow_null=True, required=False)
    status = serializers.CharField(source='Status', allow_blank=True, allow_null=True, required=False)
    nyckelord = serializers.CharField(source='Förslag på sökord/ägare_till_kodverk till databasen - fyll i detta så gott ni kan!')

    def create(self, validated_data):  
        
        try:           
            db_keys_mapped_validated_data = {kodverk_excel_db_map.get(keys, keys):values for keys,values in validated_data.items()}
            mapped_validated_data, fields_not_in_model = clean_data_dictionary(Kodverk, data_dictionary=db_keys_mapped_validated_data, json_field='extra_data')
            mapped_validated_data['ändrad_av'] = User.objects.get(id=self.context.get('data_wizard').get('run').user_id)
            return Kodverk.objects.create(**mapped_validated_data)
        except Exception as e:
            print(f'Found an error creating the data, but passing on it - {e}')
           
    class Meta:
        model = Kodverk
        fields = '__all__'

        # Optional - see options below
        data_wizard = {
            'header_row': 0,
            'start_row': 1,
            'show_in_list': True,
            'idmap': data_wizard.idmap.existing,
        }

class KodtextSerializer(serializers.ModelSerializer):

    kodverk = serializers.PrimaryKeyRelatedField(queryset=Kodverk.objects.filter(status="Aktiv").all().order_by('titel_på_kodverk'))

    class Meta:
        model = Kodtext
        fields = ('kod','kodtext','kodverk', 'kodverk_id','annan_kodtext','definition','kommentar','position','status')
        # Optional - see options below
        data_wizard = {
            'header_row': 0,
            'start_row': 1,
            'show_in_list': True,
            'idmap': data_wizard.idmap.existing,
        }

# Use default name & serializer
#data_wizard.register(Kodtext)

# Use custom name & serializer
#data_wizard.register("Kodverk Gäng Default Mall Omvandlare", KodverkSerializer)
data_wizard.register("Kodtext Omvandlare", KodtextSerializer)

import sys

from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from pdb import set_trace

import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from django.contrib.auth.models import User

import datetime
import pandas as pd
import numpy as np
import json

from itertools import islice
import pandas as pd

def create_dictionary_from_headers(header_row):
    header_dict = {}
    for headers in header_row:
        header_dict[headers.col_idx] = headers.value
    return header_dict

def return_which_attr_at_index(header_attr_dict, kodverk_header_dict, position):
    
    header = kodverk_header_dict.get(column.col_idx)
        
    if header is not None:
        attr = header_attr_dict.get(header)
        return attr

def write_to_database(dict_to_write, cursor, table_name):

    
    columns = ', '.join(dict_to_write.keys())
    placeholders = ', '.join('?' * len(dict_to_write))
    sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
    print(sql)
    #set_trace()
    cursor.execute(sql, tuple(dict_to_write.values()))
    connection.commit()

def format_date(datestamp):
    try:
        return datestamp.strftime("%Y/%m/%d")        
    except AttributeError:
        return datetime.datetime.now().strftime("%Y/%m/%d")

def find_row_position(df, keyword):
    for index, row in df.iterrows():
        try:
            if (keyword in row[0]):
                return index
        except TypeError:
            pass

def create_json(attr, key, row):
    
    if row.get(attr) is not None:        
        if ('extra_data' in row) and (row.extra_data is not None):
            try:
                json_string = json.loads(row.extra_data)
                json_string[key] = row.get(attr)
                return json.dumps(json_string)
            except AttributeError:
                set_trace()
        else:
            return json.dumps({key : row.get(attr)})
    elif ('extra_data' in row):
        return row.extra_data
    else: 
        return None

def extract_date(cell, split_text, return_position):
    if cell is not None:
        split = cell.split(split_text)
        return split_text + split[return_position]
    else:
        return None

def check_and_swop_values(row, main_value, swop_value):
    
    if row.get(main_value) is None:
        return row.get(swop_value)
    else:
        return row.get(main_value)

def create_synonyms(row):
        
        if ('extra_data' in row) and (row.extra_data is not None):
            try:
                json_string = json.loads(row.extra_data)
                split_titles = row.rubrik_på_kodverk.split(',')
                if len(split_titles) > 1:
                    json_string['synonym'] = row.rubrik_på_kodverk.split(',')[1:]
                    return row.rubrik_på_kodverk.split(',')[0], json.dumps(json_string)
                else:
                    return row.rubrik_på_kodverk, None
            except AttributeError:
                set_trace()
        else:
            return None, None

def get_kodverk_variant(cell, kod_variant_dict):
    
    replacement_value = kod_variant_dict.get(cell)
    if (cell is not None) and (replacement_value is None):
        print("There is a kodverk name, but the variant type has not been found")
        set_trace()
    elif (cell is None) and (replacement_value is None):
        return None
    else:
        return replacement_value

def start_index_from_end_previous_df(df, max_index):
    
    # reset the indexes so that they continue from the previous df
    try:
        df.index = np.arange(max_index+1, max_index+len(df)+1)            
    except (ValueError, TypeError) as e:
        print(e)
        set_trace()
    return df
    #set_trace()


def check_for_user_presence(cell, engine):
    if cell is not None:
        try:
            firstname, lastname = cell.split(" ")
        except (NameError, ValueError, AttributeError) as e:
            if e == "'datetime.datetime' object has no attribute 'split'":
                print("Looks like there is a missing name")
                set_trace()
            
            else:
                print(e, "either > 2 words per name, or > 1 user in cell. Only one name permitted")
                try:
                    if cell == 'Lai Bang Wåhlander':
                        firstname = 'Lai'
                        lastname = "Bang Wåhlander"
                    else:
                        print("User is not Lai, we need a fix")
                        set_trace()
                except IntegrityError as e:
                    print(e)
                    set_trace()

        with engine.connect() as con:
            line_exec_statement = f"SELECT * from auth_user WHERE first_name = '{firstname}' AND last_name = '{lastname}';"
            statement = text(line_exec_statement)
            result = con.execute(statement).fetchall()
            if len(result) == 0:
                user = User.objects.create_user(username=firstname, first_name=firstname, last_name=lastname, password=lastname+'2020')
            elif len(result) > 1:
                print("There are multiple users with these first and last names, please correct before proceeding")
                set_trace()
            else:
                return result[0][0]
    else:
        return 1

def compile_sql_string(row, attr_names):
    
    compiled_str_list = []
    for i in attr_names.split(','):
        if i.strip() in row.index:
            cell_value = f"{row[f'{i.strip()}']}"
            if (cell_value is None) or (cell_value.lower() == 'none'):
                compiled_str_list.append('null')
            else:
                compiled_str_list.append(f'"{cell_value}"')
    #if row.extra_data == None: set_trace()    
    return ','.join(compiled_str_list)

def max_rows_in_table(tablename, engine):
    
     with engine.connect() as con:
            line_execute_statement = f"SELECT * FROM {tablename};"
            statement = text(line_execute_statement)
            result = con.execute(statement)
            return result.rowcount
  
def write_data_to_database(df, tablename, attr_names, engine):
    
    with engine.connect() as con:
        for index, df_row in df.iterrows():
            #if df_row.extra_data == None: set_trace()
            values = compile_sql_string(row=df_row, attr_names=attr_names)
            #set_trace()
            line_execute_statement = f"INSERT INTO {tablename}({attr_names}) VALUES({values})"
            line_execute_statement = line_execute_statement.replace('"{',"\'{")
            line_execute_statement = line_execute_statement.replace('}"',"}\'")
            print(line_execute_statement+';')
            statement = text(line_execute_statement)
            #print(line_execute_statement+';')
            try:
                pass
                #con.execute(statement)
            except (UnicodeEncodeError, IntegrityError) as e:
                print(e)
                set_trace()


def convert_str_to_bytes(cell):
    
    if cell is not None:
        #set_trace()
        string_as_bytes = bytes(cell, 'utf-8')
        try:
            return '|'.join([str(byte) for byte in string_as_bytes])        
        except TypeError as e:
            print(e)
            set_trace()
    else:
        return cell


#kodverk
header_attr_dict = {
     'Värde från KV - finns det koppling till ett regionalt KV?' : 'urval_reference',
     'Syfte' : 'syfte',
     'Code set-nummer' : 'json-codeset_nummer',
     'Tillhör codeset / DTA - obligatoriskt om det är från Millennium' : 'rubrik_på_kodverk',
     'Datum - obligatorisk' : 'giltig_från',
     'Version' : 'version',
     'Konsumenter - obligatorisk' : 'ämnesområde',
     'Kommentar' : 'kommentar',
     'Ägare - obligatorisk' : 'ägare_av_kodverk',
     'Inlagt i filen av - obligatoriskt med kontaktperson' : 'ansvarig_id',
     'Kodverksrelation - vid koppling till ett regionalt utvecklat kodverk' : 'urval_referens',
     'System/modul - obligatorisk' : 'system_som_använderkodverket',
     'Tillhör DCW - obligatoriskt om det är från Millennium' : 'json-dcw',
     'Status' : 'status',
     'Förslag på sökord/nyckelord till databasen - fyll i detta så gott ni kan!' : 'nyckelord'}


kodtext_attr_dict = {
        'Tillhör DCW - code set/DTA - (fyll i om det är flera DCW/DTA i samma flik, annars lämna tom)' : 'kodverk_id',
        'Code value' : 'json-code_value',
        'Engelskt begrepp i Codeset' : 'annan_kodtext',
        'Term/kodtext - obligatoriskt' : 'kodtext',
        # going to be saved as part of kommentar
        'Förtydligande text i Millennium' : 'json-förtydligande',
        'Kodverk, code set eller alpha response' : 'kodverk_variant',
        # placed in another table that refers back to this one
        'Snomedkod (SCTID) & kodtext - Detta fylls i först när mappningen sker, ex byggfasen. ' : 'mappad_id',
        'Vid Snomed-mappning - fyll i PT eller SYN' : 'mappad_text',
        'Kommentar - status i strömarbetet (DESIGN, SKICKAT TILL BYGG, VALIDERING, REVIDERING) - obligatorisk' : 'status',
        'Kommentar - dubblett finnes / övrig synpunkt' : 'kommentar',
        # saved in another table
        'Konsument - återanvänds i flera strömmar/DCW? Fyll i vilka\narbetsström(mar) samt DCW' : 'domän',
        # used to create a kodverk as sometimes this is not placed in the kodverk rows
        'Värde från KV - finns det koppling till ett regionalt KV?' : 'kodverk_alternativ',
        # may have to create a user based on this
        'Inlagd av - obligatorisk' : 'ändrad_av_id'    
}

sheets_to_avoid = ['Instruktioner', 
                   'Register', 
                   'Mall']



def main_import_function(incoming_file):

    kodverk_max_index = max_rows_in_table('kodtjanst_kodverk', engine)
    kodtext_max_index = max_rows_in_table('kodtjanst_kodtext', engine)
    external_links_max_index = max_rows_in_table('kodtjanst_mappadtillkodtext', engine)
    ämnesområde_max_index = max_rows_in_table('kodtjanst_ämne', engine)

    kodfile = load_workbook(incoming_file)
    for sheet in kodfile:
        # loop through the sheets in the file
        if (sheet.title not in sheets_to_avoid):
            
            kodverk_df = pd.DataFrame(sheet.values)
            # take the headers from the first line
            kodverk_df.columns = kodverk_df.iloc[0]
            kodverk_df.drop([0], inplace=True)
            if None in kodverk_df.columns:
                kodverk_df.drop(columns=[None], inplace=True)
            # go through each of the columns
            # and rename it from a dictionary
            for column in kodverk_df.columns:
                if header_attr_dict.get(column) is not None:
                    new_column_name = header_attr_dict.get(column)
                    kodverk_df.rename(columns={column : header_attr_dict.get(column)}, inplace=True)
                else:
                    print("Column name not found in header_attr_dict, column", column)
                    set_trace()
            
            # find where the kodtext lines begin as it can vary
            kodtext_position = find_row_position(kodverk_df, "Tillhör DCW - code set/DTA - (fyll i om det är flera DCW/DTA i samma flik, annars lämna tom)")
                
            if kodtext_position is not None:
                
                # cut the dataframes in 2 based on the position of the kodtext header row
                kodtext_df = kodverk_df.loc[kodtext_position:,:].copy()
                kodtext_df.dropna(how='all', axis=0, inplace=True)
                
                kodverk_df = kodverk_df.drop(kodverk_df.index[kodtext_position-1:])
                kodverk_df.dropna(how='all', axis=0, inplace=True)
                
                #set_trace()
                kodverk_df = start_index_from_end_previous_df(max_index=kodverk_max_index, df=kodverk_df)
                
                # reset the index
                kodtext_df.reset_index(inplace=True, drop=True)
                kodtext_df.columns = kodtext_df.iloc[0]
                kodtext_df.drop([0], inplace=True)
                kodtext_df.rename(columns=kodtext_attr_dict, inplace=True)
                kodtext_df = start_index_from_end_previous_df(max_index=kodtext_max_index, df=kodtext_df)
                
                # copy the JSON values to the extra data column
                kodtext_df['extra_data'] = kodtext_df.apply(lambda row: create_json('json-code_value', 'millenium_code_value', row), axis=1)
                kodtext_df['extra_data'] = kodtext_df.apply(lambda row: create_json('json-förtydligande','förtydligande', row), axis=1)
                
                # split the status into "status" and "senaste_ändring"
                # as the cells have multidata
                kodtext_df['senaste_ändring'] = kodtext_df.loc[:,'status'].apply(lambda cell: extract_date(cell, '2020', -1))
                kodtext_df['status'] = kodtext_df.loc[:,'status'].apply(lambda cell: cell.split('2020')[0] if cell is not None else None)
                kodtext_df.drop(columns=['Syfte - obligatorisk', 'json-code_value','json-förtydligande'], inplace=True)
            
            # the type of kodverk is in the wrong place, but no matter
            # we group by the two columns, get the unique, and apply
            # that to the kodverk instead of the kodtext
            kod_variant_df = kodtext_df.loc[:,['kodverk_id', 'kodverk_variant']].groupby('kodverk_id')['kodverk_variant'].unique().to_frame().reset_index()
            kod_variant_df['kodverk_typ'] = kod_variant_df.loc[:,'kodverk_variant'].apply(lambda cell: cell[0])
            kod_variant_dict = {v.kodverk_id:v.kodverk_variant[0] for i,v in kod_variant_df.iterrows()}
            
            # move some of the columns in the kodverk_df
            # to the JSON columns
            kodverk_df['extra_data'] = kodverk_df.apply(lambda row: create_json('json-dcw', 'millenium_dcw', row), axis=1)
            kodverk_df['extra_data'] = kodverk_df.apply(lambda row: create_json('json-codeset_nummer', 'codeset_nummer', row), axis=1)
            # this comes after the previous ones so that the column is present
            for index, row in kodverk_df.iterrows():
                if row.rubrik_på_kodverk is not None:
                    #if (sheet.title == 'Encounter type') and (index==2): set_trace()
                    new_title, new_json = create_synonyms(row)
                if new_json is not None:
                    kodverk_df.loc[index,'extra_data'] = new_json
                if new_title is not None:
                    kodverk_df.loc[index,'rubrik_på_kodverk'] = new_title
                
            # this is placed here so that the name has been changed by this point
            kodverk_df['kodverk_variant'] = kodverk_df.loc[:,'rubrik_på_kodverk'].apply(lambda cell: get_kodverk_variant(cell, kod_variant_dict))
            
            # extract external mapping links, as these go in another table
            external_links = kodtext_df.loc[:,['kodverk_id', 'kodtext','mappad_id','mappad_text','kodverk_alternativ']].dropna(subset=['mappad_id'])
            
            # there may be no external links used in the codework
            if len(external_links) != 0:
                for index, row in external_links.iterrows():
                    if (row.kodverk_id is None) and (row.kodverk_alternativ is not None):
                        external_links.loc[index, 'kodverk_id'] = row.kodverk_alternativ
                    elif (row.kodverk_id is not None):
                        pass
                    else:
                        print("This kodtext has no associated kodverk, please fix")
                        set_trace()

                external_links['resolving_url'] = ' http://snomed.info/id/'
                external_links = start_index_from_end_previous_df(df=external_links, max_index=external_links_max_index)
            ämnesområde_df = kodverk_df.loc[:,['rubrik_på_kodverk','ämnesområde']]
            ämnesområde_df = start_index_from_end_previous_df(df=ämnesområde_df, max_index=ämnesområde_max_index)
            
            # clean up some columns that are no longer needed or that have been moved
            kodverk_df.drop(columns=['json-dcw', 'json-codeset_nummer', 'ämnesområde'], inplace=True)
            kodtext_df.drop(columns=['mappad_id','mappad_text'], inplace=True)
            
            
            ''' some of the internal codesets are place in this file as well, and they
            don't have a name in the first column. So we swop the two columns and drop
            the original one.'''

            kodtext_df['kodverk'] = kodtext_df.loc[:,['kodverk_id','kodverk_alternativ']].apply(lambda row: check_and_swop_values(row, 'kodverk_id', 'kodverk_alternativ'), axis=1)#.kodverk_alternativ if row.kodverk is not None else row.kodverk, axis=1)
            kodtext_df.drop(columns=['kodverk_alternativ', 'kodverk_variant','senaste_ändring'], inplace=True)
            
            kodtext_df.rename(columns={sheet.title : 'kategori'}, inplace=True)
            kodverk_df['kategori'] = sheet.title
            # remove empty rows that may have been inserted
            
            print(f"previous kodverk_max - {kodverk_max_index}")
            kodverk_max_index = max(kodverk_df.index.to_list())
            print(f"update kodverk_max - {kodverk_max_index}")
            #print(f"previous kodtext_max - {kodtext_max_index}")
            kodtext_max_index = max(kodtext_df.index.to_list())
            #print(f"updated kodtext_max - {kodtext_max_index}")
            if len(external_links) > 0:
                external_links_max_index = max(external_links.index.to_list())
            if len(ämnesområde_df) > 0:
                ämnesområde_max_index = max(ämnesområde_df.index.to_list())
            
            user_series = pd.concat([kodverk_df.loc[:,'ansvarig_id'], kodtext_df.loc[:,'ändrad_av_id']]).unique()
            user_id_dict = {}
            
            for user in user_series:
                user_id_dict[user] = check_for_user_presence(user, engine)
            
            kodverk_df.loc[:,'ansvarig_id'] = kodverk_df.loc[:,'ansvarig_id'].apply(lambda cell: user_id_dict.get(cell))
            kodverk_df['ändrad_av_id'] = kodverk_df.loc[:,'ansvarig_id']
            kodtext_df['ändrad_av_id'] = kodtext_df.loc[:,'ändrad_av_id'].apply(lambda cell: user_id_dict.get(cell))
                    
            # change the type of the json column to | separated bytes
                    
            #kodverk_df.loc[:,'extra_data'] = kodverk_df.loc[:,'extra_data'].apply(lambda cell: convert_str_to_bytes(cell))
            #kodtext_df.loc[:,'extra_data'] = kodtext_df.loc[:,'extra_data'].apply(lambda cell: convert_str_to_bytes(cell))
            
            #write the kodverk to the DB
            try:
                write_data_to_database(kodverk_df, 'kodtjanst_kodverk', ','.join([i for i in kodverk_df.columns if 'urval_referens' not in i]))
            except TypeError as e:
                #e = sys.exc_info()[0]
                print(e)
                set_trace()
            # change the foreign key to that of the index in the kodverk_df
            index_kodverk_dict = {kodverk:index for index,kodverk in kodverk_df.loc[:,'rubrik_på_kodverk'].iteritems()}
            
            kodtext_df['kodverk_id'] = kodtext_df.loc[:,'kodverk_id'].apply(lambda cell: index_kodverk_dict.get(cell))
            domän_df = kodtext_df.loc[:,['kodverk_id','domän']].copy()
            #set_trace()
            index_kodtext_dict = {kodtext:index for index,kodtext in kodtext_df.loc[:,'kodtext'].iteritems()}
            kodtext_df.drop(columns=['domän','kodverk'], inplace=True)
            write_data_to_database(kodtext_df, 'kodtjanst_kodtext', ','.join(kodtext_df.columns))
            
            # change the foreign key to that of the index in the kodtext_df
            if len(external_links) > 0:
                external_links['kodtext_id'] = external_links.loc[:,'kodtext'].apply(lambda cell: index_kodtext_dict.get(cell))
                external_links.drop(columns=['kodtext', 'kodverk_id', 'kodverk_alternativ'], inplace=True)
                write_data_to_database(external_links, 'kodtjanst_mappadtillkodtext', ','.join(external_links.columns))

            # change the foreign key to that of the index in the kodtext_df
            ämnesområde_df.dropna(subset=['ämnesområde'], inplace=True)
            if len(ämnesområde_df) > 0:
                ämnesområde_df['kodverk_id'] = ämnesområde_df.loc[:,'rubrik_på_kodverk'].apply(lambda cell: index_kodverk_dict.get(cell))
                ämnesområde_df.drop(columns=['rubrik_på_kodverk'], inplace=True)
                ämnesområde_df.rename(columns={'ämnesområde' : 'domän_namn'}, inplace=True)

                write_data_to_database(ämnesområde_df, 'kodtjanst_ämne', ','.join(ämnesområde_df.columns))
import csv
import math
import io
import os
import requests
import psycopg2
import pandas as pd
import agent.queries
from psycopg2 import sql
from sodapy import Socrata
from datetime import datetime, timedelta
import logging


USER = os.environ['DB_USER']
NAME = os.environ['DB_NAME']
PW = os.environ['DB_PW']
HOST = os.environ['DB_HOST']
PORT = os.environ['DB_PORT']
SSL = os.environ['SSL']
APP_TOKEN = os.environ['SODAPY_APPTOKEN']

SSL_DIR = os.path.dirname(__file__)
SSL_PATH = os.path.join(SSL_DIR, SSL)

psycopg2_connection_string = "dbname='{}' user='{}' host='{}' port='{}' password='{}' sslmode='verify-full' sslrootcert='{}'".format(NAME, USER, HOST, PORT, PW, SSL_PATH)


DOMAIN = 'https://data.cityofchicago.org'


historicals = [{'service_name':'potholes',
                'clean_cols': {'CREATION DATE': 'creation_date',
                               'STATUS': 'status',
                               'COMPLETION DATE': 'completion_date',
                               'SERVICE REQUEST NUMBER': 'service_request_number',
                               'TYPE OF SERVICE REQUEST': 'type_of_service_request',
                               'CURRENT ACTIVITY': 'current_activity',
                               'MOST RECENT ACTION': 'most_recent_action',
                               'NUMBER OF POTHOLES FILLED ON BLOCK': 'number_of_potholes_filled_on_block',
                               'STREET ADDRESS': 'street_address',
                               'ZIP': 'zip',
                               'X COORDINATE': 'x_coordinate',
                               'Y COORDINATE': 'y_coordinate',
                               'Ward': 'ward',
                               'Police District': 'police_district',
                               'Community Area': 'community_area',
                               'SSA': 'ssa',
                               'LATITUDE': 'latitude',
                               'LONGITUDE': 'longitude',
                               'LOCATION': 'location'},
                'order': ['creation_date', 'status', 'completion_date', 'service_request_number',
                          'type_of_service_request','current_activity', 'most_recent_action',
                          'number_of_potholes_filled_on_block','street_address', 'zip', 'x_coordinate',
                          'y_coordinate', 'ward','police_district', 'community_area', 'ssa',
                          'latitude', 'longitude', 'location'],
                'url': 'https://data.cityofchicago.org/api/views/7as2-ds3y/rows.csv?accessType=DOWNLOAD&api_foundry=true',
                'final_indicator': 'Final Outcome',
                'endpoint':'787j-mys9'},
               {'service_name': 'rodents',
                'clean_cols': {'Creation Date': 'creation_date',
                               'Status': 'status',
                               'Completion Date': 'completion_date',
                               'Service Request Number': 'service_request_number',
                               'Type of Service Request': 'type_of_service_request',
                               'Number of Premises Baited': 'number_of_premises_baited',
                               'Number of Premises with Garbage': 'number_of_premises_with_garbage',
                               'Number of Premises with Rats': 'number_of_premises_with_rats',
                               'Current Activity': 'current_activity',
                               'Most Recent Action': 'most_recent_action',
                               'Street Address': 'street_address',
                               'ZIP Code': 'zip',
                               'X Coordinate': 'x_coordinate',
                               'Y Coordinate': 'y_coordinate',
                               'Ward': 'ward',
                               'Police District': 'police_district',
                               'Community Area': 'community_area',
                               'Latitude': 'latitude',
                               'Longitude': 'longitude',
                               'Location': 'location'},
                'order': ['creation_date', 'status', 'completion_date', 'service_request_number',
                          'type_of_service_request','number_of_premises_baited',
                          'number_of_premises_with_garbage', 'number_of_premises_with_rats',
                          'current_activity', 'most_recent_action', 'street_address',
                          'zip', 'x_coordinate', 'y_coordinate', 'ward','police_district',
                          'community_area', 'latitude', 'longitude', 'location'],
                'url': 'https://data.cityofchicago.org/api/views/97t6-zrhs/rows.csv?accessType=DOWNLOAD&api_foundry=true',
                'final_indicator': 'Dispatch Crew',
                'endpoint': 'dvua-vftq'},
               {'service_name': 'streetlights',
                'clean_cols': {'Creation Date': 'creation_date',
                                'Status': 'status',
                                'Completion Date': 'completion_date',
                                'Service Request Number': 'service_request_number',
                                'Type of Service Request': 'type_of_service_request',
                                'Street Address': 'street_address',
                                'ZIP Code': 'zip',
                                'X Coordinate': 'x_coordinate',
                                'Y Coordinate': 'y_coordinate',
                                'Ward': 'ward',
                                'Police District': 'police_district',
                                'Community Area': 'community_area',
                                'Latitude': 'latitude',
                                'Longitude': 'longitude',
                                'Location': 'location'},
                'order': ['creation_date', 'status', 'completion_date', 'service_request_number',
                          'type_of_service_request', 'street_address', 'zip', 'x_coordinate', 'y_coordinate',
                          'ward', 'police_district', 'community_area', 'latitude', 'longitude', 'location'],
                'url': 'https://data.cityofchicago.org/api/views/3aav-uy2v/rows.csv?accessType=DOWNLOAD&api_foundry=true',
                'final_indicator': None,
                'endpoint': 'h555-t6kz'}
                ]


def convert_dates(date_series):
    '''
    Faster approach to datetime parsing for large datasets leveraging repated dates.

    Attribution: https://github.com/sanand0/benchmarks/commit/0baf65b290b10016e6c5118f6c4055b0c45be2b0
    '''
    dates = {date:pd.to_datetime(date) for date in date_series.unique()}
    return date_series.map(dates)


def build_initial_tables(historicals):
    '''
    Create databases for each of the 311 services stored as keys in a given
    dictionary, each of which is a dictionary indicating a related CSV URL and
    column names.

    Inputs:
        - historicals_list (list of dictionaries): service request type details
            including API endpoint, pertinent column names and order for
            parsing API request results for pothole, rodent, and streetlight
            reqeusts.
    Outputs:
        - intial_records (dataframe): pandas dataframe of historical 311 data
    '''
    initial_records = []

    for service_dict in historicals:
        print("Starting: {}".format(service_dict['service_name']))
        try:
            r = requests.get(service_dict['url'])

            if r.status_code == 200:
                decoded_dl = r.content.decode('utf-8')
                req_reader = csv.reader(decoded_dl.splitlines(), delimiter = ',')
                read_info = list(req_reader)

                historicals_df = pd.DataFrame(read_info[1:], columns = read_info[0])
                historicals_df.rename(columns = service_dict['clean_cols'], inplace=True)

                historicals_df['creation_date'] = convert_dates(historicals_df['creation_date'])
                historicals_df['completion_date'] = convert_dates(historicals_df['completion_date'])

                historicals_df['response_time'] = historicals_df['completion_date'] - historicals_df['creation_date']

                initial_records.append(historicals_df)

        except:
            print("{}: Could not retrive CSV for {}".format(r.status_code, service_dict['service_name']))

    return initial_records



def dedupe_df(df, service_dict):
    '''
    Parse dataframe of  311 service request data for a given service request
    type, removing duplicate service request records (multiple records for same
    service request number) based on "current activity" column value or
    completion date

    Inputs:
        - df (database): Database of 311 request records
        - service_dict (dictionary): service request type details including
            API endpoint, pertinent column names and order for parsing API
            request results for pothole, rodent, or streetlight reqeusts

    Outputs:
        - clean_df (dataframe): pandas dataframe of 311 data without duplicate
            service request numbers
    '''
    dupes = df[df.duplicated(subset = 'service_request_number', keep = False)]
    print("Found {} request numbers with duplicates.".format(len(dupes['service_request_number'].unique())))
    df.drop_duplicates(subset = 'service_request_number', keep = False, inplace = True)

    dupe_list = dupes['service_request_number'].unique()
    keep_list = []
    final_trigger = service_dict['final_indicator']

    for duplicate in dupe_list:
        focus = dupes[dupes['service_request_number'] == duplicate]

        if not final_trigger:
            # if none of the duplicate entries are noted as final steps,
            # use most recent completion date
            most_recent = focus['completion_date'].idxmax()
            keep_list.append(most_recent)

        else:
            focus = dupes[dupes['service_request_number'] == duplicate]
            final = focus[focus['current_activity'] == final_trigger]

            if final.shape[0] == 1:
                final_outcome = final.index[0]
                keep_list.append(final_outcome)

            elif final.shape[0] > 1:
                most_recent = final['completion_date'].idxmax()
                keep_list.append(most_recent)

            elif final.shape[0] == 0:
                most_recent = focus['completion_date'].idxmax()
                keep_list.append(most_recent)

    deduped_df = dupes.loc[keep_list]
    clean_df = df.append(deduped_df, ignore_index = True)

    return clean_df



def check_updates(service_dict, days_back = 1):
    '''
    Make GET request to Chicago's Socrata 311 API to get updates for
    pothole, rodent, and single-streetlight-out requests

    Inputs:
        - service_dict (dictionary): service request type details including
            API endpoint, pertinent column names and order for parsing API
            request results for pothole, rodent, or streetlight reqeusts
        - days_back (integer): number of days in the past for which to request
            updates from 311 API
    '''
    period = datetime.now() - timedelta(days = days_back)
    period = period.date().isoformat()
    offset_amt = 2000
    limit = 2000

    if service_dict['service_name'] == 'potholes':
        svc_req_number = 'SERVICE REQUEST NUMBER'
    else:
        svc_req_number = 'Service Request Number'

    base_url = DOMAIN + "/resource/{}.json?$$app_token={}".format(service_dict['endpoint'], APP_TOKEN)
    test_url = base_url + "&$select=count(*)&$where=:updated_at>'{}'".format(period)
    update_url = base_url + "&$limit={}&$where=:updated_at>'{}'".format(limit, period)

    check_result = requests.get(test_url)

    if check_result.status_code != 200:
        print("Unsuccessful result count request.")
    else:
        python_check = check_result.json()
        num_records = int(python_check[0]['count'])
        print(num_records)
        pulls = math.ceil(int(num_records) / limit)
        print(pulls)
        new_updates = requests.get(update_url)

        if new_updates.status_code != 200:
            print("Unsuccessful GET request.")
        else:
            newly_updated = pd.DataFrame(new_updates.json())

            if pulls > 1:

                # perform HTTP GET request n - 1 more times and add to dataframe
                update_list = [newly_updated]
                for pull in range(pulls - 1):
                    offset_url = base_url + "&$limit={}&$offset={}&$where=:updated_at>'{}'".format(limit, offset_amt, period)
                    offset_amt += 2000

                    next_pull = requests.get(offset_url)
                    next_pull_df = pd.DataFrame(next_pull.json())

                    update_list.append(next_pull_df)

                newly_updated = pd.concat(update_list, ignore_index = True)

            print(newly_updated.columns)
            print()

            ordered_updates = newly_updated.reindex(columns = service_dict['order'])
            print(ordered_updates.columns)

            ordered_updates['creation_date'] = convert_dates(ordered_updates['creation_date'])
            ordered_updates['completion_date'] = convert_dates(ordered_updates['completion_date'])
            ordered_updates['response_time'] = ordered_updates['completion_date'] - ordered_updates['creation_date']

            return ordered_updates



def update_table(df, tablename):
    '''
    Insert newly updated records retrieved from API GET request into Postgres
    database

    Inputs:
        - df (database): Database of updated records from Socrata API
        - tablename (string): name of table in Postrgres database into which
            updates will be inserted
    '''
    if tablename == 'streetlights':
        load_updates_query = queries.UPDATE_STREETLIGHTS

    elif tablename == 'potholes':
        load_updates_query = queries.UPDATE_POTHOLES

    elif tablename == 'rodents':
        load_updates_query = queries.UPDATE_RODENTS

    # create temporary tuple into which to load de-duped update dataframe data
    temp_table_q = sql.SQL(queries.CREATE_TEMP).format(tbl=sql.Identifier(tablename))

    # insert and/ or update temporary table data into exisiting data table for
    # specified service type
    load_table_q = sql.SQL(load_updates_query).format(tbl=sql.Identifier(tablename))

    try:
        with psycopg2.connect(psycopg2_connection_string) as conn2:
            with conn2.cursor() as cur:
                cur.execute(temp_table_q)

                output = io.StringIO()
                df.to_csv(output, sep='\t', header=False, index=False)
                output.seek(0)

                cur.copy_from(output, "tmp_table", null="")
                print(load_table_q)

                cur.execute(load_table_q)
                conn2.commit()
    except Exception as e:
        print("Update failed: {}".format(e))

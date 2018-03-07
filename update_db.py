import psycopg2
from dotenv import get_key, find_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from psycopg2 import sql
import io
import os


SSL_DIR = os.path.dirname(__file__)

USER = get_key(find_dotenv(), 'DB_USER')
NAME = get_key(find_dotenv(), 'DB_NAME')
PW = get_key(find_dotenv(), 'DB_PW')
HOST = get_key(find_dotenv(), 'DB_HOST')
PORT = get_key(find_dotenv(), 'DB_PORT')
SSL = get_key(find_dotenv(), 'SSL')

SSL_PATH = os.path.join(SSL_DIR, SSL)

engine_string = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(USER, PW, HOST, PORT, NAME)    
ssl_args = {"sslmode": "require", "sslrootcert": SSL_PATH}
engine = create_engine(engine_string, connect_args=ssl_args)
psycopg2_connection_string = "dbname='{}' user='{}' host='{}' port='{}' password='{}' sslmode='verify-full' sslrootcert='{}'".format(NAME, USER, HOST, PORT, PW, SSL_PATH)


def create_table(tablename):
    '''
    Define tables for POSTGRES database based on Chicago 311 API data formats.

    Inputs: 
        tablename (string)
    '''
    potholes_table = """
    CREATE TABLE potholes (
    creation_date date, 
    status varchar(50), 
    completion_date date, 
    service_request_number varchar(11) PRIMARY KEY, 
    type_of_service_request varchar(50), 
    current_activity varchar(50), 
    most_recent_action text,
    number_of_potholes_filled_on_block numeric,
    street_address text, 
    zip varchar(10), 
    x_coordinate double precision, 
    y_coordinate double precision, 
    ward varchar(2), 
    police_district varchar(2), 
    community_area varchar(2), 
    ssa varchar(50), 
    latitude double precision, 
    longitude double precision, 
    location varchar(50),
    response_time interval);
    """

    rodents_table = """
    CREATE TABLE rodents (
    creation_date date, 
    status varchar(50), 
    completion_date date, 
    service_request_number varchar(11) PRIMARY KEY, 
    type_of_service_request varchar(50), 
    number_of_premises_baited numeric,
    number_of_premises_with_garbage integer,
    number_of_premises_with_rats numeric,
    current_activity varchar(50), 
    most_recent_action text,
    street_address text, 
    zip varchar(10), 
    x_coordinate double precision, 
    y_coordinate double precision, 
    ward varchar(2), 
    police_district varchar(2), 
    community_area varchar(2), 
    latitude double precision, 
    longitude double precision, 
    location varchar(50),
    response_time interval);
    """

    streetlights_table = """
    CREATE TABLE streetlights 
    (
    creation_date date, 
    status varchar(50), 
    completion_date date, 
    service_request_number varchar(11) PRIMARY KEY, 
    type_of_service_request varchar(50), 
    street_address text, 
    zip varchar(10), 
    x_coordinate double precision, 
    y_coordinate double precision, 
    ward varchar(2), 
    police_district varchar(2), 
    community_area varchar(2), 
    latitude double precision, 
    longitude double precision, 
    location varchar(50), 
    response_time interval);
    """

    dialogflow_table = """
    CREATE TABLE dialogflow_transactions (
    session_Id varchar(40), 
    req_status integer, 
    request_time timestamp, 
    service_type varchar(50), 
    description text, 
    request_details varchar(20), 
    address_string text, 
    lat double precision, 
    lng double precision, 
    email text, 
    first_name varchar(20), 
    last_name varchar(50), 
    phone varchar(15), 
    open_311_status integer, 
    token varchar(50));
    """
    
    conn2 = psycopg2.connect(psycopg2_connection_string)
    print("Connection made:", type(conn2))

    cur = conn2.cursor()
    print("created cursor")

    if tablename == 'potholes':
        cur.execute(potholes_table)
        print("made potholes!")
    if tablename == 'rodents':
        cur.execute(rodents_table)
        print("made rodents!")

    if tablename == 'streetlights':
        cur.execute(streetlights_table)
        print("made streetlights!")

    if tablename == 'dialogflow':
        cur.execute(dialogflow_table)
        print("made dialogflow!")

    conn2.commit()
    cur.close()
    conn2.close()



def fill_initial_table(df, tablename):
    '''
    Populate a given table from a pandas dataframe.
    '''
    with psycopg2.connect(psycopg2_connection_string) as conn2:
        with conn2.cursor() as cur:

            # create file-like string object to copy dataframe into
            output = io.StringIO()
            df.to_csv(output, sep='\t', header=False, index=False)
            output.seek(0)

            # copy from file-like object into specified database table
            cur.copy_from(output, tablename, null="")   
            conn2.commit()

    conn2.close()




def request_triggerd_query(tablename, input_latitude, input_longitude):
    time_only ='''
SELECT
CASE WHEN EXTRACT(DAY FROM AVG("response_time")) < 14
THEN CEIL((EXTRACT(DAY FROM AVG("response_time"))))
END as days,
CASE WHEN EXTRACT(DAY FROM AVG("response_time")) >= 14
THEN CEIL(EXTRACT(DAY FROM AVG("response_time"))/7)
END as weeks,
CASE WHEN EXTRACT(DAY FROM AVG("response_time")) > 60
THEN justify_days(AVG("response_time"))
END as months
FROM {} a
INNER JOIN (SELECT service_request_number, EXTRACT(WEEK FROM a.creation_date) as week_nunm
      FROM {} a 
      WHERE age(now(), creation_date) < '4 years' 
      AND status IN ('Completed', 'Completed - Dup')
      AND EXTRACT(WEEK FROM a.creation_date) BETWEEN (EXTRACT(WEEK FROM now()) - 2) AND (EXTRACT(WEEK FROM now()) + 2) ) AS recent
ON recent.service_request_number = a.service_request_number;
'''

    
    loc_only_neighborhood = '''
SELECT b.pri_neigh as neighborhood,
CASE WHEN EXTRACT(DAY FROM AVG("response_time")) < 14
THEN CEIL((EXTRACT(DAY FROM AVG("response_time"))))
END as days,
CASE WHEN EXTRACT(DAY FROM AVG("response_time")) >= 14
THEN CEIL(EXTRACT(DAY FROM AVG("response_time"))/7)
END as weeks,
CASE WHEN EXTRACT(DAY FROM AVG("response_time")) > 60
THEN justify_days(AVG("response_time"))
END as months
FROM {tbl} a
INNER JOIN neighborhoods b ON ST_Within(ST_SetSRID(ST_MakePoint(a.longitude, a.latitude),4326), b.geom)
WHERE b.gid IN (SELECT b.gid FROM neighborhoods b  
WHERE ST_Contains(b.geom, ST_SetSRID(ST_MakePoint(%s, %s),4326)))
AND status IN ('Completed', 'Completed - Dup')
AND age(now(), creation_date) < '2 years' 
GROUP BY b.pri_neigh;
'''


    time_loc_neighborhood = '''
SELECT b.pri_neigh as neighborhood,
CASE WHEN EXTRACT(DAY FROM AVG("response_time")) < 14
THEN CEIL((EXTRACT(DAY FROM AVG("response_time"))))
END as days,
CASE WHEN EXTRACT(DAY FROM AVG(response_time)) >= 14
THEN CEIL(EXTRACT(DAY FROM AVG("response_time"))/7)
END as weeks,
CASE WHEN EXTRACT(DAY FROM AVG("response_time")) > 60
THEN justify_days(AVG("response_time"))
END as months
FROM {tbl} a
INNER JOIN neighborhoods b ON ST_Within(ST_SetSRID(ST_MakePoint(a.longitude, a.latitude),4326), b.geom)
WHERE b.gid IN (SELECT b.gid FROM neighborhoods b  
WHERE ST_Contains(b.geom, ST_SetSRID(ST_MakePoint(%s, %s),4326)))
AND age(now(), creation_date) < '4 years' 
AND status IN ('Completed', 'Completed - Dup')
AND EXTRACT(WEEK FROM a.creation_date) BETWEEN (EXTRACT(WEEK FROM now()) - 2) AND (EXTRACT(WEEK FROM now()) + 2)
GROUP BY b.pri_neigh;
'''
    
    # fill table parameters in query for 
    both_q = sql.SQL(time_loc_neighborhood).format(tbl=sql.Identifier(tablename))

    conn2 = psycopg2.connect(psycopg2_connection_string)
    cur = conn2.cursor()
    cur.execute(both_q, [input_longitude, input_latitude])
    neighb, months, weeks, days = cur.fetchone()

    unit = {0: 'neighborhood', 1: 'months', 2: 'weeks', 3: 'days'}

    if res and all(v is None for v in res):
        # check database for average resolution time in 
        loc_q = sql.SQL(loc_only_neighborhood).format(tbl=sql.Identifier(tablename))
        cur.execute(loc_q, [input_longitude, input_latitude])
        res = cur.fetchone()
        print(res)

    else: 
        for ind, v in enumerate(res):
            if v:
                completion_message = "Thank you for your 311 request! {} requests in the {} area are typically serviced within {} {} at this time of year.".format(tablename, v, unit[ind])

        if res and all(v is None for v in res):
            print("checking time ony")
            time_q = sql.SQL(time_only).format(tbl=sql.Identifier(tablename))
            cur.execute(time_q, [input_longitude, input_latitude])
            res = cur.fetchone()
            print(res)

            if res and all(v is None for v in res):
                completion_message = "Thank you for your 311 {} request! If you provided your contact information, we'll let you know when the city marks it complete.".format(tablename)
                return completion_message

        

    cur.close()
    conn2.close()

    return completion_message


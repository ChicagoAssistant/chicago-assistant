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

    def create_table(tablename):

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
    
    conn2 = psycopg2.connect(psycopg2_connection_string)
    print("Connection made:", type(conn2))

    cur = conn2.cursor()
    print("created cursor")

    
    cur.execute(potholes_table)
    print("made potholes!")

    cur.execute(rodents_table)
    print("made rodents!")

    cur.execute(streetlights_table)
    print("made streetlights!")

    conn2.commit()
    cur.close()
    conn2.close()



def fill_initial_table(df, tablename):
    conn=engine.raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    df.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    cur.copy_from(output, tablename, null="") # null values become ''   
    conn.commit()
    conn.close()



           


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
JOIN (SELECT service_request_number, EXTRACT(WEEK FROM a.creation_date) as week_nunm
      FROM {} a 
      WHERE age(now(), creation_date) < '4 years' 
      AND status IN ('Completed', 'Completed - Dup')
      AND EXTRACT(WEEK FROM a.creation_date) BETWEEN (EXTRACT(WEEK FROM now()) - 2) AND (EXTRACT(WEEK FROM now()) + 2) ) AS recent
ON recent.service_request_number = a.service_request_number;
'''

    
    loc_only_neighborhood = '''
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
FROM {tbl} a
INNER JOIN neighborhoods b ON ST_Within(ST_SetSRID(ST_MakePoint(a.longitude, a.latitude),4326), b.geom)
WHERE b.gid IN (SELECT b.gid FROM neighborhoods b  
WHERE ST_Contains(b.geom, ST_SetSRID(ST_MakePoint(%s, %s),4326)))
AND status IN ('Completed', 'Completed - Dup')
AND age(now(), creation_date) < '2 years' 
'''

    loc_only_radius = '''
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
FROM streetlights 
JOIN (SELECT service_request_number, EXTRACT(WEEK FROM streetlights.creation_date) as week_nunm
      FROM streetlights
      WHERE age(now(), creation_date) < '2 years' 
      AND status IN ('Completed', 'Completed - Dup')
      AND earth_box( ll_to_earth(%s , %s), 1000) @> ll_to_earth(streetlights.latitude, streetlights.longitude)) AS recent
ON recent.service_request_number = streetlights.service_request_number;
    '''

    time_loc_radius = '''
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
JOIN (SELECT service_request_number, EXTRACT(WEEK FROM streetlights.creation_date) as week_nunm
      FROM streetlights
      WHERE age(now(), creation_date) < '4 years' 
      AND status IN ('Completed', 'Completed - Dup')
      AND EXTRACT(WEEK FROM a.creation_date) BETWEEN (EXTRACT(WEEK FROM now()) - 2) 
      AND (EXTRACT(WEEK FROM now()) + 2) 
      AND earth_box( ll_to_earth([lat], [lon]), 1000) @> ll_to_earth(a.latitude, streetlights.longitude)) AS recent
ON recent.service_request_number = streetlights.service_request_number;
    '''


    time_loc_neighborhood = '''
SELECT 
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
AND EXTRACT(WEEK FROM a.creation_date) BETWEEN (EXTRACT(WEEK FROM now()) - 2) AND (EXTRACT(WEEK FROM now()) + 2);
'''
    
    both_q = sql.SQL(time_loc_neighborhood).format(tbl=sql.Identifier(tablename))
    loc_q = sql.SQL(time_loc_neighborhood).format(tbl=sql.Identifier(tablename))
    time_q = sql.SQL(time_loc_neighborhood).format(tbl=sql.Identifier(tablename))
   

    conn2 = psycopg2.connect(psycopg2_connection_string)
    cur = conn2.cursor()
    cur.execute(both_q, [input_longitude, input_latitude])
    res = cur.fetchone()
    print(res)

    if all(v is None for v in res):
        print("checking time only")
        cur.execute(loc_q, [input_longitude, input_latitude])
        res = cur.fetchone()
        print(res)

        if all(v is None for v in res):
            print("checking time ony")
            cur.execute(time_q, [input_longitude, input_latitude])
            res = cur.fetchone()
            print(res)

            if all(v is None for v in res):
                return "I'm sorry, we can't find the average resolution time for {} requests this time of year in your area."

    cur.close()
    conn2.close()

    return res




# CREATE OR REPLACE FUNCTION some_f(_tbl regclass, OUT result integer) AS
# $func$
# BEGIN
# EXECUTE format('SELECT (EXISTS (SELECT 1 FROM %s WHERE id = 1))::int', _tbl)
# INTO result;
# END
# $func$ LANGUAGE plpgsql;

# # function call
# SELECT some_f('myschema.mytable');





# to check primary keys
# pk_check = "select indexdef from pg_indexes where tablename = '%s';" % (table,)
# self.cursor.execute(pk_check)
# rows = self.cursor.fetchall()
# row = rows[0][0]

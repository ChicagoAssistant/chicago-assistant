import psycopg2
from dotenv import get_key, find_dotenv
from sqlalchemy import create_engine
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
# postgresql://civicchifecta:trif3cta@chi311.c1bdxz9lxp7b.us-east-2.rds.amazonaws.com:5432/chi311??sslrootcert=rds-combined-ca-bundle.pem&sslmode=require

def create_db():
    connection_string = "dbname='{}' user='{}' host='{}' port='{}' password='{}'".format(NAME, USER, HOST, PORT, PW)

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
    number_of_premises_baited integer,
    number_of_premises_with_garbage integer,
    number_of_premises_with_rats integer,
    current_activity varchar(50), 
    most_recent_action text,
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

    conn = psycopg2.connect(connection_string)
    print("Connection made:", type(conn))

    cur = conn.cursor()
    print("created cursor")

    
    cur.execute(potholes_table)
    print("made potholes!")

    cur.execute(rodents_table)
    print("made rodents!")

    cur.execute(streetlights_table)
    print("made streetlights!")

    conn.commit()
    cur.close()

    conn.close()


def create_initial_table(df, tablename):
    conn=engine.raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    df.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    contents = output.getvalue()
    cur.copy_from(output, tablename, null="") # null values become ''   
    conn.commit()



def update_table(df, tablename):
    # take de-duped update dataframe and create temporary table
    df.to_sql('temp_table', engine, if_exists='replace', dtype = {'creation_date':sqlalchemy.types.DateTime, 'completion_date':sqlalchemy.types.DateTime, 'location':sqlalchemy.types.JSON})

  
    update_query = '''
INSERT INTO potholes(creation_date, status, completion_date, service_request_number, 
  type_of_service_request, current_activity, most_recent_action, 
  number_of_potholes_filled_on_block, street_address, zip, x_coordinate, y_coordinate, 
  ward, police_district, community_area, ssa, latitude, longitude, location, response_time)
SELECT *
FROM temp_table
ON CONFLICT(svc_req_number) DO UPDATE
    SET completion_date = COALESCE(excluded.completion_date, completion_date),
        status = COALESCE(excluded.status, status),
        current_activity = COALESCE(excluded.current_activity, current_activity),
        most_recent_action = COALESCE(excluded.most_recent_action, most_recent_action);
'''

    with engine.begin() as conn:
        print("beginning!")
        conn.execute(update_query)
        print("done!")




def request_triggerd_query(tablename, input_latitude, input_longitude):
    time_only ='''
SELECT 
CASE WHEN EXTRACT(DAY FROM AVG(response_time)) < 14
THEN CEIL((EXTRACT(DAY FROM AVG(response_time))))
END as days,
CASE WHEN EXTRACT(DAY FROM AVG(response_time)) >= 14
THEN CEIL(EXTRACT(DAY FROM AVG(response_time))/7)
END as weeks,
CASE WHEN EXTRACT(DAY FROM AVG(response_time)) > 30
THEN justify_days(AVG(response_time))
END as months
FROM {} 
JOIN (SELECT service_request_number, EXTRACT(WEEK FROM {}.creation_date) as week_nunm
      FROM {} 
      WHERE age(now(), creation_date) < '4 years' AND EXTRACT(WEEK FROM {}.creation_date) BETWEEN (EXTRACT(WEEK FROM now()) - 2) AND (EXTRACT(WEEK FROM now()) + 2) ) AS recent
ON recent.service_request_number = {}.service_request_number;
'''    



    cur.execute(
        psycopg2.sql.SQL(time_only)
            .format(sql.Identifier(tablename)),
        [input_date])

    pass




full_update_query = '''
INSERT INTO potholes(creation_date, status, completion_date, service_request_number, type_of_service_request,
  current_activity, most_recent_action, number_of_potholes_filled_on_block,
  street_address, zip, x_coordinate, y_coordinate, ward, police_district,
  community_area, ssa, latitude, longitude, location, response_time)
SELECT tmp_potholes.*
FROM tmp_potholes
WHERE 
ON CONFLICT(svc_req_number) DO UPDATE
    SET completion_date = COALESCE(excluded.completion_date, completion_date),
        status = COALESCE(excluded.status, status),
        current_activity = COALESCE(excluded.current_activity, current_activity),
        most_recent_action = COALESCE(excluded.most_recent_action, most_recent_action)
    WHERE (excluded.completion_date IS DISTINCT FROM completion_date OR
           excluded.status IS DISTINCT FROM  status OR
           excluded.current_activity IS DISTINCT FROM  current_activity) OR
           excluded.most_recent_action IS DISTINCT FROM most_recent_action)
          );
'''


# location query
# user_input_lat = 41.885001
# user_input_lon = -87.645939
# pass_in = (user_input_lon, user_input_lat)
# '$where=within_circle(location, 41.885001, -87.645939, 41.867011, -87.618516)'




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

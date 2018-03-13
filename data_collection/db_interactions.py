import psycopg2
import io
import os


USER = os.environ['DB_USER']
NAME = os.environ['DB_NAME']
PW = os.environ['DB_PW']
HOST = os.environ['DB_HOST']
PORT = os.environ['DB_PORT']
SSL = os.environ['SSL']

SSL_DIR = os.path.dirname(__file__)
SSL_PATH = os.path.join(SSL_DIR, SSL)


psycopg2_connection_string = "dbname='{}' user='{}' host='{}' port='{}' password='{}' sslmode='verify-full' sslrootcert='{}'".format(NAME, USER, HOST, PORT, PW, SSL_PATH)


def create_table(tablename):
    '''
    Define tables for Postgres database based on Chicago 311 API data formats.

    Inputs: 
        tablename (string): name underwhich a table will be created in Postgres 
        database
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

    # Note: a somposite primary key was later initialized, encompassing both the
    # session ID and the request time
    dialogflow_table = """
    CREATE TABLE dialogflow_transactions (
    session_Id varchar(40) PRIMARY KEY, 
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
    
    try:
        conn2 = psycopg2.connect(psycopg2_connection_string)

        cur = conn2.cursor()

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
    except Exception as e:
        print("Encountered excption: {}".format(e))



def fill_initial_table(df, tablename):
    '''
    Populate a given table in Postgres database from a pandas dataframe.

    Inputs:
        - df (database): Database of 311 request records
        - tablename (string): name of table in Postrgres database into which 
            records will be inserted
    '''
    try:
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
    except Exception as e:
        print("Encountered excption: {}".format(e))






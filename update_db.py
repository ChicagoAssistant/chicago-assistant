import psycopg2
from dotenv import get_key, find_dotenv

USER = get_key(find_dotenv(), 'DB_USER')
NAME = get_key(find_dotenv(), 'DB_NAME')
PW = get_key(find_dotenv(), 'DB_PW')
HOST = get_key(find_dotenv(), 'DB_HOST')
PORT = get_key(find_dotenv(), 'DB_PORT')


def create_db():
    connection_string = "dbname='{}' user='{}' host='{}' port='{}' password='{}'".format(NAME, USER, HOST, PORT, PW)
    
    try:
        conn = psycopg2.connect(connection_string)
        # conn = psycopg2.connect("dbname='chi311' user='civicchifecta' host='chi311.c1bdxz9lxp7b.us-east-2.rds.amazonaws.com' port='5432' password='trif3cta'")
        print(type(conn))

        cur = conn.cursor()

        cur.execute("CREATE TABLE test3 (id serial PRIMARY KEY, num integer, data varchar);")

        cur.execute("INSERT INTO test3 (num, data) VALUES (%s, %s)", (400, "Goodbye For Now"))

        cur.execute("SELECT * FROM test3;")
        
        test = cur.fetchone()
        print(test)

        conn.commit()
        cur.close()
        conn.close()

    
    except:
        print("I am unable to connect to the database.")




    # cur.executemany(query, vars_list)
    # Execute a database operation (query or command) against all parameter 
    # tuples or mappings found in the sequence vars_list.
    # 
    # mostly useful for commands that update the database: any result set 
    # returned by the query is discarded.









# to check primary keys
# pk_check = "select indexdef from pg_indexes where tablename = '%s';" % (table,)
# self.cursor.execute(pk_check)
# rows = self.cursor.fetchall()
# row = rows[0][0]

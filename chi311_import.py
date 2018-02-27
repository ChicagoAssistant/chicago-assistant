# import psycopg2
# import psycopg2.extensions
import os
from sodapy import Socrata
from datetime import datetime, timedelta






# Execute a command: this creates a new table
# cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

# Pass data to fill a query placeholders and let Psycopg perform
# the correct conversion (no more SQL injections!)
# cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))

# Make the changes to the database persistent
# conn.commit()

# Close communication with the database
# cur.close()
# conn.close()

# to check primary keys
# pk_check = "select indexdef from pg_indexes where tablename = '%s';" % (table,)
# self.cursor.execute(pk_check)
# rows = self.cursor.fetchall()
# row = rows[0][0]

DOMAIN = 'https://data.cityofchicago.org'
POTHOLES_ENDPOINT = '787j-mys9'
RODENT_ENDPOINT = 'dvua-vftq'
STREETLIGHT_ENDPOINT = 'h555-t6kz'



# create query
def create_api_req(req_type, since_date):
    app_token = os.environ['SODAPY_APPTOKEN']
    client = Socrata(DOMAIN, app_token)
    yesterday = datetime.today() - timedelta(days=1)
    df_list = []
    query = """
limit
    20000
where
    updated_at =
""" + str(yesterday)
    offset_counter = 0


    if req_type == 'potholes':
        download_df = pd.DataFrame(cols = ['creation_date', 'status', 
                                       'completion_date', 
                                       'service_request_number', 
                                       'type_of_service_request', 
                                       'current_activity', 'most_recent_action',
                                       'number_of_potholes_filled_on_block',
                                       'street_address', 'zip', 
                                       'x_coordinate', 'y_coordinate', 'ward', 
                                       'police_district', 'community_area', 
                                       'ssa', 'latitude', 'longitude', 
                                       'location'])
        potholes_metadata = client.get_metadata(POTHOLES_ENDPOINT)
        num_records = [x for x in potholes_metadata['columns'] if x['name'] == 'SERVICE REQUEST NUMBER'][0]['cachedContents']['cardinality']
        pulls = math.ceil(int(num_records) / 20000)
        if pulls > 1:
            for pull in range(pulls + 1):
                final_query = query + 'OFFSET ' +  str(offset_counter)
                results = client.get(POTHOLES_ENDPOINT, query = final_query)
                new_updates = pd.DataFrame.from_records(results)
                df_list.append(new_updates)

    elif req_type == 'rodents':
        download_df = pd.DataFrame(cols = ['creation_date', 'status', 
                                       'completion_date', 
                                       'service_request_number', 
                                       'type_of_service_request', 
                                       'current_activity', 'most_recent_action',
                                       'number_of_premises_baited',
                                       'number_of_premises_with_garbage',
                                       'number_of_premises_with_rats',
                                       'street_address', 'zip_code', 
                                       'x_coordinate', 'y_coordinate', 'ward', 
                                       'police_district', 'community_area', 
                                       'latitude', 'longitude', 'location'])
        rodent_metadata = client.get_metadata(RODENT_ENDPOINT)
        num_records = [x for x in rodent_metadata['columns'] if x['name'] == 'Service Request Number'][0]['cachedContents']['cardinality']
        pulls = math.ceil(int(num_records) / 20000)
        if pulls > 1:
            for pull in range(pulls + 1):
                final_query = query + 'OFFSET ' +  str(offset_counter)
                results = client.get(RODENT_ENDPOINT, query = final_query)
                new_updates = pd.DataFrame.from_records(results)
                df_list.append(new_updates)

    
    elif req_type == 'streetlight':
        download_df = pd.DataFrame(cols = ['creation_date', 'status', 
                                       'completion_date', 
                                       'service_request_number', 
                                       'type_of_service_request', 
                                       'street_address', 'zip_code', 
                                       'x_coordinate', 'y_coordinate', 'ward', 
                                       'police_district', 'community_area', 
                                       'latitude', 'longitude', 'location'])

        # note for streetlight, location is a text field rather than point, so
        # within_circle cannot be used
        streetlight_metadata = client.get_metadata(STREETLIGHT_ENDPOINT)
        num_records = [x for x in streetlight_metadata['columns'] if x['name'] == 'Service Request Number'][0]['cachedContents']['cardinality']
        pulls = math.ceil(int(num_records) / 20000)
        if pulls > 1:
            for pull in range(pulls + 1):
                final_query = query + 'OFFSET ' +  str(offset_counter)
                results = client.get(STREETLIGHT_ENDPOINT, query = final_query)
                new_updates = pd.DataFrame.from_records(results)
                df_list.append(new_updates)



    client.close()
    download_df = download_df.concat(df_list, ignore_index = True)
    
    dupes = download_df[download_df.duplicated(subset='service_request_number', keep=False)]
    download_df.drop_duplicates(subset = 'service_request_number', keep = False, inplace = True)

    return (singles_df, dupes)

    
    def dedupe_download(dupes, streetlight = False):
        dupe_list = dupes['service_request_number'].unique()
        keep_list = []

        

        for duplicate in dupe_list:
            focus = dupes[dupes['service_request_number'] == duplicate]

            if streetlight:    
                focus['completion_date'] = pd.to_datetime(x['completion_date'])
                most_recent = focus['completion_date'].idxmax()
                keep_list.append(most_recent)

            else:
                focus = dupes[dupes['service_request_number'] == duplicate]
                final = focus[focus['current_activity'] == 'Final Outcome']
                
                if final.shape[0] == 1:
                    final_outcome = final.index[0]
                    keep_list.append(final_outcome)

                elif final.shape[0] > 1:
                    final['completion_date'] = pd.to_datetime(x['completion_date'])
                    most_recent = final['completion_date'].idxmax()
                    keep_list.append(most_recent)

                else:
                    # if none of the duplicate entries are marked "Final Outcome"
                    focus['completion_date'] = pd.to_datetime(x['completion_date'])
                    most_recent = focus['completion_date'].idxmax()
                    keep_list.append(most_recent)

        deduped_df = dupe_list.loc[keep_list]

        return deduped_df

def combine_requests(singles_df, deduped_df):
    full_df = singles_df.append(deduped_df, ignore_index = True)
    full_df.set_index(keys = 'service_request_number', inplace = True)
    return full_df

def update_db(full_df):
    
    conn = psycopg2.connect("dbname=test user=civicchifecta")
    # conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    c = conn.cursor()

    engine = create_engine('postgresql+psycopg2://user:pswd@mydb')

    df = pandas.read_sql("SELECT * from your_table;", engine)
    df[df['column'] == "old value", "column"] = "new value"
    df.to_sql("your_table", engine, if_exists="replace")
    pass 
    
    # SODA APIs are paged, and return a maximum of 50,000 per page. 
    # to request subsequent pages, you’ll need to use the $limit and $offset

#     if len(rv) > 1000:
#         $limit=1000&$offset=1000

#     # location query
        


#         user_input_lat = 41.885001
#         user_input_lon = -87.645939
#         pass_in = (user_input_lon, user_input_lat)
#         '$where=within_circle(location, 41.885001, -87.645939, 41.867011, -87.618516)'
#         # space = '+'

# # Package the request, send the request and catch the response: r


# # turn into python datastructue

# check_key = hist_data_json['service_request_id']



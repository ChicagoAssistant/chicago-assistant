
# query for average historical resolution time for given service request type 
# within two weeks of the triggering (new) request time
TIME_ONLY ='''
    SELECT
    CASE WHEN EXTRACT(DAY FROM AVG("response_time")) > 60
    THEN justify_days(AVG("response_time"))
    END as months,
    CASE WHEN EXTRACT(DAY FROM AVG("response_time")) >= 14
    THEN CEIL(EXTRACT(DAY FROM AVG("response_time"))/7)
    END as weeks,
    CASE WHEN EXTRACT(DAY FROM AVG("response_time")) < 14
    THEN CEIL((EXTRACT(DAY FROM AVG("response_time"))))
    END as days
    FROM {} a
    INNER JOIN (SELECT service_request_number, EXTRACT(WEEK FROM a.creation_date) as week_nunm
      FROM {} a 
      WHERE age(now(), creation_date) < '4 years' 
      AND status IN ('Completed', 'Completed - Dup')
      AND EXTRACT(WEEK FROM a.creation_date) BETWEEN (EXTRACT(WEEK FROM now()) - 2) AND (EXTRACT(WEEK FROM now()) + 2) ) AS recent
    ON recent.service_request_number = a.service_request_number;'''

 
# query for average historical resolution time for given service request type 
# in the neighborhood corresponding to a given latitude and longitude
LOC_ONLY = '''
    SELECT
    CASE WHEN EXTRACT(DAY FROM AVG("response_time")) > 60
    THEN justify_days(AVG("response_time"))
    END as months,
    CASE WHEN EXTRACT(DAY FROM AVG("response_time")) >= 14
    THEN CEIL(EXTRACT(DAY FROM AVG("response_time"))/7)
    END as weeks,
    SELECT b.pri_neigh as neighborhood,
    CASE WHEN EXTRACT(DAY FROM AVG("response_time")) < 14
    THEN CEIL((EXTRACT(DAY FROM AVG("response_time"))))
    END as days,
    FROM {tbl} a
    INNER JOIN neighborhoods b ON ST_Within(ST_SetSRID(ST_MakePoint(a.longitude, a.latitude),4326), b.geom)
    WHERE b.gid IN (SELECT b.gid FROM neighborhoods b  
    WHERE ST_Contains(b.geom, ST_SetSRID(ST_MakePoint(%s, %s),4326)))
    AND status IN ('Completed', 'Completed - Dup')
    AND age(now(), creation_date) < '2 years' 
    GROUP BY b.pri_neigh;'''

# query for average historical resolution time for given service request type 
# in the neighborhood corresponding to a given latitude and longitude within 
# two weeks of the triggering (new) request time
TIME_LOC = '''
    SELECT b.pri_neigh as neighborhood,
    CASE WHEN EXTRACT(DAY FROM AVG("response_time")) > 60
    THEN justify_days(AVG("response_time"))
    END as months,
    CASE WHEN EXTRACT(DAY FROM AVG(response_time)) >= 14
    THEN CEIL(EXTRACT(DAY FROM AVG("response_time"))/7)
    END as weeks,
    CASE WHEN EXTRACT(DAY FROM AVG("response_time")) < 14
    THEN CEIL((EXTRACT(DAY FROM AVG("response_time"))))
    END as days
    FROM {tbl} a
    INNER JOIN neighborhoods b ON ST_Within(ST_SetSRID(ST_MakePoint(a.longitude, a.latitude),4326), b.geom)
    WHERE b.gid IN (SELECT b.gid FROM neighborhoods b  
    WHERE ST_Contains(b.geom, ST_SetSRID(ST_MakePoint(%s, %s),4326)))
    AND age(now(), creation_date) < '4 years' 
    AND status IN ('Completed', 'Completed - Dup')
    AND EXTRACT(WEEK FROM a.creation_date) BETWEEN (EXTRACT(WEEK FROM now()) - 2) AND (EXTRACT(WEEK FROM now()) + 2)
    GROUP BY b.pri_neigh;'''

# query to insert Dialogflow and Open311 POST request details into Postgres 
# database
RECORD_TRANSACTION ='''
    INSERT INTO dialogflow_transactions (session_Id, request_time, 
    service_type, description, request_details, address_string, lat, lng, email, 
    first_name, last_name, phone, open_311_status, token)
    VALUES (%s,  %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    '''
    
# query to create temporary table in Postgres database when updating service
# requests
CREATE_TEMP = '''
    CREATE TEMP TABLE tmp_table
    AS
    SELECT *
    FROM {tbl}
    WITH NO DATA;
    '''
    

# query to load newly updated street light request records into Postgres databases
UPDATE_STREETLIGHTS = '''
INSERT INTO {tbl} (creation_date, status, completion_date, service_request_number, 
               type_of_service_request, street_address, zip, x_coordinate, y_coordinate, 
               ward, police_district, community_area, latitude, longitude, location, response_time)
SELECT *
FROM tmp_table
ON CONFLICT(service_request_number) DO UPDATE
    SET completion_date = COALESCE(excluded.completion_date, {tbl}.completion_date),
        status = COALESCE(excluded.status, {tbl}.status),
        response_time = COALESCE(excluded.response_time, {tbl}.response_time)
        WHERE (excluded.completion_date IS DISTINCT FROM {tbl}.completion_date) OR
           (excluded.status IS DISTINCT FROM  {tbl}.status) OR
           (excluded.response_time IS DISTINCT FROM {tbl}.response_time);'''
    
# query to load newly updated pothole request records into Postgres databases
UPDATE_POTHOLES = '''
INSERT INTO {tbl} (creation_date, status, completion_date, service_request_number,
               type_of_service_request, current_activity, most_recent_action,
               number_of_potholes_filled_on_block, street_address, zip, x_coordinate, y_coordinate,
               ward, police_district, community_area, ssa, latitude, longitude, location, response_time)
SELECT *
FROM tmp_table
ON CONFLICT(service_request_number) DO UPDATE
    SET completion_date = COALESCE(excluded.completion_date, {tbl}.completion_date),
        status = COALESCE(excluded.status, {tbl}.status),
        current_activity = COALESCE(excluded.current_activity, {tbl}.current_activity),
        most_recent_action = COALESCE(excluded.most_recent_action, {tbl}.most_recent_action),
        response_time = COALESCE(excluded.response_time, {tbl}.response_time)
        WHERE (excluded.completion_date IS DISTINCT FROM {tbl}.completion_date) OR
           (excluded.status IS DISTINCT FROM  {tbl}.status) OR
           (excluded.current_activity IS DISTINCT FROM  {tbl}.current_activity) OR
           (excluded.most_recent_action IS DISTINCT FROM {tbl}.most_recent_action) OR 
           (excluded.response_time IS DISTINCT FROM {tbl}.response_time);'''



# query to load newly updated rodent request records into Postgres databases
UPDATE_RODENTS = '''
INSERT INTO {tbl} (creation_date, status, completion_date, service_request_number, 
               type_of_service_request, number_of_premises_baited, number_of_premises_with_garbage,
               number_of_premises_with_rats, current_activity, most_recent_action, street_address, 
               zip, x_coordinate, y_coordinate, ward, police_district, community_area, latitude, 
               longitude, location, response_time)
SELECT *
FROM tmp_table
ON CONFLICT(service_request_number) DO UPDATE
    SET completion_date = COALESCE(excluded.completion_date, {tbl}.completion_date),
        status = COALESCE(excluded.status, {tbl}.status),
        current_activity = COALESCE(excluded.current_activity, {tbl}.current_activity),
        most_recent_action = COALESCE(excluded.most_recent_action, {tbl}.most_recent_action),
        response_time = COALESCE(excluded.response_time, {tbl}.response_time)
        WHERE (excluded.completion_date IS DISTINCT FROM {tbl}.completion_date) OR
           (excluded.status IS DISTINCT FROM  {tbl}.status) OR
           (excluded.current_activity IS DISTINCT FROM  {tbl}.current_activity) OR
           (excluded.most_recent_action IS DISTINCT FROM {tbl}.most_recent_action) OR 
           (excluded.response_time IS DISTINCT FROM {tbl}.response_time);'''


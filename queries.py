
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
    



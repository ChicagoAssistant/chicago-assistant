import urllib
import json
import os
import psycopg2
from psycopg2 import sql
from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
import googlemaps
import requests
from clock import sched
from chi311_import import historicals, check_updates, dedupe_df, update_table
import queries

app = Flask(__name__)
API_ENDPOINT = 'http://test311api.cityofchicago.org/open311/v2'
GMAPS_PLACES_APPTOKEN = os.environ['GMAPS_PLACES_APPTOKEN']
OPEN_311_APPTOKEN = os.environ['OPEN_311_APPTOKEN']
gmaps = googlemaps.Client(key=GMAPS_PLACES_APPTOKEN)


USER = os.environ['DB_USER']
NAME = os.environ['DB_NAME']
PW = os.environ['DB_PW']
HOST = os.environ['DB_HOST']
PORT = os.environ['DB_PORT']
SSL_DIR = os.path.dirname(__file__)
SSL = os.environ['SSL']
SSL_PATH = os.path.join(SSL_DIR, SSL)
CONNECTION_STRING = "dbname='{}' user='{}' host='{}' port='{}' password='{}' sslmode='verify-full' sslrootcert='{}'".format(
    NAME, USER, HOST, PORT, PW, SSL_PATH)


@app.route('/webhook', methods=['POST'])
def webhook():
    '''
    Recieves and responds to DialogFlow webhook post requests.
    '''
    req = request.get_json(silent=True, force=True)
    print('Request:\n', json.dumps(req, indent=4))
    with open('data.json', 'w') as f:
        json.dump(req, f)
    res = makeWebhookResult(req)
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'

    return r


@app.route('/', methods=['GET'])
def hello():
    return "Hello World!"


@app.route('/test')
def test():
    return render_template('page.html')


def makeWebhookResult(req):
    '''
    Takes a request from DialogFlow webhook and triages what the request
    is to produce the appropriate response.
    Inputs:
        - req (json): information passed from DialogFlow webhook
    '''
    action = get_action(req)
    if action == 'name':
        return followupEvent('get_address')

    if action == 'get.address':
        return process_address(req)

    if action == 'address.corrected':
        return process_address(req, True)

    if action == 'request.complete':
        # process the average number of days to complete request
        status_message = post_request(req)
        service_type = get_service_type(req)
        table = get_tablename(service_type)
        lat, lng, formatted_address = return_address_params(req)
        completion_message = request_triggerd_query(table, lat, lng)

        data = {"completion_time": completion_message,
                "post_status": status_message}

        return followupEvent('completion_time', data)


def process_address(req, corrected=False):
    '''
    Manages collection of viable address. If an adequate address is given
    (i.e. a single match is found via google maps autocomplete), then
    the conversation continues. If there aren't any matches, then the
    conversation will direct the user to enter the address again. In the case
    that there is more than one match, this function will pass back up to
    three address recommended matches for the user to select from.

    Inputs:
        - req (dict) data from DialogFlow where the address given by the
            user is stored
    Outputs:
        - followupEvent action: depending on the quality of the address
            provided by the user, this funciton will steer the conversation
            to the end of obtaining an adequate address
    '''
    if corrected:
        address = req['result']['parameters']['corrected-address']
    else:
        address = req['result']['parameters']['address']
    service_type = get_service_type(req)

    if 'and' in address or '&' in address:
        return followupEvent(service_type)

    if 'Chicago' not in address:
        address += ' Chicago, IL'
    matched_addresses = gmaps.places_autocomplete(address)
    matched_addresses = filter_city('Chicago', matched_addresses)

    if len(matched_addresses) == 0:
        return followupEvent('get_address')
    elif len(matched_addresses) == 1:
        return followupEvent(service_type)
    else:
        address_recs = get_address_recs(matched_addresses)
        return followupEvent('address_correct', address_recs)


def return_address_params(req):
    parameters = req['result']['parameters']
    address = parameters['corrected-address']
    if not address:
        address = parameters['address']
    if 'Chicago' not in address:
        address += ' Chicago, IL'
    clean_geos = geocode(address)
    return clean_geos


def post_request(req):
    '''
    Extracts all required data from DialogFlow post request containing
    all user inputs, structures the data into a dictionary which can
    then be passed as a post request to the Chicago Open311 environment.

    Inputs:
        - req (json): information passed from DialogFlow webhook containing
            user inputs
    Outputs:
        - status_message (string): status message indicating whether
            the post request submitted successfully or failed
    '''
    url = API_ENDPOINT + '/requests.json'

    parameters = req['result']['parameters']
    service_type = get_service_type(req)
    service_code = get_service_code(service_type)

    request_spec = parameters['request-spec']
    attribute = generate_attribute(service_type, request_spec)
    description = parameters['description']
    request_spec = parameters['request-spec']
    try:
        email = parameters['email']
        phone = parameters['phone-number']
    except BaseException:
        email = ''
        phone = ''
    first_name = parameters['first-name']
    last_name = parameters['last-name']
    lat, lng, address_string = return_address_params(req)
    post_data = structure_post_data(
        service_code,
        attribute,
        lat,
        lng,
        description,
        address_string,
        email,
        first_name,
        last_name,
        phone)

    print('OPEN_311_POST_REQUEST:', post_data)
    response = requests.post(url, data=post_data)
    print('OPEN_311_RESPONSE:', response.text)
    try:
        token = response.json()[0]['token']
    except BaseException:
        token = ''
    status_code = response.status_code
    status_message = generate_post_status_message(status_code)

    write_to_db(
        req,
        token,
        service_type,
        request_spec,
        lat,
        lng,
        description,
        address_string,
        status_code,
        email,
        first_name,
        last_name,
        phone)

    return status_message


def followupEvent(event_key, data=None):
    '''
    Helper function that returns the webhook response needed
    based on where the conversation needs to go next. The 'events'
    below specify one of any events that are triggered in the
    conversation. This function simply constructs the appropriate
    event response for DialogFlow.

    Inputs:
        - event_key (string): event key that will be used to map
            to the appropriate event name recognized by DialogFlow
        - data (dict): data that is passed along to DialogFlow as
            parameters to be passed back to the messaging interface
    Outputs:
        - followupEvent (dict): dict formatted in necessary format
            for DialogFlow to trigger the next event in conversation
    '''
    events = {'pothole': 'pothole_request',
              'rodent': 'rodent_request',
              'street light': 'street_light_request',
              'completion_time': 'completion_time',
              'get_address': 'get-address',
              'address_correct': 'address-correct'}

    event = events[event_key]

    if data:
        return {"followupEvent": {"name": '{}'.format(event), "data": data}}

    return {"followupEvent": {"name": '{}'.format(event)}}


def filter_city(city, gmaps_locs):
    '''
    Filter out any locations that are not in the city of interest.
    Inputs:
        - city (string): name of the city of jurisdiction
        - gmaps_locs (list of dicts): results returned from call to googlemaps
             places_autocomplete method
    Outputs:
        - locations (list of dict(s)): filtered locations for city of interest
    '''
    locations = [gmaps_loc for gmaps_loc in gmaps_locs
                 if city in gmaps_loc['description']]
    return locations


def get_action(req):
    '''
    Helper function to get action from request.
    Inputs:
        - req (json): information passed from DialogFlow webhook
    Outputs:
        - action (string) action from DialogFlow which determines proceeding
          action.
    '''
    # ACTION_TYPES = {'get.address':'flow','address.corrected':'flow','name':'flow','request.complete':''}
    try:
        action = req['result']['action']
        return action
    except Exception:
        print('No action to grab from request.')


def get_service_type(req):
    '''
    Given a DialogFlow json, get the service type of the request.
    Inputs:
        - req (json): information passed from DialogFlow webhook
    Outputs:
        - service_type (string): service type of request
    '''
    service_type = req['result']['parameters']['service-type']
    return service_type


def get_address_recs(matched_addresses):
    '''
    Helper function, in the case of multiple address matches, this function will
    return up to the top three address recommendations.
    Inputs:
        - matched_addresses (dict): address match results from google maps
            places autocomplete
    Outputs:
        - recommendations (dict): three addresses in a dictionary in the
            required format to be passed back to DialogFlow as data in a
            followupEvent dictionary.
    '''
    address_recs = ['', '', '']
    for num, matched_addresses in enumerate(matched_addresses[:3]):
        address = matched_addresses['description']
        address_recs[num] = address

    recommendations = {"address1": address_recs[0],
                       "address2": address_recs[1],
                       "address3": address_recs[2]}

    return recommendations


def get_service_code(service_type):
    '''
    Helper function to get the service code given a string.
    Inputs:
        - service_type (string): service type generated in DialogueFlow
            based on user input
    Outputs:
        - service_code (string): Open311 service code for service request
    '''
    service_types = {'pothole': '4fd3b656e750846c53000004',
                     'rodent': '4fd3b9bce750846c5300004a',
                     'street light': '4ffa9f2d6018277d400000c8'}

    return service_types[service_type]


def generate_post_status_message(status_code):
    '''
    Helper function to return status message given a status code.
    '''
    status_messages = {201: 'Your request has been submitted successfully!',
                       400: 'Your request is a duplicate in our system!'}

    return status_messages[status_code]


def structure_post_data(service_code, attribute, lat, lng, description,
                        address_string, email, first_name, last_name, phone):
    '''
    Helper function to structure all user inputs into appropriate
    dictionary format that will be passed to Open311 systems.
    '''
    post_data = {'service_code': service_code,
                 'attribute': attribute,
                 'lat': lat,
                 'long': lng,
                 'first_name': first_name,
                 'last_name': last_name,
                 'email': email,
                 'address_string': address_string,
                 'phone_number': phone,
                 'description': description,
                 'api_key': OPEN_311_APPTOKEN}

    return post_data


def generate_attribute(service_type, request_spec):
    '''
    Helper function to create dictionary needed for the Open311 post request.
    '''
    attributes = {
        'pothole':
        {'intersection': {'WHEREIST': {'key': 'INTERSEC', 'name': 'Intersection'}},
         'bike lane': {'WHEREIST': {'key': 'BIKE', 'name': 'Bike Lane'}},
         'crosswalk': {'WHEREIST': {'key': 'CROSS', 'name': 'Crosswalk'}},
         'curb lane': {'WHEREIST': {'key': 'CURB', 'name': 'Curb Lane'}},
         'traffic lane': {'WHEREIST': {'key': 'TRAFFIC', 'name': 'Traffic Lane'}}},
        'rodent':
        {'yes': {'DOYOUWAN': {'key': 'BAITBYAR', 'name': 'Bait Back Yard'}},
         'no': {'DOYOUWAN': {'key': 'NOTOBAIT', 'name': 'No'}}},
        'street light':
        {'completely out': {'ISTHELI2': {'key': 'COMPLETE', 'name': 'Completely Out'}},
         'on and off': {'ISTHELI2': {'key': 'ONOFF', 'name': 'On and Off'}}}}

    return attributes[service_type][request_spec]


def geocode(address):
    '''
    Function that will geocode an address and return lat, long, and
    a formatted address. Google Maps used for geocoding.

    Inputs:
        - address (string): address of service request given by user
    Outputs:
        - lat (float): latitude of address as given by google maps
        - lng (float): longitude of address as given by google maps
        - formatted_address (string): full address of location as given
            by google maps
    '''
    result = gmaps.geocode(address)[0]

    lat = result['geometry']['location']['lat']
    lng = result['geometry']['location']['lng']
    formatted_address = result['formatted_address']

    return lat, lng, formatted_address


def get_tablename(db_key):
    '''
    Return name of associated Postgres database table from Open311/ 
    Dialogflow service request type names
    '''
    db_map = {'pothole': 'potholes', 'rodent': 'rodents',
              'street light': 'streetlights',
              'dialogflow': 'dialogflow_transactions'}

    return db_map[db_key]


def request_triggerd_query(tablename, input_latitude, input_longitude):
    '''
    Given a user's location and the type of request, query average historical
    resolution time for the two weeks pre- and post- today's day/ month in the 
    last four years for the type of request. Limit query to the neighborhood 
    containing reported location according to Chicago Open Data Portal 
    Neighborhood Boundaries. 

    Inputs:
        - tablename (string): name of table in Postgres database associated with
            customer's service request type 
        - input_latitude (float): latitude associated with customer's address 
            returned from googlemaps API
        - input_longitude (float): longitude associated with customer's address 
            returned from googlemaps API

    Output: 
        - completion_message (str): formatted message indicating historical
            average response time  

    Attribution:
        - Calls to psycopg2.sql function crafted based on examples in psycog2 
            documentation for parameterizing table names in SQL queries via 
            Python (http://initd.org/psycopg/docs/sql.html)
    '''
    both_q = sql.SQL(queries.TIME_LOC).format(tbl=sql.Identifier(tablename))
    loc_only = False

    conn2 = psycopg2.connect(CONNECTION_STRING)
    cur = conn2.cursor()
    cur.execute(both_q, [input_longitude, input_latitude])
    res = cur.fetchone()
    print(res)

    unit_index = {0: 'months', 1: 'weeks', 2: 'days'}

    # if there is no information on the specific neighborhood at the given time
    # of year, check for that neighborhood only; check for that time only if there
    # are no results for the given neighborhood
    if res and all(v is None for v in res):
        loc_only = True

        loc_q = sql.SQL(queries.LOC_ONLY).format(tbl=sql.Identifier(tablename))
        cur.execute(loc_q, [input_longitude, input_latitude])
        res = cur.fetchone()
        print(res)

        if res and all(v is None for v in res):
            loc_only = False
            time_q = sql.SQL(queries.TIME_ONLY).format(tbl=sql.Identifier(tablename))
            cur.execute(time_q)
            res = cur.fetchone()
            print(res)

    cur.close()
    conn2.close()

    # for time-only results, there will only be three entries in the response 
    # tuple (res)
    if res and len(res) == 3:
        for i, num in enumerate(res):
            if num:
                num = int(num)
                unit = unit_index[i]
                completion_message = "Requests for {} are typically serviced within {} {} at this time of year.".format(
                    tablename, num, unit)
                return completion_message
                print(res)

    if res and len(res) == 4:
        neighb = res[0]
        for i, num in enumerate(res[1:]):
            if num:
                num = int(num)
                unit = unit_index[i]
                if loc_only:
                    completion_message = "Requests for {} in the {} area are typically serviced within {} {}.".format(
                        tablename, neighb, num, unit)

                else:
                    completion_message = "Requests for {} in the {} area are typically serviced within {} {} at this time of year.".format(
                        tablename, neighb, num, unit)

                return completion_message

    # if no results returned, proceed with default message.
    if not res:
        completion_message = "Thank you for your 311 {} request! If you provided your contact information, we'll let you know when the city marks it complete.".format(
            tablename)
        return completion_message


def write_to_db(req, token, service_type, request_spec, lat, lng, description,
                address_string, post_status, email=None, first_name=None,
                last_name=None, phone=None):
    '''
    Captures details of a Dialogflow transaction and Open311 POST request in
    Postgres database, including token associated with POST request that will
    be attached to a service request number once the request is approved by 
    the city.
    '''
    session_Id = req['sessionId']
    request_time = req['timestamp']
    req_status = req['status']['code']

    try:
        with psycopg2.connect(CONNECTION_STRING) as conn2:
            with conn2.cursor() as cur:

                cur.execute(queries.RECORD_TRANSACTION,
                            (session_Id, request_time, service_type, description, 
                             request_spec, address_string, lat, lng, email, first_name,
                             last_name, phone, post_status, token))

                conn2.commit()
    except Exception as e:
        print(
            "transaction recording of session_Id {} failed: {}". format(
                session_Id, e))


def daily_db_update(historicals_list, days_back=1):
    '''
    Make GET request to Chicago's Socrata 311 API to get the previous day's
    updates for pothole, rodent, and single-streetlight-out requests.

    Inputs:
        - historicals_list (list of dictionaries): service request type details 
            including API endpoint, pertinent column names and order for 
            parsing API request results for pothole, rodent, and streetlight 
            reqeusts.
        - days_back (integer): number of days in the past for which to request 
            updates from the 311 API.
    '''
    # iterate over the list of service request detail dictionaries, updating 
    # each one in the Postgres database
    for service_dict in historicals_list:
        updated = check_updates(service_dict, days_back)
        clean_updates = dedupe_df(updated, service_dict)
        update_table(clean_updates, service_dict['service_name'])


if __name__ == '__main__':
    app.run(debug=True)

    update_job_id = 'nightly_update_' + datetime.now().isoformat()
    sched.add_job(
        func=daily_db_update,
        trigger='interval',
        args=[historicals],
        minutes=5,
        id=update_job_id)
    if not sched.running:
        sched.start()

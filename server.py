#                     Documentation of Code Ownership
# Original code or heavily modified given structure unless otherwise noted in
# function header.


import urllib
import json
import os
import psycopg2
from psycopg2 import sql 
from flask import Flask, request, make_response, render_template
import googlemaps
import requests
from agent.clock import sched
from agent.util import (filter_city, get_action, get_service_code, get_service_type,
                   get_address_recs, get_tablename,
                   generate_post_status_message,
                   generate_attribute, structure_post_data, geocode)
from agent.chi311_import import historicals, check_updates, dedupe_df, update_table
import agent.queries

app = Flask(__name__, static_url_path='/static')
API_ENDPOINT = 'http://test311api.cityofchicago.org/open311/v2'
GMAPS_PLACES_APPTOKEN = os.environ['GMAPS_PLACES_APPTOKEN']
OPEN_311_APPTOKEN = os.environ['OPEN_311_APPTOKEN']
GMAPS = googlemaps.Client(key=GMAPS_PLACES_APPTOKEN)
USER = os.environ['DB_USER']
NAME = os.environ['DB_NAME']
PW = os.environ['DB_PW']
HOST = os.environ['DB_HOST']
PORT = os.environ['DB_PORT']
SSL_DIR = os.path.dirname(__file__)
SSL = os.environ['SSL']
SSL_PATH = os.path.join(SSL_DIR, SSL)
CONNECTION_STRING = """dbname='{}' user='{}' host='{}' port='{}'
                        password='{}' sslmode='verify-full'
                        sslrootcert='{}'""".format(
                        NAME, USER, HOST, PORT, PW, SSL_PATH)


@app.route('/webhook', methods=['POST'])
def webhook():
    '''
    Recieves DialogFlow requests, generates response via makeWebhookResult,
    and sends back the response.
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

@app.route('/')
def render_page2():
    return render_template('page1.html')

@app.route('/classproject')
def render_page():
    return render_template('page.html')


def makeWebhookResult(req):
    '''
    Takes a request from DialogFlow webhook and triages what the request
    is to produce the appropriate response back to DialogFlow.
    Inputs:
        - req (json): information passed from DialogFlow webhook
    '''
    action = get_action(req)
    if action == 'name':
        return followupEvent('get_address') #Triggers question to get address

    if action == 'get.address':
        return process_address(req) #Checks address provided by user

    if action == 'address.corrected':
        return process_address(req, True) #Checks corrected address

    if action == 'request.complete': #Triggers post of request and average
        #number of days to complete request
        status_message = post_request(req)
        completion_message = request_triggered_query(req)

        data = {"completion_time": completion_message,
                "post_status": status_message}

        return followupEvent('completion_time', data) #Triggers confirmation
                                                      #message to the user.


def followupEvent(event_key, data=None):
    '''
    Function that returns the webhook response needed
    based on where the conversation needs to go next. The 'events'
    below specify one of any events that are triggered in the
    conversation. This function simply constructs the appropriate
    event response for DialogFlow. DialogFlow uses the response
    to know which "Intent" to trigger next. If data is passed
    as part of the response, DialogFlow can use that data to
    insert into its response to the user. For more info, see
    https://dialogflow.com/docs/events.

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


def process_address(req, corrected = False):
    '''
    Manages collection of viable address. If a viable address is given
    (i.e. a single match is found via google maps autocomplete), then
    the conversation continues. If there aren't any matches, then the
    conversation will direct the user to enter the address again. In the case
    that there is more than one match, this function will pass back up to
    three address recommended matches for the user to select from.

    Inputs:
        - req (dict) data from DialogFlow where the address given by the
            user is stored
        - corrected (boolean) True if used to process a corrected address
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

    matched_addresses = GMAPS.places_autocomplete(address)
    matched_addresses = filter_city('Chicago', matched_addresses)

    if len(matched_addresses) == 0:
        return followupEvent('get_address') #Ask for address again.
    elif len(matched_addresses) == 1:
        return followupEvent(service_type) #Address collected, continue convo.
    else:
        address_recs = get_address_recs(matched_addresses)
        return followupEvent('address_correct', #Send back address matches.
                             address_recs)


def post_request(req):
    '''
    Extracts all required data from DialogFlow request containing
    all user inputs, structures the data into a dictionary which can
    then be passed as a post request to the Chicago Open311 test system.
    Will also update our own datebase recording user interactions.

    Inputs:
        - req (json): information passed from DialogFlow webhook containing
            user inputs
    Outputs:
        - status_message (string): status message indicating whether
            the post request submitted successfully or failed
    '''
    url = API_ENDPOINT + '/requests.json'
    service_type = get_service_type(req)
    service_code = get_service_code(service_type)

    parameters = req['result']['parameters']
    request_spec = parameters['request-spec']
    attribute = generate_attribute(service_type, request_spec)
    description = parameters['description']
    request_spec = parameters['request-spec']
    email = parameters['email']
    phone = parameters['phone-number']
    first_name = parameters['first-name']
    last_name = parameters['last-name']
    lat, lng, address_string = geocode(req, GMAPS)

    post_data = structure_post_data(service_code, attribute, lat, lng,
                                    description, address_string, email,
                                    first_name, last_name, phone,
                                    OPEN_311_APPTOKEN)

    response = requests.post(url, data = post_data)

    try:
        token = response.json()[0]['token']
    except BaseException:
        token = ''

    status_code = response.status_code
    status_message = generate_post_status_message(status_code)

    write_to_db(req, token, service_type, request_spec, lat, lng, description,
                address_string, status_code, email, first_name, last_name, phone)

    return status_message


def request_triggered_query(req):
    '''
    Query average historical resolution time for the two weeks pre- and post-
    today's day/ month in the last four years for the type of request.
    Limit query to the neighborhood containing reported location according
    to Chicago Open Data Portal Neighborhood Boundaries.

    Inputs:
        -req (request): request containing information from DialogFlow
            including service type and query parameters

    Output:
        - completion_message (str): formatted message indicating historical
            average response time

    Attribution:
        - Calls to psycopg2.sql function crafted based on examples in psycog2
            documentation for parameterizing table names in SQL queries via
            Python (http://initd.org/psycopg/docs/sql.html)
    '''
    service_type = get_service_type(req)
    tablename = get_tablename(service_type)
    lat, lng, formatted_address = geocode(req, GMAPS)

    both_q = sql.SQL(queries.TIME_LOC).format(tbl=sql.Identifier(tablename))
    loc_only = False

    conn2 = psycopg2.connect(CONNECTION_STRING)
    cur = conn2.cursor()
    cur.execute(both_q, [lng, lat])
    res = cur.fetchone()
    print(res)

    unit_index = {0: 'months', 1: 'weeks', 2: 'days'}

    # if there is no information on the specific neighborhood at the given time
    # of year, check for that neighborhood only; check for that time only if
    # there are no results for the given neighborhood
    if res and all(v is None for v in res):
        loc_only = True

        loc_q = sql.SQL(queries.LOC_ONLY).format(tbl=sql.Identifier(tablename))
        cur.execute(loc_q, [lng, lat])
        res = cur.fetchone()
        print(res)

        if res and all(v is None for v in res):
            loc_only = False
            time_q = sql.SQL(queries.TIME_ONLY).format(
                                                tbl=sql.Identifier(tablename))
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
                completion_message = '''Requests for {} are typically
                                        serviced within {} {} at this
                                        time of year.'''.format(
                                                 tablename, num, unit)
                return completion_message

    if res and len(res) == 4:
        neighb = res[0]
        for i, num in enumerate(res[1:]):
            if num:
                num = int(num)
                unit = unit_index[i]
                if loc_only:
                    completion_message = '''Requests for {} in the {} area
                                            are typically serviced within
                                            {} {}.'''.format(
                                            tablename, neighb, num, unit)
                else:
                    completion_message = '''Requests for {} in the {} area are
                                            typically serviced within {} {} at
                                            this time of year.'''.format(
                                                 tablename, neighb, num, unit)
                return completion_message

    # if no results returned, proceed with default message
    if not res:
        completion_message = '''Thank you for your {} request!
                                If you provided your contact
                                information, we'll let you know when the
                                city marks it complete.'''.format(tablename)
        return completion_message



def write_to_db(req, token, service_type, request_spec, lat, lng, description,
                address_string, post_status, email=None, first_name=None,
                last_name=None, phone=None):
    '''
    Captures details of a Dialogflow transaction and Open311 POST request in
    Postgres database, including token associated with POST request that will
    be attached to a service request number once the request is approved by
    the city.
    Inputs:
        - req (json) request containing all user input information
        - token (string) token generated as response from Open311
        - service_type (string) service type of the request
        - request_spec (string) request specific information
        - lat (float) latitude of service request
        - lng (float) longitude of service request
        - description (string) description given by user
        - address_string (string) address of service request
        - post_status (string) status of post request from Open311
        - email (string) email of user, if given
        - first_name (string) user first name, if given
        - last_name (string) user last name, if given
        - phone (string) user phone number, if given
    '''
    session_Id = req['sessionId']
    request_time = req['timestamp']
    req_status = req['status']['code']

    try:
        with psycopg2.connect(CONNECTION_STRING) as conn2:
            with conn2.cursor() as cur:

                cur.execute(queries.RECORD_TRANSACTION,
                            (session_Id, request_time, service_type,
                             description, request_spec, address_string, lat,
                             lng, email, first_name, last_name, phone,
                             post_status, token))

                conn2.commit()
    except Exception as e:
        print(
            "transaction recording of session_Id {} failed: {}". format(
                session_Id, e))


def daily_db_update(historicals_list, days_back = 1):
    '''
    Make GET request to Chicago's Socrata 311 API to get the previous day's
    updates for pothole, rodent, and single-streetlight-out requests; remove
    duplicates, and insert into Postgres database table corresponding to each
    service request type

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
        trigger='cron',
        id=update_job_id,
        day_of_week='0-6',
        hour=10, minute=12,
        args=[historicals],
        jitter=30)
    if not sched.running:
        sched.start()

import urllib
import json
import os
from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
import googlemaps
import requests

app = Flask(__name__)
API_ENDPOINT = 'http://test311api.cityofchicago.org/open311/v2'
GMAPS_PLACES_APPTOKEN = os.environ['GMAPS_PLACES_APPTOKEN']
OPEN_311_APPTOKEN = os.environ['OPEN_311_APPTOKEN']
gmaps = googlemaps.Client(key=GMAPS_PLACES_APPTOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    '''
    Recieves and responds to DialogFlow webhook post requests.
    '''
    req = request.get_json(silent = True, force = True)
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
    to produce the appropriate response.
    Inputs:
        - req (json): information passed from DialogFlow webhook
    '''
    action = get_action(req)
    print('****ACTION PRINT*****', action, '***************')
    if action == 'name':
        return followupEvent('get_address')

    if action == 'get.address':
        return process_address(req)

    if action == 'address.corrected':
        service_type = get_service_type(req)
        return followupEvent(service_type)

    if action == 'request.complete':
        #process the average number of days to complete request
        status_message = post_request(req)
        data = {"days": 5,
                "post_status": status_message}
        return followupEvent('completion_time', data)


def process_address(req):
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
    address = parameters['corrected-address']
    if not address:
        address = parameters['address']
    if 'Chicago' not in address:
        address += ' Chicago, IL'
    lat, lng, formatted_address = geocode(address)
    request_spec = parameters['request-spec']
    attribute = generate_attribute(service_type,request_spec)
    description = parameters['description']
    request_spec = parameters['request-spec']
    address_string = formatted_address
    try:
        email = parameters['email']
        phone = parameters['phone-number']
    except:
        email = ''
        phone = ''
    first_name = parameters['first-name']
    last_name = parameters['last-name']

    post_data = structure_post_data(service_code, attribute, lat, lng, description,
                 address_string, email, first_name, last_name, phone)

    print('OPEN_311_POST_REQUEST:', post_data)
    response = requests.post(url, data= post_data)
    print('OPEN_311_RESPONSE:', response)
    token = response.json()[0]['token']
    status_code = response.status_code
    status_message = generate_post_status_message(status_code)

    return status_message

def followupEvent(event_key, data = None):
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
              'address_correct':'address-correct'}

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
    address_recs = ['','','']
    for num, matched_addresses in enumerate(matched_addresses[:3]):
        address = matched_addresses['description']
        address_recs[num] = address

    recommendations = {"address1" : address_recs[0],
                       "address2" : address_recs[1],
                       "address3" : address_recs[2]}

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
    post_data = {'service_code' : service_code,
             'attribute' : attribute,
             'lat' : lat,
             'long' : lng,
             'first_name' : first_name,
             'last_name' : last_name,
             'email': email,
             'address_string': address_string,
             'phone_number' : phone,
             'description': description,
             'api_key' : OPEN_311_APPTOKEN}

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
     'no':  {'DOYOUWAN': {'key': 'NOTOBAIT', 'name': 'No'}}},
    'street light': 
    {'on and off': {'ISTHELI2': {'key': 'COMPLETE', 'name': 'Completely Out'}},
     'completely out': {'ISTHELI2': {'key': 'ONOFF', 'name': 'On and Off'}}}}

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


if __name__ == '__main__':
	app.run(debug=True)

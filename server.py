import urllib
import json
import os
from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
import googlemaps

app = Flask(__name__)
API_ENDPOINT = 'http://test311api.cityofchicago.org/open311/v2'
GMAPS_PLACES_APPTOKEN = os.environ['GMAPS_PLACES_APPTOKEN']
OPEN_311_APPTOKEN = os.environ['OPEN_311_APPTOKEN']
gmaps = googlemaps.Client(key=GMAPS_PLACES_APPTOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
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
        #geocode address
        #create object to post to open311 servers
        #process the average number of days to complete request
        token = post_request(req)
        data = {"days": 5,
                "token": token}
        return followupEvent('completion_time', data)


def process_address(req):
    '''
    Enter description.
    '''
    address = req['result']['parameters']['address']
    service_type = get_service_type(req)
    if 'Chicago' not in address:
        address += ' Chicago, IL'

    if 'and' in address or '&' in address:
        return followupEvent(service_type)

    matched_addresses = gmaps.places_autocomplete(address)
    matched_addresses = filter_city('Chicago', matched_addresses)

    if len(matched_addresses) == 0:
        return followupEvent('get_address')
    elif len(matched_addresses) == 1:
        return followupEvent(service_type)
    else:
        address_recs = get_address_recs(matched_addresses)
        return followupEvent('address_correct', address_recs)


def followupEvent(event_key, data = None):
    '''
    Enter description.
    '''
    events = {'pothole': 'pothole_request','rodent': 'rodent_request',
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
    In the case of multiple address matches, this function will
    return up to the top three address recommendations
    '''
    address_recs = ['','','']
    for num, matched_addresses in enumerate(matched_addresses[:3]):
        address = matched_addresses['structured_formatting']['main_text']
        address_recs[num] = address

    recommendations = {"address1" : address_recs[0],
                       "address2" : address_recs[1],
                       "address3" : address_recs[2]}

    return recommendations


def post_request(req):
    parameters = req['result']['parameters']
    service_type = get_service_type(req)
    service_code = get_service_code(service_type)
    address = parameters['corrected-address']
    if not address:
        address = parameters['address']
    lat, lng, formatted_address = geocode(address)
    request_spec = parameters['request_spec']
    attribute = generate_attribute[service_type][request_spec]
    description = parameters['description']
    request_spec = parameters['request_spec']
    address_string = formatted_address
    email = parameters['email']
    first_name = parameters['first_name']
    last_name = parameters['last_name']
    phone_number = parameters['phone-number']

    response = post(service_code, attribute, lat, lng, description,
               address_string, email, first_name, last_name, phone)




def post(service_code, attribute, lat, lng, description,
                 address_string, email, first_name, last_name, phone):
    url = API_ENDPOINT + '/requests.json'

    post_data = {'service_code' : service_code,
             'attribute' : attribute,
             'lat' : lat,
             'long' : lng,
             'first_name' : first_name,
             'last_name' : last_name,
             'email': email,
             'phone_number' : phone,
             'description': description,
             'api_key' : OPEN_311_APPTOKEN}

    response = requests.post(url, data= post_data)

    return response.text
    
def get_service_code(service_type):
    service_types = {'pothole': '4fd3b656e750846c53000004',
                     'rodent': '4fd3b9bce750846c5300004a',
                     'street light': '4ffa9f2d6018277d400000c8'}

    return service_types[service_type]

def generate_attribute(service_type, request_spec):
    attributes = {'pothole': {'intersection': {'WHEREIST': {'key': 'INTERSEC', 'name': 'Intersection'}},
                              'bike lane': {'WHEREIST': {'key': 'BIKE', 'name': 'Bike Lane'}},
                              'crosswalk': {'WHEREIST': {'key': 'CROSS', 'name': 'Crosswalk'}},
                              'curb lane': {'WHEREIST': {'key': 'CURB', 'name': 'Curb Lane'}},
                              'traffic lane': {'WHEREIST': {'key': 'TRAFFIC', 'name': 'Traffic Lane'}}},
                  'rodent':  {'yes': {'DOUYOUWAN': {'key': 'BAITBYAR', 'name': 'Bait Back Yard'}},
                              'no':  {'DOUYOUWAN': {'key': 'NOTOBAIT', 'name': 'No'}}},
                  'street light': {'on and off': {'ISTHELI2': {'key': 'COMPLETE', 'name': 'Completely Out'}},
                                   'completely out': {'ISTHELI2': {'key': 'ONOFF', 'name': 'On and Off'}}}}
    return attributes[service_type][request_spec]

def geocode(address):
    result = maps.geocode(address)[0]

    lat = result['geometry']['location']['lat']
    lng = result['geometry']['location']['lng']
    formatted_address = result['formatted_address']

    return lat, lng, formatted_address



if __name__ == '__main__':
	app.run(debug=True)


# {
#         "jurisdiction_id": jurisdiction_id,
#         "service_code": service_code,
#         "attribute": attribute,
#         "description": description,
#         "lat": lat,
#         "long": long_,
#         "address_string": address_string,
#         "address_id": address_id,
#         "email": email,
#         "device_id": device_id,
#         "accont_id": account_id,
#         "first_name": first_name,
#         "last_name": last_name,
#         "phone": phone,
#         "description": description,
#         "media_url": media_url
#     }
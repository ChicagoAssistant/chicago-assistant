import urllib
import json
import os
from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
import googlemaps

app = Flask(__name__)
api_url = 'http://test311api.cityofchicago.org/open311/v2'
GMAPS_PLACES_APPTOKEN = os.environ['GMAPS_PLACES_APPTOKEN']
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

def get_service_type(req):
    '''
    Given a DialogFlow json, get the service type of the request.
    Inputs:
        - req (json): information passed from DialogFlow webhook
    Outputs:
        - service_type (string): service type of request
    '''
    service_type = req['results']['parameters']['service-type']
    return service_type

def process_address(req):
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

    if action == 'reqeust.complete':
        #geocode address
        #create object to post to open311 servers
        #process the average number of days to complete request
        return followupEvent('completion_time',5)
        
       


    
# def makeWebhookResult(req):
#     if req['result']['action'] in ['name.collected','name.not.collected']:
#         return {"followupEvent": {
#                 "name": 'get-address'}
#                    }
#     # elif req['result']['action'] == 'notification':
#     elif req['result']['action'] == 'get.address':
#         gmaps = googlemaps.Client(key=GMAPS_PLACES_APPTOKEN)
#         address = req['result']['parameters']['address']
#         if 'and' in address or '&' in address:
#             key = req['result']['parameters']['service-type']
#             return followupEvent(key)
#         if 'Chicago' not in address:
#             address += ' Chicago, IL'
#         results = gmaps.places_autocomplete(address)
#         if len(results) == 0:
#             return {"followupEvent": {
#                 "name": 'get-address'}
#                    }
#         elif len(results) == 1:
#             key = req['result']['parameters']['service-type']
#             return followupEvent(key)
#         else:
#             addresses = ['','','']
#             for num, result in enumerate(results[:3]):
#                 address = result['structured_formatting']['main_text']
#                 addresses[num] = address
#             return {"followupEvent": {
#                 "name": "address-correct",
#                 "data": {"address1" : addresses[0],
#                          "address2" : addresses[1],
#                          "address3" : addresses[2]}}
#                    }
#     elif req['result']['action'] == 'request.complete':
#         return {"followupEvent": {
#                 "name": 'completion_time',
#                 "data": {
#                 "days":"5"}}
#                 }
#     elif req['result']['action'] == 'address.corrected':
#         key = req['result']['parameters']['service-type']
#         return followupEvent(key)
#     else:
#         return None


def followupEvent(event_key, data = ''):
    events = {'pothole': 'pothole_request','rodent': 'rodent_request',
              'street light': 'street_light_request',
              'completion_time': 'completion_time', 
              'get_address': 'get-address',
              'address_correct':'address-correct'}

    event = events[event_key]
    event_full = {"followupEvent": {"name": '{}'.format(event),
                              "data": data}}

    print(event_full)
    return event_full

def capture_response(req):
    pass
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
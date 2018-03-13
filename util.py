def geocode(req, client):
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
    parameters = req['result']['parameters']
    address = parameters['corrected-address']
    if not address:
        address = parameters['address']
    if 'Chicago' not in address:
        address += ' Chicago, IL'
    result = client.geocode(address)[0]
    lat = result['geometry']['location']['lat']
    lng = result['geometry']['location']['lng']
    formatted_address = result['formatted_address']

    return lat, lng, formatted_address

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
                        address_string, email, first_name, last_name, phone,
                        api_key):
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
                 'api_key': api_key}

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


def get_tablename(db_key):
    '''
    Return name of associated Postgres database table from Open311/ 
    Dialogflow service request type names
    '''
    db_map = {'pothole': 'potholes', 'rodent': 'rodents',
              'street light': 'streetlights',
              'dialogflow': 'dialogflow_transactions'}

    return db_map[db_key]
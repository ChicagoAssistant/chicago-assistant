import requests
import yaml

SERVICE_TYPES = './requests_311/service_types.yml'
API_ENDPOINT = 'http://test311api.cityofchicago.org/open311/v2'

def generate_post_status_message(status_code):
    '''
    Helper function to return status message given a status code.
    Inputs:
        - status_code (int) status code returned by post request to Open311
    Outputs:
        - status_message (string) status message indicating status of post
            request
    '''
    status_messages = {201: 'Your request has been submitted successfully!',
                       400: 'Your request is a duplicate in our system!'}

    return status_messages[status_code]


def get_service_code(service_type):
    '''
    Helper function to get the service code given a string.
    Inputs:
        - service_type (string): service type generated in DialogueFlow
            based on user input
    Outputs:
        - service_code (string): Open311 service code for post service
            request to Open311 systems
            See http://dev.cityofchicago.org/docs/open311/
    '''
    service_types = yaml.load(open(SERVICE_TYPES))['service_codes']
    assert service_type in service_types, "Sorry, not a valid service type."

    return service_types[service_type]


def generate_attribute(service_type, question_response):
    '''
    Helper function to create dictionary needed for the Open311 post request.
    Inputs:
        - service_type (string): service request type
        - question_response (string): answer to request specific question
    Outputs:
        - attribute (dict): dictionary sent to Open311 as attribute to specify
            answer to required question. See http://dev.cityofchicago.org/docs/open311/
    '''
    attributes = yaml.load(open(SERVICE_TYPES))['attributes']

    return attributes[service_type][question_response]

'''
WHAT IS MISSING HERE ARE FUNCTIONS THAT WILL TAKE AS AN INPUT DATA FROM RASA
AND RETURN THE REQUEST DATA IN THE FOLLOWING FORMAT:

{
  "service_code": "4fd3b656e750846c53000004",
  "attribute": {
    "WHEREIST": {
      "key": "INTERSEC",
      "name": "Intersection"
    }},
    "lat": 41.882785,
    "long": -87.632409,
    "first_name": "FirstName",
    "last_name": "LastName",
    "email": "email@address.com",
    "address_string": "30 N LaSalle Ave",
    "phone_number": "555-555-5555",
    "description": "I saw a pothole on the street",
    "api_key": "apikey"
}

ONCE THIS INPUT DATA IS CONSTRUCTED, IT CAN BE PASSED TO THE post_request
FUNCTION. UNTIL WE BUILD THE RASA DIALOGUE THAT WILL COLLECT THE RELEVANT
INFORMATION, WE CAN'T BUILD THIS FUNCTION BECAUSE WE DON'T YET KNOW THE
STRUCTURE OF THE DATA RASA PROVIDES.
'''

def post_request(post_data):
    '''
    The input is a dictionary which can then be passed in a post request to the
    Chicago Open311 test system.
    Inputs:
        - post_data (json): data collected and packaged for 311 API POST
    Outputs:
        - status_message (string): status message indicating whether
            the post request submitted successfully or failed
    '''
    url = API_ENDPOINT + '/requests.json'
    response = requests.post(url, data = post_data)
    status_code = response.status_code
    status_message = generate_post_status_message(status_code)

    return status_message

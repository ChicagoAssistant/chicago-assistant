import requests
import json
import os
from datetime import date


API_ENDPOINT = 'http://test311api.cityofchicago.org/open311/v2'
POTHOLE_SERVICE_CODE = '4fd3b656e750846c53000004'


url = API_ENDPOINT + '/requests.json'

attribute = {'WHEREIST' : "{'key': 'BIKE', 'name': 'Bike Lane'}",
             'A511OPTN' : '444-555-5555'}


lat = 41.8781
lon = -87.6298

address_string = '964 E 62nd Street Chicago, IL 60637'

post_data = {'service_code' : POTHOLE_SERVICE_CODE,
             'attribute' : '''{'WHEREIST' : "{'key': 'BIKE', 'name': 'Bike Lane'}",'A511OPTN' : '444-555-5555'}''',
             'lat' : lat,
             'long' : lon,
             'address_string' : address_string,
             'description': 'thisisatest',
             'api_key' : API_KEY}

# requests.post(url, data=post_data)







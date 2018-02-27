import requests
import json
import os
from datetime import date


API_ENDPOINT = 'http://test311api.cityofchicago.org/open311/v2'
POTHOLE_SERVICE_CODE = '4fd3b656e750846c53000004'
RODENT_SERVICE_CODE = '4fd3b9bce750846c5300004a'
STREET_LIGHT_SERVICE_CODE = '4ffa9f2d6018277d400000c8'


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
             'first_name' : 'John',
             'last_name' : 'Johnson',
             'phone_number' : '224-444-4444',
             'description': 'thisisaffftedddst',
             'api_key' : API_KEY}

# requests.post(url, data=post_data)

# https://github.com/googlemaps/google-maps-services-python






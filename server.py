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
    if req['result']['action'] in ['name.collected','name.not.collected']:
        return {"followupEvent": {
                "name": 'get-address'}
                   }
    # elif req['result']['action'] == 'notification':
    elif req['result']['action'] == 'get.address':
        gmaps = googlemaps.Client(key=GMAPS_PLACES_APPTOKEN)
        address = req['result']['parameters']['address']
        if 'and' in address or '&' in address:
            return followupEvent(req)
        if 'Chicago' not in address:
            address += ' Chicago, IL'
        results = gmaps.places_autocomplete(address)
        if len(results) == 0:
            return {"followupEvent": {
                "name": 'get-address'}
                   }
        elif len(results) == 1:
            return followupEvent(req)
        else:
            addresses = ['','','']
            for num, result in enumerate(results[:3]):
                address = result['structured_formatting']['main_text']
                addresses[num] = address
            return {"followupEvent": {
                "name": "address-correct",
                "data": {"address1" : addresses[0],
                         "address2" : addresses[1],
                         "address3" : addresses[2]}}
                   }
    elif req['result']['action'] == 'request.complete':
        return {"followupEvent": {
                "name": 'completion_time',
                "data": {
                "days":"5"}}
                }
    elif req['result']['action'] == 'address.corrected':
        return followupEvent(req)
    else:
        speech = "Hi, Vidal!"
        return {"fulfillmentText": speech,
            "source": 'Vidal\'s Mind!'}

def followupEvent(req):
    if req['result']['parameters']['service-type'] == 'pothole':
        return {"followupEvent": {
                "name": 'pothole_request'}
                   }
    if req['result']['parameters']['service-type'] == 'rodent':
        return {"followupEvent": {
                "name": 'rodent_request'}
                   }
    if req['result']['parameters']['service-type'] == 'street light':
        return {"followupEvent": {
                "name": 'street_light_request'}
                   }

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
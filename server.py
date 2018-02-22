import urllib
import json
import os
from flask import Flask
from flask import request
from flask import make_response
from flask import render_template

app = Flask(__name__)
api_url = 'http://test311api.cityofchicago.org/open311/v2'

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
# def makeWebhokResult(req):
# 	pri

@app.route('/test')
def test():
    return render_template('page.html')

def makeWebhookResult(req):
    speech = "Hi, Vidal!"
    return {"fulfillmentText": speech,
            "source": 'Vidal\'s Mind!'}



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
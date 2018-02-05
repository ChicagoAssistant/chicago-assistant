import urllib
import json
import os
from flask import Flask
from flask import request
from flask import make_response

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
	req = request.get_json(silent = True, force = True)
	print('Request:\n', json.dumps(req, indent=4))
	# res = makeWebhookResult(req)
	# res = json.dumps(res, indent=4)
	# print(res)
	# r = make_response(res)
	# r.headers['Content-Type'] = 'application/json'
	
	return req

# def makeWebhokResult(req):
# 	pri


if __name__ == '__main__':
	app.run()
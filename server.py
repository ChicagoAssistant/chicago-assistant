#                     Documentation of Code Ownership
# Original code or heavily modified given structure unless otherwise noted in
# function header.

from flask import Flask, request, make_response, render_template
import requests
<<<<<<< HEAD
=======
from agent.clock import sched
from agent.util import (filter_city, get_action, get_service_code, get_service_type,
                   get_address_recs, get_tablename,
                   generate_post_status_message,
                   generate_attribute, structure_post_data, geocode)
from agent.chi311_import import historicals, check_updates, dedupe_df, update_table
import agent.queries as queries

app = Flask(__name__, static_url_path='/static')
API_ENDPOINT = 'http://test311api.cityofchicago.org/open311/v2'
GMAPS_PLACES_APPTOKEN = os.environ['GMAPS_PLACES_APPTOKEN']
OPEN_311_APPTOKEN = os.environ['OPEN_311_APPTOKEN']
GMAPS = googlemaps.Client(key=GMAPS_PLACES_APPTOKEN)
USER = os.environ['DB_USER']
NAME = os.environ['DB_NAME']
PW = os.environ['DB_PW']
HOST = os.environ['DB_HOST']
PORT = os.environ['DB_PORT']
SSL_DIR = os.path.dirname(__file__)
SSL = os.environ['SSL']
SSL_PATH = os.path.join(SSL_DIR, SSL)
CONNECTION_STRING = """dbname='{}' user='{}' host='{}' port='{}'
                        password='{}' sslmode='verify-full'
                        sslrootcert='{}'""".format(
                        NAME, USER, HOST, PORT, PW, SSL_PATH)

>>>>>>> 536b7daaf9eb746d5af5edb5ad13b46f7bf18917


app = Flask(__name__, static_url_path='/static')

@app.route('/')
def render_page():
    return render_template('page.html')

if __name__ == '__main__':
    app.run(debug=True)

#                     Documentation of Code Ownership
# Original code or heavily modified given structure unless otherwise noted in
# function header.

from flask import Flask, request, make_response, render_template
import requests


app = Flask(__name__, static_url_path='/static')

@app.route('/')
def render_page():
    return render_template('page.html')

if __name__ == '__main__':
    app.run(debug=True)

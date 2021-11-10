#!/usr/bin/env python3
from flask import Flask, jsonify, request, abort, make_response
from flask_httpauth import HTTPTokenAuth
from flask_cors import CORS
from methods import get_recs
import pandas as pd
import os
import logging
import json

application = Flask(__name__)
application.logger.setLevel(logging.DEBUG)
CORS(application)
auth = HTTPTokenAuth(header='key')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Read in data.
# Data is stored in a .csv file that is read in with pandas.
# We should eventually convert to am sql database for better scalability.
data = pd.read_csv('./data/acs_geo_data_with_descriptions.csv',
    dtype={'id': str, 'state_id': str, 'place_id': str,
    'metro_area_id': str}).set_index('id')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# View functions
@application.route('/api/v1.0/recs', methods=['POST'])
@auth.login_required
def return_recs():
    # Log request headers and body
    application.logger.debug('Headers: %s', request.headers)
    application.logger.debug('Body: %s', request.get_data())
    # validate request
    if not request.json or not 'params' in request.json or not 'meta' in \
    request.json:
        abort(400)
    response = make_response(get_recs(data, request.json))
    response.headers['Content-Type'] = 'application/json'
    return response

@application.route('/api/v1.0/city/<city_id>', methods=['GET'])
@auth.login_required
def get_city(city_id):
    # Log request headers and body
    application.logger.debug('Headers: %s', request.headers)
    application.logger.debug('Body: %s', request.get_data())
    try:
        city = data.loc[str(city_id)]
    except KeyError:
        abort(404)
    # Some hacky solution to return map_center coords as a list instead of str.
    response = json.loads(city.to_json())
    response['map_center'] = json.loads(response['map_center'])
    response = make_response(response)

    response.headers['Content-Type'] = 'application/json'
    return response

@application.route('/', methods=['GET'])
def index():
    return '', 200
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Error handlers
@application.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'bad request'}), 400)

@application.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'unauthorized access'}), 403)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Token authentication
@auth.verify_token
def verify_token(token):
    if token and token == os.environ.get('API_KEY'):
        return True
    return False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == '__main__':
    application.run(debug=True)

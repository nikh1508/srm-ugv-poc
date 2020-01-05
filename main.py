import logging
import os
import sys
import datetime
from flask import Flask, request, jsonify, Response, render_template
# import database

logging.basicConfig(filename='server.log', format='[%(levelname)-7s] : %(asctime)s : %(name)-8s : %(message)s',
                    level=logging.DEBUG, datefmt='%b %d, %g | %H:%M:%S')
log = logging.getLogger(__name__)

try:
    shared_file_path = os.environ['SHARED_FILE_PATH']
except KeyError:
    log.error('Error obatining shared file path')

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # For Developement Only
#
# Sample Data for Developement:
loc = {'lat': 12.60789, 'lng': 80.77654, 'sat': 14}
compass = {'heading': 35}
suggestions = {'suggestions': ['option1', 'option2', 'option3']}
#

# Client Web-Page
@app.route('/')
def index():
    return render_template('index.html')


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.route('/api/sensor-data', methods=['GET'])
def sensorData():
    log.info('Sensor data requested.')
    sensor = request.args.get('sensor')
    if sensor == 'gps':
        return jsonify(loc)
    elif sensor == 'compass':
        return jsonify(compass)


@app.route('/api/search', methods=['GET'])
def searchSuggestions():
    query = request.args.get('query')
    return jsonify(suggestions)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == "__main__":
    log.info('Starting Flask Sever.')
    app.run(host='0.0.0.0', port=8080, debug=True)

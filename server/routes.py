from app import app, shared_data, ipc
from flask import Flask, request, jsonify, Response, render_template
import logging
from db_models import *

log = logging.getLogger(__name__)
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

# Get Sensor Data
@app.route('/api/sensor-data', methods=['GET'])
def sensorData():
    log.info('Sensor data requested.')
    sensor = request.args.get('sensor')
    if sensor == 'gps':
        return jsonify(loc)
    elif sensor == 'compass':
        return jsonify(compass)

# Search Suggestions
@app.route('/api/search', methods=['GET'])
def searchSuggestions():
    query = request.args.get('query')
    possible_locations = Location.query.filter(Location.pretty_name.like('%{}%'.format(query))).all()
    possible_locations = locations_schema.dump(possible_locations)
    suggestions = []
    for location in possible_locations:
        suggestions.append({'id':location['id'], 'pretty_name':location['pretty_name']})
    return jsonify(suggestions)

# Add new location
@app.route('/api/location', methods=['POST'])
def add_location():
    latitude = request.json['latitude']
    longitude = request.json['longitude']
    loc_type = request.json['loc_type']
    pretty_name = request.json['pretty_name']
    description = request.json['description']
    # print(latitude, longitude, loc_type, pretty_name, description)
    new_location = Location(latitude, longitude,
                            loc_type, pretty_name, description)
    db.session.add(new_location)
    db.session.commit()
    return location_schema.jsonify(new_location)

# Get all location
@app.route('/api/location', methods=['GET'])
def get_locations():
    all_locations = Location.query.all()
    result = locations_schema.dump(all_locations)
    return jsonify(result)

# Get Single Location
@app.route('/api/location/<id>', methods=['GET'])
def get_location(id):
    location = Location.query.get_or_404(id)
    return location_schema.jsonify(location)

# Update Location
@app.route('/api/location/<id>', methods=['PUT'])
def update_location(id):
    location = Location.query.get(id)
    location.latitude = request.json['latitude']
    location.longitude = request.json['longitude']
    location.loc_type = request.json['loc_type']
    location.pretty_name = request.json['pretty_name']
    location.description = request.json['description']
    db.session.commit()
    return location_schema.jsonify(location)

# Delete Location
@app.route('/api/location/<id>', methods=['DELETE'])
def delete_location(id):
    location = Location.query.get(id)
    db.session.delete(location)
    db.session.commit()
    return location_schema.jsonify(location)

# Set Parameters
@app.route('/api/set/<parameter>', methods=['POST'])
def set_parameter(parameter):
    if parameter == 'destination':
        with ipc.lock:
            shared_data['destination']['latitude'] = request.json['latitude']
            shared_data['destination']['longitude'] = request.json['longitude']
            ipc.send_data(shared_data)
        return jsonify(shared_data)
    elif parameter == 'velocity':
        with ipc.lock:
            shared_data['velocity'] = request.json['velocity']
            ipc.send_data(shared_data)
        return jsonify(shared_data)

# Start/Stop Journey
@app.route('/api/control/<signal>', methods=['GET'])
def start_bot(signal):
    if signal == 'start' or signal == 'stop':
        shared_data['toggleSignal'] = signal
        ipc.send_data(shared_data)
        return '{} signal sent to the bot'.format(signal)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

import re

from flask import render_template, request, jsonify

from sta_dashboard import app
from sta_dashboard.models import Location, Thing


@app.route('/')
def index():
    locations = Thing.query.with_entities(Thing.latitude, Thing.longitude).filter(
        Thing.endpoint == 'internetofwater').all()
    return render_template('index.html', locations=locations, zoom_level=5)


@app.route('/show_points', methods=['POST'])
def show_points():
    
    # regex to extract endpoint names from strings
    endpoints = re.findall(r'\w+', request.form['endpoints']) #TODO: support names that contain non-letter chars
    
    locations = []
    for endpoint in endpoints:
        locations.extend(
            Thing.query.with_entities(Thing.latitude, Thing.longitude, Thing.datastreams).filter(
                Thing.endpoint == endpoint).all()
        )
    zoom_level = 2 if len(endpoints) > 1 else 5
    
    return jsonify({
        'locations': locations,
        'zoom_level': zoom_level
    })

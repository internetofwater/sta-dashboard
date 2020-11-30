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
    first_latlons = [] # save first latlon pair at each endpoint, use the average pair as default view latlon
    
    for endpoint in endpoints:
        
        query_result = Thing.query.with_entities(Thing.latitude, Thing.longitude, Thing.datastreams).filter(
            Thing.endpoint == endpoint).all()
        
        locations.extend(query_result)
        first_latlons.append(query_result[0][:2])
        
    zoom_level = 3 if len(endpoints) > 1 else 5
    
    return jsonify({
        'viewLatlon': [sum(latlon) / len(latlon) for latlon in zip(*first_latlons)],
        'locations': locations,
        'zoom_level': zoom_level
    })

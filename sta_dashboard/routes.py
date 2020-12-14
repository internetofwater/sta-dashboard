import re
from datetime import datetime
import pdb

from flask import render_template, request, jsonify
from sqlalchemy import create_engine

from sta_dashboard import app
from sta_dashboard.models import Thing, Datastream
from sta_dashboard.utils import *
    

@app.route('/')
def index():
    locations = Thing.query.with_entities(Thing.latitude, Thing.longitude).filter(
        Thing.endpoint == 'internetofwater').all()
    return render_template('index.html', locations=locations, zoom_level=5)


@app.route('/query_points', methods=['POST'])
def query_points():
    
    # regex to extract endpoint names from strings
    endpoints = re.findall(r'\w+', request.form['endpoints']) #TODO: support names that contain non-letter chars
    # TODO: use regex to extract datetime string
    queryStartDate = datetime.strptime(request.form['startDate'][1:-1], '%Y-%m-%d')
    queryEndDate = datetime.strptime(request.form['endDate'][1:-1], '%Y-%m-%d')
    locations = []
    first_latlons = [] # save first latlon pair at each endpoint, use the average pair as default view latlon
    
    for endpoint in endpoints:
        
        query_result = Datastream.query.with_entities(
            Datastream.resultStartDate, 
            Datastream.resultEndDate, 
            Datastream.endpoint,
            Datastream.name,
            Datastream.selfLink, 
            Thing.latitude, 
            Thing.longitude
            ).\
                join(Thing, Datastream.thingId==Thing.id).\
                    filter(
                        Datastream.resultStartDate >= queryStartDate,
                        Datastream.resultEndDate <= queryEndDate,
                        Datastream.endpoint == endpoint
                    ).all()
        locations.extend(query_result)
        first_latlons.append(query_result[0][-2:])
        # pdb.set_trace()

    zoom_level = 3 if len(endpoints) > 1 else 5
    
    return jsonify({
        'viewLatlon': [sum(latlon) / len(latlon) for latlon in zip(*first_latlons)],
        'locations': locations,
        'zoom_level': zoom_level
    })

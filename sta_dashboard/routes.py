import re
from datetime import datetime as dt

from flask import render_template, request, jsonify

from sta_dashboard import app
from sta_dashboard.models import Location, Thing


def extract_date(resultTimeString):
    # Example datetime format: '1954-09-10T12:00:00.000Z/2019-12-13T21:26:00.000Z'
    assert len(resultTimeString) == 49
    
    year = [s[:10] for s in resultTimeString.split('/')]
    startDate, endDate = year[0], year[1]
    
    return startDate, endDate


def stringToDate(dateString):
    # Example date format: '1954-09-10'
    assert len(dateString) == 10
    return dt.strptime(dateString, "%Y-%m-%d")


def compare_date(dataDateTuple: tuple, queryDateTuple: tuple) -> bool:
    dataStartDate, dataEndDate = dataDateTuple
    queryStartDate, queryEndDate = queryDateTuple
    return dataStartDate <= queryStartDate and dataEndDate >= queryEndDate
    

@app.route('/')
def index():
    locations = Thing.query.with_entities(Thing.latitude, Thing.longitude).filter(
        Thing.endpoint == 'internetofwater').all()
    return render_template('index.html', locations=locations, zoom_level=5)


@app.route('/query_points', methods=['POST'])
def query_points():
    
    # regex to extract endpoint names from strings
    endpoints = re.findall(r'\w+', request.form['endpoints']) #TODO: support names that contain non-letter chars
    queryStartDate = request.form['startDate'][1:-1] #TODO: use regex to extract
    queryEndDate = request.form['endDate'][1:-1]
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

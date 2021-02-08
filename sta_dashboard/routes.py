import re
from datetime import datetime
import requests
import pdb

from flask import render_template, request, jsonify
from sqlalchemy import or_, and_
import pandas as pd

from sta_dashboard import app
from sta_dashboard.models import Thing, Datastream
from sta_dashboard.utils import extract_date
    

@app.route('/')
def index():
    # locations = Thing.query.with_entities(Thing.latitude, Thing.longitude).filter(
    #     Thing.endpoint == 'internetofwater').all()
    return render_template('index.html')


@app.route('/query_points', methods=['POST'])
def query_points():
    
    # regex to extract endpoint names from strings
    endpoints = re.findall(r'\w+', request.form['endpoints']) #TODO: support names that contain non-letter chars
    # TODO: use regex to extract datetime string
    
    queryStartDate, queryEndDate = \
        extract_date(request.form['startDate'], request.form['endDate'])
    
    locations = []
    first_latlons = [] # save first latlon pair at each endpoint, use the average pair as default view latlon
    
    query_result_keys = [
        'phenomenonStartDate', 'phenomenonEndDate', 'endpoint', 'name', 'selfLink', 'thingId', 'latitude', 'longitude'
    ]
    for endpoint in endpoints:
        
        query_result = Datastream.query.with_entities(
            Datastream.phenomenonStartDate,
            Datastream.phenomenonEndDate,
            Datastream.endpoint,
            Datastream.name,
            Datastream.selfLink,
            Datastream.thingId,
            Thing.latitude, 
            Thing.longitude
            ).\
                join(Thing, Datastream.thingId==Thing.id).\
                    filter(
                        or_(
                            and_(
                                Datastream.phenomenonStartDate <= queryEndDate,
                                Datastream.phenomenonStartDate >= queryStartDate
                            ),
                            and_(
                                Datastream.phenomenonEndDate >= queryStartDate,
                                Datastream.phenomenonEndDate <= queryEndDate
                            ),
                            and_(
                                Datastream.phenomenonStartDate >= queryStartDate,
                                Datastream.phenomenonEndDate <= queryEndDate
                            ),
                            and_(
                                Datastream.phenomenonStartDate <= queryStartDate,
                                Datastream.phenomenonEndDate >= queryEndDate
                            )
                        ),
                        Datastream.endpoint == endpoint
                    ).\
                        all()
        if query_result:
            first_latlons.append(query_result[0][-2:]) # Get the first lat/lon pair as the default view point
            
        query_df = pd.DataFrame(query_result, columns=query_result_keys)
        
        unique_locations = query_df.drop_duplicates(
            'thingId')[['thingId', 'latitude', 'longitude']]
        locations.extend(list(unique_locations.T.to_dict().values()))

    zoom_level = 3 if len(endpoints) > 1 else 5
    if not first_latlons:
        first_latlons = [(35.99,  -78.90)]

    return jsonify({
        'viewLatlon': [sum(latlon) / len(latlon) for latlon in zip(*first_latlons)],
        'locations': locations,
        'zoom_level': zoom_level
    })


@app.route('/show_available_datastreams', methods=['POST'])
def select_datastreams():
    thingId = request.form['thingId'][1:-1]
    query_result = Datastream.query.with_entities(
        Datastream.name
    ).\
        filter(Datastream.thingId == thingId).\
        all()
    
    available_ds = list(set([ds for qr in query_result for ds in qr]))
    
    return jsonify({
        'availableDatastreams': available_ds
    })


@app.route('/visualize_observations', methods=['POST'])
def visualize_observations():
    thingId = request.form['thingId'][1:-1]
    dsList = [s[1:-1] for s in request.form['dsList'][1:-1].split(',')]

    query_result = Datastream.query.with_entities(
        Datastream.selfLink,
        Datastream.unitOfMeasurement
    ).\
        filter(
            Datastream.thingId == thingId,
            Datastream.name.in_(dsList)
            ).\
                all()

    queryStartDate, queryEndDate = \
        extract_date(request.form['startDate'], request.form['endDate'])
    
    def makeAPICallUrl(selfLink, queryStartDate, queryEndDate):
        
        startDateISO = queryStartDate.isoformat() + 'Z'
        endDateISO = queryEndDate.isoformat() + 'Z'
        
        observationsUrl = '&$'.join([
            selfLink + r'/Observations?$orderby=phenomenonTime asc',
            r'expand=Datastream',
            r'resultFormat=dataArray'
        ])
        
        if queryStartDate != datetime.min and queryEndDate != datetime.max:
            observationsUrl += \
                r'&$filter=phenomenonTime ge ' + startDateISO + \
                    r' and ' + r'phenomenonTime le ' + endDateISO
        elif queryStartDate == datetime.min and queryEndDate != datetime.max:
            observationsUrl += \
                r'&$filter=phenomenonTime le ' + endDateISO
        elif queryStartDate != datetime.min and queryEndDate == datetime.max:
            observationsUrl += \
                r'&$filter=phenomenonTime ge ' + startDateISO
                
        observedPropertyUrl = selfLink + r'/ObservedProperty'
        
        return observedPropertyUrl, observationsUrl
    
    output_data = []
    for selfLink, unitOfMeasurement in query_result:
        dataset = {}
        points = []

        observedPropertyUrl, observationsUrl = makeAPICallUrl(
            selfLink, queryStartDate, queryEndDate)
        # pdb.set_trace()
        observationsResponse = requests.get(observationsUrl)
        observedPropertyResponse = requests.get(observedPropertyUrl)

        observedProperty = observedPropertyResponse.json()
        dataset['label'] = observedProperty['name'] + ' ({})'.format(unitOfMeasurement['name'])
        dataset['description'] = observedProperty['description']

        observations = observationsResponse.json()['value'][0]
        values_df = pd.DataFrame(
            observations['dataArray'], columns=observations['components'])
        for _, row in values_df.iterrows():
            points.append(
                {
                    'x': datetime.strptime(
                        row['phenomenonTime'].split('/')[0], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp(),
                    'y': row['result']
                }
            )
        dataset['data'] = points
        output_data.append(dataset)

    return jsonify({
        'value': output_data
    })

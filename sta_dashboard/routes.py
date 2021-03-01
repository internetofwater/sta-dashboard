import re
from datetime import datetime
import requests
import pdb

from flask import render_template, request, jsonify
from sqlalchemy import or_, and_
import pandas as pd

from sta_dashboard import app
from sta_dashboard.models import Thing, Datastream, ObservedProperty
from sta_dashboard.utils import extract_date
    

@app.route('/')
def index():
    properties = ObservedProperty.query.with_entities(
        ObservedProperty.endpoint, ObservedProperty.name).distinct().all()
    endpoints = set([s[0] for s in properties])
    property_mapping = {}
    for edp in endpoints:
        property_mapping[edp] = []
    
    for prop in properties:
        property_mapping[prop[0]].append(prop[1])
    
    return render_template('index.html', property_mapping=property_mapping)


@app.route('/query_points', methods=['POST'])
def query_points():
    
    # regex to extract endpoint names from strings
    endpoints = re.findall(r'\w+', request.form['endpoints']) #TODO: support names that contain non-letter chars
    properties_raw = request.form['properties']
    properties = [' '.join(re.findall(r'\w+', s)) for s in properties_raw.split(',')]
    # TODO: use regex to extract datetime string
    
    # get ids of datastreams that have selected observed properties
    ds_ids = ObservedProperty.query.with_entities(
        ObservedProperty.datastreams
    ).filter(ObservedProperty.name.in_(properties)).all()
    
    ds_ids = [s[0].split(',') for s in ds_ids]
    ds_ids = [item for sublist in ds_ids for item in sublist]
    
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
                        Datastream.endpoint == endpoint,
                        Datastream.id.in_(ds_ids)
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
        Datastream.id
    ).\
        filter(Datastream.thingId == thingId).\
            all()
    
    ds_ids = [s[0] for s in query_result]
    out_ops = []
    out_ds_ids = []
    for ds in ds_ids:
        op = ObservedProperty.query.with_entities(
            ObservedProperty.name
        ).\
            filter(ObservedProperty.datastreams.contains(ds)).\
                all()
        if op:
            out_ops.append(op[0])
            out_ds_ids.append(ds)
    
    available_ds_op = [s[0] for s in out_ops]
    # available_ds = list(set([ds for qr in query_result for ds in qr]))
    
    return jsonify({
        'availableDatastreamsByProperty': available_ds_op,
        'availableDatastreamsById': out_ds_ids
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
            Datastream.id.in_(dsList)
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

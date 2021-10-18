import re
from datetime import datetime
import requests
import pdb
from zipfile import ZipFile
from io import BytesIO
from pathlib import Path
import json

from flask import render_template, request, jsonify, send_file
from sqlalchemy import or_, and_
import pandas as pd

from sta_dashboard import app
from sta_dashboard.models import Thing, Datastream, ObservedProperty
from sta_dashboard.utils import extract_date
    
with open(Path(__file__).parent / '..' / 'endpoints.json') as f:
    ENDPOINTS = json.load(f)

@app.route('/')
def index():
    endpoint_properties_pairs = ObservedProperty.query.with_entities(
        ObservedProperty.endpoint, ObservedProperty.name).distinct().all()
    
    endpoint_properties_df = pd.DataFrame.from_records(
        endpoint_properties_pairs,
        columns=['endpoint', 'properties']
        )
    
    # If there are cached endpoints which aren't selected, don't show them
    cached_endpoints = set(endpoint_properties_df.endpoint.unique())
    included_endpoints = [k for k, v in ENDPOINTS.items() if v['include']]
    intersection_endpoints = cached_endpoints.intersection(set(included_endpoints))

    endpoint_filter = endpoint_properties_df.endpoint.isin(list(intersection_endpoints))
    property_mapping = endpoint_properties_df[endpoint_filter]\
        .groupby('endpoint')['properties'].apply(list).to_dict()
    
    return render_template('index.html', property_mapping=property_mapping)


@app.route('/query_points', methods=['POST'])
def query_points():
    
    # regex to extract endpoint names from strings
    endpoints = re.findall(r'\w+', request.form['endpoints']) #TODO: support names that contain non-letter chars
    endpoints = list(set(endpoints))
    properties_raw = request.form['properties'].strip('[]')
    properties = [s.strip(r'""') for s in properties_raw.split(',')]
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
        'phenomenonStartDate', 'phenomenonEndDate', 'endpoint', 'name', 'selfLink', 'thingId', 'location_geojson'
    ]

    for endpoint in endpoints:
        
        geojson_recoding = False

        query_result = Datastream.query.with_entities(
            Datastream.phenomenonStartDate,
            Datastream.phenomenonEndDate,
            Datastream.endpoint,
            Datastream.name,
            Datastream.selfLink,
            Datastream.thingId,
            Thing.location_geojson
            ).join(Thing, Datastream.thingId==Thing.id)
        
        if queryStartDate == datetime.min and queryEndDate == datetime.max:
            query_result = query_result.filter(
                Datastream.endpoint == endpoint,
                Datastream.id.in_(ds_ids)
            ).all()
            
        else:
            
            query_result = query_result.filter(
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
            ).all()
            
        geojson_recoding = False
        if query_result:
            
            first_row_thing = query_result[0][-1]
            if 'geometry' in first_row_thing.keys():
                first_latlon = first_row_thing['geometry']['coordinates']
                geojson_recoding = True # flag for if geojson needs to be recoded
                
            else:
                first_latlon = first_row_thing['coordinates']
                
            while True:
                if not isinstance(first_latlon[0], list):
                    break
                else:
                    # Get the first lat/lon pair as the default view point
                    first_latlon = first_latlon[0]
                    
            first_latlons.append(tuple(first_latlon[::-1]))
            
        query_df = pd.DataFrame(query_result, columns=query_result_keys)
        
        if geojson_recoding:
            query_df['location_geojson'] = \
                query_df['location_geojson'].apply(lambda x: x['geometry'])
        
        unique_locations = query_df.drop_duplicates(
            'thingId')[['thingId', 'location_geojson']]
        
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
        Datastream.id, Datastream.selfLink
    ).\
        filter(Datastream.thingId == thingId).\
            all()
    
    out_ops = []
    out_ds_ids = []
    out_ds_links = []
    for ds_id, ds_link in query_result:
        op = ObservedProperty.query.with_entities(
            ObservedProperty.name
        ).\
            filter(ObservedProperty.datastreams.contains(ds_id)).\
                all()
        if op:
            out_ops.append(op[0])
            out_ds_ids.append(ds_id)
            out_ds_links.append(ds_link)
    
    available_ds_op = [s[0] for s in out_ops]
    
    return jsonify({
        'availableDatastreamsByProperty': available_ds_op,
        'availableDatastreamsById': out_ds_ids,
        'availableDatastreamsByLink': out_ds_links
    })
    
def makeAPICallUrl(selfLink, queryStartDate, queryEndDate):
    
    startDateISO = queryStartDate.isoformat() + 'Z'
    endDateISO = queryEndDate.isoformat() + 'Z'
    
    observationsUrl = '&$'.join([
        selfLink + r'/Observations?$orderby=phenomenonTime desc',
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


def query_multiple_pages(response, upperLimit=1000):
    
    total_obs_list = []
    total_obs = 0
    
    while total_obs <= upperLimit:
        obs = response.json()['value'][0]
        total_obs += obs['dataArray@iot.count']
        total_obs_list += obs['dataArray']
        
        if '@iot.nextLink' in response.json().keys():
            response = requests.get(response.json()['@iot.nextLink'])
        else:
            break
        
    total_obs_df = pd.DataFrame(
        total_obs_list, columns=obs['components']
    )
    return total_obs_df.loc[:upperLimit-1], len(total_obs_df)>=upperLimit


def query_observations(thingId, dsList, startDate, endDate):
    query_results = Datastream.query.with_entities(
        Datastream.name,
        Datastream.selfLink,
        Datastream.unitOfMeasurement
    ).\
        filter(
            Datastream.thingId == thingId,
            Datastream.id.in_(dsList)
            ).\
                all()
                
    queryStartDate, queryEndDate = \
        extract_date(startDate, endDate)
                
    output_observations = []
    unavailable_list = []
    if_truncate_list = []
    for name, selfLink, unitOfMeasurement in query_results:
        dataset = {}
        points = []

        observedPropertyUrl, observationsUrl = makeAPICallUrl(
            selfLink, queryStartDate, queryEndDate)
        
        observedPropertyResponse = requests.get(observedPropertyUrl)

        observedProperty = observedPropertyResponse.json()
        dataset['label'] = ' '.join([
            observedProperty['name'],
            '({})'.format(unitOfMeasurement['name'])
        ])
        
        observationsResponse = requests.get(observationsUrl)
                
        if not observationsResponse.json()['value']:
            unavailable_list.append(observedProperty['name'])
            continue
        
        observations_df, observations_if_truncate = query_multiple_pages(observationsResponse)
        if observations_if_truncate:
            if_truncate_list.append(observedProperty['name'])

        dataset['description'] = observedProperty['description']
        dataset['showLine'] = True
        dataset['fill'] = False
        dataset['observationsUrl'] = observationsUrl
        
        for _, row in observations_df.iterrows():
            x_timestamp = datetime.strptime(row['phenomenonTime'].split(
                '/')[0], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
            points.append(
                {
                    'x': str(x_timestamp),
                    'y': row['result']
                }
            )
        dataset['data'] = points
        output_observations.append(dataset)
        
    return output_observations, unavailable_list, if_truncate_list

@app.route('/visualize_observations', methods=['POST'])
def visualize_observations():
    thingId = request.form['thingId'][1:-1]
    dsList = [s[1:-1] for s in request.form['dsList'][1:-1].split(',')]
    
    output_data, unavailable_dict, if_truncate_list = query_observations(
        thingId, dsList, request.form['startDate'], request.form['endDate']
    )
    return jsonify({
        'value': output_data,
        'unavailables': unavailable_dict,
        'ifTruncateList': if_truncate_list
    })


@app.route('/download_observations', methods=['POST'])
def download_observations():
    thingId = request.form['thingId'][1:-1]
    dsList = [s[1:-1] for s in request.form['dsList'][1:-1].split(',')]
    
    output_data, _, _ = query_observations(
        thingId, dsList, request.form['startDate'], request.form['endDate']
    )
    
    in_memory = BytesIO()
        
    with ZipFile(in_memory, 'a') as zf:
    
        for ds in output_data:
            data_pd = pd.DataFrame.from_records(ds['data'])
            data_pd['x'] = pd.to_datetime(data_pd['x'], unit='s')
            data_pd_str = data_pd.rename(
                columns={
                    'x': 'datetime',
                    'y': ds['label']
                }
            ).to_csv(index=False)
            
            pd_filename = \
                '{}_{}_thing_{}.csv'.format(
                    '_'.join([w.lower() for w in ds['label'].split(' ')[:-1]]),
                    *thingId.split('@')[::-1]
                )
                
            zf.writestr(pd_filename, data_pd_str)
            
        # fix for Linux zip files read in Windows
        for file in zf.filelist:
            file.create_system = 0
        
    
    in_memory.seek(0)    
    return send_file(
        in_memory, 
        attachment_filename='{}_thing_{}.zip'.format(*thingId.split('@')[::-1]),
        as_attachment=True,
        mimetype='application/zip'
    )
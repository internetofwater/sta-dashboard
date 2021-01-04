import re
from datetime import datetime

from flask import render_template, request, jsonify
from sqlalchemy import or_, and_
import pandas as pd

from sta_dashboard import app
from sta_dashboard.models import Thing, Datastream
from sta_dashboard.utils import *
    

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
    if len(request.form['startDate'][1:-1]) == 0:
        queryStartDate = datetime.min
    else:
        queryStartDate = datetime.strptime(
            request.form['startDate'][1:-1], '%Y-%m-%d')
        
    if len(request.form['endDate'][1:-1]) == 0:
        queryEndDate = datetime.max
    else:
        queryEndDate = datetime.strptime(
            request.form['endDate'][1:-1], '%Y-%m-%d')
    
    # pdb.set_trace()
    
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

        thing_id_list = query_df['thingId'].unique()
        for thing_id in thing_id_list:
            group_df = query_df[query_df['thingId'] == thing_id]
            group_dict = group_df[query_result_keys[:5]].to_dict()
            for dict_key in list(group_dict.keys()):
                group_dict[dict_key] = list(group_dict[dict_key].values())
                
            group_result = {
                'latitude': group_df['latitude'].iloc[0],
                'longitude': group_df['longitude'].iloc[0],
                'thingId': group_df['thingId'].iloc[0],
                'length': len(group_dict['name']),
                'datastreams': group_dict
            }

            locations.append(group_result)

    zoom_level = 3 if len(endpoints) > 1 else 5
    if not first_latlons:
        first_latlons = [(35.99,  -78.90)]
    
    return jsonify({
        'viewLatlon': [sum(latlon) / len(latlon) for latlon in zip(*first_latlons)],
        'locations': locations,
        'zoom_level': zoom_level
    })

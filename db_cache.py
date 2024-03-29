import requests
import time
import json
import os

import pandas as pd

from sta_dashboard import db
from sta_dashboard.models import Thing, Datastream, ObservedProperty
from sta_dashboard.utils import *

with open('endpoints.json') as f:
    ENDPOINTS = json.load(f)


class Endpoint:
    def __init__(self, endpoint_name):
        self.endpoint_name = endpoint_name

        response = requests.get(ENDPOINTS[self.endpoint_name]['url'])
        entities_url = {}
        for entity in response.json()['value']:
            entities_url[entity['name']] = entity['url']

        self.entities_url = entities_url

    def get_locations_from_locations(self):

        url = self.entities_url['Locations']
        locations_list = []

        response = requests.get(url)
        while True:
            locations_list.extend(
                response.json()['value']
            )
            if '@iot.nextLink' in response.json().keys():
                    response = requests.get(response.json()['@iot.nextLink'])
            else:
                break

        return locations_list
    
    
    def get_things_and_datastreams(self):
        url = self.entities_url['Things']
        url += '?$expand=Locations($select=location),Datastreams'
        cached_things = []
        
        response = requests.get(url)
        while True:
            response_json = response.json()
            for thing in response_json['value']:
                
                if not thing['Locations'] or not thing['@iot.id']:
                    continue # skip the records that don't have location info or an iot.id
                
                for thing_key in ['name', 'description', 'Datastreams']:
                    if thing_key not in thing.keys():
                        thing[thing_key] = 'NA'
                
                cached_things.append(
                    {
                        'id': '@'.join([str(thing['@iot.id']), endpoint]),
                        'endpoint': self.endpoint_name,
                        'name': thing['name'],
                        'description': thing['description'],
                        'location_geojson': thing['Locations'][0]['location'],
                        'datastreams': thing['Datastreams']
                    }
                )
            if '@iot.nextLink' in response.json().keys():
                response = requests.get(response.json()['@iot.nextLink'])
            else:
                break
        
        cached_things_df = pd.DataFrame.from_records(cached_things)
        cached_things_df = cached_things_df.drop_duplicates(subset=['id'])
        cached_things = cached_things_df.to_dict(orient='records')
            
        return cached_things
    
    
    def get_observed_properties(self):
        url = self.entities_url['ObservedProperties']
        url += '?$expand=Datastreams($select=@iot.id)'
        cached_ops = []
        
        response = requests.get(url)
        while True:
            response_json = response.json()
            for op in response_json['value']:

                if not op['Datastreams']:
                    continue

                ds_list = ','.join(
                    ['@'.join([str(list(v.values())[0]), endpoint]) for v in op['Datastreams']])

                if 'Datastreams@iot.nextLink' in op.keys():
                    next_resp = requests.get(op['Datastreams@iot.nextLink'])
                    next_ds = next_resp.json()['value']
                    ds_list = \
                        ','.join([ds_list, ','.join(['@'.join([str(list(v.values())[0]), endpoint])
                                                     for v in next_ds])])

                    while '@iot.nextLink' in next_resp.json().keys():
                        next_resp = requests.get(
                            next_resp.json()['@iot.nextLink'])
                        next_ds = next_resp.json()['value']
                        ds_list = \
                            ','.join([ds_list, ','.join(['@'.join([str(list(v.values())[0]), endpoint])
                                                         for v in next_ds])])

                cached_ops.append(
                    {
                        'id': '@'.join([str(op['@iot.id']), endpoint]),
                        'endpoint': endpoint,
                        'name': op['name'],
                        'description': op['description'],
                        'definition': op['definition'],
                        'datastreams': ds_list
                    }
                )
            if '@iot.nextLink' in response.json().keys():
                response = requests.get(response.json()['@iot.nextLink'])
            else:
                break
        
        cached_ops_df = pd.DataFrame.from_records(cached_ops)
        cached_ops_df = cached_ops_df.drop_duplicates(subset=['id'])
        cached_ops = cached_ops_df.to_dict(orient='records')    
        
        return cached_ops


if __name__ == '__main__':

    if os.environ['DROP_ALL'].title() == "True" or \
        not os.path.exists(os.path.join('sta_dashboard', 'data', os.environ['SQLITE_DB_FILENAME'])):
        db.drop_all()
        db.create_all()
        endpoints_to_cache = ENDPOINTS

    else:
        cached_endpoints = \
            [t[0] for t in Thing.query.with_entities(Thing.endpoint).distinct().all()]
        selected_endpoints = \
            [k for k, v in ENDPOINTS.items() if v['include']]
        endpoints_to_cache = \
            {k: ENDPOINTS[k] 
             for k in list(set(selected_endpoints) - set(cached_endpoints))
             if ENDPOINTS[k]['include']
             }
    
    for endpoint, endpoint_values in list(endpoints_to_cache.items()):
        
        if not endpoint_values['include']:
            continue
        
        print('{}...'.format(endpoint))
        start_timestamp = time.time()
        edp = Endpoint(endpoint)
        
        print('Caching things and datastreams...')
        cached_things = edp.get_things_and_datastreams()
        print('Caching observed properties...')
        cached_ops = edp.get_observed_properties()

        # Insert thing and datastream rows
        for thing in cached_things:
            
            new_thing_row = Thing(**thing)
            new_thing_row.datastreams = \
                ','.join(['@'.join([str(ds['@iot.id']), endpoint]) for ds in thing['datastreams']])
            db.session.add(new_thing_row)

            ds_ids = []
            # Add datastream rows
            for ds in thing['datastreams']:
                
                # 'phenomenonTime' and 'resultTime' are optional properties
                if 'phenomenonTime' in ds.keys() and ds['phenomenonTime']:
                    phenomenonStartDate, phenomenonEndDate = \
                        [convert_date(d) for d in ds['phenomenonTime'].split('/')]
                else:
                    phenomenonStartDate, phenomenonEndDate = None, None
                    
                if str(ds['@iot.id']) in ds_ids:
                    continue
                ds_ids.append(str(ds['@iot.id']))
                    
                new_datastream_row = Datastream(
                    id='@'.join([str(ds['@iot.id']), endpoint]),
                    endpoint=endpoint,
                    name=ds['name'],
                    description=ds['description'],
                    observationType=ds['observationType'],
                    unitOfMeasurement=ds['unitOfMeasurement'],
                    phenomenonStartDate=phenomenonStartDate,
                    phenomenonEndDate=phenomenonEndDate,
                    selfLink=ds['@iot.selfLink'],
                    thingId=new_thing_row.id
                )
                db.session.add(new_datastream_row)
            
        # Insert observed property rows
        for op in cached_ops:
            new_op_row = ObservedProperty(**op)
            db.session.add(new_op_row)
        
        print('{} finished within {:.2f} seconds'.format(endpoint, time.time() - start_timestamp))

    db.session.commit()

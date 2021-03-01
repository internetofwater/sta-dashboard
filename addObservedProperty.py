import requests
import time

from sqlalchemy import create_engine

from sta_dashboard import db
from sta_dashboard.models import Thing, Datastream, ObservedProperty
from sta_dashboard.utils import *

ENDPOINTS = {
    'internetofwater': 'https://sta-demo.internetofwater.dev/api/v1.1',
    # 'taiwan': 'https://sta.ci.taiwan.gov.tw/STA_AirQuality_EPAIoT/v1.1',
    'newmexicowaterdata': 'https://st.newmexicowaterdata.org/FROST-Server/v1.1',
    'datacove': 'https://service.datacove.eu/AirThings/v1.1/'
}


if __name__ == '__main__':
    
    ObservedProperty.__table__.drop(db.session.bind)
    ObservedProperty.__table__.create(db.session.bind)
    
    for endpoint in list(ENDPOINTS.keys()):
        print('{}...'.format(endpoint), end='')
        start_timestamp = time.time()
        base_url = ENDPOINTS[endpoint]
        url = base_url + '/ObservedProperties?$expand=Datastreams($select=@iot.id)'
        cached_ops = []
        
        response = requests.get(url)
        while True:
            response_json = response.json()
            for op in response_json['value']:
                
                if not op['Datastreams']:
                    continue
                
                ds_list = ','.join(['@'.join([str(list(v.values())[0]), endpoint]) for v in op['Datastreams']])
                                   
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
                time.sleep(1)
                response = requests.get(response.json()['@iot.nextLink'])
            else:
                break
            
        print('finished within {:.2f} seconds'.format(
            time.time() - start_timestamp))
        
        for op in cached_ops:
            new_op_row = ObservedProperty(**op)
            db.session.add(new_op_row)
        
    db.session.commit()

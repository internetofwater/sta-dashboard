import pickle
import requests
import time

from sta_dashboard import db
from sta_dashboard.models import Location, Thing

ENDPOINTS = {
    'internetofwater': 'https://sta-demo.internetofwater.dev/api/v1.1',
    'taiwan': 'https://sta.ci.taiwan.gov.tw/STA_AirQuality_EPAIoT/v1.1',
    'newmexicowaterdata': 'https://st.newmexicowaterdata.org/FROST-Server/v1.1',
    'datacove': 'https://service.datacove.eu/AirThings/v1.1/'
}


class Endpoint:
    def __init__(self, endpoint_name):
        self.endpoint_name = endpoint_name

        response = requests.get(ENDPOINTS[self.endpoint_name])
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
                try:
                    response = requests.get(response.json()['@iot.nextLink'])
                except requests.exceptions.ConnectionError:
                    time.sleep(5)
                    continue
            else:
                break

        return locations_list
    
    def cache_from_things(self):
        url = self.entities_url['Things']
        url += '?$expand=Locations($select=location),Datastreams'
        cached_things = []
        
        response = requests.get(url)
        while True:
            response_json = response.json()
            for thing in response_json['value']:
                cached_things.append(
                    (
                        thing['@iot.id'],
                        thing['name'],
                        thing['description'],
                        thing['Locations'][0]['location']['coordinates'][::-1],
                        thing['Datastreams']
                    )
                )
            if '@iot.nextLink' in response.json().keys():
                try:
                    response = requests.get(response.json()['@iot.nextLink'])
                except requests.exceptions.ConnectionError:
                    time.sleep(5)
                    continue
            else:
                break
            
        return cached_things


if __name__ == '__main__':

    db.drop_all()
    db.create_all()

    # for endpoint in list(ENDPOINTS.keys()):
    #     print('{}...'.format(endpoint), end='')
    #     tmp = Endpoint(endpoint)
    #     locations_list = tmp.get_locations()

    #     for location in locations_list:
    #         location = Location(
    #             endpoint=endpoint,
    #             name=location['name'],
    #             description=location['description'],
    #             # properties=pickle.dumps(location['properties']),
    #             encodingtype=location['encodingType'],
    #             longitude=location['location']['coordinates'][0],
    #             latitude=location['location']['coordinates'][1],
    #             iotid=location['@iot.id']
    #         )
    #         db.session.add(location)
        
    #     print('finished')
        
    # db.session.commit()
    
    for endpoint in list(ENDPOINTS.keys()):
        print('{}...'.format(endpoint), end='')
        start_timestamp = time.time()
        edp = Endpoint(endpoint)
        cached_things = edp.cache_from_things()

        for thing in cached_things:
            new_thing = Thing(
                endpoint=endpoint,
                iotid=thing[0],
                name=thing[1],
                description=thing[2],
                latitude=thing[3][0],
                longitude=thing[3][1],
                datastreams=thing[-1],
            )
            db.session.add(new_thing)

        print('finished within {:.2f} seconds'.format(time.time() - start_timestamp))

    db.session.commit()


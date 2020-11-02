import pickle
import requests

from sta_dashboard import db
from sta_dashboard.models import Location

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

    def get_locations(self):

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


db.drop_all()
db.create_all()

for endpoint in list(ENDPOINTS.keys()):
    tmp = Endpoint(endpoint)
    locations_list = tmp.get_locations()

    for location in locations_list:
        location = Location(
            endpoint=endpoint,
            name=location['name'],
            description=location['description'],
            # properties=pickle.dumps(location['properties']),
            encodingtype=location['encodingType'],
            longitude=location['location']['coordinates'][0],
            latitude=location['location']['coordinates'][1],
            iotid=location['@iot.id']
        )
        db.session.add(location)
db.session.commit()


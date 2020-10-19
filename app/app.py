from flask import Flask, render_template
import requests

app = Flask(__name__)

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
        
    @property
    def locations(self):
        
        url = self.entities_url['Locations']
        locations_list = []
        
        response = requests.get(url)
        while True:
            locations_list.extend(
                response.json()['value']
            )
            if not '@iot.nextLink' in response.json().keys():
                break
        
        return locations_list
    
    @property
    def locations_latlon(self):
        
        locations_latlon_list = []
        for location in self.locations:
            locations_latlon_list.append(
                ['iot.id: {}'.format(location['@iot.id']), 
                 *location['location']['coordinates'][::-1]]
            )

        return locations_latlon_list
        

@app.route('/<string:endpoint_name>')
def index(endpoint_name):
    endpoint = Endpoint(endpoint_name)
    locations_latlon = endpoint.locations_latlon
    return render_template('index.html', locations_latlon=locations_latlon)


if __name__ == '__main__':
    app.run(debug=True)

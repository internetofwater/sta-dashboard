from flask import render_template, request

from sta_dashboard import app
from sta_dashboard.models import Location, Thing

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        endpoints = request.form.getlist('endpoint')
        
        locations = []
        for endpoint in endpoints:
            locations.append(
                Thing.query.with_entities(Thing.latitude, Thing.longitude).filter(
                    Thing.endpoint == endpoint).all()
                )
            
        import pdb; pdb.set_trace()
        zoom_level = 3 if len(endpoints) > 1 else 5
        return render_template('index.html', locations=locations, zoom_level=zoom_level)
    
    locations = Thing.query.with_entities(Thing.latitude, Thing.longitude).filter(
        Thing.endpoint == 'internetofwater').all()
    return render_template('index.html', locations=locations, zoom_level=5)

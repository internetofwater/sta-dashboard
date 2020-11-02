from flask import render_template, request

from sta_dashboard import app
from sta_dashboard.models import Location

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        endpoints = request.form.getlist('endpoint')
        
        locations = []
        for endpoint in endpoints:
            locations.extend(
                Location.query.filter(
                    Location.endpoint == endpoint).limit(500).all()
                )
            
        zoom_level = 3 if len(endpoints) > 1 else 5
        return render_template('index.html', locations=locations, zoom_level=zoom_level)
    
    locations = Location.query.filter(
        Location.endpoint == 'internetofwater').limit(500).all()
    return render_template('index.html', locations=locations, zoom_level=5)

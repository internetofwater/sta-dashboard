from flask import render_template

# Own modules
from sta_dashboard import app
from sta_dashboard.models import Location

@app.route('/', methods=['GET', 'POST'])
def index():
    locations = Location.query.limit(50).all()
    return render_template('index.html', locations=locations)

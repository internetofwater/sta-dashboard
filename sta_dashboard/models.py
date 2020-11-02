from sta_dashboard import db

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    encodingtype = db.Column(db.String, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    iotid = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return 'name: {}; location coordinates: {}, {}; iot.id: {}'.format(
            self.name, self.latitude, self.longitude, self.iotid)
    
    
    

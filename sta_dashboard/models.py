from sta_dashboard import db
from sqlalchemy.dialects.postgresql import JSON
    
    
class Thing(db.Model):
    __tablename__ = 'thing'
    id = db.Column(db.String, primary_key=True)
    endpoint = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    location_geojson = db.Column(JSON, nullable=False)
    datastreams = db.Column(db.String, nullable=False)

    def __repr__(self):
        return 'endpoint: {}; name: {}; description: {}; iot.id: {}'.format(
            self.endpoint, self.name, self.description, self.iotid)
        
        
class Datastream(db.Model):
    __tablename__ = 'datastream'
    id = db.Column(db.String, primary_key=True)
    endpoint = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    observationType = db.Column(db.String, nullable=False)
    unitOfMeasurement = db.Column(db.JSON, nullable=False)
    phenomenonStartDate = db.Column(db.DateTime)
    phenomenonEndDate = db.Column(db.DateTime)
    selfLink = db.Column(db.String, nullable=False)
    thingId = db.Column(db.String, nullable=False)
    
    def __repr__(self):
        return 'endpoint: {}; name: {}; description: {}; iot.id: {}'.format(
            self.endpoint, self.name, self.description, self.iotid)

class ObservedProperty(db.Model):
    __tablename__ = 'observed_property'
    id = db.Column(db.String, primary_key=True)
    endpoint = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    definition = db.Column(db.String, nullable=False)
    datastreams = db.Column(db.String, nullable=False)
    
    def __repr__(self):
        return 'endpoint: {}; name: {}; description: {}; iot.id: {}'.format(
            self.endpoint, self.name, self.description, self.iotid)

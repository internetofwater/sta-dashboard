from sta_dashboard import db

# class Location(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     endpoint = db.Column(db.String, nullable=False)
#     name = db.Column(db.String, nullable=False)
#     description = db.Column(db.String, nullable=False)
#     encodingtype = db.Column(db.String, nullable=False)
#     longitude = db.Column(db.Float, nullable=False)
#     latitude = db.Column(db.Float, nullable=False)
#     iotid = db.Column(db.Integer, nullable=False)
    
#     def __repr__(self):
#         return 'endpoint: {}; name: {}; location coordinates: {}, {}; iot.id: {}'.format(
#             self.endpoint, self.name, self.latitude, self.longitude, self.iotid)
    
    
class Thing(db.Model):
    id = db.Column(db.String, primary_key=True)
    endpoint = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    iotid = db.Column(db.Integer, nullable=False)
    
    datastream = db.relationship('Datastream', backref='thingOfDatastream', lazy=True)

    def __repr__(self):
        return 'endpoint: {}; name: {}; description: {}; iot.id: {}'.format(
            self.endpoint, self.name, self.description, self.iotid)
        
        
class Datastream(db.Model):
    id = db.Column(db.String, primary_key=True)
    endpoint = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    observationType = db.Column(db.String, nullable=False)
    unitOfMeasurement = db.Column(db.JSON, nullable=False)
    iotid = db.Column(db.Integer, nullable=False)
    phenomenonStartDate = db.Column(db.DateTime)
    phenomenonEndDate = db.Column(db.DateTime)
    resultStartDate = db.Column(db.DateTime)
    resultEndDate = db.Column(db.DateTime)
    selfLink = db.Column(db.String, nullable=False)
    
    thingId = db.Column(db.String, db.ForeignKey('thing.id'), nullable=False)

    def __repr__(self):
        return 'endpoint: {}; name: {}; description: {}; iot.id: {}'.format(
            self.endpoint, self.name, self.description, self.iotid)

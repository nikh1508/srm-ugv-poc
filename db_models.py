from app import db
from app import ma


class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    loc_type = db.Column(db.String(10), nullable=False)
    pretty_name = db.Column(db.String(50))
    description = db.Column(db.String(100))

    def __init__(self, latitude, longitude, loc_type, pretty_name='', description=''):
        self.latitude = latitude
        self.longitude = longitude
        self.loc_type = loc_type
        self.pretty_name = pretty_name
        self.description = description

# class LocationSchema(ma.ModelSchema):
#     class Meta:
#         model = Location
#         sqla_session = db.session


class LocationSchema(ma.Schema):
    class Meta:
        fields = ('id',  'latitude', 'longitude',
                  'loc_type', 'pretty_name', 'description')


location_schema = LocationSchema()
locations_schema = LocationSchema(many=True)

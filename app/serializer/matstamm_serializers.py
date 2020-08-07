from flask_restplus import fields
from flask_restplus.model import Model
from sqlalchemy import func


class NullableString(fields.String):
    __schema_type__ = ['string', 'null']
    __schema_example__ = 'nullable string'


class NullableInteger(fields.Integer):
    __schema_type__ = ['integer', 'null']
    __schema_example__ = 1


class NullableFloat(fields.Float):
    __schema_type__ = ['number', 'null']
    __schema_example__ = 1.1

"""
    id = db.Column(db.Integer, primary_key=True)
    turbine_new = db.Column(db.String(250), nullable=False)
    turbine_alt = db.Column(db.String(250), nullable=False)
    stufe = db.Column(db.String(100), nullable=False)
    prozessmatstamm = db.Column(db.String(100), nullable=False, unique=True)
    technologie = db.Column(db.String(250), nullable=False)
    beschichtung = db.Column(db.String(250), nullable=False)
    werkstoff = db.Column(db.String(250), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_updated = db.Column(db.DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now())
"""

matstamm_serializer = Model('matstamm_serializer', {
    'id':  fields.Integer(description='Matstamm id', readonly=True),
    'turbine_new': fields.String(description='Neuer Name der Turbine', required=True),
    'turbine_alt': fields.String(description='Alter Name der Turbine', required=True),
    'stufe': fields.String(description='Schaufelart', required=True),
    'prozessmatstamm': fields.String(description='Materialstamm', required=True),
    'technologie': fields.Integer(description='Art der Technologie'),
    'beschichtung': fields.String(description='Art der Beschichtung'),
    'werkstoff': fields.String(description='Werkstoff')
})

update_matstamm_serializer = matstamm_serializer.clone("update_matstamm_serializer")
update_matstamm_serializer['prozessmatstamm'].required = False
update_matstamm_serializer['id'].readonly = False

anlegen_matstamm_serializer = matstamm_serializer.clone("anlegen_matstamm_serializer")
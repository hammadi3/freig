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


freigabe_serializer = Model('freigabe_serializer', {
    'id':  fields.Integer(description='Freigabe id', readonly=True),
    'name': fields.String(description='Name der Freigabe', required=True),
    'Auflagen': fields.Boolean(description='Auflagen true oder false', required=True),
    'Freigabeart': fields.String(description='auftragsbezogen, gültig oder gesperrt etc..', required=True),
    'Auslaufdatum': fields.Date(description='3 Jahre nach dem Freigabedatum', required=True),
    'Freigabe_gültig_für_n_Ansätze': fields.Integer(description='Anzahl der Ansätze, für die die Freigabe noch gültig ist'),
    'Bemerkung': fields.String(description='Beschreibungstext der Freigabe'),
    'Fertigungsaufträge': fields.String(description='Fertigungsaufträgenummern'),
    'last_updated': fields.DateTime(description='Date of update', readonly=True),
    'last_updated_by': NullableString(description='Updated by', example='Aladin')
})

update_freigabe_serializer = freigabe_serializer.clone("update_freigabe_serializer")
update_freigabe_serializer['name'].required = False
update_freigabe_serializer['id'].readonly = False

anlegen_freigabe_serializer = freigabe_serializer.clone("anlegen_freigabe_serializer")
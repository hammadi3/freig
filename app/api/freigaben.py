from flask_restplus import Namespace, Resource, fields, inputs, reqparse
from flask_restplus.errors import abort
from flask import request
from app.core.errors import exception_to_response
from app.model.freigabe import Freigabe
from datetime import datetime
from app.db import db
from app.serializer.freigabe_serializers import freigabe_serializer, update_freigabe_serializer

api = Namespace('Freigabe Operationen', description='API fürs Anlegen/Bearbeiten und Anzeigen der Freigaben ',
                path="/freigabe")

api.models[freigabe_serializer.name] = freigabe_serializer
api.models[update_freigabe_serializer.name] = update_freigabe_serializer

freigabe_name_parser = reqparse.RequestParser()
freigabe_name_parser.add_argument('Freigabe', help="freigabe name", required=True)

query_freigabe_parser = reqparse.RequestParser()
query_freigabe_parser.add_argument('id')
query_freigabe_parser.add_argument('name')

freigabe_parser = reqparse.RequestParser()
freigabe_parser.add_argument('name', required=True, help='Name der Freigabe')
freigabe_parser.add_argument('Auflagen')
freigabe_parser.add_argument('Freigabeart')
freigabe_parser.add_argument('Auslaufdatum')
freigabe_parser.add_argument('Fertigungsaufträge')


@api.route('/', strict_slashes=False)
@api.response(400, 'Validation Error')
class Freigaben(Resource):
    @exception_to_response
    @api.expect([freigabe_serializer], validate=True)
    @api.marshal_list_with(freigabe_serializer, skip_none=True)
    @api.response(200, 'created successfully')
    def post(self):
        """
        Freigabeliste wird in die Datenbank hinzugefügt
        """
        freigabe_info = request.json
        inserted_freigaben = []
        for freigabe in freigabe_info:
            inserted_freigabe = Freigabe.create(freigabe_dict=freigabe)
            inserted_freigaben.append(inserted_freigabe)
        return inserted_freigaben

    @exception_to_response
    @api.expect(update_freigabe_serializer, validate=True)
    @api.marshal_with(freigabe_serializer, skip_none=True)
    @api.response(200, 'Updated successfully')
    def put(self):
        """
        Freigabe bearbeiten
        """
        freigabe_info = request.json
        freigabe_info['last_updated'] = datetime.utcnow()
        freigabe = Freigabe.find_by_id(freigabe_info['id'])
        if freigabe is None:
            abort(400, message='error.freigabe_bearbeiten')
        freigabe.update(data=freigabe_info)
        return freigabe

    @exception_to_response
    @api.expect(query_freigabe_parser)
    @api.marshal_list_with(freigabe_serializer, skip_none=True)
    def get(self):
        """
        Freigabe anzeigen
        """
        query = query_freigabe_parser.parse_args()
        clean_query = {k: v for k, v in query.items() if v is not None}

        db_query = db.session.query(Freigabe)
        for key in clean_query:
            db_query = db_query.filter(getattr(Freigabe, key) == clean_query[key])
        # now we can run the query
        results = db_query.all()
        return results


@api.route('/add', strict_slashes=False)
@api.response(400, 'Validation Error')
class FreigabeAdd(Resource):
    @exception_to_response
    @api.expect(freigabe_parser, validate=True)
    @api.marshal_list_with(freigabe_serializer, skip_none=True)
    @api.response(200, 'created successfully')
    def post(self):
        """
        Freigabe anlegen
        """
        freigabe_dict = freigabe_parser.parse_args()

        freigabe = Freigabe(**freigabe_dict).insert()

        return freigabe


@api.route('/<int:id>', strict_slashes=False)
class FreigabesById(Resource):
    @exception_to_response
    @api.marshal_with(freigabe_serializer, skip_none=True)
    def get(self, id):
        """
        Freigabe mittels Datenbank_ID suchen
        """
        return Freigabe.find_by_id(id)

    def delete(self, id):
        """
        Freigabe mittels Datenbank_ID löschen
        """
        Freigabe.delete_by_id(id)
        return "Freigabe gelöscht", 200

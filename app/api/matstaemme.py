from flask_restplus import Namespace, Resource, fields, inputs, reqparse
from flask_restplus.errors import abort
from flask import request
from app.core.errors import exception_to_response
from app.model.matstamm import Matstamm
from datetime import datetime
from app.db import db
from app.serializer.matstamm_serializers import matstamm_serializer, update_matstamm_serializer

api = Namespace('Materialstämme Operationen', description='API fürs Anlegen/Bearbeiten und Anzeigen der Materialstämme ',
                path="/matstamm")

api.models[matstamm_serializer.name] = matstamm_serializer
api.models[update_matstamm_serializer.name] = update_matstamm_serializer

matstamm_name_parser = reqparse.RequestParser()
matstamm_name_parser.add_argument('Matstamm', help="matstamm name", required=True)

query_matstamm_parser = reqparse.RequestParser()
query_matstamm_parser.add_argument('id')
query_matstamm_parser.add_argument('prozessmatstamm')

matstamm_parser = reqparse.RequestParser()
matstamm_parser.add_argument('prozessmatstamm', required=True, help='Matstamm')
matstamm_parser.add_argument('turbine_new')
matstamm_parser.add_argument('turbine_alt')
matstamm_parser.add_argument('stufe')
matstamm_parser.add_argument('beschichtung')
matstamm_parser.add_argument('werkstoff')



@api.route('/', strict_slashes=False)
@api.response(400, 'Validation Error')
class Matstammn(Resource):
    @exception_to_response
    @api.expect([matstamm_serializer], validate=True)
    @api.marshal_list_with(matstamm_serializer, skip_none=True)
    @api.response(200, 'created successfully')
    def post(self):
        """
        Matstammliste wird in die Datenbank hinzugefügt
        """
        matstamm_info = request.json
        inserted_matstaemme = []
        for matstamm in matstamm_info:
            inserted_matstamm = Matstamm.create(matstamm_dict=matstamm)
            inserted_matstaemme.append(inserted_matstamm)
        return inserted_matstaemme

    @exception_to_response
    @api.expect(update_matstamm_serializer, validate=True)
    @api.marshal_with(matstamm_serializer, skip_none=True)
    @api.response(200, 'Updated successfully')
    def put(self):
        """
        Matstamm bearbeiten
        """
        matstamm_info = request.json
        matstamm_info['last_updated'] = datetime.utcnow()
        matstamm = Matstamm.find_by_id(matstamm_info['id'])
        if matstamm is None:
            abort(400, message='error.matstamm_bearbeiten')
        matstamm.update(data=matstamm_info)
        return matstamm

    @exception_to_response
    @api.expect(query_matstamm_parser)
    @api.marshal_list_with(matstamm_serializer, skip_none=True)
    def get(self):
        """
        Matstamm anzeigen
        """
        query = query_matstamm_parser.parse_args()
        clean_query = {k: v for k, v in query.items() if v is not None}

        db_query = db.session.query(Matstamm)
        for key in clean_query:
            db_query = db_query.filter(getattr(Matstamm, key) == clean_query[key])
        # now we can run the query
        results = db_query.all()
        return results


@api.route('/add', strict_slashes=False)
@api.response(400, 'Validation Error')
class MatstammAdd(Resource):
    @exception_to_response
    @api.expect(matstamm_parser, validate=True)
    @api.marshal_list_with(matstamm_serializer, skip_none=True)
    @api.response(200, 'created successfully')
    def post(self):
        """
        Matstamm anlegen
        """
        matstamm_dict = matstamm_parser.parse_args()

        matstamm = Matstamm(**matstamm_dict).insert()

        return matstamm


@api.route('/<int:id>', strict_slashes=False)
class MatstammsById(Resource):
    @exception_to_response
    @api.marshal_with(matstamm_serializer, skip_none=True)
    def get(self, id):
        """
        Matstamm mittels Datenbank_ID suchen
        """
        return Matstamm.find_by_id(id)

    def delete(self, id):
        """
        Matstamm mittels Datenbank_ID löschen
        """
        Matstamm.delete_by_id(id)
        return "Matstamm gelöscht", 200

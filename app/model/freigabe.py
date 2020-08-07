import datetime
import logging

import requests
from flask_restplus.errors import abort
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.types import Enum

from app.db import db
from app.model.support.model_support import ModelSupport
log = logging.getLogger(__name__)



class Freigabe(db.Model, ModelSupport):
    __tablename__ = 'freigabe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False, unique=True)
    Auflagen = db.Column(db.Boolean, default=False, nullable=False)
    Freigabeart = db.Column(db.String(250))
    Auslaufdatum = db.Column(db.DateTime, nullable=False)
    Freigabe_gültig_für_n_Ansätze = db.Column(db.Integer)
    Bemerkung = db.Column(db.String(1000))
    Fertigungsaufträge = db.Column(db.String(500))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_updated = db.Column(db.DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now())
    last_updated_by = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return '<Freigabe id:{} text:{}>'.format(self.id, self.Freigabe)

    @staticmethod
    def find_by_id(freigabe_id):
        assert (freigabe_id is not None), "Freigabe id shouldn't be null"
        freigabe = Freigabe.query.get(freigabe_id)
        return freigabe

    @staticmethod
    def delete_by_id(id):
        Freigabe.query.get(id).delete()
        db.session.commit()

    @staticmethod
    def create(freigabe_dict=None, freigabe_obj=None):
        if freigabe_dict:
            try:
                return Freigabe(**freigabe_dict).insert()
            except IntegrityError as e:
                if e.orig.__class__.__name__ == "UniqueViolation":
                    abort(400, message='error.create_user.already_exist')
                else:
                    raise e
        else:
            return freigabe_obj.insert()

    @staticmethod
    def upsert(freigabe_dict):
        freigabe = Freigabe.find_by_id(freigabe_dict['id'])
        if freigabe is not None:
            freigabe.update(freigabe_dict)
            return "update"
        else:
            freigabe_clean_dict = {}
            for key, value in freigabe_dict.items():
                if hasattr(Freigabe, key):
                    freigabe_clean_dict[key] = value
            Freigabe(**freigabe_clean_dict).insert()
            return "insert"

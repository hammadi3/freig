import logging

from sqlalchemy import func

from app.db import db
from app.model.support.model_support import ModelSupport
from flask_restplus.errors import abort
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.schema import ForeignKey

log = logging.getLogger(__name__)


class Matstamm(db.Model, ModelSupport):
    __tablename__ = 'materialstamm'
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

    def __repr__(self):
        return '<Alias id:{} text:{}>'.format(self.id, self.text)

    @staticmethod
    def find_by_aid(mts_id):
        assert (mts_id is not None), "Matstamm id shouldn't be null"
        mts = Matstamm.query.get(mts_id)
        return mts

    @staticmethod
    def create(mts_dict=None, mts_obj=None):
        if mts_dict:
            try:
                return Matstamm(**mts_dict).insert()
            except IntegrityError as e:
                if e.orig.__class__.__name__ == "UniqueViolation":
                    abort(400, message='error.create_alias.already_exist')
                else:
                    raise e
        else:
            return mts_obj.insert()

    @staticmethod
    def delete_by_prozessmatstamm(id):
        Matstamm.query.get(id).delete()
        db.session.commit()

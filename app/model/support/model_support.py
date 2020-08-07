from sqlalchemy.inspection import inspect

from app.db import db
from datetime import datetime


class ModelSupport(object):

    # fix me to serialize datatime properly
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

    def set_properties(self, dict=None):
        if dict is not None:
            for key, value in dict.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        return self

    def as_dict(self):
        return {c.key: getattr(self, c.key)
                for c in inspect(self).mapper.column_attrs}

    def update(self, data=None):
        if data:
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self.last_updated = datetime.utcnow()
            db.session.add(self)
            db.session.commit()
        else:
            self.last_updated = datetime.utcnow()
            db.session.add(self)
            db.session.commit()

    def insert(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

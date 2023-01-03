import datetime
import uuid

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

db = SQLAlchemy()
bcrypt = Bcrypt()


def generate_public_id():
    return str(uuid.uuid4())


def save_bulk(data):
    db.session.bulk_save_objects(data)
    db.session.flush()
    db.session.commit()


def delete(data):
    try:
        db.session.delete(data)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
    except SQLAlchemyError:
        db.session.rollback()


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_on = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())

    def save(self):
        try:
            db.session.add(self)
            db.session.flush()
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        except SQLAlchemyError:
            db.session.rollback()

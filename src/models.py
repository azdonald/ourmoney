import datetime
import uuid

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()


def generate_public_id():
    return str(uuid.uuid4())


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(100))
    public_id = db.Column(db.String(100), unique=True, default=generate_public_id)
    email_verified = db.Column(db.Boolean, default=False)
    account_linked = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_on = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())
    accounts = db.relationship('Account', backref=db.backref('user_account', lazy=True))

    @property
    def password(self):
        raise AttributeError('Write only field')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def as_dict(self):
        return {'id': self.id, 'public_id': self.public_id, 'firstname': self.firstname, 'lastname': self.lastname,
                'email': self.email}

    def __repr__(self):
        return "<User '{} {} {}' ".format(self.firstname, self.lastname, self.public_id)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.String(255))
    name = db.Column(db.String(255))
    mask = db.Column(db.String(100))
    type = db.Column(db.String(50))
    subtype = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance = db.relationship('Balance', backref=db.backref('account', lazy=True))
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_on = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())


class Balance(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    current = db.Column(db.Float)
    available = db.Column(db.Float)
    limit = db.Column(db.Float)
    currency_code = db.Column(db.String(3))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_on = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    institution_id = db.Column(db.String(50), unique=True)
    accounts = db.relationship('Account', backref=db.backref('accounts', lazy=True))


class BankAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(255), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_on = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())


# class Transaction(db.Model):
#     pass

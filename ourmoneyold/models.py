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
    account_id = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255))
    mask = db.Column(db.String(100))
    type = db.Column(db.String(50))
    subtype = db.Column(db.String(50))
    current = db.Column(db.Float, nullable=True)
    available = db.Column(db.Float, nullable=True)
    limit = db.Column(db.Float, nullable=True)
    currency_code = db.Column(db.String(3), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    transactions = db.relationship('Transaction', backref=db.backref('accounts', lazy=True))
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_on = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    institution_id = db.Column(db.String(50), unique=True)
    accounts = db.relationship('Account', backref=db.backref('accounts', lazy=True))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))


class BankAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(255), unique=True)
    item_id = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_on = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.String(255))
    amount = db.Column(db.Float)
    name = db.Column(db.String(255))
    authorized_date = db.Column(db.String(20), nullable=True)
    date = db.Column(db.Date)
    type = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    currency_code = db.Column(db.String(3), nullable=True)
    unofficial_currency_code = db.Column(db.String(10), nullable=True)
    payment_channel = db.Column(db.String(50))
    pending = db.Column(db.Boolean)
    account_id = db.Column(db.String(255), db.ForeignKey('account.account_id'), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_on = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    expected_expenditure = db.Column(db.Float)
    expected_income = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_on = db.Column(db.DateTime, default=datetime.date.today())
    updated_on = db.Column(db.DateTime, onupdate=datetime.date.today())
    details = db.relationship('BudgetDetails', backref=db.backref('budget', lazy=True))


class BudgetDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Float)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_on = db.Column(db.Date, default=datetime.datetime.utcnow())
    updated_on = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow())

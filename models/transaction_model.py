from models import BaseModel, db
from models.account_model import Account
from models.user_model import User

from datetime import datetime
from sqlalchemy.sql import func

PER_PAGE = 15
PAGE = 1


class Transaction(BaseModel):
    transaction_id = db.Column(db.String(255), unique=True)
    amount = db.Column(db.Float)
    name = db.Column(db.String(255))
    authorized_date = db.Column(db.String(20), nullable=True)
    date = db.Column(db.Date)
    type = db.Column(db.Integer)
    currency_code = db.Column(db.String(3), nullable=True)
    unofficial_currency_code = db.Column(db.String(10), nullable=True)
    payment_channel = db.Column(db.String(50))
    pending = db.Column(db.Boolean)
    account_id = db.Column(db.String(255), db.ForeignKey('account.account_id'), nullable=False)

    @classmethod
    def search(cls, search_params, user_id: int):
        transactions = cls.query.filter(Transaction.name.like(search_params)) \
            .join(Account, Account.account_id == Transaction.account_id) \
            .join(User, Account.user_id == User.id).filter_by(id=user_id).all()
        return transactions

    @classmethod
    def get(cls, user_id: int, page, per_page=15, **kwargs):
        query = cls.query.join(Account, Account.account_id == Transaction.account_id) \
            .join(User, Account.user_id == User.id).filter_by(id=user_id)
        if 'start_date' in kwargs:
            start_date = datetime.strptime(kwargs.get('start_date'), '%Y-%m-%d')
            query = query.filter(Transaction.date >= start_date)
        if 'end_date' in kwargs:
            end_date = datetime.strptime(kwargs.get('end_date'), '%Y-%m-%d')
            query = query.filter(Transaction.date <= end_date)
        page, per_page = PAGE, PER_PAGE
        if 'page' in kwargs:
            page = kwargs.get('page')
        if 'per_page' in kwargs:
            per_page = kwargs.get('per_page')
        transactions = query.order_by(Transaction.date.desc()).paginate(
            page,
            per_page,
            False)
        return transactions

    @classmethod
    def get_by_transaction_id(cls, transaction_id):
        return cls.query.filter_by(transaction_id=transaction_id).first()

    @classmethod
    def get_by_date(cls, user_id: int, start_date='2021-06-20', end_date='2021-06-29', page=1, per_page=15):
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        transactions = cls.query.join(Account, Account.account_id == Transaction.account_id) \
            .join(User, Account.user_id == User.id).filter_by(id=user_id).filter(Transaction.date >= start). \
            filter(Transaction.date <= end).order_by(Transaction.date.desc()).paginate(page, per_page, False)
        return transactions

    @classmethod
    def get_transaction_stat(cls, user_id: int, start_date: date, end_date: date, trans_type: int) -> int:
        debit_sum = cls.query.with_entities(func.sum(Transaction.amount))\
            .join(Account, Account.account_id == Transaction.account_id) \
            .join(User, Account.user_id == User.id).filter_by(id=user_id).filter(Transaction.date >= start_date). \
            filter(Transaction.date <= end_date).filter(Transaction.type == trans_type).all()
        return debit_sum


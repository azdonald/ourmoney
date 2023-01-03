from marshmallow import Schema, fields, post_load, pre_load
from ourmoneyold.models import User, Account, Institution, Transaction, Budget, BankAccess
from datetime import datetime

CREDIT = 1
DEBIT = 2


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    firstname = fields.Str(required=True)
    lastname = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


class AccountSchema(Schema):
    id = fields.Int(dump_only=True)
    account_id = fields.Str()
    name = fields.Str()
    mask = fields.Str()
    type = fields.Str()
    subtype = fields.Str()
    user_id = fields.Int()
    institution_id = fields.Int()

    @pre_load
    def add_type(self, data, **kwargs):
        data['account_id'] = data['id']
        return data

    @post_load
    def make_account(self, data, **kwargs):
        return Account(**data)


class InstitutionSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    institution_id = fields.Str()
    accounts = fields.Nested(AccountSchema(many=True))

    @post_load
    def make_institution(self, data, **kwargs):
        return Institution(**data)


class TransactionSchema(Schema):
    id = fields.Int(dump_only=True)
    transaction_id = fields.Str()
    amount = fields.Float()
    name = fields.Str()
    authorized_date = fields.Str(allow_none=True)
    date = fields.DateTime()
    type = fields.Int()
    currency_code = fields.Str(allow_none=True)
    unofficial_currency_code = fields.Str(allow_none=True)
    payment_channel = fields.Str()
    pending = fields.Boolean()
    account_id = fields.Str()
    accounts = fields.Nested(AccountSchema())

    @pre_load
    def add_type(self, data, **kwargs):
        data['type'] = DEBIT if data['amount'] > 0 else CREDIT
        data['date'] = datetime.strptime(data['date'], '%Y-%m-%d')
        return data

    @post_load
    def make_transaction(self, data, **kwargs):
        return Transaction(**data)

    @classmethod
    def str_date(cls, obj):
        if isinstance(obj.date, str):
            return datetime.strptime(obj.date, '%Y-%m-%d')
        return obj.date

    @classmethod
    def transaction_type(cls, obj):
        if obj.amount > 0:
            return DEBIT
        return CREDIT


class BudgetSchema(Schema):
    id = fields.Int(dump_only=True)
    expected_expenditure = fields.Float()
    expected_income = fields.Float()
    user_id = fields.Int(dump_only=True)
    start_date = fields.DateTime()
    end_date = fields.DateTime()

    @post_load
    def make_budget(self, data, **kwargs):
        return Budget(**data)


class BankAccessSchema(Schema):
    id = fields.Int(dump_only=True)
    token = fields.Str()
    item_id = fields.Str()
    user_id = fields.Int()
    institution_id = fields.Int()

    @post_load
    def make_bank_access(self, data, **kwargs):
        return BankAccess(**data)
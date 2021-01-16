from marshmallow import Schema, fields, post_load, pre_load
from src.models import User, Account, Institution


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    firstname = fields.Str()
    lastname = fields.Str()
    email = fields.Email()
    password = fields.Str()

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
    user_id = fields.Int(dump_only=True)
    institution_id = fields.Int()

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


class BalanceSchema(Schema):
    id = fields.Int(dump_only=True)
    current = fields.Float()
    available = fields.Float()
    limit = fields.Float()
    accounts = fields.Nested(AccountSchema(many=True))

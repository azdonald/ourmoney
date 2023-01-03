from pprint import pprint

from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request
from marshmallow.exceptions import ValidationError

from utils.token import get_user_details
from services import institution_service, plaid_access_service, account_service
from utils.schemas import InstitutionSchema, PlaidAccessSchema, AccountSchema
from utils.plaid import Plaid

from http import HTTPStatus

account_schema = AccountSchema(many=True, unknown='EXCLUDE')
institution_schema = InstitutionSchema()
plaid_access_schema = PlaidAccessSchema(unknown='EXCLUDE')
plaid = Plaid()


class  Accounts(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.user_details = get_user_details()

    def get(self):
        print(self.user_details)
        accounts = institution_service.get_institution_and_accounts(self.user_details['id'])
        return InstitutionSchema(many=True).dump(accounts), HTTPStatus.OK

    def post(self):
        data = request.get_json()
        try:
            new_institution = institution_schema.load(data['metadata']['institution'])
            institution = institution_service.add_institution(new_institution)
            plaid_data = plaid.get_token_and_item_id(data['public_token'])
            plaid_access_data = {'public_token': data['public_token'], 'user_id': self.user_details['id'],
                                 'institution_id': institution.id, 'item_id': plaid_data['item_id'],
                                 'token': plaid_data['access_token']}
            new_plaid_access = plaid_access_schema.load(plaid_access_data)
            plaid_access_service.add_new_plaid_access(new_plaid_access)
            accounts_data = data['metadata']['accounts']
            for i in accounts_data:
                i.update({'user_id': self.user_details['id'], 'institution_id': institution.id})
            accounts = account_schema.load(accounts_data)
            account_service.add_accounts(accounts)
            institution_and_accounts = institution_service.get_institution_and_accounts(self.user_details['id'])
            return institution_schema.dump(institution_and_accounts, many=True), HTTPStatus.CREATED
        except ValidationError as error:
            return error.messages, HTTPStatus.BAD_REQUEST

from flask_restful import Resource, fields, marshal, marshal_with
from plaid import Client
from src.plaid import Plaid
from flask import request, jsonify, current_app as app
from src.token import generate_token, get_user_details
from flask import request
from src.services import register, login, add_account, add_institution, transform_accounts_for_schema, \
    get_institution_and_accounts_for_user, get_balance, save_plaid_access_token
from flask_jwt_extended import jwt_required
from src.task import get_access_token


plaid = Plaid()


class UserToken(fields.Raw):
    def output(self, key, obj):
        return generate_token(obj.as_dict())


user_fields = {
    'firstname': fields.String,
    'lastname': fields.String,
    'email': fields.String,
    'userId': fields.String(attribute='public_id'),
    'account_linked': fields.Boolean,
    'token': UserToken
}


class UserRegistration(Resource):
    def post(self):
        user_details = register(request.get_json())
        return marshal(user_details, user_fields), 201


class UserLogin(Resource):
    def post(self):
        user_details = login(request.get_json())
        return marshal(user_details, user_fields), 200


class Transactions(Resource):
    decorators = [jwt_required]

    def post(self):
        public_token = request.get_json()
        app.logger.info(public_token['public_token'])
        print('public token sent is ' + public_token['public_token'])
        client = Client(client_id='5e65448edf1def0011a4e73c', secret='e66361791d54659f54b13ef24ef9ac',
                        public_key='035925d9da8f6f0049d002f812d691', environment='sandbox')
        response = client.Item.public_token.exchange(public_token['public_token'])
        resp = client.Transactions.get(response['access_token'], start_date='2020-02-01', end_date='2020-03-01')
        transactions = resp['transactions']
        return jsonify(transactions)

    def get(self):
        client = Client(client_id='5e65448edf1def0011a4e73c', secret='e66361791d54659f54b13ef24ef9ac', public_key='035925d9da8f6f0049d002f812d691', environment='sandbox')


class Accounts(Resource):
    decorators = [jwt_required]

    def get(self):
        user_details = get_user_details()
        accounts = get_institution_and_accounts_for_user(user_details['id'])

        return accounts, 200

    def post(self):
        user_details = get_user_details()
        request_data = request.get_json()
        public_token = request_data['public_token']
        access_token = plaid.get_access_token(public_token)
        institution = add_institution(request_data['metadata']['institution'])
        save_plaid_access_token(access_token, user_details['id'], institution.id)
        account_data = request_data['metadata']['accounts']
        for i in account_data:
            transformed_account_data = transform_accounts_for_schema(i, user_details['id'], institution.id)
            accounts = add_account(transformed_account_data, user_details['id'])
        return get_institution_and_accounts_for_user(user_details['id'])


class Balance(Resource):
    decorators = [jwt_required]

    def get(self):
        user_details = get_user_details()
        balance = get_balance(user_details['id'])
        return balance, 200

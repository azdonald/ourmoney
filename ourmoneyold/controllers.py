from flask_restful import Resource, fields, marshal, marshal_with
from ourmoneyold.token import generate_token, get_user_details
from flask import request, jsonify
from ourmoneyold.services import create_new_account, search_transactions, UserService, AccountService, \
    InstitutionService, TransactionService, BudgetService, BankAccessService
from flask_jwt_extended import jwt_required
from pprint import pprint


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


class Home(Resource):

    def get(self):
        return 'Ok!', 200


class UserRegistration(Resource):
    def post(self):
        user_service = UserService()
        user_details = user_service.register(request.get_json())
        return marshal(user_details, user_fields), 201


class UserLogin(Resource):
    def __init__(self):
        self.user_service = UserService()

    def post(self):
        user_details = self.user_service.login(request.get_json())
        return marshal(user_details, user_fields), 200


class UserPasswordChange(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.user_service = UserService()

    def post(self):
        user_details = get_user_details()
        user_details = self.user_service.update_password(user_details['id'], request.get_json())
        return marshal(user_details, user_fields), 200


class Transactions(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.trans_service = TransactionService()

    def get(self):
        params = request.args
        user_details = get_user_details()
        transactions = self.trans_service.get(user_details['id'], int(params['page']))
        return transactions, 200


class Accounts(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.inst_service = InstitutionService()
        self.account_service = AccountService()
        self.bank_access_service = BankAccessService()

    def get(self):
        user_details = get_user_details()
        accounts = self.inst_service.get(user_details['id'])
        pprint(accounts)
        return accounts, 200

    def post(self):
        user_details = get_user_details()
        data = request.get_json()
        institution = self.inst_service.add(data['metadata']['institution'])
        bank_access_data = {'public_token': data['public_token'],
                            'user_id': user_details['id'], 'institution_id': institution.id}
        self.bank_access_service.add(bank_access_data)
        accounts_data = data['metadata']['accounts']
        self.account_service.add_accounts(accounts_data, user_details['id'], institution.id)
        return self.inst_service.get(user_details['id']), 201


class Search(Resource):
    decorators = [jwt_required]

    def get(self):
        user_details = get_user_details()
        params = request.args
        transactions = search_transactions(params['q'], user_details['id'])
        return transactions, 200


class Profile(Resource):
    decorators = [jwt_required]

    def get(self):
        user_details = get_user_details()
        user_service = UserService()
        user = user_service.get(user_details['id'])
        return user, 200


class Budget(Resource):
    decorators = [jwt_required]

    def get(self):
        user_details = get_user_details()
        budget_service = BudgetService()
        budget = budget_service.get(user_details['id'])
        return budget, 200

    def post(self):
        user_details = get_user_details()
        budget_service = BudgetService()
        budget = budget_service.create(user_details['id'], request.get_json())
        return budget, 201


class Stats(Resource):
    decorators = [jwt_required]

    def get(self):
        user_details = get_user_details()


class WebHooks(Resource):
    pass

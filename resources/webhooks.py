from flask_restful import Resource
from flask import request
from http import HTTPStatus

from services import plaid_access_service
from utils.task import get_transaction, remove_transactions
from utils.plaid import Plaid

from datetime import datetime, timedelta


class PlaidHooks(Resource):
    def get(self):
        plaid = Plaid()
        return plaid.get_categories()

    def post(self):
        web_hook_data = request.get_json()
        if not web_hook_data:
            return HTTPStatus.BAD_REQUEST
        plaid_access_data = plaid_access_service.get_plaid_access_token(web_hook_data['item_id'])
        if not plaid_access_data:
            return HTTPStatus.BAD_REQUEST
        if web_hook_data['webhook_code'] == "INITIAL_UPDATE":
            get_transaction(plaid_access_data.token)
            return HTTPStatus.OK
        if web_hook_data['webhook_code'] == "HISTORICAL_UPDATE ":
            start_date = datetime.today() - timedelta(days=730)
            end_date = datetime.today() - timedelta(days=31)
            get_transaction(plaid_access_data.token, start_date, end_date)
            return HTTPStatus.OK
        if web_hook_data['webhook_code'] == "DEFAULT_UPDATE ":
            get_transaction(plaid_access_data.token)
            return HTTPStatus.OK
        if web_hook_data['webhook_code'] == "TRANSACTIONS_REMOVED ":
            remove_transactions(web_hook_data['removed_transactions'])
            return HTTPStatus.OK
        return HTTPStatus.OK

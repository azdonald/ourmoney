from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request

from utils.token import get_user_details
from services import transaction_service
from utils.schemas import TransactionSchema
from datetime import datetime, timedelta, date

from http import HTTPStatus

transaction_schema = TransactionSchema(many=True, unknown='EXCLUDE')


class Transactions(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.user_details = get_user_details()

    def get(self):
        params = request.args
        transactions = transaction_service.get_transactions(self.user_details['id'], int(params['page']))
        transactions_result = {
            "data": transaction_schema.dump(transactions.items),
            "total": transactions.total,
            "page": transactions.page,
            "per_page": transactions.per_page
        }
        return transactions_result, HTTPStatus.OK


class TransactionSearch(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.user_details = get_user_details()

    def get(self):
        params = request.args
        transactions = transaction_service.search(params['q'], self.user_details['id'])
        return transaction_schema.dump(transactions), HTTPStatus.OK


class Stats(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.user_details = get_user_details()

    def get(self):
        params = request.args
        start_date = params.get('start_date', date.today() - timedelta(days=7))
        end_date = params.get('end_date', date.today())
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        transaction_stats = transaction_service.get_user_transaction_stat(self.user_details['id'], start_date, end_date)
        transaction_stats['start_date'] = start_date.isoformat()
        transaction_stats['end_date'] = end_date.isoformat()
        return transaction_stats, HTTPStatus.OK

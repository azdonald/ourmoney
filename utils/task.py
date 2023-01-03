from celery import Celery
from .plaid import Plaid
from .schemas import TransactionSchema
from models import save_bulk
from services import transaction_service
from marshmallow.exceptions import ValidationError

celery = Celery()
plaid = Plaid()
trans_schema = TransactionSchema(many=True, unknown='EXCLUDE')


@celery.task
def get_transaction(access_token: str, start_date=None, end_date=None):
    plaid_transactions = plaid.get_transactions(access_token, start_date, end_date)
    try:
        transactions = trans_schema.load(plaid_transactions)
        for t in transactions:
            t.save()
    except ValidationError as error:
        print(error.messages)


@celery.task
def remove_transactions(removed_transactions):
    for i in removed_transactions:
        transaction_service.remove_transaction(removed_transactions[i])

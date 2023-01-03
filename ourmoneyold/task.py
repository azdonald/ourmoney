from celery import Celery
from ourmoneyold.plaid import Plaid

celery = Celery()


@celery.task
def get_access_token(public_token):
    plaid = Plaid()
    token = plaid.get_token_and_item_id(public_token)

from celery import Celery
from src.plaid import Plaid

celery = Celery()


@celery.task
def get_access_token(public_token):
    plaid = Plaid()
    token = plaid.get_access_token(public_token)

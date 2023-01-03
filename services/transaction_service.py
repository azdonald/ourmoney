from models.transaction_model import Transaction
from models import delete
from utils.constants import CREDIT, DEBIT

from datetime import date, datetime


def get_transactions(user_id: int, page: int):
    return Transaction.get(user_id, page)


def search(q, user_id: int):
    search_params = "%{}%".format(q)
    return Transaction.search(search_params, user_id)


def remove_transaction(removed_transaction_id):
    transaction = Transaction.get_by_transaction_id(removed_transaction_id)
    if not transaction:
        pass
    delete(transaction)


def get_user_transaction_stat(user_id: int, start_date: date, end_date: date):
    user_transaction_stat = {}
    debit_sum = Transaction.get_transaction_stat(user_id, start_date, end_date, DEBIT)
    credit_sum = Transaction.get_transaction_stat(user_id, start_date, end_date, CREDIT)
    user_transaction_stat['debit'] = debit_sum[0][0]
    user_transaction_stat['credit'] = credit_sum[0][0]
    return user_transaction_stat

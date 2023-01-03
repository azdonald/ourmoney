from models.account_model import Account
from models import save_bulk


def add_accounts(accounts):
    save_bulk(accounts)

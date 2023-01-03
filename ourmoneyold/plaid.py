from plaid import Client
from datetime import datetime, timedelta


class Plaid(object):
    def __init__(self):
        self.client = Client(client_id='5e65448edf1def0011a4e73c', secret='e66361791d54659f54b13ef24ef9ac',
                             environment='sandbox')

    def get_token_and_item_id(self, public_token):
        response = self.client.Item.public_token.exchange(public_token)
        return response

    def get_balance(self, access_token):
        response = self.client.Accounts.balance.get_with_accounts(access_token)
        return response['accounts']

    def get_transactions(self, access_token, start_date=None, end_date=None):
        if not start_date:
            end_date = datetime.today().strftime('%Y-%m-%d')
            start_date = datetime.today() - timedelta(days=30)
            start_date = start_date.strftime('%Y-%m-%d')
        if not end_date:
            cur_start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = cur_start_date + timedelta(days=30)
            end_date = end_date.strftime('%Y-%m-%d')
        response = self.client.Transactions.get_with_accounts(access_token, start_date, end_date)
        return response['transactions']

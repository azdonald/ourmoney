from plaid import Client


class Plaid(object):
    def __init__(self):
        self.client = Client(client_id='5e65448edf1def0011a4e73c', secret='e66361791d54659f54b13ef24ef9ac',
                             environment='sandbox')

    def get_access_token(self, public_token):
        response = self.client.Item.public_token.exchange(public_token)
        return response['access_token']

    def get_balance(self, access_token):
        response = self.client.Accounts.balance.get(access_token)
        return response['accounts']

    def get_transactions(self, access_token, start_date, end_date):
        response = self.client.Transactions.get(access_token, start_date, end_date)
        return response['transactions']

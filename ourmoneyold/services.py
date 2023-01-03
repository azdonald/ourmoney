from ourmoneyold.models import db, User, Account, Institution, BankAccess, Transaction
from ourmoneyold.exceptions import *
from ourmoneyold.schemas import UserSchema, AccountSchema, InstitutionSchema, TransactionSchema, BudgetSchema, BankAccessSchema
from ourmoneyold.plaid import Plaid
from ourmoneyold.repositories import UserRepository, TransactionRepository, AccountRepository, InstitutionRepository, \
    BudgetRepository, BankAccessRepository
from typing import Any, List, Optional
from pprint import pprint

plaid = Plaid()


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.user_schema = UserSchema()

    def register(self, registration_data) -> User:
        user = self.user_repo.get_user_by_email(registration_data['email'])
        if user:
            raise DuplicateUserException('User with that email already exists')
        user = self.user_schema.load(registration_data)
        self.user_repo.save(user)
        return user

    def login(self, login_data) -> User:
        user = self.user_repo.get_user_by_email(login_data['email'])
        if not user:
            raise InvalidUserException('User not found')
        auth = user.check_password(login_data['password'])
        if not auth:
            raise InvalidUserException('Incorrect login details')
        return user

    def get(self, user_id: int):
        user = self.user_repo.get_user_by_id(id=user_id)
        return self.user_schema.dump(user)

    def update_password(self, user_id: int, data):
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise InvalidUserException('User not found')
        auth = user.check_password(data['currentPassword'])
        if not auth:
            raise InvalidUserException('In correct login details')
        user.password = data['newPassword']
        self.user_repo.save(user)
        return user


class AccountService:
    def __init__(self):
        self.account_repo = AccountRepository()
        self.account_schema = AccountSchema(many=True, unknown='EXCLUDE')

    def get(self, user_id):
        accounts = self.account_repo.get(user_id)
        return self.account_schema.dump(accounts)

    def add_accounts(self, accounts_data, user_id: int, institution_id):
        for i in accounts_data:
            i.update({'user_id': user_id, 'institution_id': institution_id})
        accounts = self.account_schema.load(accounts_data)
        self.account_repo.save_bulk(accounts)


class BankAccessService:
    def __init__(self):
        self.bank_access_repo = BankAccessRepository()
        self.bank_access_schema = BankAccessSchema(unknown='EXCLUDE')

    def add(self, bank_access_data):
        plaid_data = plaid.get_token_and_item_id(bank_access_data['public_token'])
        pprint(plaid_data)
        bank_access_data['item_id'] = plaid_data['item_id']
        bank_access_data['token'] = plaid_data['access_token']
        bank_access = self.bank_access_schema.load(bank_access_data)
        self.bank_access_repo.save(bank_access)

    def get_by_item_id(self, item_id: str) -> Optional[BankAccess]:
        return self.bank_access_repo.get_by_item_id(item_id)

    def get(self, user_id: int) -> Optional[BankAccess]:
        return self.bank_access_repo.get(user_id)


class InstitutionService:
    def __init__(self):
        self.institution_repo = InstitutionRepository()
        self.institution_schema = InstitutionSchema()

    def get(self, user_id: int):
        institutions = self.institution_repo.get_with_accounts(user_id)
        return self.institution_schema.dump(institutions, many=True)

    def add(self, institution_data) -> Institution:
        institution = self.institution_repo.get_by_name(institution_data['name'])
        if institution:
            return institution
        institution = self.institution_schema.load(institution_data)
        self.institution_repo.save(institution)
        return institution


class TransactionService:
    def __init__(self):
        self.trans_repo = TransactionRepository()
        self.bank_access_repo = BankAccessRepository()
        self.trans_schema = TransactionSchema(many=True, unknown='EXCLUDE')

    def get(self, user_id: int, page: int):
        transactions = self.trans_repo.get(user_id, page)
        result = {
            "data": self.trans_schema.dump(transactions.items),
            "total": transactions.total,
            "page": transactions.page,
            "per_page": transactions.per_page
        }
        return result

    def search(self, q: Any, user_id: int) -> Optional[List[Transaction]]:
        search_params = "%{}%".format(q)
        transactions = self.trans_repo.search(search_params, user_id)
        return self.trans_schema.dump(transactions)

    def get_from_plaid(self, item_id: str):
        bank_access = self.bank_access_repo.get_by_item_id(item_id)
        if not bank_access:
            raise InvalidPlaidItemException("Item ID {plaid_item_id} is invalid".format(plaid_item_id=item_id))
        transactions = plaid.get_transactions(bank_access.token, None, None)
        self.add(transactions)

    def add(self, transaction_data):
        transactions = self.trans_schema.load(transaction_data)
        self.trans_repo.save_bulk(transactions)


class BudgetService:
    def __init__(self):
        self.budget_repo = BudgetRepository()
        self.budget_schema = BudgetSchema()

    def create(self, user_id: int, data):
        budget = self.budget_schema.load(data)
        budget.user_id = user_id
        self.budget_repo.save(budget)

    def get(self, user_id: int, start=None, end=None):
        pass

    def update(self, user_id: int, data):
        pass


# Add a new bank account for users as well as getting plaid's access token
def create_new_account(data, user_id: int):
    institution = add_institution(data['metadata']['institution'])
    access_token = plaid.get_token_and_item_id(data['public_token'])
    save_plaid_access_token(access_token, user_id, institution.id)
    account_data = data['metadata']['accounts']
    for i in account_data:
        transformed_account_data = transform_accounts_for_schema(i, user_id, institution.id)
        add_account(transformed_account_data, user_id)
    get_balance_from_plaid(user_id, access_token)
    return get_institution_and_accounts_for_user(user_id)


def add_institution(data) -> Institution:
    institution = get_institution_by_name(data['name'])
    if institution:
        return institution
    institution_schema = InstitutionSchema()
    institution = institution_schema.load(data)
    save_changes(institution)
    return institution


def add_account(data, user_id: int):
    account_schema = AccountSchema()
    account = account_schema.load(data)
    account.user_id = user_id
    save_changes(account)


def get_transactions(user_id: int):
    transaction_schema = TransactionSchema(many=True)
    transactions = Transaction.query.join(Account, Account.account_id == Transaction.account_id)\
        .join(User, Account.user_id == User.id).filter_by(id=user_id).all()
    if not transactions:
        transactions = get_transaction_from_plaid(user_id)
    return transaction_schema.dump(transactions)


def add_balance(data, account: Account):
    account.current = data['current']
    account.available = data['available']
    account.limit = data['limit']
    account.currency_code = data['currency_code']
    save_changes(account)


def add_transactions(data):
    transaction_schema = TransactionSchema(many=True, unknown='EXCLUDE')
    transactions = transaction_schema.load(data)
    save_bulk(transactions)
    return transactions


def get_user_by_email(email: str) -> User:
    return User.query.filter_by(email=email).first()


def get_user_by_public_id(public_id: str) -> User:
    return User.query.filter_by(public_id=public_id).first()


def get_institution_by_name(name: str) -> object:
    return Institution.query.filter_by(name=name).first()


def get_balance_from_plaid(user_id: int, access_token=None):
    if not access_token:
        bank_access_details = get_bank_access(user_id)
        access_token = bank_access_details.token
    balance_data = plaid.get_balance(access_token)
    for i in balance_data:
        balance = i['balances']
        balance['currency_code'] = balance['iso_currency_code']
        del balance['iso_currency_code']
        del balance['unofficial_currency_code']
        account = Account.query.with_entities(Account.id).filter_by(account_id=i['account_id']).first()
        add_balance(balance, account)


def get_institution_and_accounts_for_user(user_id: int):
    institution_schema = InstitutionSchema(many=True)
    institutions = Institution.query.join(Account).join(User, Account.user_id == User.id).filter_by(id=user_id).all()
    return institution_schema.dump(institutions)


def transform_accounts_for_schema(account: dict, user_id: int, institution_id: str) -> dict:
    account['account_id'] = account['id']
    account['institution_id'] = institution_id
    del account['id']
    return account


def save_plaid_access_token(access_token: str, user_id: int, institution_id: int):
    bank_access = BankAccess(token=access_token, user_id=user_id, institution_id=institution_id)
    save_changes(bank_access)


def get_bank_access(user_id: int) -> BankAccess:
    bank_access = BankAccess.query.filter_by(user_id=user_id).first()
    if not bank_access:
        raise NoAccessTokenException("No Access Token found")
    return bank_access


def get_transaction_from_plaid(user_id: int, access_token=None, start_date=None, end_date=None):
    if not access_token:
        bank_access_details = get_bank_access(user_id)
        access_token = bank_access_details.token
    transactions = plaid.get_transactions(access_token, start_date, end_date)
    trans = add_transactions(transactions)
    return trans


def search_transactions(q, user_id: int):
    transaction_schema = TransactionSchema(many=True)
    search_params = "%{}%".format(q)
    transactions = Transaction.query.filter(Transaction.name.like(search_params)).join(Account, Account.account_id == Transaction.account_id)\
        .join(User, Account.user_id == User.id).filter_by(id=user_id).all()
    return transaction_schema.dump(transactions)


def save_changes(data):
    db.session.add(data)
    db.session.flush()
    db.session.commit()


def save_bulk(data):
    db.session.bulk_save_objects(data)
    db.session.flush()
    db.session.commit()

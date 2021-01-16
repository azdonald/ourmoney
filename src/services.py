from src.models import db, User, Account, Balance, Institution, BankAccess
from src.exceptions import *
from src.schemas import UserSchema, AccountSchema, InstitutionSchema, BalanceSchema


def register(data) -> User:
    user = get_user_by_email(data['email'])
    if user:
        raise DuplicateUserException('User with that email already exists')
    user_schema = UserSchema()
    user = user_schema.load(data)
    save_changes(user)
    return user


def login(data) -> User:
    user = get_user_by_email(data['email'])
    if not user:
        raise InvalidUserException('User not found')
    auth = user.check_password(data['password'])
    if not auth:
        raise InvalidUserException('In correct login details')
    return user


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
    return account


def get_user_by_email(email: str) -> User:
    return User.query.filter_by(email=email).first()


def get_user_by_public_id(public_id: str) -> User:
    return User.query.filter_by(public_id=public_id).first()


def get_institution_by_name(name: str) -> object:
    return Institution.query.filter_by(name=name).first()


def get_balance(user_id: int):
    balance_schema = BalanceSchema(many=True)
    balance = Balance.query.join(Account).join(User, Account.user_id == User.id).filter_by(id=user_id).all()
    return balance_schema.dump(balance)


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


def save_changes(data):
    db.session.add(data)
    db.session.flush()
    db.session.commit()

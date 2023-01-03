from ourmoneyold.models import db, User, Transaction, Account, Budget, Institution, BudgetDetails, BankAccess
from ourmoneyold.schemas import UserSchema, TransactionSchema
from typing import List, Optional


class BaseRepository:

    def save(self, data):
        db.session.add(data)
        db.session.flush()
        db.session.commit()

    def save_bulk(self, data):
        db.session.bulk_save_objects(data)
        db.session.flush()
        db.session.commit()


class UserRepository(BaseRepository):
    def __init__(self):
        super()
        self.user_model = User
        self.user_schema = UserSchema()

    def get_user_by_email(self, email: str) -> User:
        return self.user_model.query.filter_by(email=email).first()

    def get_user_by_id(self, user_id: int) -> User:
        return self.user_model.query.filter_by(id=user_id).first()


class AccountRepository(BaseRepository):
    def __init__(self):
        super()
        self.account_model = Account

    def get(self, user_id: int):
        accounts = self.account_model.query.join(Institution, Institution.id == Account.institution_id)\
            .join(User, Account.user_id == User.id).filter_by(id=user_id).all()
        return accounts


class InstitutionRepository(BaseRepository):
    def __init__(self):
        super()
        self.institution_model = Institution()

    def get_with_accounts(self, user_id: int) -> Optional[List[Institution]]:
        institutions = self.institution_model.query.join(Account).join(User, Account.user_id == User.id).\
            filter_by(id=user_id).all()
        return institutions

    def get_by_name(self, name: str) -> Optional[Institution]:
        return self.institution_model.query.filter_by(name=name).first()


class TransactionRepository(BaseRepository):
    def __init__(self):
        super()
        self.transaction = Transaction

    def search(self, search_params, user_id: int) -> Optional[List[Transaction]]:
        transactions = self.transaction.query.filter(Transaction.name.like(search_params))\
            .join(Account, Account.account_id == Transaction.account_id) \
            .join(User, Account.user_id == User.id).filter_by(id=user_id).all()
        return transactions

    def get(self, user_id: int, page, per_page=5) -> Optional[List[Transaction]]:
        transactions = self.transaction.query.join(Account, Account.account_id == Transaction.account_id) \
            .join(User, Account.user_id == User.id).filter_by(id=user_id).order_by(Transaction.date).paginate(page, per_page, False)
        return transactions


class BudgetRepository(BaseRepository):
    def __init__(self):
        self.budget = Budget

    def get(self, user_id: int, start, end):
        return self.budget.query.join(BudgetDetails).join(User, Budget.user_id == User.id).\
            filter_by(id=user_id, start_date=start, end_date=end).first()


class BankAccessRepository(BaseRepository):
    def __init__(self):
        self.bank_access = BankAccess

    def get(self, user_id: int) -> Optional[BankAccess]:
        return self.bank_access.query.filter_by(user_id=user_id).first()

    def get_by_item_id(self, item_id: str) -> Optional[BankAccess]:
        return self.bank_access.query.filter_by(item_id=item_id).first()

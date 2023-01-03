from models import BaseModel, db
from models.account_model import Account
from models.user_model import User


class Institution(BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True)
    institution_id = db.Column(db.String(50), unique=True)
    accounts = db.relationship('Account', backref=db.backref('accounts', lazy=True))

    @classmethod
    def get_with_accounts(cls, user_id: int):
        institutions = cls.query.join(Account).join(User, Account.user_id == User.id).\
            filter_by(id=user_id).all()
        return institutions

    @classmethod
    def get_by_name(cls, name: str):
        return cls.query.filter_by(name=name).first()

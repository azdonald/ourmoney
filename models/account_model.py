from models import BaseModel, db


class Account(BaseModel):
    account_id = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255))
    mask = db.Column(db.String(100))
    type = db.Column(db.String(50))
    subtype = db.Column(db.String(50))
    current = db.Column(db.Float, nullable=True)
    available = db.Column(db.Float, nullable=True)
    limit = db.Column(db.Float, nullable=True)
    currency_code = db.Column(db.String(3), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    transactions = db.relationship('Transaction', backref=db.backref('accounts', lazy=True))

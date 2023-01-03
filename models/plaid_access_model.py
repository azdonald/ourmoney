from models import BaseModel, db


class PlaidAccess(BaseModel):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(255), unique=True)
    item_id = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)

    @classmethod
    def get(cls, user_id: int):
        return cls.filter_by(user_id=user_id).all()

    @classmethod
    def get_by_item_id(cls, item_id: str):
        return cls.query.filter_by(item_id=item_id).first()

    @classmethod
    def get_by_user_and_institution(cls, user_id: int, institution_id: int):
        return cls.query.filter_by(user_id=user_id, institution_id=institution_id).first()

from models import BaseModel, bcrypt, db, generate_public_id


class User(BaseModel):
    email = db.Column(db.String(255), unique=True, nullable=False)
    firstname = db.Column(db.String(255), nullable=False)
    lastname = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(100))
    public_id = db.Column(db.String(100), unique=True, default=generate_public_id)
    email_verified = db.Column(db.Boolean, default=False)
    account_linked = db.Column(db.Boolean, default=False)
    partner_id = db.Column(db.Integer, nullable=True)
    accounts = db.relationship('Account', backref=db.backref('user_account', lazy=True))

    @property
    def password(self):
        raise AttributeError('Write only field')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def as_dict(self):
        return {'id': self.id, 'public_id': self.public_id, 'firstname': self.firstname, 'lastname': self.lastname,
                'email': self.email}

    def __repr__(self):
        return "<User '{} {} {}' ".format(self.firstname, self.lastname, self.public_id)

    @classmethod
    def get_user_by_email(cls, email: str):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_user_by_id(cls, user_id: int):
        return cls.query.filter_by(id=user_id).first()

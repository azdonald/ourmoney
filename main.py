from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from celery import Celery
from datetime import timedelta

import os

cors = CORS()
migrate = Migrate()
errors = {
    'DuplicateUserException': {
        'message': "A user with that email already exists, please login",
        'status': 400,
    },
    'InvalidUserException': {
        'message': "Invalid login details.",
        'status': 400,
    },
}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    from resources import users, account, transaction, webhooks
    from models import db, bcrypt
    from utils.token import jwt
    db.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = os.environ.get("JWT_ACCESS_TOKEN_EXPIRES")
    jwt.init_app(app)
    api = Api(app, errors=errors)
    api.add_resource(users.Registration, '/api/register')
    api.add_resource(users.Login, '/api/login')
    api.add_resource(transaction.Transactions, '/api/transactions')
    api.add_resource(account.Accounts, '/api/accounts')
    api.add_resource(transaction.TransactionSearch, '/api/transactions/search')
    api.add_resource(webhooks.PlaidHooks, '/api/webhook')
    api.add_resource(users.PasswordChange, '/api/password/change')
    api.add_resource(transaction.Stats, '/api/transactions/stats')
    api.add_resource(users.LinkPartner, '/api/users/link')
    return app


def init_celery(application):
    from utils.task import celery
    celery.conf.broker_url = application.config['CELERY_BROKER_URL']
    celery.conf.result_backend = application.config['CELERY_BACKEND_RESULT']
    celery.conf.update(application.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with application.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

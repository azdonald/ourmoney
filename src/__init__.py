from flask import Flask
from flask_restful import Api
from src.controllers import *
from flask_cors import CORS
from src.config import Config
from celery import Celery


cors = CORS()
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
    from src.models import db, bcrypt
    from src.token import jwt
    db.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    app.config['JWT_SECRET_KEY'] = 'secretKeyPeople'
    jwt.init_app(app)
    api = Api(app, errors=errors)
    api.add_resource(UserRegistration, '/api/register')
    api.add_resource(UserLogin, '/api/login')
    api.add_resource(Transactions, '/api/transactions')
    api.add_resource(Accounts, '/api/accounts')
    return app


def init_celery(application):
    from src.task import celery
    celery.conf.broker_url = application.config['CELERY_BROKER_URL']
    celery.conf.result_backend = application.config['CELERY_BACKEND_RESULT']
    celery.conf.update(application.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with application.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

import os


class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_BACKEND_RESULT = "redis://localhost:6379/0"

from werkzeug.exceptions import HTTPException


class DuplicateUserException(HTTPException):
    pass


class InvalidUserException(HTTPException):
    pass

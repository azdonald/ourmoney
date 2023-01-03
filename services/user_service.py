from models.user_model import User
from utils.execptions import *


def create_user(user: User) -> User:
    existing_user = User.get_user_by_email(user.email)
    if existing_user:
        raise DuplicateUserException("User with email already exists")
    user.save()
    return user


def login(email: str, password: str) -> User:
    user = User.get_user_by_email(email)
    if not user:
        raise InvalidUserException("Invalid login details")
    if not user.check_password(password):
        raise InvalidUserException("Invalid login details")
    return user


def update_password(self, user_id: int, data):
    user = User.get_user_by_id(user_id)
    if not user:
        raise InvalidUserException('User not found')
    auth = user.check_password(data['currentPassword'])
    if not auth:
        raise InvalidUserException('In correct login details')
    user.password = data['newPassword']
    user.save()
    return user


def link_partner(user_id: int, partner_email: str):
    user = User.get_user_by_id(user_id)
    if not user:
        raise InvalidUserException('User not found')
    user_partner = User.get_user_by_email(partner_email)
    if not user_partner:
        raise InvalidUserException('Partner not found')
    user.is_account_linked = True
    user.partner_id = user_partner.id
    user.save()
    user_partner.is_account_linked = True
    user_partner.partner_id = user.id
    user_partner.save()
    return user, user_partner

from pprint import pprint

from flask_restful import Resource, fields, marshal
from flask_jwt_extended import jwt_required
from utils.schemas import UserSchema
from utils.token import generate_token, get_user_details
from services import user_service
from flask import request
from werkzeug.exceptions import BadRequest
from marshmallow.exceptions import ValidationError
from http import HTTPStatus

user_schema = UserSchema()


class UserToken(fields.Raw):
    def output(self, key, obj):
        return generate_token(obj.as_dict())


user_fields = {
    'firstname': fields.String,
    'lastname': fields.String,
    'email': fields.String,
    'userId': fields.String(attribute='public_id'),
    'account_linked': fields.Boolean,
    'partner': fields.String(default=None),
    'token': UserToken
}


class Registration(Resource):
    def post(self):
        user_json_data = request.get_json()
        if not user_json_data:
            raise BadRequest
        try:
            user = user_schema.load(user_json_data)
            new_user = user_service.create_user(user)
            return marshal(new_user, user_fields), HTTPStatus.CREATED
        except ValidationError as error:
            return error.messages, HTTPStatus.BAD_REQUEST


class Login(Resource):
    def post(self):
        login_data = request.get_json()
        if not login_data:
            raise BadRequest
        user = user_service.login(login_data['email'], login_data['password'])
        return marshal(user, user_fields), HTTPStatus.OK


class PasswordChange(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.user_details = get_user_details()

    def post(self):
        user_details = user_service.update_password(self.user_details['id'], request.get_json())
        return marshal(user_details, user_fields), HTTPStatus.OK


class LinkPartner(Resource):
    decorators = [jwt_required]

    def __init__(self):
        self.user_details = get_user_details()

    def post(self):
        user_data = request.get_json()
        if not user_data:
            raise BadRequest
        user, user_partner = user_service.link_partner(self.user_details['id'], user_data['email'])
        if not user or not user_partner:
            pass
        user.partner = user_partner.firstname + " " + user_partner.lastname
        return marshal(user, user_fields), HTTPStatus.OK



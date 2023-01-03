from flask_jwt_extended import JWTManager, create_access_token, get_jwt

jwt = JWTManager()


@jwt.additional_claims_loader
def add_user_to_claims(user):
    return {
        'id': user['id'],
        'firstname': user['firstname'],
        'lastname': user['lastname'],
        'email': user['email']
    }


def generate_token(user):
    return create_access_token(user)


def get_user_details():
    return get_jwt()

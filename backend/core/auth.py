from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
import os

class AuthManager:
    def __init__(self, app=None):
        self.jwt = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret')
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
        self.jwt = JWTManager(app)

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    @staticmethod
    def verify_password(password, password_hash):
        return check_password_hash(password_hash, password)

    @staticmethod
    def create_token(identity, role):
        return create_access_token(identity={"user": identity, "role": role})

from app.services.user_service import UserService
from app.security.password import verify_password
from app.security.jwt import create_access_token

class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def authenticate_user(self, email: str, password: str):
        user = self.user_service.get_user_by_email(email)

        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    def login(self, email: str, password: str):
        user = self.authenticate_user(email, password)

        if user is None:
            return None

        access_token = create_access_token({
            "sub": str(user.id)
        })

        return access_token
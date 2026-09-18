from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from uuid import UUID
from app.security.password import hash_password

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    # CREATE
    def create_user(self, user: UserCreate):
        password_hash = hash_password(user.password)

        return self.repository.create(
            user,
            password_hash
        )

    # READ ALL
    def get_all_users(self):
        return self.repository.get_all()

    # READ ONE
    def get_user(self, user_id: UUID):
        return self.repository.get_by_id(user_id)

    # UPDATE
    def update_user(self, user_id: UUID, user: UserUpdate):
        return self.repository.update(user_id, user)
    
    # DELETE
    def delete_user(self, user_id: UUID):
        return self.repository.delete(user_id)

    # READ BY EMAIL
    def get_user_by_email(self, email: str):
        return self.repository.get_by_email(email)
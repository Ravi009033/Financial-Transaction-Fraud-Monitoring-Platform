from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from uuid import UUID

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

  # CREATE
    def create(self, user: UserCreate, password_hash: str):
        db_user = User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            address=user.address,
            password_hash=password_hash
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    # READ ALL
    def get_all(self):
        return self.db.query(User).all()

    # READ ONE
    def get_by_id(self, user_id: UUID):
        return self.db.query(User).filter(User.id == user_id).first()

    # UPDATE
    def update(self, user_id: UUID, user: UserUpdate):

        db_user = self.get_by_id(user_id)

        if db_user is None:
            return None

        db_user.name = user.name
        db_user.email = user.email
        db_user.phone = user.phone
        db_user.address = user.address

        self.db.commit()
        self.db.refresh(db_user)

        return db_user

    # DELETE
    def delete(self, user_id: UUID):

        db_user = self.get_by_id(user_id)

        if db_user is None:
            return None

        self.db.delete(db_user)
        self.db.commit()

        return db_user

    def get_by_email(self, email: str):
        return self.db.query(User).filter(
            User.email == email
        ).first()
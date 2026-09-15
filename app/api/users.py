from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.db.dependencies import get_db
from app.repositories.user_repository import UserRepository
from uuid import UUID

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# GET ALL USERS
@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    repository = UserRepository(db)
    service = UserService(repository)

    return service.get_all_users()

# GET USER BY ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    repository = UserRepository(db)
    service = UserService(repository)

    user = service.get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

# CREATE USER
@router.post("/", response_model=UserResponse)
def add_user(user: UserCreate, db: Session=Depends(get_db)):
    repository = UserRepository(db)
    service = UserService(repository)

    return service.create_user(user)

# UPDATE USER
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, user: UserUpdate, db: Session = Depends(get_db)):

    repository = UserRepository(db)
    service = UserService(repository)

    updated_user = service.update_user(user_id, user)

    if updated_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return updated_user

# DELETE USER
@router.delete("/{user_id}")
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    repository = UserRepository(db)
    service = UserService(repository)

    deleted_user = service.delete_user(user_id)

    if deleted_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }
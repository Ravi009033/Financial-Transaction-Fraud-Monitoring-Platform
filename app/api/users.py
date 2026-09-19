from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.db.dependencies import get_db
from app.repositories.user_repository import UserRepository
from uuid import UUID
from app.security.dependencies import get_current_user
from app.models.user import User
from app.schemas.error import ErrorResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# GET ALL USERS
@router.get(
    "/",
    response_model=list[UserResponse],
    responses={
        401: {"model": ErrorResponse},
    }
)
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    repository = UserRepository(db)
    service = UserService(repository)

    return service.get_all_users()

# GET USER BY ID
@router.get("/{user_id}",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    }
)
def get_user(
    user_id: UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    repository = UserRepository(db)
    service = UserService(repository)

    user = service.get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    if user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this user"
            )
        
    return user

# CREATE USER
@router.post("/",
    response_model=UserResponse,
    responses={
        422: {"model": ErrorResponse},
    }
)
def add_user(user: UserCreate, db: Session=Depends(get_db)):
    repository = UserRepository(db)
    service = UserService(repository)

    return service.create_user(user)

# UPDATE USER
@router.put("/{user_id}",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    }
)
def update_user(
    user_id: UUID,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    repository = UserRepository(db)
    service = UserService(repository)

    existing_user = service.get_user(user_id)

    if existing_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this user"
        )

    return service.update_user(user_id, user)


# DELETE USER
@router.delete("/{user_id}",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    }
)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = UserRepository(db)
    service = UserService(repository)

    existing_user = service.get_user(user_id)

    if existing_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this user"
        )

    service.delete_user(user_id)

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }


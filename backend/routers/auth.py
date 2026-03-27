from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schema.schemas import UserCreate, UserLogin, Token, UserResponse, ChangePasswordRequest, ForgotPasswordRequest, ResetPasswordRequest
from backend.controllers import auth_controller
from backend.utils.auth import get_current_user
from backend.model.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return auth_controller.register(data, db)


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    return auth_controller.login(data, db)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return auth_controller.change_password(data, current_user, db)


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return auth_controller.forgot_password(data, db)


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    return auth_controller.reset_password(data, db)

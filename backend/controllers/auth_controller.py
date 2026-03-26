"""Auth controller — register, login, change password."""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.model.models import User, UserRole
from backend.schema.schemas import UserCreate, UserLogin, Token, ChangePasswordRequest, UserResponse
from backend.services.auth_service import verify_password, hash_password, create_access_token
from backend.services.email_service import send_welcome_email, send_password_changed_email


def register(data: UserCreate, db: Session) -> Token:
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Username already taken")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")

    user = User(
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role=data.role,
        location=data.location,
        phone=data.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Send welcome email (non-blocking — failure doesn't abort registration)
    send_welcome_email(
        to=user.email,
        full_name=user.full_name,
        username=user.username,
        password=data.password,   # plain-text from the request, before hashing
        role=user.role.value,
    )

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=token, token_type="bearer", user=user)


def login(data: UserLogin, db: Session) -> Token:
    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Invalid username or password")
    if user.role.value != data.role.value:
        raise HTTPException(
            401,
            f"This account is registered as a {user.role.value}. Select the correct role.",
        )
    if not user.is_active:
        raise HTTPException(
            403,
            "Your account has been deactivated. Contact an administrator.",
        )

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=token, token_type="bearer", user=user)


def change_password(data: ChangePasswordRequest, current_user: User, db: Session) -> dict:
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(400, "Current password is incorrect")
    if len(data.new_password) < 6:
        raise HTTPException(400, "New password must be at least 6 characters")

    current_user.hashed_password = hash_password(data.new_password)
    db.commit()

    send_password_changed_email(
        to=current_user.email,
        full_name=current_user.full_name,
        new_password=data.new_password,
    )

    return {"message": "Password updated successfully"}

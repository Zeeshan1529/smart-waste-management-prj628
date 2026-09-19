from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .db import get_db
from .models import User
from .schemas import (
    CurrentUserOut,
    Token,
    UserCreate,
    UserOut,
)
from .security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserOut,
)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    existing_username = (
        db.query(User)
        .filter(User.username == payload.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    existing_email = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(
            payload.password
        ),
        role="CITIZEN",
        is_active=1,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(
            User.username == form_data.username,
            User.is_active == 1,
        )
        .first()
    )

    if not user or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        username=user.username,
        role=user.role,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=CurrentUserOut,
)
def current_user(
    user=Depends(get_current_user),
):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }

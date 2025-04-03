"""
Модуль роутера для работы с пользователями и аутентификацией.
Реализует регистрацию, логин, просмотр профиля и логаут.
"""

from fastapi import APIRouter, Response, Depends, HTTPException
import json
from taskapp.schemas.users import SUserRegister, SUserOut
from taskapp.services.user_service import UserService
from taskapp.authenticate.auth import authenticate_user, create_access_token, get_password_hash
from taskapp.authenticate.dependencies import get_current_user
from taskapp.models.user import Users
from taskapp.exceptions import UserAlreadyExistsException, UnauthorizedException

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация&Пользователи"],
)


@router.post("/register")
async def register_user(user_data: SUserRegister):
    existing_user = await UserService.find_one_or_none(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistsException
    hashed_password = get_password_hash(user_data.password)
    await UserService.add_some(email=user_data.email, hashed_password=hashed_password)
    return {"message": "Пользователь успешно зарегистрирован"}


@router.post("/login")
async def login_user(response: Response, user_data: SUserRegister):
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise UnauthorizedException

    access_token = create_access_token({"sub": str(user.id)})

    response.set_cookie(
        key="booking_access_token",
        value=access_token,
        httponly=True,
        path="/",
        # domain="example.com",  # Указывать ТОЛЬКО если реально нужен домен
        # secure=True,           # Если работаем по HTTPS
        # samesite="None",       # Если нужно кросс-доменное использование
    )

    return {"access_token": access_token}


@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie(
        key="booking_access_token",
        httponly=True,
        path="/",
        # Должно совпадать с параметрами из /login:
        # secure=True,
        # samesite="None"
    )
    return {"message": "Logged out"}


@router.get("/me")
async def read_me_users(current_user: Users = Depends(get_current_user)):
    return current_user

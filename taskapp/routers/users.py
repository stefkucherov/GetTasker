"""
Модуль роутера для работы с пользователями.
Авторизирует и регистрирует пользователей с использованием FastAPI.
"""
from typing import Optional

from fastapi import (
    APIRouter, Request, Depends,
    HTTPException, Form, status, Body
)
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from taskapp.authenticate.auth import (
    create_access_token, get_password_hash, verify_password
)
from taskapp.authenticate.dependencies import get_current_user
from taskapp.database import get_async_session
from taskapp.models.user import Users
from taskapp.services.user_service import UserService

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация и Пользователи"],
)

templates = Jinja2Templates(directory="templates")


class RegisterIn(BaseModel):
    username: str
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class ProfileUpdate(BaseModel):
    username: Optional[str] = None


@router.post("/register")
async def register_user_form(
        request: Request,
        username: str = Form(None),
        email: str = Form(None),
        password: str = Form(None),
        session: AsyncSession = Depends(get_async_session),
):
    svc = UserService(session)
    if await svc.find_one_or_none(email=email):
        return templates.TemplateResponse(
            "regs.html",
            {"request": request, "error": "Пользователь с такой почтой уже существует"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    hashed = get_password_hash(password)
    await svc.add_some(username=username, email=email, hashed_password=hashed)
    return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/register", response_class=JSONResponse)
async def register_user_json(
        body: RegisterIn = Body(...),
        session: AsyncSession = Depends(get_async_session),
):
    svc = UserService(session)
    if await svc.find_one_or_none(email=body.email):
        raise HTTPException(status_code=409, detail="user already exists")
    hashed = get_password_hash(body.password)
    await svc.add_some(username=body.username, email=body.email, hashed_password=hashed)
    return {"message": "Пользователь успешно зарегистрирован"}


@router.post("/login")
async def login_user_form(
        request: Request,
        email: str = Form(None),
        password: str = Form(None),
        session: AsyncSession = Depends(get_async_session),
):
    user = await UserService(session).find_one_or_none(email=email)
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth.html",
            {"request": request, "error": "Неверная почта или пароль"},
            status_code=status.HTTP_200_OK
        )
    token = create_access_token({"sub": str(user.id)})
    resp = RedirectResponse("/pages/boards", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie("booking_access_token", token, httponly=True, path="/")
    return resp


@router.post("/login", response_class=JSONResponse)
async def login_user_json(
        body: LoginIn,
        session: AsyncSession = Depends(get_async_session),
):
    user = await UserService(session).find_one_or_none(email=body.email)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token}


@router.post("/logout")
async def logout_user():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie(
        key="booking_access_token",
        httponly=True,
        path="/"
    )
    return response


@router.get("/me", response_class=JSONResponse)
async def read_me_users(current_user: Users = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email}


@router.patch("/profile", response_class=JSONResponse)
async def update_profile(
        body: ProfileUpdate,
        current_user: Users = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
):
    if body.username:
        current_user.username = body.username
        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email}

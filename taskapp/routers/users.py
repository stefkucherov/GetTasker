"""
Модуль роутера для работы с пользователями и аутентификацией.
Реализует регистрацию, логин, просмотр профиля и логаут.
"""
from fastapi import (
    APIRouter, Request, Depends,
    HTTPException, Form, status
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from taskapp.services.user_service import UserService
from taskapp.authenticate.auth import (
    create_access_token, get_password_hash, verify_password
)
from taskapp.authenticate.dependencies import get_current_user
from taskapp.models.user import Users
from taskapp.exceptions import UserAlreadyExistsException, UnauthorizedException

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация и Пользователи"],
)

templates = Jinja2Templates(directory="templates")


@router.get("/login")
async def get_login_page(request: Request):
    """
    Отобразить страницу входа
    """
    return templates.TemplateResponse("auth.html", {"request": request})


@router.post("/login")
async def login_user(
        request: Request,
        email: str = Form(...),
        password: str = Form(...)
):
    """
    Обработать вход пользователя

    Проверяет наличие пользователя и корректность пароля.
    В случае успеха выдает токен и устанавливает cookie.
    """
    user = await UserService.find_one_or_none(email=email)
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth.html",
            {"request": request, "error": "Неверная почта или пароль"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse(url="/pages/boards", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="booking_access_token",
        value=token,
        httponly=True,
        path="/"
    )
    return response


@router.get("/register")
async def get_register_page(request: Request):
    """
    Отобразить страницу регистрации
    """
    return templates.TemplateResponse("regs.html", {"request": request})


@router.post("/register")
async def register_user(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...)
):
    """
    Обработать регистрацию нового пользователя

    Проверяет, существует ли пользователь с такой почтой.
    В случае успеха создает нового пользователя.
    """
    if await UserService.find_one_or_none(email=email):
        return templates.TemplateResponse(
            "regs.html",
            {"request": request, "error": "Пользователь с такой почтой уже существует"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    hashed_password = get_password_hash(password)
    await UserService.add_some(
        email=email,
        username=username,
        hashed_password=hashed_password
    )

    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout")
async def logout_user():
    """
    Выйти из аккаунта (удалить токен из cookie)
    """
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="booking_access_token", httponly=True, path="/")
    return response


@router.get("/me")
async def read_me_users(current_user: Users = Depends(get_current_user)):
    """
    Получить данные текущего авторизованного пользователя
    """
    return {"username": current_user.username, "email": current_user.email}

"""
Роуты для Jinja2-интерфейса.
Обрабатывают авторизацию, регистрацию, отображение досок и задач, а также формы создания и редактирования.
"""
from datetime import datetime
from typing import Optional

from fastapi import (
    APIRouter, Request, HTTPException, Form, status, Depends
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from taskapp.authenticate.auth import verify_password, create_access_token, get_password_hash
from taskapp.authenticate.dependencies import get_token, get_current_user
from taskapp.database import get_async_session
from taskapp.services.board_service import BoardService
from taskapp.services.task_service import TaskService
from taskapp.services.user_service import UserService

router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"],
)

templates = Jinja2Templates(directory="templates")


def parse_due_date_safe(due_date_str: Optional[str]) -> Optional[datetime]:
    if due_date_str:
        try:
            return datetime.strptime(due_date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты")
    return None


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def post_login_page(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        session: AsyncSession = Depends(get_async_session)
):
    user = await UserService(session).find_one_or_none(email=email)
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth.html",
            {"request": request, "error": "Неверная почта или пароль"},
        )

    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse("/pages/boards", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("booking_access_token", token, httponly=True, path="/")
    return response


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse("regs.html", {"request": request})


@router.post("/register")
async def post_register_page(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        session: AsyncSession = Depends(get_async_session)
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
    return RedirectResponse("/pages/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/", response_class=RedirectResponse)
async def root_redirect(
        request: Request,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        token = get_token(request)
        await get_current_user(token, session)
        return RedirectResponse("/pages/boards", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        return RedirectResponse("/pages/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout")
async def logout_page():
    response = RedirectResponse(url="/pages/login", status_code=303)
    response.delete_cookie(
        key="booking_access_token",
        httponly=True,
        path="/"
    )
    return response


@router.get("/boards", response_class=HTMLResponse)
async def get_boards(
        request: Request,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        token = get_token(request)
        user = await get_current_user(token, session)
    except HTTPException:
        return RedirectResponse("/pages/login", status_code=status.HTTP_303_SEE_OTHER)

    boards = await BoardService(session).get_boards_with_tasks_count(user_id=user.id)
    return templates.TemplateResponse(
        "taskboard.html",
        {"request": request, "user": user, "boards": boards}
    )


@router.post("/boards")
async def create_board_form(
        request: Request,
        name: str = Form(...),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        token = get_token(request)
        user = await get_current_user(token, session)
    except HTTPException:
        return RedirectResponse("/pages/login", status_code=status.HTTP_303_SEE_OTHER)

    await BoardService(session).add_some(user_id=user.id, name=name)
    return RedirectResponse("/pages/boards", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/boards/{board_id}", response_class=HTMLResponse)
async def get_board_details(
        request: Request,
        board_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        token = get_token(request)
        user = await get_current_user(token, session)
    except HTTPException:
        return RedirectResponse("/pages/login", status_code=status.HTTP_303_SEE_OTHER)

    board = await BoardService(session).find_one_or_none(id=board_id, user_id=user.id)
    if not board:
        raise HTTPException(status_code=404, detail="Доска не найдена")

    task_svc = TaskService(session)
    tasks = await task_svc.get_all(board_id=board_id)
    return templates.TemplateResponse(
        "taskboard.html",
        {
            "request": request,
            "user": user,
            "boards": await BoardService(session).get_boards_with_tasks_count(user_id=user.id),
            "board": board,
            "planned_tasks": [t for t in tasks if t.status == "Запланировано"],
            "in_progress_tasks": [t for t in tasks if t.status == "В работе"],
            "completed_tasks": [t for t in tasks if t.status == "Готово"],
        }
    )


@router.post("/boards/{board_id}/tasks")
async def create_task_form(
        request: Request,
        board_id: int,
        task_name: str = Form(...),
        task_description: str = Form(None),
        due_date: str = Form(None),
        task_status: str = Form("Запланировано"),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        token = get_token(request)
        user = await get_current_user(token, session)
    except HTTPException:
        return RedirectResponse("/pages/login", status_code=status.HTTP_303_SEE_OTHER)

    await TaskService(session).add_some(
        user_id=user.id,
        email=user.email,
        board_id=board_id,
        task_name=task_name,
        task_description=task_description or None,
        due_date=parse_due_date_safe(due_date),
        status=task_status,
    )
    return RedirectResponse(f"/pages/boards/{board_id}", status_code=status.HTTP_303_SEE_OTHER)

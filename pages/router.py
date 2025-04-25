"""
Роуты для Jinja2-интерфейса.
Обрабатывают авторизацию, регистрацию, отображение досок и задач, а также формы создания и редактирования.
"""

from fastapi import (
    APIRouter, Request, Depends, HTTPException, Form, status
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
from typing import Optional

from taskapp.authenticate.auth import verify_password, create_access_token, get_password_hash
from taskapp.authenticate.dependencies import get_current_user, get_token
from taskapp.services.user_service import UserService
from taskapp.services.board_service import BoardService
from taskapp.models.user import Users

router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"],
)

templates = Jinja2Templates(directory="templates")


# —————— Вспомогательная функция ——————

def parse_due_date_safe(due_date_str: Optional[str]) -> Optional[datetime]:
    """
    Преобразует строку вида YYYY-MM-DD в объект datetime. Возвращает None при ошибке.
    """
    if due_date_str:
        try:
            return datetime.strptime(due_date_str, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Неверный формат даты")
    return None


# —————— AUTH ——————

@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@router.post("/login")
async def post_login_page(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
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


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse("regs.html", {"request": request})


@router.post("/register")
async def post_register_page(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    if await UserService.find_one_or_none(email=email):
        return templates.TemplateResponse(
            "regs.html",
            {"request": request, "error": "Пользователь с такой почтой уже существует"},
            status_code=status.HTTP_400_BAD_REQUEST
        )

    hashed = get_password_hash(password)
    await UserService.add_some(username=username, email=email, hashed_password=hashed)
    return RedirectResponse(url="/pages/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/", response_class=RedirectResponse)
async def root_redirect(request: Request):
    try:
        token = get_token(request)
        await get_current_user(token)
        return RedirectResponse(url="/pages/boards", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException:
        return RedirectResponse(url="/pages/login", status_code=status.HTTP_303_SEE_OTHER)


# —————— BOARDS ——————

@router.get("/boards", response_class=HTMLResponse)
async def get_boards(request: Request, current_user: Users = Depends(get_current_user)):
    boards = await BoardService.get_boards_with_tasks_count(user_id=current_user.id)
    return templates.TemplateResponse(
        "taskboard.html",
        {"request": request, "user": current_user, "boards": boards}
    )


@router.post("/boards")
async def create_board_form(
    name: str = Form(...),
    current_user: Users = Depends(get_current_user)
):
    await BoardService.add_some(user_id=current_user.id, name=name)
    return RedirectResponse(url="/pages/boards", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/boards/{board_id}/edit")
async def edit_board_form(
    board_id: int,
    name: str = Form(...),
    current_user: Users = Depends(get_current_user)
):
    await BoardService.update_some(model_id=board_id, user_id=current_user.id, name=name)
    return RedirectResponse(url=f"/pages/boards/{board_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/boards/{board_id}/delete")
async def delete_board_form(
    board_id: int,
    current_user: Users = Depends(get_current_user)
):
    await BoardService.delete_some(model_id=board_id, user_id=current_user.id)
    return RedirectResponse(url="/pages/boards", status_code=status.HTTP_303_SEE_OTHER)


# —————— BOARD DETAILS / TASKS ——————

@router.get("/boards/{board_id}", response_class=HTMLResponse)
async def get_board_details(
    request: Request,
    board_id: int,
    current_user: Users = Depends(get_current_user)
):
    from taskapp.services.task_service import TaskService

    board = await BoardService.find_one_or_none(id=board_id, user_id=current_user.id)
    if not board:
        raise HTTPException(status_code=404, detail="Доска не найдена")

    tasks = await TaskService.get_all(board_id=board_id)
    planned = [t for t in tasks if t.status == "Запланировано"]
    in_prog = [t for t in tasks if t.status == "В работе"]
    complete = [t for t in tasks if t.status == "Готово"]

    boards = await BoardService.get_boards_with_tasks_count(user_id=current_user.id)
    return templates.TemplateResponse(
        "taskboard.html",
        {
            "request": request,
            "user": current_user,
            "boards": boards,
            "board": board,
            "planned_tasks": planned,
            "in_progress_tasks": in_prog,
            "completed_tasks": complete,
        }
    )


@router.post("/boards/{board_id}/tasks")
async def create_task_form(
    board_id: int,
    task_name: str = Form(...),
    task_description: str = Form(None),
    due_date: str = Form(None),
    task_status: str = Form("Запланировано"),
    current_user: Users = Depends(get_current_user)
):
    from taskapp.services.task_service import TaskService

    due_date_dt = parse_due_date_safe(due_date)

    await TaskService.add_some(
        user_id=current_user.id,
        email=current_user.email,
        board_id=board_id,
        task_name=task_name,
        task_description=task_description or None,
        due_date=due_date_dt,
        status=task_status,
    )
    return RedirectResponse(url=f"/pages/boards/{board_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/boards/{board_id}/tasks/{task_id}/edit")
async def edit_task_form(
    board_id: int,
    task_id: int,
    task_name: str = Form(...),
    task_description: str = Form(None),
    due_date: str = Form(None),
    current_user: Users = Depends(get_current_user)
):
    from taskapp.services.task_service import TaskService

    due_date_dt = parse_due_date_safe(due_date)

    await TaskService.update_some(
        model_id=task_id,
        user_id=current_user.id,
        task_name=task_name,
        task_description=task_description or None,
        due_date=due_date_dt,
    )
    return RedirectResponse(url=f"/pages/boards/{board_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/boards/{board_id}/tasks/{task_id}/delete")
async def delete_task_form(
    board_id: int,
    task_id: int,
    current_user: Users = Depends(get_current_user)
):
    from taskapp.services.task_service import TaskService
    await TaskService.delete_some(model_id=task_id, user_id=current_user.id)
    return RedirectResponse(url=f"/pages/boards/{board_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/boards/{board_id}/tasks/{task_id}/status")
async def change_task_status_form(
    board_id: int,
    task_id: int,
    status_value: str = Form(...),
    current_user: Users = Depends(get_current_user)
):
    from taskapp.services.task_service import TaskService
    await TaskService.update_some(model_id=task_id, user_id=current_user.id, status=status_value)
    return RedirectResponse(url=f"/pages/boards/{board_id}", status_code=status.HTTP_303_SEE_OTHER)

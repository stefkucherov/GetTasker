from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

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


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def post_login_page(
        request: Request,
        email: str = Form(...),
        password: str = Form(...)
):
    user = await UserService.find_one_or_none(email=email)
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth.html",
            {"request": request, "error": "Неверная почта или пароль"},
            status_code=400
        )

    token = create_access_token({"sub": str(user.id)})
    response = RedirectResponse(url="/pages/boards", status_code=302)
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


@router.post("/register", response_class=HTMLResponse)
async def post_register_page(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...)
):
    if await UserService.find_one_or_none(email=email):
        return templates.TemplateResponse(
            "regs.html",
            {"request": request, "error": "Пользователь с такой почтой уже существует"},
            status_code=400
        )

    hashed = get_password_hash(password)
    await UserService.add_some(
        username=username,
        email=email,
        hashed_password=hashed
    )

    return RedirectResponse(url="/pages/login", status_code=302)


@router.get("/", response_class=RedirectResponse)
async def root_redirect(request: Request):
    try:
        token = get_token(request)
        await get_current_user(token)
        return RedirectResponse(url="/pages/boards")
    except HTTPException:
        return RedirectResponse(url="/pages/login")


@router.get("/boards", response_class=HTMLResponse)
async def get_boards(request: Request, current_user: Users = Depends(get_current_user)):
    boards = await BoardService.get_boards_with_tasks_count(user_id=current_user.id)
    return templates.TemplateResponse(
        "taskboard.html",
        {"request": request, "user": current_user, "boards": boards}
    )


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

    return templates.TemplateResponse(
        "taskboard.html",
        {
            "request": request,
            "user": current_user,
            "boards": [],  # этот параметр необязателен здесь
            "board": board,
            "planned_tasks": planned,
            "in_progress_tasks": in_prog,
            "completed_tasks": complete,
        }
    )

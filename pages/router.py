from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from taskapp.authenticate.dependencies import get_current_user
from taskapp.models.user import Users
from taskapp.services.board_service import BoardService

router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"],
)

templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse("auth.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    """Страница регистрации"""
    return templates.TemplateResponse("regs.html", {"request": request})


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Перенаправление на доски или на страницу входа"""
    try:
        user = await get_current_user(request)
        return RedirectResponse(url="/pages/boards")
    except:
        return RedirectResponse(url="/pages/login")


@router.get("/boards", response_class=HTMLResponse)
async def get_boards(
        request: Request,
        current_user: Users = Depends(get_current_user)
):
    """Список досок пользователя"""
    boards = await BoardService.get_boards_with_tasks_count(user_id=current_user.id)

    return templates.TemplateResponse(
        "taskboard.html",
        {
            "request": request,
            "user": current_user,
            "boards": boards
        }
    )


@router.get("/boards/{board_id}", response_class=HTMLResponse)
async def get_board_details(
        request: Request,
        board_id: int,
        current_user: Users = Depends(get_current_user)
):
    """Детальная страница доски с задачами"""
    board = await BoardService.find_one_or_none(id=board_id, user_id=current_user.id)
    if not board:
        raise HTTPException(status_code=404, detail="Доска не найдена")

    from taskapp.services.task_service import TaskService

    # Получаем задачи, сгруппированные по статусу
    tasks = await TaskService.get_all(board_id=board_id)

    planned_tasks = [task for task in tasks if task.status == "Запланировано"]
    in_progress_tasks = [task for task in tasks if task.status == "В работе"]
    completed_tasks = [task for task in tasks if task.status == "Готово"]

    return templates.TemplateResponse(
        "taskboard.html",
        {
            "request": request,
            "user": current_user,
            "board": board,
            "planned_tasks": planned_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completed_tasks": completed_tasks
        }
    )

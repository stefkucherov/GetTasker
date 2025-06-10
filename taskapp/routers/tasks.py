"""
Модуль роутера для работы с задачами.
Реализует CRUD операции для задач с использованием FastAPI.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, status, Query, HTTPException

from taskapp.authenticate.dependencies import get_current_user, verify_ownership
from taskapp.models.user import Users
from taskapp.schemas.tasks import TaskCreate, TaskUpdate, TaskOut, TaskStatusUpdate
from taskapp.services.board_service import BoardService, get_board_service
from taskapp.services.task_service import TaskService, get_task_service

router = APIRouter(
    prefix="/tasks",
    tags=["Задачи"],
)


@router.get("/", response_model=List[TaskOut])
async def get_tasks(
        board_id: Optional[int] = Query(None),
        status_filter: Optional[str] = Query(None),
        current_user: Users = Depends(get_current_user),
        task_svc: TaskService = Depends(get_task_service),
        board_svc: BoardService = Depends(get_board_service),
) -> List[TaskOut]:
    """
    Получает список задач текущего пользователя.
    Можно фильтровать по ID доски и по статусу.
    """
    params = {"user_id": current_user.id}

    if board_id is not None:
        await verify_ownership(board_svc, board_id, current_user.id)
        params["board_id"] = board_id

    if status_filter:
        params["status"] = status_filter

    tasks = await task_svc.get_all(**params)
    return [TaskOut.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
        task_id: int,
        current_user: Users = Depends(get_current_user),
        task_svc: TaskService = Depends(get_task_service),
) -> TaskOut:
    """
    Получает задачу по её ID, если она принадлежит текущему пользователю.
    """
    await verify_ownership(task_svc, task_id, current_user.id)

    task = await task_svc.find_one_or_none(id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return TaskOut.model_validate(task)


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
        task_data: TaskCreate,
        current_user: Users = Depends(get_current_user),
        task_svc: TaskService = Depends(get_task_service),
        board_svc: BoardService = Depends(get_board_service),
) -> TaskOut:
    """
    Создаёт новую задачу на указанной доске.
    Проверяет, что доска принадлежит текущему пользователю.
    """
    await verify_ownership(board_svc, task_data.board_id, current_user.id)

    task = await task_svc.add_some(
        user_id=current_user.id,
        email=current_user.email,
        **task_data.model_dump()
    )
    return TaskOut.model_validate(task)


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
        task_id: int,
        task_data: TaskUpdate,
        current_user: Users = Depends(get_current_user),
        task_svc: TaskService = Depends(get_task_service),
        board_svc: BoardService = Depends(get_board_service),
) -> TaskOut:
    """
    Обновляет задачу. Проверяет, что задача и новая доска принадлежат текущему пользователю.
    """
    await verify_ownership(task_svc, task_id, current_user.id)

    if task_data.board_id is not None:
        await verify_ownership(board_svc, task_data.board_id, current_user.id)

    task = await task_svc.update_some(
        model_id=task_id,
        user_id=current_user.id,
        **task_data.model_dump(exclude_unset=True)
    )
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return TaskOut.model_validate(task)


@router.patch("/{task_id}/status", response_model=TaskOut)
async def update_task_status(
        task_id: int,
        status_data: TaskStatusUpdate,
        current_user: Users = Depends(get_current_user),
        task_svc: TaskService = Depends(get_task_service),
) -> TaskOut:
    """
    Обновляет только статус задачи.
    Использует строго типизированный Enum TaskStatus.
    """
    await verify_ownership(task_svc, task_id, current_user.id)

    task = await task_svc.update_some(
        model_id=task_id,
        user_id=current_user.id,
        status=status_data.status
    )
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return TaskOut.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        current_user: Users = Depends(get_current_user),
        task_svc: TaskService = Depends(get_task_service),
):
    """
    Удаляет задачу, если она принадлежит текущему пользователю.
    """
    await verify_ownership(task_svc, task_id, current_user.id)
    await task_svc.delete_some(model_id=task_id, user_id=current_user.id)

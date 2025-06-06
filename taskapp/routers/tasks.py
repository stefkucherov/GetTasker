"""
Модуль роутера для работы с задачами.
Реализует CRUD операции для задач с использованием FastAPI.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from taskapp.authenticate.dependencies import get_current_user
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
    params = {"user_id": current_user.id}

    if board_id is not None:
        if not await board_svc.find_one_or_none(id=board_id, user_id=current_user.id):
            raise HTTPException(status_code=404, detail="board not found")
        params["board_id"] = board_id

    if status_filter:
        params["status"] = status_filter

    return await task_svc.get_all(**params)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
        task_id: int,
        current_user: Users = Depends(get_current_user),
        task_svc: TaskService = Depends(get_task_service),
) -> TaskOut:
    task = await task_svc.find_one_or_none(id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
        task_data: TaskCreate,
        current_user: Users = Depends(get_current_user),
        task_svc: TaskService = Depends(get_task_service),
        board_svc: BoardService = Depends(get_board_service),
) -> TaskOut:
    if not await board_svc.find_one_or_none(id=task_data.board_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="board not found")

    return await task_svc.add_some(
        user_id=current_user.id,
        email=current_user.email,
        **task_data.model_dump()
    )


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
        task_id: int,
        task_data: TaskUpdate,
        current_user: Users = Depends(get_current_user),
        task_svc: TaskService = Depends(get_task_service),
        board_svc: BoardService = Depends(get_board_service),
) -> TaskOut:
    if not await task_svc.find_one_or_none(id=task_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="task not found")

    if task_data.board_id is not None:
        if not await board_svc.find_one_or_none(id=task_data.board_id, user_id=current_user.id):
            raise HTTPException(status_code=404, detail="board not found")

    return await task_svc.update_some(
        model_id=task_id,
        user_id=current_user.id,
        **task_data.model_dump(exclude_unset=True)
    )


@router.patch("/{task_id}/status", response_model=TaskOut)
async def update_task_status(
        task_id: int,
        status_data: TaskStatusUpdate,
        current_user: Users = Depends(get_current_user),
        task_svc: TaskService = Depends(get_task_service),
) -> TaskOut:
    valid = ["Запланировано", "В работе", "Готово"]
    if status_data.status not in valid:
        raise HTTPException(status_code=400, detail="invalid status")

    if not await task_svc.find_one_or_none(id=task_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="task not found")

    return await task_svc.update_some(
        model_id=task_id,
        user_id=current_user.id,
        status=status_data.status
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        current_user: Users = Depends(get_current_user),
        task_svc: TaskService = Depends(get_task_service),
):
    if not await task_svc.find_one_or_none(id=task_id, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="task not found")

    await task_svc.delete_some(model_id=task_id, user_id=current_user.id)

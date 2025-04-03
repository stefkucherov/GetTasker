"""
Модуль роутера для работы с задачами.
Реализует CRUD операции для задач с использованием FastAPI.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from taskapp.schemas.tasks import TaskCreate, TaskUpdate, TaskOut
from taskapp.services.task_service import TaskService
from taskapp.authenticate.dependencies import get_current_user
from taskapp.models.task import Tasks
from taskapp.models.user import Users

router = APIRouter(
    prefix="/tasks",
    tags=["Задачи"],
)


@router.get("/", response_model=List[TaskOut])
async def get_all_tasks(
        current_user: Users = Depends(get_current_user)
) -> List[TaskOut]:
    """
    Получить список всех задач текущего пользователя
    """
    try:
        tasks = await TaskService.get_all(user_id=current_user.id)
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
        task_id: int,
        current_user: Users = Depends(get_current_user)
) -> TaskOut:
    """
    Получить задачу по ID
    """
    task = await TaskService.find_one_or_none(id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    return task


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
        task_data: TaskCreate,
        current_user: Users = Depends(get_current_user)
) -> TaskOut:
    """
    Создать новую задачу
    """
    try:
        return await TaskService.add_some(
            user_id=current_user.id,
            email=current_user.email,
            **task_data.model_dump()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
        task_id: int,
        task_data: TaskUpdate,
        current_user: Users = Depends(get_current_user)
) -> TaskOut:
    """
    Обновить существующую задачу
    """
    updated = await TaskService.update_some(
        model_id=task_id,
        user_id=current_user.id,
        **task_data.model_dump()
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        current_user: Users = Depends(get_current_user)
):
    """
    Удалить задачу
    """
    success = await TaskService.delete_some(model_id=task_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"

        )

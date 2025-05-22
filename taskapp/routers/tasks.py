"""
Модуль роутера для работы с задачами.
Реализует CRUD операции для задач с использованием FastAPI.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from uuid import UUID

from taskapp.schemas.tasks import TaskCreate, TaskUpdate, TaskOut, TaskStatusUpdate
from taskapp.services.task_service import TaskService, get_task_service
from taskapp.services.board_service import BoardService, get_board_service
from taskapp.authenticate.dependencies import get_current_user
from taskapp.models.user import Users

router = APIRouter(
    prefix="/tasks",
    tags=["Задачи"],
)


@router.get("/", response_model=List[TaskOut])
async def get_tasks(
        board_id: Optional[int] = Query(None, description="ID доски для фильтрации задач"),
        status_filter: Optional[str] = Query(None, description="Фильтр статуса задачи"),
        current_user: Users = Depends(get_current_user),
        task_service: TaskService = Depends(get_task_service),
        board_service: BoardService = Depends(get_board_service)
) -> List[TaskOut]:
    """
    Получить список задач текущего пользователя с возможностью фильтрации
    """
    try:
        filter_params = {"user_id": current_user.id}

        if board_id is not None:
            # Проверяем, что доска принадлежит пользователю
            board = await board_service.find_one_or_none(id=board_id, user_id=current_user.id)
            if not board:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Доска не найдена"
                )
            filter_params["board_id"] = board_id

        if status_filter:
            filter_params["status"] = status_filter

        tasks = await task_service.get_all(**filter_params)
        return tasks
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
        task_id: int,
        current_user: Users = Depends(get_current_user),
        task_service: TaskService = Depends(get_task_service)
) -> TaskOut:
    """
    Получить задачу по ID
    """
    task = await task_service.find_one_or_none(id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )
    return task


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
        task_data: TaskCreate,
        current_user: Users = Depends(get_current_user),
        task_service: TaskService = Depends(get_task_service),
        board_service: BoardService = Depends(get_board_service)
) -> TaskOut:
    """
    Создать новую задачу
    """
    try:
        # Проверяем, что доска принадлежит пользователю
        board = await board_service.find_one_or_none(id=task_data.board_id, user_id=current_user.id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Доска не найдена"
            )

        return await task_service.add_some(
            user_id=current_user.id,
            email=current_user.email,
            **task_data.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
        task_id: int,
        task_data: TaskUpdate,
        current_user: Users = Depends(get_current_user),
        task_service: TaskService = Depends(get_task_service),
        board_service: BoardService = Depends(get_board_service)
) -> TaskOut:
    """
    Обновить существующую задачу
    """
    # Проверяем, что задача существует и принадлежит пользователю
    task = await task_service.find_one_or_none(id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    # Если указан новый board_id, проверяем, что доска принадлежит пользователю
    if task_data.board_id is not None:
        board = await board_service.find_one_or_none(id=task_data.board_id, user_id=current_user.id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Доска не найдена"
            )

    updated = await task_service.update_some(
        model_id=task_id,
        user_id=current_user.id,
        **task_data.model_dump(exclude_unset=True)
    )

    return updated


@router.patch("/{task_id}/status", response_model=TaskOut)
async def update_task_status(
        task_id: int,
        status_data: TaskStatusUpdate,
        current_user: Users = Depends(get_current_user),
        task_service: TaskService = Depends(get_task_service)
) -> TaskOut:
    """
    Обновить только статус задачи
    """
    # Проверяем валидность статуса
    valid_statuses = ["Запланировано", "В работе", "Готово"]
    if status_data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неверный статус. Допустимые значения: {', '.join(valid_statuses)}"
        )

    # Проверяем, что задача существует и принадлежит пользователю
    task = await task_service.find_one_or_none(id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    updated = await task_service.update_some(
        model_id=task_id,
        user_id=current_user.id,
        status=status_data.status
    )

    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        current_user: Users = Depends(get_current_user),
        task_service: TaskService = Depends(get_task_service)
):
    """
    Удалить задачу
    """
    task = await task_service.find_one_or_none(id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена"
        )

    success = await task_service.delete_some(model_id=task_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении задачи"
        )

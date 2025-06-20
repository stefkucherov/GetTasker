"""
Модуль роутера для работы с досками.
Реализует CRUD операции для досок с использованием FastAPI.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from taskapp.authenticate.dependencies import get_current_user, verify_ownership
from taskapp.models.user import Users
from taskapp.schemas.boards import BoardCreate, BoardUpdate, BoardOut, BoardWithTasks
from taskapp.services.board_service import BoardService, get_board_service
from taskapp.services.task_service import TaskService, get_task_service

router = APIRouter(
    prefix="/boards",
    tags=["Доски задач"],
)


@router.get("/", response_model=List[BoardOut])
async def get_all_boards(
        current_user: Users = Depends(get_current_user),
        board_service: BoardService = Depends(get_board_service),
) -> List[BoardOut]:
    """
    Получает список всех досок текущего пользователя с количеством задач.
    """
    try:
        boards = await board_service.get_boards_with_tasks_count(user_id=current_user.id)
        return [BoardOut.model_validate(board) for board in boards]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{board_id}", response_model=BoardWithTasks)
async def get_board(
        board_id: int,
        current_user: Users = Depends(get_current_user),
        board_service: BoardService = Depends(get_board_service),
        task_service: TaskService = Depends(get_task_service),
) -> BoardWithTasks:
    """
    Получает доску по её ID вместе со списком всех задач.
    Проверяет, что доска принадлежит текущему пользователю.
    """
    await verify_ownership(board_service, board_id, current_user.id)

    board = await board_service.find_by_id(board_id)
    tasks = await task_service.get_all(board_id=board_id)

    board_data = BoardWithTasks.model_validate(board)
    board_data.tasks = tasks
    return board_data


@router.post("/", response_model=BoardOut, status_code=status.HTTP_201_CREATED)
async def create_board(
        board_data: BoardCreate,
        current_user: Users = Depends(get_current_user),
        board_service: BoardService = Depends(get_board_service),
) -> BoardOut:
    """
    Создаёт новую доску для текущего пользователя.
    """
    try:
        board = await board_service.add_some(
            user_id=current_user.id,
            **board_data.model_dump()
        )
        return BoardOut.model_validate(board)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{board_id}", response_model=BoardOut)
async def update_board(
        board_id: int,
        board_data: BoardUpdate,
        current_user: Users = Depends(get_current_user),
        board_service: BoardService = Depends(get_board_service),
) -> BoardOut:
    """
    Обновляет существующую доску текущего пользователя.
    Проверяет, что доска принадлежит текущему пользователю.
    """
    await verify_ownership(board_service, board_id, current_user.id)

    board = await board_service.update_some(
        model_id=board_id,
        user_id=current_user.id,
        **board_data.model_dump(exclude_unset=True)
    )
    if not board:
        raise HTTPException(status_code=404, detail="Доска не найдена")
    return BoardOut.model_validate(board)


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
        board_id: int,
        current_user: Users = Depends(get_current_user),
        board_service: BoardService = Depends(get_board_service),
):
    """
    Удаляет доску и все связанные задачи.
    Проверяет, что доска принадлежит текущему пользователю.
    """
    await verify_ownership(board_service, board_id, current_user.id)

    success = await board_service.delete_some(model_id=board_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении доски"
        )

from datetime import datetime, timedelta, UTC

import pytest
from httpx import AsyncClient

from taskapp.models.board import Boards
from taskapp.models.task import Tasks


@pytest.mark.asyncio
async def test_get_all_tasks_success(authenticated_ac: AsyncClient, test_task: Tasks):
    """
    Проверяет успешное получение всех задач.
    Ожидается, что возвращается список, содержащий тестовую задачу.
    """
    response = await authenticated_ac.get("/tasks/")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list), "Response should be a list of tasks"
    assert any(task["id"] == test_task.id for task in tasks), "Test task not found in response"


@pytest.mark.asyncio
async def test_get_tasks_with_board_filter(authenticated_ac: AsyncClient, test_task: Tasks, test_board: Boards):
    """
    Проверяет фильтрацию задач по ID доски.
    Все задачи в ответе должны принадлежать указанной доске.
    """
    response = await authenticated_ac.get(f"/tasks/?board_id={test_board.id}")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list), "Response should be a list of tasks"
    assert all(task["board_id"] == test_board.id for task in tasks), "Filtered tasks should all belong to test board"


@pytest.mark.asyncio
async def test_get_tasks_with_status_filter(authenticated_ac: AsyncClient, test_task: Tasks):
    """
    Проверяет фильтрацию задач по статусу.
    Все возвращённые задачи должны иметь запрошенный статус.
    """
    status = "Запланировано"
    response = await authenticated_ac.get(f"/tasks/?status_filter={status}")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list), "Response should be a list of tasks"
    if tasks:
        assert all(task["status"] == status for task in tasks), "All filtered tasks should have requested status"


@pytest.mark.asyncio
async def test_get_task_by_id_success(authenticated_ac: AsyncClient, test_task: Tasks):
    """
    Проверяет успешное получение задачи по ID.
    """
    response = await authenticated_ac.get(f"/tasks/{test_task.id}")
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == test_task.id
    assert task["task_name"] == test_task.task_name


@pytest.mark.asyncio
async def test_get_task_not_found(authenticated_ac: AsyncClient):
    """
    Проверяет, что запрос несуществующей задачи возвращает 404.
    """
    response = await authenticated_ac.get("/tasks/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower() or "не найден" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_task_success(authenticated_ac: AsyncClient, test_board: Boards):
    """
    Проверяет успешное создание новой задачи.
    После создания задача удаляется (cleanup).
    """
    due_date = (datetime.now(UTC) + timedelta(days=1)).isoformat()

    payload = {
        "task_name": "New Task",
        "task_description": "Task description",
        "status": "Запланировано",
        "due_date": due_date,
        "board_id": test_board.id
    }

    response = await authenticated_ac.post("/tasks/", json=payload)
    assert response.status_code == 201
    task = response.json()
    assert task["task_name"] == payload["task_name"]
    assert task["board_id"] == test_board.id

    # Clean up - delete the task we just created
    delete_response = await authenticated_ac.delete(f"/tasks/{task['id']}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_update_task_success(authenticated_ac: AsyncClient, test_task: Tasks, test_board: Boards):
    """
    Проверяет успешное обновление задачи.
    """
    due_date = (datetime.now(UTC) + timedelta(days=3)).isoformat()

    update_data = {
        "task_name": "Updated Task Name",
        "task_description": "Updated description",
        "status": "В работе",
        "due_date": due_date,
        "board_id": test_board.id
    }

    response = await authenticated_ac.put(f"/tasks/{test_task.id}", json=update_data)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["task_name"] == update_data["task_name"]
    assert updated_task["status"] == update_data["status"]


@pytest.mark.asyncio
async def test_update_task_status_success(authenticated_ac: AsyncClient, test_task: Tasks):
    """
    Проверяет успешное обновление только статуса задачи.
    """
    status_data = {"status": "Готово"}
    response = await authenticated_ac.patch(f"/tasks/{test_task.id}/status", json=status_data)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["status"] == status_data["status"]
    assert updated_task["id"] == test_task.id


@pytest.mark.asyncio
async def test_delete_task_success(authenticated_ac: AsyncClient, test_board: Boards):
    """
    Проверяет успешное удаление задачи.
    Создаёт задачу, удаляет её, затем проверяет, что она не доступна.
    """
    create_response = await authenticated_ac.post(
        "/tasks/",
        json={
            "task_name": "Task to Delete",
            "task_description": "Will be deleted",
            "status": "Запланировано",
            "board_id": test_board.id
        }
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Now delete it
    response = await authenticated_ac.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await authenticated_ac.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_task_unauthorized_access(ac: AsyncClient, test_task: Tasks):
    """
    Проверяет, что доступ к задаче без авторизации запрещён.
    """
    response = await ac.get(f"/tasks/{test_task.id}")
    assert response.status_code == 401
    assert "токен истек" in response.json()["detail"].lower() or "не авторизован" in response.json()["detail"].lower()

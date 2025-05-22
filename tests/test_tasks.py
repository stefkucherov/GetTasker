import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, UTC
from taskapp.models.task import Tasks
from taskapp.models.board import Boards


@pytest.mark.asyncio
async def test_get_all_tasks_success(authenticated_ac: AsyncClient, test_task: Tasks):
    """Test successfully retrieving all tasks."""
    response = await authenticated_ac.get("/tasks/")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list), "Response should be a list of tasks"
    assert any(task["id"] == test_task.id for task in tasks), "Test task not found in response"


@pytest.mark.asyncio
async def test_get_tasks_with_board_filter(authenticated_ac: AsyncClient, test_task: Tasks, test_board: Boards):
    """Test filtering tasks by board ID."""
    response = await authenticated_ac.get(f"/tasks/?board_id={test_board.id}")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list), "Response should be a list of tasks"
    assert all(task["board_id"] == test_board.id for task in tasks), "Filtered tasks should all belong to test board"


@pytest.mark.asyncio
async def test_get_tasks_with_status_filter(authenticated_ac: AsyncClient, test_task: Tasks):
    """Test filtering tasks by status."""
    status = "Запланировано"
    response = await authenticated_ac.get(f"/tasks/?status_filter={status}")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list), "Response should be a list of tasks"
    if tasks:
        assert all(task["status"] == status for task in tasks), "All filtered tasks should have requested status"


@pytest.mark.asyncio
async def test_get_task_by_id_success(authenticated_ac: AsyncClient, test_task: Tasks):
    """Test successfully retrieving a specific task by ID."""
    response = await authenticated_ac.get(f"/tasks/{test_task.id}")
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == test_task.id
    assert task["task_name"] == test_task.task_name


@pytest.mark.asyncio
async def test_get_task_not_found(authenticated_ac: AsyncClient):
    """Test attempting to get a non-existent task returns 404."""
    response = await authenticated_ac.get("/tasks/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower() or "не найден" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_task_success(authenticated_ac: AsyncClient, test_board: Boards):
    """Test successfully creating a new task."""
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
async def test_create_task_invalid_board(authenticated_ac: AsyncClient):
    """Test creating a task with non-existent board ID fails."""
    due_date = (datetime.now(UTC) + timedelta(days=1)).isoformat()

    payload = {
        "task_name": "Invalid Task",
        "task_description": "desc",
        "status": "Запланировано",
        "due_date": due_date,
        "board_id": 999999
    }

    response = await authenticated_ac.post("/tasks/", json=payload)
    assert response.status_code == 404
    assert "board" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_task_success(authenticated_ac: AsyncClient, test_task: Tasks, test_board: Boards):
    """Test successfully updating a task."""
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
    """Test successfully updating only a task's status."""
    status_data = {"status": "Готово"}
    response = await authenticated_ac.patch(f"/tasks/{test_task.id}/status", json=status_data)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["status"] == status_data["status"]
    assert updated_task["id"] == test_task.id


@pytest.mark.asyncio
async def test_update_task_status_invalid(authenticated_ac: AsyncClient, test_task: Tasks):
    """Test updating a task with invalid status fails."""
    response = await authenticated_ac.patch(
        f"/tasks/{test_task.id}/status",
        json={"status": "Неверный статус"}
    )
    assert response.status_code == 400
    assert "status" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_task_success(authenticated_ac: AsyncClient, test_board: Boards):
    """Test successfully deleting a task."""
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
    """Test that unauthorized access to tasks fails."""
    response = await ac.get(f"/tasks/{test_task.id}")
    assert response.status_code == 401
    assert "токен истек" in response.json()["detail"].lower() or "не авторизован" in response.json()["detail"].lower()

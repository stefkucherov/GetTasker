// Функции для работы с API

// Базовый URL API
const API_BASE_URL = "http://localhost:8000";

// Общая функция для выполнения запроса к API
async function apiRequest(url, method = "GET", data = null) {
    const options = {
        method,
        headers: {
            "Content-Type": "application/json"
        },
        credentials: "include" // Включаем отправку куки для аутентификации
    };

    if (data && (method === "POST" || method === "PUT" || method === "PATCH")) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(`${API_BASE_URL}${url}`, options);

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Ошибка запроса: ${response.status}`);
    }

    if (response.status === 204) {
        return null; // No content
    }

    return await response.json();
}

// Функции для работы с пользователями
const auth = {
    async register(email, password) {
        return await apiRequest("/auth/register", "POST", { email, password });
    },

    async login(email, password) {
        return await apiRequest("/auth/login", "POST", { email, password });
    },

    async logout() {
        return await apiRequest("/auth/logout", "POST");
    },

    async getProfile() {
        return await apiRequest("/auth/me");
    }
};

// Функции для работы с досками
const boards = {
    async getAll() {
        return await apiRequest("/boards");
    },

    async getById(boardId) {
        return await apiRequest(`/boards/${boardId}`);
    },

    async create(name) {
        return await apiRequest("/boards", "POST", { name });
    },

    async update(boardId, data) {
        return await apiRequest(`/boards/${boardId}`, "PUT", data);
    },

    async delete(boardId) {
        return await apiRequest(`/boards/${boardId}`, "DELETE");
    }
};

// Функции для работы с задачами
const tasks = {
    async getAll(boardId = null, status = null) {
        let url = "/tasks";
        const params = [];

        if (boardId !== null) {
            params.push(`board_id=${boardId}`);
        }

        if (status !== null) {
            params.push(`status_filter=${encodeURIComponent(status)}`);
        }

        if (params.length > 0) {
            url += `?${params.join("&")}`;
        }

        return await apiRequest(url);
    },

    async getById(taskId) {
        return await apiRequest(`/tasks/${taskId}`);
    },

    async create(data) {
        return await apiRequest("/tasks", "POST", data);
    },

    async update(taskId, data) {
        return await apiRequest(`/tasks/${taskId}`, "PUT", data);
    },

    async updateStatus(taskId, status) {
        return await apiRequest(`/tasks/${taskId}/status`, "PATCH", { status });
    },

    async delete(taskId) {
        return await apiRequest(`/tasks/${taskId}`, "DELETE");
    }
};

// Настройка drag-and-drop функционала для задач
function initDragAndDrop() {
    const taskCards = document.querySelectorAll('.task-card');
    const taskColumns = document.querySelectorAll('.task-column');

    // Настройка перетаскиваемых элементов
    taskCards.forEach(card => {
        card.setAttribute('draggable', true);

        card.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', card.dataset.taskId);
            card.classList.add('dragging');
        });

        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
        });
    });

    // Настройка контейнеров для перетаскивания
    taskColumns.forEach(column => {
        column.addEventListener('dragover', (e) => {
            e.preventDefault();
            column.classList.add('bg-light');
        });

        column.addEventListener('dragleave', () => {
            column.classList.remove('bg-light');
        });

        column.addEventListener('drop', async (e) => {
            e.preventDefault();
            column.classList.remove('bg-light');

            const taskId = e.dataTransfer.getData('text/plain');
            const newStatus = column.dataset.status; // Предполагается, что у колонки есть атрибут data-status

            // Перемещаем карточку визуально
            const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
            column.querySelector('.tasks-container').appendChild(taskCard);

            try {
                // Обновляем статус задачи через API
                await tasks.updateStatus(taskId, newStatus);

                // Показываем уведомление об успешном обновлении
                showToast('Статус задачи успешно обновлен', 'success');
            } catch (error) {
                console.error('Ошибка при обновлении статуса:', error);
                showToast('Ошибка при обновлении статуса: ' + error.message, 'danger');

                // В случае ошибки можно вернуть карточку на прежнее место,
                // но для этого потребуется отслеживать исходное положение
            }
        });
    });
}

// Функция для показа уведомлений через Bootstrap Toast
function showToast(message, type = 'info') {
    // Создаем элемент для Toast
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        // Если контейнера нет, создаем его
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(container);
    }

    // Создаем Toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.id = toastId;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    document.getElementById('toast-container').appendChild(toast);

    // Инициализируем Toast через Bootstrap JS
    const bsToast = new bootstrap.Toast(toast, { autohide: true, delay: 3000 });
    bsToast.show();

    // Удаляем Toast из DOM после скрытия
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Инициализация функционала при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Добавляем контейнер для Toast уведомлений, если его еще нет
    if (!document.getElementById('toast-container')) {
        const toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }

    // Инициализируем drag-and-drop для задач
    initDragAndDrop();

    // Инициализация форм и кнопок
    initForms();

    // Обработчик выхода из системы
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                await auth.logout();
                window.location.href = '/pages/login';
            } catch (error) {
                showToast('Ошибка при выходе из системы: ' + error.message, 'danger');
            }
        });
    }
});

// Инициализация форм и обработчиков событий
function initForms() {
    // Форма входа
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(loginForm);
        const email = formData.get('email');
        const password = formData.get('password');

            try {
                await auth.login(email, password);
                window.location.href = '/pages/boards';
            } catch (error) {
                showToast('Ошибка при входе: ' + error.message, 'danger');
            }
        });
    }

    // Форма регистрации
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(registerForm);
            const email = formData.get('email');
            const password = formData.get('password');

            try {
                await auth.register(email, password);
                showToast('Регистрация прошла успешно! Теперь вы можете войти', 'success');
                window.location.href = '/pages/login';
            } catch (error) {
                showToast('Ошибка при регистрации: ' + error.message, 'danger');
            }
        });
    }

    // Форма создания новой доски
    const newBoardForm = document.getElementById('newBoardForm');
    if (newBoardForm) {
        newBoardForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(newBoardForm);
            const boardName = formData.get('name');

            try {
                await boards.create(boardName);
                window.location.reload(); // Перезагружаем страницу для отображения новой доски
            } catch (error) {
                showToast('Ошибка при создании доски: ' + error.message, 'danger');
            }
        });
    }

    // Форма создания новой задачи
    const newTaskForm = document.getElementById('newTaskForm');
    if (newTaskForm) {
        newTaskForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(newTaskForm);
            const taskData = {
                title: formData.get('title'),
                description: formData.get('description'),
                board_id: parseInt(formData.get('board_id')),
                status: formData.get('status') || 'Запланировано' // По умолчанию задача планируется
            };

            try {
                await tasks.create(taskData);
                // Перезагружаем страницу, чтобы показать новую задачу
                window.location.reload();

                // Сбрасываем форму
                newTaskForm.reset();

                // Закрываем модальное окно
                const modal = document.getElementById('newTaskModal');
                if (modal) {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) {
                        bsModal.hide();
                    }
                }
            } catch (error) {
                showToast('Ошибка при создании задачи: ' + error.message, 'danger');
            }
        });
    }

    // Инициализация кнопок редактирования задач
    document.querySelectorAll('.edit-task-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const taskId = btn.dataset.taskId;
            try {
                const task = await tasks.getById(taskId);
                openEditTaskModal(task);
            } catch (error) {
                showToast('Ошибка при получении данных задачи: ' + error.message, 'danger');
            }
        });
    });

    // Обработчики кнопок удаления доски
    document.querySelectorAll('.delete-board-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            if (confirm('Вы уверены, что хотите удалить эту доску?')) {
                const boardId = btn.dataset.boardId;
                try {
                    await boards.delete(boardId);
                    window.location.href = '/pages/boards'; // Перенаправляем на страницу со списком досок
                } catch (error) {
                    showToast('Ошибка при удалении доски: ' + error.message, 'danger');
                }
            }
        });
    });

    // Обработчики кнопок удаления задачи
    document.querySelectorAll('.delete-task-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation(); // Предотвращаем всплытие события
            if (confirm('Вы уверены, что хотите удалить эту задачу?')) {
                const taskId = btn.dataset.taskId;
                try {
                    await tasks.delete(taskId);
                    // Удаляем карточку задачи из DOM
                    const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
                    if (taskCard) {
                        taskCard.remove();
                    }
                    showToast('Задача успешно удалена', 'success');
                } catch (error) {
                    showToast('Ошибка при удалении задачи: ' + error.message, 'danger');
                }
            }
        });
    });

    // Инициализация формы редактирования задачи
    const editTaskForm = document.getElementById('editTaskForm');
    if (editTaskForm) {
        editTaskForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(editTaskForm);
            const taskId = formData.get('task_id');
            const taskData = {
                title: formData.get('title'),
                description: formData.get('description'),
                status: formData.get('status')
            };

            try {
                const updatedTask = await tasks.update(taskId, taskData);

                // Получаем текущий статус задачи для определения, нужно ли перемещать карточку
                const taskCard = document.querySelector(`[data-task-id="${taskId}"]`);
                const currentStatus = taskCard.closest('.task-column').dataset.status;

                // Если статус изменился, перезагружаем страницу
                if (currentStatus !== taskData.status) {
                    window.location.reload();
                } else {
                    // Иначе просто обновляем данные в карточке
                    taskCard.querySelector('.task-title').textContent = updatedTask.title;
                    const descriptionElement = taskCard.querySelector('.task-description');
                    if (descriptionElement) {
                        descriptionElement.textContent = updatedTask.description || '';
                    }
                }

                // Закрываем модальное окно
                const modal = document.getElementById('editTaskModal');
                if (modal) {
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) {
                        bsModal.hide();
                    }
                }

                showToast('Задача успешно обновлена', 'success');
            } catch (error) {
                showToast('Ошибка при обновлении задачи: ' + error.message, 'danger');
            }
        });
    }
}

// Функция для открытия модального окна редактирования задачи
function openEditTaskModal(task) {
    const modal = document.getElementById('editTaskModal');
    if (!modal) return;

    const form = modal.querySelector('form');
    if (!form) return;

    // Заполняем форму данными задачи
    form.elements['title'].value = task.title;
    form.elements['description'].value = task.description || '';
    form.elements['status'].value = task.status;
    form.elements['task_id'].value = task.id;

    // Открываем модальное окно
    const bsModal = new
    bootstrap.Modal(modal);
    bsModal.show();
}

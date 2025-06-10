# GetTasker — Task Management App

🗂️ Простое веб-приложение для управления задачами на FastAPI.

## 🚀 Возможности
- Регистрация и авторизация
- Управление досками
- Создание и отслеживание задач
- Статусы задач ("Запланировано", "В работе", "Готово")
- Веб-интерфейс (Jinja2)
- API-эндпоинты

## ⚙️ Стек
- Python 3.12+
- FastAPI
- PostgreSQL (asyncpg)
- SQLAlchemy
- Jinja2
- Alembic
- Pytest

## 📌 API и страницы: список эндпоинтов

### 🔐 Аутентификация (`/auth`)
| Метод | Путь           | Описание                                      |
|-------|----------------|-----------------------------------------------|
| GET   | /auth/login    | Отображает страницу входа                     |
| POST  | /auth/login    | Аутентификация пользователя, установка токена |
| GET   | /auth/register | Страница регистрации                          |
| POST  | /auth/register | Регистрация нового пользователя               |
| POST  | /auth/logout   | Удаление токена из cookie (логаут)            |
| GET   | /auth/me       | Получение информации о текущем пользователе   |

---

### 📋 Доски (`/boards`)
| Метод  | Путь         | Описание                           |
|--------|--------------|------------------------------------|
| GET    | /boards      | Получить список досок пользователя |
| GET    | /boards/{id} | Получить доску с задачами по ID    |
| POST   | /boards      | Создать новую доску                |
| PUT    | /boards/{id} | Обновить доску                     |
| DELETE | /boards/{id} | Удалить доску и связанные задачи   |

---

### ✅ Задачи (`/tasks`)
| Метод  | Путь               | Описание                                       |
|--------|--------------------|------------------------------------------------|
| GET    | /tasks             | Получить задачи (опционально по доске/статусу) |
| GET    | /tasks/{id}        | Получить задачу по ID                          |
| POST   | /tasks             | Создать задачу                                 |
| PUT    | /tasks/{id}        | Обновить задачу                                |
| PATCH  | /tasks/{id}/status | Изменить только статус задачи                  |
| DELETE | /tasks/{id}        | Удалить задачу                                 |

---

### 🖥️ HTML-страницы (`/pages`)
| Метод | Путь                                            | Описание                              |
|-------|-------------------------------------------------|---------------------------------------|
| GET   | /pages/login                                    | HTML-страница входа                   |
| POST  | /pages/login                                    | Обработка формы входа                 |
| GET   | /pages/register                                 | HTML-страница регистрации             |
| POST  | /pages/register                                 | Обработка формы регистрации           |
| GET   | /pages/boards                                   | Страница со списком досок             |
| POST  | /pages/boards                                   | Создание доски из формы               |
| POST  | /pages/boards/{board_id}/edit                   | Редактирование доски через форму      |
| POST  | /pages/boards/{board_id}/delete                 | Удаление доски через форму            |
| GET   | /pages/boards/{board_id}                        | Просмотр задач по доске               |
| POST  | /pages/boards/{board_id}/tasks                  | Создание задачи через HTML-форму      |
| POST  | /pages/boards/{board_id}/tasks/{task_id}/edit   | Редактирование задачи через форму     |
| POST  | /pages/boards/{board_id}/tasks/{task_id}/delete | Удаление задачи через форму           |
| POST  | /pages/boards/{board_id}/tasks/{task_id}/status | Обновление статуса задачи через форму |

---

🛡️ Все API-защищенные маршруты требуют авторизации.  
🍰 Для frontend-интерфейса используются Jinja2-шаблоны (`/pages/...`).

## 📸 Скриншоты интерфейса

Ниже представлены скриншоты ключевых страниц приложения GetTasker, демонстрирующие функциональность веб-интерфейса.

### Страница авторизации
![Страница авторизации](screenshots/login.jpg)
*Вход в систему с использованием логина и пароля.*

### Страница регистрации
![Страница регистрации](screenshots/register.jpg)
*Регистрация в системе.*

### Доска задач
![Доска задач](screenshots/alltaskboard.jpg)
*Управление задачами с возможностью изменения статуса ("Запланировано", "В работе", "Готово").*

### Управление задачами
![Создание новой задачи](screenshots/taskcreate.jpg)
*Форма для добавления новой задачи на доску.*

![Редактирование задачи](screenshots/taskedit.jpg)
*Функционал редактирования задачи.*

![Удаление задачи](screenshots/deletetask.jpg)
*Функционал удаления задачи.*

### Управление досками 
![Создание новой доски](screenshots/boardcreate.jpg)
*Форма для добавления новой доски.*

![Редактирование доски](screenshots/boardedit.jpg)
*Функционал редактирования доски.*

![Удаление доски](screenshots/deleteboard.jpg)
*Функционал удаления доски.*

## 📦 Установка и запуск проекта
Следуйте приведённым ниже шагам для локального развертывания проекта.
### 1. Клонирование репозитория
Склонируйте проект с GitHub:
```bash
git clone https://github.com/yourusername/gettasker.git
cd gettasker
````

### 2. Создание и активация виртуального окружения

Для Unix/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Для Windows (CMD):

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Установка зависимостей

Убедитесь, что вы в активированном виртуальном окружении:

```bash
pip install -r requirements.txt
```

Если вы используете Poetry:

```bash
poetry install
```

### 4. Настройка переменных окружения (.env), (.env.test)

Создайте файл `.env` в корне проекта и укажите в нём:

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=projectbase

SECRET_KEY=your_secret_key
ALGORITHM=HS256

Эти переменные автоматически собираются в DATABASE_URL внутри настроек приложения
# Или укажите полную строку подключения напрямую:
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/projectbase
```

Для тестов создайте аналогично файл `.env.test` (опционально).

### 5. Настройка базы данных

Убедитесь, что у вас установлен PostgreSQL и создана база данных `projectbase`.

Примените миграции Alembic:

```bash
alembic upgrade head
```

Если база данных отсутствует, создайте её:

```bash
createdb -U postgres projectbase
```

### 6. Запуск проекта

Запустите сервер разработки:

```bash
uvicorn taskapp.main:app --reload
```

Теперь приложение будет доступно по адресу:

```
http://127.0.0.1:8000
```

### 7. Доступные интерфейсы

* Веб-интерфейс (Jinja2): [http://127.0.0.1:8000/pages/login](http://127.0.0.1:8000/pages/login)
* Swagger (API документация): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Запуск тестов

Для запуска всех тестов:

```bash
pytest -v --tb=short -rA
```
## 📂 Структура проекта
```bash
├── alembic.ini
├── config.py
├── database.py
├── exceptions.py
├── main.py
├── poetry.lock
├── pyproject.toml
├── pytest.ini
├── requirements.txt
├── .env
├── .env.test
├── README.md
├── pages/
│   └── router.py
├── migrations/
│   └── versions/
│       └── env.py
├── taskapp/
│   ├── authenticate/
│   │   ├── auth.py
│   │   └── dependencies.py
│   ├── models/
│   │   ├── task.py
│   │   ├── user.py
│   │   └── boards.py
│   ├── routers/
│   │   ├── tasks.py
│   │   ├── users.py
│   │   └── boards.py
│   ├── schemas/
│   │   ├── tasks.py
│   │   ├── users.py
│   │   └── boards.py
│   ├── services/
│   │   ├── base.py
│   │   ├── task_service.py
│   │   ├── user_service.py
│   │   └── board_service.py
│   └── __init__.py
├── templates/
│   ├── base.html
│   ├── taskboard.html
│   ├── auth.html
│   └── regs.html
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_boards.py
│   ├── test_pages.py
│   ├── test_tasks.py
│   └── test_users.py
```

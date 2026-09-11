 # Task Management System

FastAPI task management backend with JWT authentication, admin/user RBAC, task workflows, comments, attachments, notifications, dashboards, pagination, audit logs, Alembic migrations, and OpenAPI documentation.

## Setup

### Prerequisites

- Python 3.11 or newer
- PostgreSQL running locally or on a reachable server
- A PostgreSQL database created for the application, for example `task_db`

### Windows installation

Run these commands from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, run this once for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Environment configuration

Open `.env` and set values for the database and JWT signing key:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/task_db
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
UPLOAD_DIRECTORY=uploads
MAX_UPLOAD_SIZE_BYTES=10485760
```

Do not commit `.env` or real secrets. `.env.example` is only a template.

### Create database tables

Run the Alembic migrations from the project root:

```powershell
python -m alembic upgrade head
```

### Create the first administrator

The public registration endpoint creates regular users. Create the first admin directly with the interactive script:

```powershell
python -m scripts.create_admin
```

The script asks for the admin name, email, password, and optional phone number. The email must be unique.

### Start the API

```powershell
python -m uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

- Swagger UI: `http://127.0.0.1:8000/docs`


## Authentication and rules

Register or log in through `/auth/register` and `/auth/login`, then send `Authorization: Bearer <token>`. Authentication uses JWT access tokens; there is no refresh-token endpoint or database token table. `/auth/logout` invalidates the current user's active token version. Admin-only resources return `403` to regular users. Tasks accept only valid transitions, inactive users cannot be assigned, closed tasks cannot be edited or commented on, and comments are owned by their author unless managed by an admin.

## Tests

```powershell
python -m pytest

or

py -m pytest -q
```

Uploads are stored under `UPLOAD_DIRECTORY` and restricted to PDF, JPG, PNG, DOC, DOCX, and TXT within `MAX_UPLOAD_SIZE_BYTES` (10 MB by default).

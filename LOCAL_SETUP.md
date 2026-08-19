# MailForge Local Setup

This guide explains how to run MailForge after cloning the repository.

## What You Need

Install these tools before starting:

- Git
- Python 3.11 or newer
- Node.js 20 or newer, including npm
- Docker Desktop
- PostgreSQL and Redis are provided by Docker, so you do not need to install them separately.

## Clone the Repository

```powershell
git clone https://github.com/novas-joker/BulkManagementSystem.git
cd BulkManagementSystem
```

## Configure Environment Variables

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

For local development, make sure the database and Redis values in `.env` match the Docker services:

```env
APP_ENV=development
APP_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
LOG_LEVEL=INFO

DATABASE_URL=postgresql+asyncpg://mailforge:mailforge_dev@localhost:5432/mailforge
SYNC_DATABASE_URL=postgresql://mailforge:mailforge_dev@localhost:5432/mailforge
REDIS_URL=redis://:redis_dev@localhost:6379/0

JWT_SECRET=local-dev-jwt-secret-change-later
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ACCESS_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=

ZEPTOMAIL_MOCK=true
ZOHO_CAMPAIGNS_MOCK=true
```

Keep `.env` private. Never commit it or place SMTP/API passwords in frontend files.

## Start PostgreSQL and Redis

From the repository root:

```powershell
docker compose up -d postgres redis
```

Check that both containers are running:

```powershell
docker compose ps
```

## Start the Backend

Open a new PowerShell terminal at the repository root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend URLs:

- API: http://localhost:8000
- Health check: http://localhost:8000/health
- API documentation: http://localhost:8000/docs

Leave this terminal running.

## Start the Frontend

Open another PowerShell terminal at the repository root:

```powershell
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Open the application at:

http://localhost:5173

## First Use

1. Register a user account in the application.
2. Create or import contacts.
3. Create an email template.
4. Create a campaign and select the template.
5. Expand the campaign and click **Send Campaign**.

The campaign excludes unsubscribed and suppressed contacts. With `ZEPTOMAIL_MOCK=true`, delivery is simulated and no real email is sent.

## Send Real Email

For local SMTP testing, add credentials to `.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
```

Restart the backend after changing `.env`.

For real bulk email, use a transactional provider or a verified sending domain with SPF, DKIM, and DMARC. Personal Gmail accounts are not suitable for production bulk campaigns and may deliver messages to Spam or throttle the account.

## Stop Local Services

Stop the frontend and backend with `Ctrl+C` in their terminals. Stop Docker services with:

```powershell
docker compose stop postgres redis
```

To remove the containers and development data:

```powershell
docker compose down -v
```

The `-v` option deletes the PostgreSQL and Redis volumes.

## Run Tests

Backend tests:

```powershell
cd backend
.\..\venv\Scripts\Activate.ps1
$env:PYTHONPATH = (Get-Location).Path
python -m pytest
```

Frontend production build:

```powershell
cd frontend
npm run build
```

## Troubleshooting

### Python cannot import `app`

Run backend commands from the `backend` directory and set the package path:

```powershell
cd backend
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn app.main:app --reload --port 8000
```

### Database connection fails

Check Docker services:

```powershell
docker compose ps
docker compose logs postgres
```

Confirm that `.env` uses `mailforge_dev`, `mailforge`, and port `5432` in the database URLs.

### Redis connection fails

Check Redis logs:

```powershell
docker compose logs redis
```

Confirm that `.env` uses:

```env
REDIS_URL=redis://:redis_dev@localhost:6379/0
```

### Port already in use

The default ports are:

- Frontend: `5173`
- Backend: `8000`
- PostgreSQL: `5432`
- Redis: `6379`

Stop the process using the port or change the corresponding local command/configuration.

### Frontend cannot reach the backend

Confirm that the backend is running at http://localhost:8000 and that the frontend is running at http://localhost:5173. The Vite development proxy forwards the application API paths to port `8000`.

## Docker-Only Setup

The repository also contains `docker-compose.yml` and Dockerfiles for a full containerized stack. The hybrid setup above is recommended for development because it provides Vite and Uvicorn hot reload and keeps the local environment easier to debug.

Before using the full Docker stack, review the environment names and database URL in `docker-compose.yml` against `backend/app/core/config.py`. The backend requires an async database URL using the `postgresql+asyncpg://` driver.

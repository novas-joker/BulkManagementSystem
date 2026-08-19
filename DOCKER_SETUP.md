# MailForge Docker Setup Guide

## Overview
This Docker Compose configuration sets up the complete MailForge application stack for local development and production deployment.

### Services Included
1. **PostgreSQL** - Database (port 5432)
2. **Redis** - Cache & message broker (port 6379)
3. **FastAPI Backend** - API server (port 8000)
4. **Celery Worker** - Async email delivery
5. **Celery Beat** - Scheduled campaigns
6. **React Frontend** - Web UI (port 3000)

## Prerequisites
- Docker & Docker Compose installed
- `.env` file with required environment variables (see `.env.example`)

## Environment Configuration

Create a `.env` file in the root directory:

```env
# Database
DB_USER=mailforge
DB_PASSWORD=mailforge_dev
DB_NAME=mailforge

# Redis
REDIS_PASSWORD=redis_dev

# Backend
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development

# SMTP Configuration (Zoho/ZeptoMail)
SMTP_HOST=smtp.zoho.com
SMTP_PORT=465
SMTP_USER=your-email@zoho.com
SMTP_PASSWORD=your-app-password

# CORS (for frontend access)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Running the Stack

### Start all services:
```bash
docker-compose up -d
```

### View logs:
```bash
docker-compose logs -f [service-name]
# Examples:
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f frontend
```

### Access applications:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Database migrations:
Migrations run automatically on backend startup. To run manually:
```bash
docker-compose exec backend alembic upgrade head
```

### Stop services:
```bash
docker-compose down
```

### Remove volumes (WARNING: deletes data):
```bash
docker-compose down -v
```

## Development Workflow

### Hot reload (development):
For development with hot reload, use the local Vite dev server instead of the Docker frontend:
```bash
# Terminal 1: Start Docker services (excluding frontend)
docker-compose up -d postgres redis backend celery-worker celery-beat

# Terminal 2: Run frontend locally
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

### Execute commands in containers:
```bash
# Run a command in backend
docker-compose exec backend python -c "import app; print(app)"

# Enter backend shell
docker-compose exec backend /bin/bash

# Access database
docker-compose exec postgres psql -U mailforge -d mailforge
```

## Production Deployment Notes

### Security considerations:
1. Change all default passwords in `.env`
2. Set `ENVIRONMENT=production`
3. Use strong `SECRET_KEY`
4. Configure proper SMTP credentials
5. Enable HTTPS/TLS in reverse proxy
6. Set restrictive `CORS_ORIGINS`

### Scaling:
- Increase `--concurrency` in celery-worker for higher email throughput
- Add additional celery-worker services for parallel processing
- Configure load balancer for backend service

### Monitoring:
- Add Prometheus/Grafana for metrics
- Configure centralized logging (ELK stack)
- Set up alerting for service failures

## Troubleshooting

### Backend won't start
```bash
# Check database connection
docker-compose logs backend

# Run migrations manually
docker-compose exec backend alembic upgrade head

# Reset database (development only)
docker-compose down -v
docker-compose up -d
```

### Celery worker issues
```bash
# Check worker logs
docker-compose logs celery-worker

# Verify Redis connection
docker-compose exec redis redis-cli -a redis_dev ping
```

### Frontend can't reach API
- Verify backend is healthy: `docker-compose logs backend`
- Check `VITE_API_URL` in frontend environment
- Ensure backend CORS settings allow frontend origin

### Database issues
```bash
# Connect to database
docker-compose exec postgres psql -U mailforge -d mailforge

# Reset data (dev only)
docker-compose exec postgres dropdb -U mailforge mailforge
docker-compose up -d postgres
```

## Network
All services communicate via the `mailforge` bridge network. Service names can be used as hostnames (e.g., `postgres:5432`).

## Volumes
- `postgres_data`: PostgreSQL data persistence
- `redis_data`: Redis data persistence
- `./backend`: Backend source code (development volume mount)

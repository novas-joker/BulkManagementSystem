# MailForge - Bulk Email Management System

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-org/mailforge)
[![Architecture](https://img.shields.io/badge/architecture-Clean%20Architecture-emerald.svg)]()
[![Backend](https://img.shields.io/badge/backend-Python%20FastAPI-009688.svg)]()
[![Frontend](https://img.shields.io/badge/frontend-React%2018%20%7C%20TypeScript%20%7C%20Vite-61DAFB.svg)]()
[![Database](https://img.shields.io/badge/database-PostgreSQL%20%7C%20SQLAlchemy-336791.svg)]()
[![Queue](https://img.shields.io/badge/queue-Celery%20%7C%20Redis-CC0000.svg)]()

MailForge is a high-performance, production-oriented bulk email campaign management platform engineered for managing contacts, dynamic audiences, reusable email templates, multi-step campaign lifecycles, high-throughput email delivery, engagement tracking, suppression rules, and external campaign integrations.

---

## 🌟 Key Features

- **Contacts & Audience Management**:
  - Full CRUD operations with custom dynamic fields.
  - High-speed CSV import with column mapping and deduplication.
  - Static Mailing Lists and Tagging system.
  - Dynamic Segments with real-time condition evaluation (filters, tags, properties).
  - Smart **AudienceResolver** that automatically excludes unsubscribed, hard-bounced, complained, and suppressed contacts.
- **Template Engine**:
  - HTML & plain text email template management.
  - Personalization variable engine (`{{first_name}}`, `{{company}}`, custom attributes).
  - Live preview and instant test email dispatch.
  - Automated tracking pixel and click URL rewriting.
- **Email Delivery Provider Infrastructure**:
  - **ZeptoMail (Primary Provider)**: Native transactional and bulk delivery integration with built-in mock mode (`ZEPTOMAIL_MOCK=true`) for zero-dependency local development.
  - **SMTP (Configurable Fallback)**: Full TLS/SSL SMTP client.
  - **Provider Isolation**: Provider Strategy Pattern decoupled behind the `EmailProvider` interface.
  - **Credential Security**: Encrypted database storage for provider secrets using Fernet symmetric encryption.
- **Campaign Engine & Lifecycle**:
  - Strict finite state machine (`draft` → `scheduled` / `queued` → `sending` → `sent` / `paused` / `failed` / `cancelled`).
  - Guided 4-step Campaign Builder (Settings → Audience → Content & Preview → Review & Dispatch).
  - Test email dispatch before launching.
- **Asynchronous Processing & Scheduling**:
  - Powered by **Celery** workers with **Redis** broker.
  - Batching and exponential backoff retry policy for transient delivery failures.
  - **Celery Beat** periodic scheduler for timezone-aware scheduled campaigns.
- **Engagement Tracking & Compliance**:
  - 1x1 transparent tracking pixel for open tracking (`/track/open/{token}`).
  - Secure signed click tracking with 302 redirects (`/track/click/{token}`).
  - Instant one-click and web-based unsubscribe handling (`/unsubscribe/{token}`).
  - Global Suppression List preventing accidental deliveries.
- **External Integrations**:
  - **Zoho Campaigns**: Bi-directional contact/list sync, campaign metadata push, and statistics retrieval with mock mode support (`ZOHO_CAMPAIGNS_MOCK=true`).
- **Comprehensive Analytics**:
  - Real-time campaign stats (Sent, Delivered, Open Rate, Click Rate, Bounce Rate, Unsubscribes).
  - Visual time-series engagement graphs (Recharts).
  - Global system performance dashboard.

---

## 🏛 Architecture & Design Principles

MailForge follows **Clean Architecture** and **Modular Monolith** principles with strict separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│    FastAPI Routers, Middleware, Request/Response Schemas    │
└──────────────────────────────┬──────────────────────────────┘
                               │ (calls)
┌──────────────────────────────▼──────────────────────────────┐
│                    Application Layer                        │
│   Use Cases & Orchestration Services (CampaignService,      │
│   AudienceResolver, TemplateRenderer, DeliveryService)      │
└──────────────────┬───────────────────────────┬──────────────┘
                   │ (uses)                    │ (calls abstractions)
┌──────────────────▼──────────┐   ┌────────────▼──────────────┐
│        Domain Layer         │   │   Domain Interfaces       │
│  Entities, Business Rules,  │   │   UserRepository,         │
│  Value Objects, Exceptions  │   │   EmailProvider, etc.     │
└─────────────────────────────┘   └────────────▲──────────────┘
                                               │ (implements)
┌──────────────────────────────────────────────┴──────────────┐
│                    Infrastructure Layer                     │
│  PostgreSQL/SQLAlchemy Repositories, Redis/Celery Workers,  │
│  ZeptoMailClient, SMTPClient, ZohoCampaignsClient           │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Rules
1. **Presentation** depends on **Application**.
2. **Application** depends on **Domain**.
3. **Infrastructure** implements **Application & Domain interfaces**.
4. **Domain Layer** has zero dependencies on FastAPI, SQLAlchemy, PostgreSQL, Redis, ZeptoMail, or Zoho.
5. **Design Patterns**: Repository Pattern, Service Layer Pattern, Strategy Pattern (Email Providers), Factory Pattern, Unit of Work, Adapter Pattern, DTO Pattern.

---

## 💻 Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, Passlib (Argon2/Bcrypt), Cryptography (Fernet) |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Zustand, React Hook Form, Zod, Recharts, Lucide React |
| **Database & ORM** | PostgreSQL 15+, SQLAlchemy 2.0 (Async + Sync), Alembic Migrations |
| **Queue & Broker** | Celery 5.3+, Celery Beat, Redis 7+ |
| **Email Providers** | ZeptoMail (API), SMTP (TLS/SSL) |
| **Integrations** | Zoho Campaigns API (OAuth 2.0) |
| **DevOps & Deploy** | Docker, Docker Compose |

---

## 📦 Project Structure

```
BulkManagementSystem/
├── backend/
│   ├── alembic/                         # Database migrations
│   ├── app/
│   │   ├── api/                         # Presentation Layer
│   │   │   ├── middleware/              # Auth & error handling middleware
│   │   │   ├── routes/                  # FastAPI router endpoints
│   │   │   └── dependencies.py          # FastApi dependencies (Auth, DB session)
│   │   ├── application/                 # Application Layer
│   │   │   ├── services/                # Business logic services
│   │   │   └── use_cases/               # Orchestrated application use cases
│   │   ├── domain/                      # Domain Layer
│   │   │   ├── entities/                # Pure business entities
│   │   │   └── interfaces/              # Repository & Provider interfaces
│   │   ├── infrastructure/              # Infrastructure Layer
│   │   │   ├── database/                # SQLAlchemy models & engine
│   │   │   ├── email/                   # ZeptoMail, SMTP adapters & clients
│   │   │   ├── redis/                   # Redis cache & helpers
│   │   │   ├── repositories/            # SQLAlchemy repository implementations
│   │   │   └── zoho/                    # Zoho Campaigns client & OAuth service
│   │   ├── core/                        # Core configuration & security
│   │   │   ├── config.py                # Environment BaseSettings
│   │   │   └── security.py              # JWT, password hashing & encryption
│   │   ├── schemas/                     # Pydantic request/response DTOs
│   │   ├── tasks/                       # Celery tasks & queues
│   │   └── main.py                      # FastAPI application entrypoint
│   ├── tests/                           # Unit & integration test suites
│   ├── Dockerfile                       # Backend container definition
│   └── requirements.txt                 # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/                  # Reusable UI components & modals
│   │   │   └── ui/                      # Base design system primitives
│   │   ├── features/                    # Feature modules (Campaign builder, etc.)
│   │   ├── hooks/                       # Custom React hooks
│   │   ├── layouts/                     # Dashboard & Auth layouts
│   │   ├── pages/                       # Application view pages
│   │   ├── routes/                      # React Router configuration
│   │   ├── services/                    # Axios/Fetch API client services
│   │   ├── stores/                      # Zustand state management stores
│   │   ├── types/                       # TypeScript interfaces & types
│   │   ├── utils/                       # Helper functions
│   │   ├── App.tsx                      # App root component
│   │   └── main.tsx                     # Vite entry point
│   ├── Dockerfile                       # Frontend container definition
│   ├── package.json                     # Node dependencies
│   ├── tailwind.config.js               # Tailwind design tokens
│   └── vite.config.ts                   # Vite configuration
├── docker-compose.yml                   # Multi-container orchestration
├── context.json                         # Full system specifications
└── README.md                            # Documentation
```

---

## 🗄 Database Schema

The relational database architecture is defined in PostgreSQL with SQLAlchemy:

```
[Users] 1 ──< [RefreshTokens]
[Contacts] M ── M [MailingLists] (via list_contacts)
[Contacts] M ── M [Tags] (via contact_tags)
[Contacts] 1 ──< [ContactCustomValues] >── 1 [CustomFields]
[Campaigns] >── 1 [EmailTemplates]
[Campaigns] >── 1 [MailingLists]
[Campaigns] >── 1 [Segments]
[Campaigns] 1 ──< [CampaignRecipients] >── 1 [Contacts]
[Campaigns] 1 ──< [EmailEvents] >── 1 [Contacts]
[Campaigns] 1 ──< [CampaignLinks]
[Suppressions] (email, reason, source)
[ProviderCredentials] (encrypted_credentials)
[Integrations] (zoho metadata_json)
```

---

## 🔄 Campaign Lifecycle & State Machine

Campaigns transition through strictly validated states:

```mermaid
stateDiagram-v2
    [*] --> draft: Create Campaign
    draft --> scheduled: Set Schedule
    draft --> queued: Send Immediately
    scheduled --> queued: Scheduled Time Reached
    scheduled --> cancelled: Cancel
    queued --> sending: Celery Worker Picked Up
    queued --> cancelled: Cancel
    sending --> sent: All Batches Finished
    sending --> paused: Pause
    sending --> failed: Critical Error
    paused --> sending: Resume
    paused --> cancelled: Cancel
    sent --> [*]
    cancelled --> [*]
    failed --> [*]
```

---

## ⚡ Background Processing Architecture

Celery workers process asynchronous workloads via Redis queues:

1. **`queue_campaign`**: Evaluates audience selection (Lists/Segments), applies suppression & unsubscribe filters, creates `CampaignRecipient` records, and enqueues recipient batches.
2. **`send_campaign_batch`**: Pulls recipient batches, prepares personalized content, injects tracking tokens, and dispatches via `EmailDeliveryService`.
3. **`send_single_email`**: Dispatches individual email via configured provider (`ZeptoMailProvider` or `SMTPProvider`).
4. **`process_scheduled_campaigns`**: Celery Beat cron task executing every minute to trigger due scheduled campaigns.
5. **`retry_failed_email`**: Handles transient delivery failures with exponential backoff.
6. **`aggregate_campaign_analytics`**: Calculates real-time delivery and engagement rates.
7. **`sync_zoho_campaigns`**: Background sync with external Zoho Campaigns API.

---

## 🔌 API Endpoints Summary

### Authentication
- `POST /api/auth/login` - Authenticate user & return tokens
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Revoke refresh token
- `GET /api/auth/me` - Get current user profile

### Contacts & Audiences
- `GET /api/contacts` - List & filter contacts (pagination & search)
- `POST /api/contacts` - Create new contact
- `GET|PUT|DELETE /api/contacts/{id}` - Contact detail / update / delete
- `POST /api/contacts/import` - CSV file import with column mapping
- `GET /api/contacts/export` - Export contacts to CSV
- `POST /api/contacts/bulk-subscribe` - Bulk subscribe contacts
- `POST /api/contacts/bulk-unsubscribe` - Bulk unsubscribe contacts
- `POST /api/contacts/bulk-delete` - Bulk delete contacts
- `GET|POST|PUT|DELETE /api/lists` - Mailing lists CRUD
- `GET|POST|DELETE /api/lists/{id}/contacts` - List membership management
- `GET|POST|PUT|DELETE /api/tags` - Contact tags CRUD
- `GET|POST|PUT|DELETE /api/segments` - Dynamic segments CRUD
- `POST /api/segments/{id}/preview` - Preview matching audience count

### Templates
- `GET|POST /api/templates` - List and create email templates
- `GET|PUT|DELETE /api/templates/{id}` - Template detail, update, delete
- `POST /api/templates/{id}/duplicate` - Clone template
- `POST /api/templates/{id}/test` - Send test email with rendered variables

### Campaigns
- `GET|POST /api/campaigns` - List and create campaigns
- `GET|PUT|DELETE /api/campaigns/{id}` - Campaign detail, update, delete
- `POST /api/campaigns/{id}/test` - Send test preview email
- `POST /api/campaigns/{id}/send` - Launch campaign immediately
- `POST /api/campaigns/{id}/schedule` - Schedule campaign for future dispatch
- `POST /api/campaigns/{id}/pause` - Pause in-flight campaign
- `POST /api/campaigns/{id}/cancel` - Cancel scheduled/queued/paused campaign
- `POST /api/campaigns/{id}/duplicate` - Duplicate campaign
- `GET /api/campaigns/{id}/progress` - Real-time recipient delivery progress
- `GET /api/campaigns/{id}/analytics` - Detailed campaign analytics report

### Analytics
- `GET /api/analytics/overview` - System-wide key metrics
- `GET /api/analytics/campaigns` - Comparative campaign performance table
- `GET /api/analytics/engagement` - Time-series open/click engagement data
- `GET /api/analytics/delivery` - Delivery success/failure metrics

### Delivery Providers & Integrations
- `GET /api/providers` - Get available providers and active selection
- `GET /api/providers/status` - Provider health & connectivity check
- `POST /api/providers/zeptomail/test` - Test ZeptoMail credentials
- `POST /api/providers/smtp/test` - Test SMTP credentials
- `GET /api/integrations/zoho/status` - Zoho Campaigns connection status
- `POST /api/integrations/zoho/connect` - Authenticate Zoho OAuth tokens
- `POST /api/integrations/zoho/sync` - Trigger on-demand synchronization
- `POST /api/integrations/zoho/disconnect` - Revoke Zoho integration

### Public Tracking & Compliance
- `GET /track/open/{token}` - Transparent 1x1 GIF tracking pixel
- `GET /track/click/{token}` - Track link click and 302 redirect
- `GET|POST /unsubscribe/{token}` - Public unsubscribe confirmation flow
- `GET|POST|DELETE /api/suppressions` - Manage global suppression list

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory (refer to `.env.example`):

```env
# Application Settings
APP_ENV=development
APP_URL=http://localhost:5000
FRONTEND_URL=http://localhost:5173
LOG_LEVEL=INFO

# Databases & Broker
DATABASE_URL=postgresql+asyncpg://mailforge:mailforge_password@localhost:5432/mailforge_db
SYNC_DATABASE_URL=postgresql://mailforge:mailforge_password@localhost:5432/mailforge_db
REDIS_URL=redis://localhost:6379/0

# Security & Encryption
JWT_SECRET=super-secret-jwt-signing-key-replace-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ACCESS_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=32-character-or-base64-fernet-key-here=

# ZeptoMail Provider (Primary)
ZEPTOMAIL_API_URL=https://api.zeptomail.com/v1.1/email
ZEPTOMAIL_SEND_MAIL_TOKEN=your-zeptomail-token
ZEPTOMAIL_MOCK=true

# SMTP Provider (Fallback)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=user@example.com
SMTP_PASSWORD=smtp-password

# Zoho Campaigns Integration
ZOHO_CLIENT_ID=your-zoho-client-id
ZOHO_CLIENT_SECRET=your-zoho-client-secret
ZOHO_REFRESH_TOKEN=your-zoho-refresh-token
ZOHO_CAMPAIGNS_API_URL=https://campaigns.zoho.com/api/v1.1
ZOHO_CAMPAIGNS_MOCK=true
```

### 🔒 Security Principles
- **Never commit `.env` files.**
- **Never expose provider secrets, tokens, or encryption keys to the frontend or API responses.**
- **Store provider credentials encrypted in the database.**
- **Sensitive environment variables are automatically redacted in application logs.**

---

## 🚀 Getting Started

### Option 1: Docker Compose (Recommended)

Run the entire MailForge ecosystem with a single command:

```bash
# Clone the repository
git clone https://github.com/your-org/mailforge.git
cd mailforge

# Copy environment configuration
cp .env.example .env

# Build and start all services (Backend, Frontend, Postgres, Redis, Celery Worker & Beat)
docker-compose up --build
```

Access the services:
- **Frontend Application**: `http://localhost:5173`
- **FastAPI Documentation**: `http://localhost:5000/docs`
- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`

---

### Option 2: Local Development Setup

#### 1. Start Prerequisites (PostgreSQL & Redis)
```bash
docker run -d --name mailforge-postgres -p 5432:5432 -e POSTGRES_USER=mailforge -e POSTGRES_PASSWORD=mailforge_password -e POSTGRES_DB=mailforge_db postgres:15
docker run -d --name mailforge-redis -p 6379:6379 redis:7-alpine
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
```

#### 3. Start Celery Worker & Beat
```bash
# In a new terminal (with active venv)
celery -A app.tasks.worker worker --loglevel=info

# In another terminal for scheduling
celery -A app.tasks.worker beat --loglevel=info
```

#### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing

Run the automated test suite with **pytest**:

```bash
cd backend
pytest tests/ -v --cov=app
```

Critical test cases covered:
- Unsubscribed and suppressed recipients are strictly excluded from campaigns.
- Duplicate recipient prevention in single campaign batches.
- Invalid campaign state transitions are rejected.
- Transient provider failures trigger exponential backoff retries.
- Permanent failures do not cause infinite retry loops.
- `ZEPTOMAIL_MOCK` and `ZOHO_CAMPAIGNS_MOCK` execute deterministic local workflows.
- Credential encryption and secret redaction verification.

---

## 📄 License

MailForge is distributed under the **MIT License**.

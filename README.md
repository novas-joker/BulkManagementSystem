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
  - High-speed CSV import from a file or pasted content, with visible format guidance, column mapping, preview, and deduplication.
  - Static Mailing Lists with visible contact membership, add/remove controls, and user-scoped membership validation.
  - Tagging system.
  - Dynamic Segments with real-time condition evaluation (filters, tags, properties).
  - Smart **AudienceResolver** that automatically excludes unsubscribed, hard-bounced, complained, and suppressed contacts.
- **Template Engine**:
  - HTML & plain text email template management.
  - Card-based template library with an always-visible rendered preview.
  - Selecting a template card reveals duplicate, test email, edit, and delete actions.
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

### Overview Dashboard

The authenticated MailForge workspace opens on a focused overview designed for quick scanning:

- A personalized workspace header with a primary **Create campaign** action.
- KPI cards for total contacts, active campaigns, mailing lists, and reusable templates.
- Seven-day campaign activity view with campaign count and sending trend.
- A first-send setup checklist linking directly to Contacts, Templates, and Mailing Lists.
- A recent campaigns list with status labels and an empty state for new workspaces.

The overview uses MailForge-owned copy, marks, and styling throughout; it does not depend on third-party product branding or assets.

Workspace pages show linked breadcrumbs at the top. Multi-step onboarding and campaign-building flows use numbered horizontal progress bars: each step is a circle connected by a track, the active step uses the primary MailForge color, completed steps use green, and upcoming steps use the secondary muted color.

Mailing-list rows have an explicit **Manage contacts** action and can also be opened by selecting the list name. Contacts can be added from the user’s available contacts or removed from the selected list; deleting a list does not delete its contacts.

### CSV Contact Import

The Contacts page accepts either a local `.csv` file or pasted CSV content. The upload step shows the expected format before validation:

```csv
email,first_name,last_name,status
alex@example.com,Alex,Johnson,subscribed
```

The `email` column is required. `first_name`, `last_name`, and `status` are optional. After validation, users can review detected columns, configure duplicate handling (`skip`, `merge`, or `overwrite`), preview the resulting contacts, and complete the import.

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

## Low-Level Design (LLD)

The implementation is a modular monolith. HTTP requests enter through FastAPI routers, are authenticated and given a database session through FastAPI dependencies, and then use application services or repositories. SQLAlchemy models and external provider clients remain in infrastructure. The React frontend calls the API through feature-specific service modules and renders the returned data in page components.

### Runtime Component Diagram

```mermaid
flowchart LR
  Browser[Browser]
  App[React App\nApp.jsx]
  Pages[Pages and components\nDashboardShell, CampaignsPage, ContactsPage]
  ApiClients[Frontend API services\nauthApi, campaignApi, contactApi, ...]
  Router[FastAPI routers\nauth, campaigns, contacts, templates, onboarding, ...]
  Deps[FastAPI dependencies\nJWT validation + DB session]
  Services[Application services\nCampaignService, TemplateService, ContactService, ...]
  Renderer[TemplateRendererService]
  Repositories[SQLAlchemy repositories\nBaseRepository + feature repositories]
  Models[SQLAlchemy models]
  Database[(PostgreSQL)]
  Factory[EmailProviderFactory]
  Provider[EmailProvider protocol]
  Zepto[ZeptoMailProvider]
  SMTP[SMTPProvider]
  Celery[Celery tasks\napp/tasks]
  Redis[(Redis broker)]
  Tracking[Tracking router\nopen, click, unsubscribe]
  Zoho[Zoho integration client]

  Browser --> App --> Pages --> ApiClients --> Router
  Router --> Deps
  Router --> Services
  Router --> Repositories
  Services --> Repositories
  Services --> Renderer
  Services --> Factory
  Repositories --> Models --> Database
  Factory --> Provider
  Provider --> Zepto
  Provider --> SMTP
  Router --> Celery
  Celery --> Redis
  Celery --> Services
  Router --> Tracking
  Services --> Zoho
```

### LLD Class Diagram

```mermaid
classDiagram
  direction LR

  class App {
    +create_app() FastAPI
    +lifespan(app)
  }
  class Router {
    <<Presentation>>
    +auth_router
    +campaigns_router
    +contacts_router
    +templates_router
    +onboarding_router
    +tracking_router
  }
  class FastAPIDependencies {
    <<Dependency Injection>>
    +get_current_user_id(credentials) str
    +get_current_user(user_id, db) User
    +get_db() AsyncSession
  }

  class BaseService~RepositoryType~ {
    <<Template Method>>
    #repository RepositoryType
  }
  class CampaignService {
    +VALID_STATUS_TRANSITIONS dict
    +create_campaign(user_id, payload) dict
    +update_campaign(user_id, campaign_id, payload) dict
    +send_campaign(user_id, campaign_id) dict
    +send_test_email(user_id, campaign_id, recipient_email) dict
  }
  class ContactService
  class ContactImportService
  class AuthService
  class TemplateService
  class TemplateRendererService {
    <<Service / Facade>>
    +replace_variables(content, variables) str
    +render_html(template_html, variables, campaign_id, contact_id) str
    +render_text(template_text, variables) str
    +inject_tracking_pixel(html, campaign_id, contact_id) str
    +inject_unsubscribe_link(html, contact_id, campaign_id) str
  }

  class BaseRepository~ModelType~ {
    <<Repository>>
    #session AsyncSession
    +create(obj) ModelType
    +get_by_id(entity_id) ModelType
    +get_all() list
    +update(obj) ModelType
    +delete(obj)
    +count() int
  }
  class UserRepository
  class CampaignRepository {
    +get_by_user_and_name(user_id, name) CampaignModel
    +list_for_user(user_id) list
    +create(campaign) CampaignModel
  }
  class ContactRepository
  class TemplateRepository
  class SQLAlchemyModels {
    <<Persistence Model>>
    +User
    +Contact
    +Campaign
    +CampaignRecipient
    +EmailTemplate
    +MailingList
    +Segment
    +Tag
    +Suppression
    +EmailEvent
  }
  class AsyncSession {
    <<Unit of Work boundary>>
    +add(obj)
    +commit()
    +rollback()
    +refresh(obj)
  }

  class Campaign {
    <<Domain Entity>>
    +id str
    +user_id str
    +template_id str
    +name str
    +subject str
    +status CampaignStatus
    +campaign_type CampaignType
    +audience_criteria dict
    +is_active() bool
  }
  class CampaignRecipient {
    <<Domain Entity>>
    +campaign_id str
    +contact_id str
    +email str
    +status str
    +delivered_at datetime
    +failed_reason str
  }
  class EmailEvent {
    <<Domain Entity>>
    +campaign_id str
    +contact_id str
    +email str
    +event_type str
    +event_data dict
  }
  class CampaignStatus {
    <<Enumeration>>
    DRAFT
    SCHEDULED
    QUEUED
    SENDING
    SENT
    PAUSED
    CANCELLED
    FAILED
  }
  class CampaignType {
    <<Enumeration>>
    BULK
    TRANSACTIONAL
    AUTOMATION
    NEWSLETTER
  }

  class EmailProvider {
    <<Protocol / Strategy>>
    +provider_name str
    +send(to_email, subject, body, from_email, metadata) EmailSendResult
  }
  class BaseEmailProvider {
    <<Template Method>>
    +send(...) EmailSendResult
  }
  class ZeptoMailProvider {
    <<Adapter>>
    +provider_name zeptomail
    +send(...) EmailSendResult
  }
  class SMTPProvider {
    <<Adapter>>
    +provider_name smtp
    +send(...) EmailSendResult
  }
  class MockEmailProvider {
    <<Adapter>>
    +provider_name mock
    +send(...) EmailSendResult
  }
  class EmailSendResult {
    +success bool
    +provider str
    +status str
    +to_email str
    +message_id str
    +error str
    +metadata dict
  }
  class EmailProviderFactory {
    <<Factory>>
    +get_provider(provider_name) EmailProvider
  }

  class CeleryTasks {
    <<Producer / Consumer>>
    +send_campaign_email_task(recipient_id, campaign_id, user_id)
    +process_queued_campaigns()
  }
  class Redis {
    <<Message Broker>>
  }
  class ApiServiceModules {
    <<Frontend Facade>>
    +authApi
    +campaignApi
    +contactApi
    +templateApi
    +listApi
  }
  class ReactPages {
    <<Frontend UI>>
    +App
    +DashboardShell
    +CampaignsPage
    +ContactsPage
    +TemplatesPage
    +OnboardingPage
  }
  class OnboardingDTO {
    <<DTO>>
    +subscriber_count_bracket str
    +previous_tool str
    +business_industry str
    +business_website str
    +compliance_address dict
    +user_primary_goal str
    +product_updates_consent bool
    +onboarding_phase int
    +onboarding_completed bool
  }

  App *-- Router : registers
  Router --> FastAPIDependencies : Depends()
  Router --> CampaignService : invokes
  Router --> OnboardingDTO : validates / serializes
  CampaignService --> CampaignRepository : uses
  CampaignService --> TemplateRepository : uses
  CampaignService --> TemplateRendererService : renders
  CampaignService --> EmailProviderFactory : selects provider
  BaseService~RepositoryType~ <|-- AuthService
  BaseService~RepositoryType~ <|-- ContactService
  BaseService~RepositoryType~ <|-- ContactImportService
  BaseService~RepositoryType~ <|-- TemplateService
  BaseRepository~ModelType~ <|-- UserRepository
  BaseRepository~ModelType~ <|-- CampaignRepository
  BaseRepository~ModelType~ <|-- ContactRepository
  BaseRepository~ModelType~ <|-- TemplateRepository
  BaseRepository~ModelType~ --> AsyncSession : transaction boundary
  UserRepository --> SQLAlchemyModels : persists User
  CampaignRepository --> SQLAlchemyModels : maps Campaign
  ContactRepository --> SQLAlchemyModels : persists Contact
  TemplateRepository --> SQLAlchemyModels : persists EmailTemplate
  CampaignService --> Campaign : creates / validates
  Campaign --> CampaignStatus : has
  Campaign --> CampaignType : has
  Campaign "1" --> "many" CampaignRecipient : contains
  Campaign "1" --> "many" EmailEvent : records
  EmailProviderFactory --> EmailProvider : returns
  EmailProvider <|.. BaseEmailProvider : implements contract
  BaseEmailProvider <|-- ZeptoMailProvider : Strategy
  BaseEmailProvider <|-- SMTPProvider : Strategy
  BaseEmailProvider <|-- MockEmailProvider : Strategy
  ZeptoMailProvider ..> EmailSendResult : returns
  SMTPProvider ..> EmailSendResult : returns
  MockEmailProvider ..> EmailSendResult : returns
  CeleryTasks --> Redis : publishes / consumes
  CeleryTasks --> CampaignService : background workflow
  ReactPages --> ApiServiceModules : calls
  ApiServiceModules --> Router : HTTP / JSON
```

### Class Diagram Pattern Legend

- `<<Presentation>>`: FastAPI routers expose HTTP endpoints and delegate work inward.
- `<<Dependency Injection>>`: FastAPI supplies the database session and authenticated user through `Depends`.
- `<<Service / Facade>>`: application services coordinate use cases; `TemplateRendererService` exposes a simple rendering API over several operations.
- `<<Repository>>`: repositories isolate common and feature-specific SQLAlchemy persistence operations.
- `<<DTO>>`: Pydantic schemas define request and response contracts, including onboarding data.
- `<<Strategy>>`: `EmailProvider` lets delivery use ZeptoMail, SMTP, or mock behavior through one contract.
- `<<Factory>>`: `EmailProviderFactory` chooses and constructs the provider implementation.
- `<<Adapter>>`: provider classes translate MailForge send requests to external provider APIs and return `EmailSendResult`.
- `<<Unit of Work boundary>>`: `AsyncSession` groups persistence changes and commits or rolls them back; there is no separate `UnitOfWork` class.
- `<<Producer / Consumer>>`: Celery tasks process queued work through Redis.
- `<<Frontend Facade>>`: frontend API modules hide Axios configuration and authorization headers from page components.

### Request and Delivery Sequence

```mermaid
sequenceDiagram
  participant UI as React page
  participant Client as Frontend API service
  participant Route as FastAPI router
  participant Auth as JWT dependency
  participant Service as Application service
  participant Repo as Repository
  participant DB as PostgreSQL
  participant Factory as EmailProviderFactory
  participant Provider as ZeptoMail or SMTP

  UI->>Client: Submit campaign or request data
  Client->>Route: HTTP request with Bearer token
  Route->>Auth: Resolve current user and DB session
  Auth->>Repo: Load user
  Repo->>DB: SELECT user
  DB-->>Repo: User record
  Repo-->>Auth: Authenticated user
  Route->>Service: Validate and execute use case
  Service->>Repo: Read or write domain data
  Repo->>DB: SQLAlchemy query / transaction
  DB-->>Repo: Persisted model
  Service->>Factory: Select configured provider
  Factory-->>Service: Provider implementation
  Service->>Provider: Send normalized email request
  Provider-->>Service: EmailSendResult
  Service-->>Route: Serialized result
  Route-->>Client: JSON response
  Client-->>UI: Update page state
```

### Pattern-to-Code Map

| LLD pattern | Where it is used | Implementation evidence and role |
| :--- | :--- | :--- |
| **Layered / Clean Architecture** | `backend/app/api`, `application`, `domain`, `infrastructure` | Routers handle HTTP, services handle orchestration, entities hold domain concepts, and repositories/providers handle persistence and integrations. |
| **Modular Monolith** | `backend/app/api/routes` and matching services/repositories | Auth, campaigns, contacts, templates, lists, tags, segments, suppressions, onboarding, and tracking are isolated modules inside one FastAPI application. |
| **Dependency Injection** | `backend/app/core/dependencies.py`, route function parameters | FastAPI `Depends` injects the authenticated user, JWT-derived user ID, and `AsyncSession`; routes do not construct those concerns themselves. |
| **Repository** | `backend/app/infrastructure/repositories/base.py` and feature repositories | `BaseRepository` centralizes CRUD behavior; `UserRepository`, `CampaignRepository`, `ContactRepository`, `TemplateRepository`, and others add feature-specific queries. |
| **Service Layer** | `backend/app/application/services/*.py` | `CampaignService`, `AuthService`, `ContactService`, `TemplateService`, `MailingListService`, and related classes coordinate validation and business workflows above persistence. |
| **DTO / Data Mapper boundary** | `backend/app/schemas/*.py`, route responses | Pydantic request and response schemas such as `OnboardingPhaseOneRequest` and `OnboardingPhaseOneResponse` define the HTTP data contract instead of exposing arbitrary database payloads. |
| **Strategy / Polymorphism** | `backend/app/infrastructure/email/providers/base.py`, `smtp.py`, `zeptomail.py`, `mock.py` | `EmailProvider` defines the common `send` contract; concrete providers can be selected without changing the campaign service. |
| **Factory** | `backend/app/infrastructure/email/providers/factory.py` | `EmailProviderFactory.get_provider()` creates the mock, SMTP, or ZeptoMail implementation from a provider name. |
| **Adapter** | `SMTPProvider`, `ZeptoMailProvider`, and Zoho infrastructure clients | External email and campaign APIs are translated into MailForge-facing provider/client contracts and normalized results such as `EmailSendResult`. |
| **Unit of Work / transaction boundary** | `AsyncSession` usage in repositories, routes, and services | SQLAlchemy sessions group writes and call `commit`, `refresh`, and `rollback` around a request or task. This is a lightweight transaction boundary rather than a dedicated `UnitOfWork` class. |
| **Template Method / shared base class** | `BaseService`, `BaseRepository`, `BaseEmailProvider` | Shared constructors and CRUD/provider scaffolding are defined once and specialized by feature implementations. |
| **State Machine** | `CampaignService.VALID_STATUS_TRANSITIONS` | Campaign lifecycle transitions are explicitly allowed from `draft`, `scheduled`, `queued`, `sending`, and `paused` states, preventing invalid status changes. |
| **Producer / Consumer with retry** | `backend/app/tasks`, `backend/app/core/celery.py`, Redis | API/application code produces background work; Celery workers consume it through Redis and retry transient email failures with backoff. |
| **Facade** | Frontend modules in `frontend/src/services` | `authApi`, `campaignApi`, `contactApi`, and related modules provide small feature-focused facades over Axios and attach authentication headers consistently. |

### Important Boundary Notes

- The current `backend/app/domain/interfaces` directory contains only `__init__.py`; repository behavior is currently expressed through concrete repository classes and Python typing rather than a separate repository-interface hierarchy.
- `CampaignService` directly uses SQLAlchemy models and queries in parts of campaign dispatch, so the architecture is layered but not completely dependency-inverted.
- `AsyncSession` provides transaction handling, but there is no dedicated `UnitOfWork` abstraction in the current source.
- The frontend is implemented with JavaScript/JSX in `frontend/src`, despite older documentation labels mentioning TypeScript and Tailwind.

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

Authentication uses a short-lived JWT access token plus a database-backed refresh token. The frontend Axios client retries a protected request once after a 401 response by calling `/auth/refresh`; concurrent 401 responses share the same refresh request. If the refresh token is missing, revoked, expired, or invalid, local auth state is cleared and the user is returned to sign-in. Protected backend routes reject malformed, invalid, and expired JWTs with 401 responses and reject non-active user accounts with 403 responses. Access and refresh lifetimes are controlled by `ACCESS_TOKEN_EXPIRE_MINUTES` and `ACCESS_TOKEN_EXPIRE_DAYS`.

For local Vite development, the proxy forwards all frontend API route groups, including `/auth`, `/onboarding`, `/track`, and the authenticated workspace resources, to the FastAPI server on port 8000.

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

# Voice Summary API — Architecture & Refactoring Plan

---

## 1. Current Scenarios (As-Is)

### Authentication
| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | POST | `/auth/register` | Register with email + password |
| 2 | POST | `/auth/login` | Login, returns JWT |
| 3 | POST | `/auth/loginSwagger` | Form-based login for Swagger UI |
| 4 | GET | `/auth/me` | Get current user profile |

### User — Audio
| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 5 | POST | `/user/audio/upload` | Upload audio → transcribe |
| 6 | POST | `/user/audio/upload_summarize` | Upload audio → transcribe → summarize |
| 7 | GET | `/user/audio/` | List user's transcriptions |
| 8 | GET | `/user/audio/{audio_id}` | Get summaries for a transcription |
| 9 | POST | `/user/audio/summarize` | Summarize existing transcription |

### User — Prompts
| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 10 | GET | `/user/prompt/` | List non-deleted prompts |

### Admin — Prompts
| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 11 | POST | `/admin/prompt/` | Create prompt |
| 12 | GET | `/admin/prompt/` | List all prompts (incl. deleted) |
| 13 | PUT | `/admin/prompt/{id}` | Update prompt |
| 14 | PATCH | `/admin/prompt/{id}/delete` | Soft-delete prompt |
| 15 | PATCH | `/admin/prompt/{id}/restore` | Restore prompt |

### System
| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 16 | GET | `/health` | Health check (API + DB) |
| 17 | GET | `/` | Redirect to `/docs` |

---

## 2. Current Architecture Issues

| # | Severity | Issue | Location |
|---|----------|-------|----------|
| 1 | 🔴 CRITICAL | Dead code — `app/api/upload.py` is 109 lines of duplicate logic not connected to any router | `app/api/upload.py` |
| 2 | 🔴 CRITICAL | Service layer raises HTTPExceptions — `app/services/audio.py` imports FastAPI types, making it untestable without HTTP stack | `app/services/audio.py` |
| 3 | 🔴 CRITICAL | Synchronous network calls block the event loop — Whisper + LLM calls are `def` but called with `await` from async endpoints | `transcription_service.py`, `summarise_service.py` |
| 4 | 🔴 CRITICAL | Timestamp defaults evaluate at import time — `datetime.now(timezone.utc)` without lambda = all records get same timestamp | `models/transcription.py`, `models/summary.py` |
| 5 | 🔴 CRITICAL | No rollback on failure — partial commits leave orphaned records in DB | `services/audio.py` |
| 6 | 🟡 MODERATE | No standard response envelope — 3+ different response shapes across endpoints | All routes |
| 7 | 🟡 MODERATE | Provider config is hardcoded — adding a new AI provider means editing `openai_client.py` | `services/openai_client.py` |
| 8 | 🟡 MODERATE | No request tracing / correlation IDs — impossible to trace a request through logs | Entire app |
| 9 | 🟡 MODERATE | No background task queue — long audio files hold HTTP connection open | All upload endpoints |
| 10 | 🟡 MODERATE | All endpoints use `response_model=None` — no response validation or docs schema | All route files |

---

## 3. Target Architecture (To-Be)

### Layer Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI App (main.py)                  │
├─────────────────────────────────────────────────────────┤
│                      CORS Middleware                      │
├─────────────────────────────────────────────────────────┤
│  API Layer (app/api/v1/)  ← Thin routes, only HTTP logic │
│  ┌──────────┬───────────┬────────────┬────────────────┐  │
│  │ auth.py  │user/audio │user/prompt │ admin/prompt   │  │
│  └────┬─────┴─────┬─────┴──────┬─────┴───────┬────────┘  │
│       │           │            │             │           │
├───────┴───────────┴────────────┴─────────────┴───────────┤
│  Services (app/services/)  ← Orchestration + Business    │
│  ┌─────────┬────────────┬──────────────┬──────────────┐  │
│  │ auth    │ audio      │ transcribe   │ summarize    │  │
│  └────┬────┴─────┬──────┴──────┬───────┴──────┬───────┘  │
│       │          │             │              │          │
├───────┴──────────┴─────────────┴──────────────┴──────────┤
│  Repositories (app/repositories/)  ← Data access only     │
│  ┌──────┬──────────────┬─────────┬───────────────┐       │
│  │ user │ transcription│  prompt │  summary      │       │
│  └──┬───┴──────┬───────┴────┬────┴──────┬────────┘       │
│     │          │            │           │                │
├─────┴──────────┴────────────┴───────────┴────────────────┤
│  Models (app/models/)  ← SQLAlchemy ORM definitions       │
│  Providers (app/providers/)  ← AI API abstraction         │
│  Core (app/core/)  ← Config, Security, Exceptions         │
└──────────────────────────────────────────────────────────┘
```

### Directory Structure (New)

```
app/
├── main.py                        # App factory, lifespan, route registration
├── core/
│   ├── __init__.py
│   ├── config.py                  # pydantic-settings (reads .env)
│   ├── security.py                # Password hashing, JWT encode/decode
│   ├── dependencies.py            # get_db, get_current_user, admin_required
│   ├── response.py                # Standard API response envelope
│   └── exceptions.py              # Domain exceptions (no HTTP knowledge)
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── router.py              # Aggregates all v1 routes
│       ├── auth.py                # /auth/*
│       ├── health.py              # /health
│       ├── user/
│       │   ├── __init__.py
│       │   ├── audio.py           # /user/audio/*
│       │   └── prompt.py          # /user/prompt/*
│       └── admin/
│           ├── __init__.py
│           └── prompt.py          # /admin/prompt/*
├── models/
│   ├── __init__.py                # Imports all models for Alembic
│   ├── base.py                    # DeclarativeBase
│   ├── user.py
│   ├── transcription.py
│   ├── prompt.py
│   └── summary.py
├── schemas/                       # Pydantic request/response models
│   ├── __init__.py
│   ├── auth.py
│   ├── audio.py
│   ├── prompt.py
│   └── common.py                  # PaginatedResponse, ErrorResponse, etc.
├── repositories/                  # Data access layer
│   ├── __init__.py
│   ├── base.py                    # BaseRepository with common CRUD
│   ├── user_repo.py
│   ├── transcription_repo.py
│   ├── prompt_repo.py
│   └── summary_repo.py
├── services/                      # Business logic / orchestration
│   ├── __init__.py
│   ├── auth_service.py
│   ├── audio_service.py           # Orchestrates transcribe → summarize
│   ├── transcription_service.py   # Whisper/Groq transcription calls
│   ├── summarization_service.py   # LLM summarization calls
│   └── prompt_service.py          # Prompt CRUD
├── providers/                     # AI provider abstraction
│   ├── __init__.py
│   ├── base.py                    # Abstract base class
│   ├── openai_provider.py         # OpenAI implementation
│   └── factory.py                 # Provider factory
├── db/
│   ├── __init__.py
│   └── database.py                # Engine + SessionLocal
├── utils/
│   ├── __init__.py
│   └── logging.py                 # Structured logging setup
└── __init__.py

alembic/
├── env.py
├── script.py.mako
└── versions/                      # Unchanged, Alembic auto-detects models
```

---

## 4. Data Flow — Request Lifecycle

```
Client Request
    │
    ▼
┌────────────────────────────────┐
│  FastAPI App (main.py)          │
│  • CORS middleware              │
│  • Request ID middleware        │
│  • Route matching               │
└────────────────────────────────┘
    │
    ▼
┌────────────────────────────────┐
│  API Route (app/api/v1/)        │
│  • Parse request (path, query,  │
│    body via Pydantic schemas)   │
│  • Inject dependencies          │
│    (get_db, get_current_user)   │
│  • Call service, return response│
└────────────────────────────────┘
    │
    ▼
┌────────────────────────────────┐
│  Service (app/services/)        │
│  • Orchestrate business logic   │
│  • Call repositories for data   │
│  • Call providers for AI        │
│  • Raise domain exceptions      │
│  • Return domain objects        │
└────────────────────────────────┘
    │
    ├──────────────────────┐
    ▼                      ▼
┌──────────────┐  ┌──────────────────┐
│ Repositories  │  │ Providers         │
│ (SQLAlchemy)  │  │ (Groq / OpenAI)   │
└──────┬───────┘  └────────┬─────────┘
       │                   │
       ▼                   ▼
┌──────────────┐  ┌──────────────────┐
│   MySQL DB   │  │  Groq API        │
└──────────────┘  └──────────────────┘
    │                   │
    └───────────────────┘
           │
           ▼
┌────────────────────────────────┐
│  Response                      │
│  • Standard envelope:          │
│    {success, data, error}      │
│  • Domain → Pydantic schema    │
│  • Auto-docs via response_model│
└────────────────────────────────┘
```

---

## 5. Key Design Decisions

### 5.1 Standardized API Response Envelope

Every endpoint returns:

```json
// Success
{
  "success": true,
  "data": { ... },
  "error": null
}

// Error
{
  "success": false,
  "data": null,
  "error": {
    "code": "TRANSCRIPTION_FAILED",
    "message": "Whisper transcription failed: ..."
  }
}

// List
{
  "success": true,
  "data": [ ... ],
  "error": null
}
```

### 5.2 Repository Pattern

```python
class BaseRepository(Generic[ModelT]):
    def __init__(self, db: Session): ...
    def get(self, id: int) -> ModelT | None: ...
    def list(self, **filters) -> list[ModelT]: ...
    def create(self, **data) -> ModelT: ...
    def update(self, id: int, **data) -> ModelT: ...
    def delete(self, id: int) -> None: ...
```

Benefits:
- Services never write raw SQL or SQLAlchemy queries
- Repositories are swappable (test with in-memory SQLite)
- Query logic is centralized, not scattered across services

### 5.3 Provider Abstraction

```python
class AIProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_file: BinaryIO, prompt: str | None = None) -> str: ...
    @abstractmethod
    async def summarize(self, text: str, system_prompt: str) -> str: ...
```

- `OpenAIProvider` — uses `AsyncOpenAI` client
- `GroqProvider` — uses `AsyncOpenAI` with Groq base URL
- Factory picks the right one based on `AI_PROVIDER` config
- Adding a new provider = new class, no other code changes

### 5.4 Async AI Calls

```python
# transcription_service.py
async def transcribe_audio(file_path: str, prompt: str | None = None) -> str:
    client = AsyncOpenAI(...)  # or provider.transcribe()
    chunks = split_audio(file_path)
    results = await asyncio.gather(*[transcribe_chunk(c) for c in chunks])
    return " ".join(results)
```

### 5.5 Transaction Safety

```python
async def upload_and_summarize(...):
    try:
        transcription = transcription_repo.create(...)
        db.flush()  # or rely on auto-flush before AI calls
        transcript = await transcription_service.transcribe(...)
        transcription_repo.update(transcription.id, result=transcript, status="done")
        
        summary = summary_repo.create(...)
        db.flush()
        summary_text = await summarization_service.summarize(...)
        summary_repo.update(summary.id, summary=summary_text, status="success")
        
        db.commit()
    except Exception:
        db.rollback()
        raise
```

### 5.6 Model Timestamps (Fixed)

```python
# In ALL models — use lambdas
created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                    onupdate=lambda: datetime.now(timezone.utc))
```

---

## 6. Differences: Current → New

| Aspect | Current | New |
|--------|---------|-----|
| **Dead code** | `app/api/upload.py` (109 lines) | **Deleted** |
| **Service layer** | Raises `HTTPException`, imports FastAPI types | Raises domain exceptions, pure Python |
| **AI calls** | Synchronous (`def`, blocks event loop) | Async (`async def`, non-blocking) |
| **Provider config** | Hardcoded in `openai_client.py` | Plugin via `providers/` with factory |
| **Model timestamps** | Eval at import (bug) | Lambda-wrapped (correct) |
| **Response format** | 3+ inconsistent shapes | Standard `{success, data, error}` |
| **Data access** | Raw queries in services | Repository pattern |
| **Transaction mgmt** | Partial commits on error | Rollback on any failure |
| **Error handling** | `HTTPException` in services | Domain exceptions → HTTP in routes |
| **Dependencies** | `get_db`, `get_current_user` in a single file | Organized in `core/dependencies.py` |
| **Config** | Raw `os.getenv()` | `pydantic-settings` validation |
| **Request tracing** | None | Request ID middleware + structured logging |
| **Security** | `allow_origins=["*"]`, weak default secret | Configurable via env, documented |
| **Auth** | JWT only, 30-min expiry, no refresh | Same (out of scope for this refactor) |
| **Background tasks** | None | Same (future: add Celery/Redis) |
| **Tests** | None | Out of scope for this refactor |

---

## 7. Implementation Order

### Phase 1 — Foundation (current refactor)
1. Create `app/core/` — config, security, response, exceptions, dependencies
2. Create `app/schemas/` — Pydantic request/response models
3. Create `app/repositories/` — data access layer
4. Create `app/providers/` — AI provider abstraction
5. Refactor `app/models/` — fix timestamps, add base
6. Refactor `app/services/` — clean orchestration, async AI calls
7. Create `app/api/v1/` — thin routes using new stack
8. Update `app/main.py` — new router, lifespan, middleware
9. Delete dead code
10. Update Alembic config if needed

### Phase 2 — Future
- Add background task queue (Celery / Redis Queue)
- Add request rate limiting
- Add API versioning (already structured for v1)
- Add integration tests
- Add metrics / monitoring
- Add file storage abstraction (S3, not just temp files)

---

## 8. Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Framework** | FastAPI 0.116+ | Native async, Pydantic integration, auto-docs |
| **ORM** | SQLAlchemy 2.0+ | Mature, Alembic integration, type-safe |
| **DB Driver** | PyMySQL | MySQL-compatible via Docker |
| **Validation** | Pydantic v2 | FastAPI-native, `from_attributes` for ORM mode |
| **Auth** | python-jose + passlib | JWT + bcrypt, lightweight |
| **AI Client** | openai SDK (AsyncOpenAI) | OpenAI-compatible, works with Groq endpoint |
| **Config** | pydantic-settings | Type-safe env vars, `.env` file support |
| **Server** | Uvicorn | ASGI server for FastAPI |

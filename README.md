# Voice Summary API

Convert voice messages to transcriptions and summaries using OpenAI's Whisper and GPT models, with multi-user support and customizable prompts.

---

title: Voice Summary API  
description: Backend API for processing audio files with automatic transcription and summarization, featuring multi-user authentication and admin-managed prompt templates.  
status: Active Development  
category: Backend / Audio Processing  
stack: FastAPI, SQLAlchemy, PostgreSQL, OpenAI API, Alembic  
featured: false  
github: https://github.com/imanlangaran/SpeachToSummaryText_backend  
demo: N/A

---

## Overview

Voice Summary API is a backend service that enables users to upload audio files and receive automatic transcriptions and summaries in Persian. The system leverages OpenAI's Whisper for accurate speech-to-text conversion and GPT models (via OpenAI Assistants) for intelligent text summarization.

**What it solves:**
- Converts voice messages into written transcriptions
- Generates contextual summaries from transcribed content
- Manages multiple users with isolated data access
- Allows admins to create and manage custom summarization prompts

**Who it's for:**
- Organizations handling Persian-language voice communications
- Applications requiring audio processing capabilities
- Teams that need flexible, custom summarization logic

**Why it matters:**
Combines multiple AI services into a cohesive workflow with proper state management, user isolation, and customizable behavior. The architecture separates concerns between transcription, summarization, and prompt management—allowing different summaries to be generated from the same transcript using different prompts.

## Features

- **Audio Upload & Transcription** – Upload MP3/audio files; automatic speech-to-text conversion using OpenAI Whisper with Persian language support
- **Custom Summarization Prompts** – Admins define and manage prompts; users generate multiple summaries from the same transcript using different prompts
- **Multi-User Architecture** – Role-based access (user/admin) with isolated data per user
- **JWT Authentication** – Token-based auth with 30-minute expiration
- **OpenAI Assistants Integration** – Uses OpenAI's Assistant API for advanced summarization workflows
- **Health Checks** – Built-in API health monitoring with optional database connectivity checks
- **Audio Management** – Retrieve user's transcription history and associated summaries
- **Database Migrations** – Alembic-powered schema versioning

## Tech Stack

**Backend**
- FastAPI 0.116.1 – Modern async Python web framework
- SQLAlchemy 2.0.41 – ORM for database interactions
- Uvicorn 0.35.0 – ASGI server

**Database**
- PostgreSQL (via SQLAlchemy) or MySQL compatible via PyMySQL 1.1.1
- Alembic 1.16.4 – Schema migrations

**AI/Services**
- OpenAI SDK 1.97.1 – Whisper transcription and GPT summarization
- Pydub 0.25.1 – Audio processing and chunking

**Authentication & Security**
- Python-Jose 3.5.0 – JWT token handling
- Passlib 1.7.4 – Password hashing (bcrypt)
- PyASN1 0.6.1 – ASN.1 support

**Utilities**
- Pydantic 2.11.7 – Data validation and serialization
- Python-dotenv 1.1.1 – Environment variable management
- CORS middleware – Cross-origin request handling

## Architecture

### Request Flow

```
Client Request
    ↓
CORS Middleware
    ↓
Router (Admin/User)
    ↓
Authentication (JWT → get_current_user)
    ↓
Service Layer (audio.py, prompt.py, transcription_service.py, summarise_service.py)
    ↓
Database Layer (SQLAlchemy models → PostgreSQL/MySQL)
    ↓
External APIs (OpenAI Whisper, OpenAI Assistants)
    ↓
Response to Client
```

### Service Boundaries

**Authentication Service**
- User registration and login
- JWT token generation and validation
- Role-based authorization (admin vs. regular user)

**Audio Service** (`app/services/audio.py`)
- Handles file upload validation
- Coordinates transcription and summarization
- Manages temporary file cleanup
- Supports batch audio chunking for files exceeding 2-minute limit

**Transcription Service** (`app/services/transcription_service.py`)
- Calls OpenAI Whisper API
- Splits large audio files (>2 min or >25 MB) into chunks
- Standardizes audio to 16kHz mono for consistency
- Accumulates chunked transcriptions

**Summarization Service** (`app/services/summarise_service.py`)
- Two paths: direct GPT summarization or OpenAI Assistants
- Uses OpenAI Assistants for advanced, template-based summaries
- Threads messages and polls for completion

**Prompt Service** (`app/services/prompt.py`)
- Full CRUD for admin-managed prompts
- Soft-delete pattern for data retention
- Tracks each prompt's associated OpenAI Assistant ID

### Data Model

**Users** – Email, hashed password, Telegram ID (optional), admin flag, creation timestamp

**Transcriptions** – Audio metadata, user reference, transcription result, processing status, optional prompt hints

**Prompts** – Template definitions for summaries, OpenAI Assistant ID, soft-delete support, update tracking

**Summaries** – Results of summarization runs, linked to transcription + prompt + user, status tracking

**Relationships:**
- Users → many Transcriptions
- Users → many Summaries
- Prompts → many Summaries
- Transcriptions → many Summaries
- Unique constraint: (user_id, transcription_id, prompt_id) prevents duplicate summaries

## Project Structure

```
app/
├── main.py                 # FastAPI app setup, health check, route registration
├── auth/
│   ├── auth_router.py      # Register, login endpoints
│   ├── auth_utils.py       # Password hashing, user lookup
│   ├── jwt_handler.py      # JWT creation/decoding
│   └── dependencies.py     # OAuth2 scheme, get_current_user, admin_required
├── api/
│   ├── upload.py           # Legacy audio upload (not currently used)
│   ├── admin/
│   │   ├── routes.py       # Admin route aggregator
│   │   └── prompt.py       # Prompt CRUD endpoints (create, list, update, soft-delete, restore)
│   └── client/
│       ├── routes.py       # User route aggregator
│       ├── audio.py        # User audio endpoints (upload, upload+summarize, list, fetch)
│       └── prompt.py       # User prompt listing
├── services/
│   ├── openai_client.py    # Singleton OpenAI client initialization
│   ├── audio.py            # Core audio processing workflows
│   ├── transcription_service.py  # Whisper integration with chunking
│   ├── summarise_service.py      # GPT and Assistant-based summarization
│   └── prompt.py           # Prompt CRUD business logic
├── models/
│   ├── __init__.py         # Alembic auto-detection
│   ├── user.py
│   ├── transcription.py
│   ├── prompt.py
│   └── summary.py
├── db/
│   ├── database.py         # SQLAlchemy engine, session, health check
│   └── schemas.py          # Pydantic models (UserCreate, UserLogin, UserOut)

alembic/
├── env.py                  # Migration environment configuration
├── script.py.mako          # Migration template
└── versions/               # Versioned migration scripts

requirements.txt            # Python dependencies
alembic.ini                 # Alembic configuration
.env.example                # Environment variable template
```

## API Documentation

### Authentication

**POST /auth/register**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```
Returns: User object with ID, email, admin flag

**POST /auth/login**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```
Returns: `{"access_token": "...", "token_type": "bearer"}`

**POST /auth/loginSwagger** (Form-based for Swagger UI)
- Use this endpoint in Swagger's "Authorize" button
- Parameters: `username` (email), `password`

**GET /auth/me** (Requires Bearer token)
Returns: Current user's email and admin status

### Health Check

**GET /health?include_db=true**
- `include_db`: Optional boolean (default: true)
- Returns: `{"api": "✅ Service is operational", "database": "...", "timestamp": "..."}`

### User Audio Endpoints

All require valid JWT token in `Authorization: Bearer <token>` header.

**POST /user/audio/upload**
- Multipart form data:
  - `file`: MP3/audio file
  - `prompt` (optional): Hint text for Whisper
- Returns: `{"filename": "...", "transcript": "...", "id": <transcription_id>}`

**POST /user/audio/upload_summarize**
- Multipart form data:
  - `file`: MP3/audio file
  - `transcribePrompt` (optional): Hint for transcription
  - `summaryPromptId`: ID of the prompt to use
- Returns: `{"success": "true", "data": {"summarise_text": "...", "audioId": <id>}}`

**GET /user/audio/**
- Returns all transcriptions for the authenticated user
- Returns: `{"success": "true", "data": [...]}`

**GET /user/audio/{audio_id}**
- Returns all summaries for a specific transcription
- Returns: `{"success": "true", "data": [...]}`

**POST /user/audio/summarize**
- Query parameters:
  - `audioId`: Transcription ID
  - `summaryPromptId`: Prompt ID to apply
- Generates a new summary from existing transcription
- Returns: `{"success": "true", "data": {"summarise_text": "..."}}`

**GET /user/prompt/**
- Returns available prompts (non-deleted)
- Returns: Array of `{"id": <int>, "title": <str>, "is_deleted": <bool>}`

### Admin Endpoints

All require valid JWT token with `is_admin=true`.

**POST /admin/prompt/**
- Query parameters: `title`, `content`
- Creates a new summarization prompt
- Note: `assistant_id` must be set manually in the database or via PATCH

**GET /admin/prompt/?include_deleted=false**
- Query parameters: `include_deleted` (default: false)
- Lists prompts

**PUT /admin/prompt/{prompt_id}**
- Query parameters: `title`, `content`
- Updates a prompt's metadata

**PATCH /admin/prompt/{prompt_id}/delete**
- Soft-deletes a prompt (marks `is_deleted=true`)

**PATCH /admin/prompt/{prompt_id}/restore**
- Restores a soft-deleted prompt

## Database Design

### Users Table
```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  email VARCHAR(254) UNIQUE NOT NULL,
  hashed_password VARCHAR(60) NOT NULL,
  telegram_id VARCHAR(128),
  is_admin BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT UTC_NOW
);
```

### Transcriptions Table
```sql
CREATE TABLE transcriptions (
  id INT PRIMARY KEY,
  user_id INT FOREIGN KEY,
  file_path VARCHAR(512),
  prompt TEXT,
  status VARCHAR(20) DEFAULT 'pending',
  result TEXT,
  error_message TEXT,
  created_at DATETIME,
  updated_at DATETIME
);
```

### Prompts Table
```sql
CREATE TABLE prompts (
  id INT PRIMARY KEY,
  title VARCHAR(100) NOT NULL,
  content TEXT,
  assistant_id TEXT NOT NULL,
  is_deleted BOOLEAN DEFAULT FALSE,
  created_at DATETIME,
  updated_at DATETIME
);
```

### Summaries Table
```sql
CREATE TABLE summaries (
  id INT PRIMARY KEY,
  user_id INT FOREIGN KEY,
  transcription_id INT FOREIGN KEY,
  prompt_id INT FOREIGN KEY,
  summary TEXT,
  result TEXT,
  status VARCHAR(20) DEFAULT 'pending',
  created_at DATETIME,
  UNIQUE(user_id, transcription_id, prompt_id)
);
```

**Key Design Decision:** The unique constraint on (user_id, transcription_id, prompt_id) prevents duplicate summaries. The same transcript can be summarized multiple times with different prompts, but only one summary per (transcript, prompt) pair per user.

## Authentication & Authorization

**JWT-based Authentication**
- Token creation: `create_access_token(data={"sub": user_email})` with 30-minute expiration
- Token validation: `decode_access_token(token)` returns payload or None
- Algorithm: HS256

**Authorization**
- `get_current_user` dependency: Validates token and fetches user from database
- `admin_required` dependency: Extends `get_current_user` with `is_admin` check
- All routes requiring auth use these dependencies via FastAPI's `Depends()`

**Password Security**
- Bcrypt hashing via Passlib
- Passwords verified during login only; never stored plaintext

## Performance & Scalability

**Audio Processing**
- Large files (>2 min or >25 MB) are split into 2-minute chunks before sending to Whisper
- Each chunk is transcribed independently; results are concatenated
- Temporary files are cleaned up immediately after processing

**Database**
- SQLAlchemy ORM with connection pooling
- Indexed columns: user_id, email, prompt.is_deleted
- Unique constraint on summaries table prevents redundant processing

**OpenAI API Considerations**
- Whisper API has 25 MB file limit; chunking strategy handles larger files
- Assistant API uses thread-based polling (not streaming)
- No retry logic or backoff implemented; client should handle rate limits

**Async I/O**
- Audio upload endpoints are async (`async def`)
- Leverages Uvicorn's async runtime for I/O-bound operations

## Engineering Decisions

### Why FastAPI?
- Native async/await support enables handling multiple concurrent uploads
- Built-in request validation via Pydantic reduces boilerplate
- Auto-generated OpenAPI documentation (Swagger)
- Dependency injection system (FastAPI's `Depends()`) simplifies auth and database access

### Why SQLAlchemy 2.0?
- Modern async support (though currently using sync mode with ThreadPoolExecutor via Uvicorn)
- Type hints and expressive query API
- Alembic integration for versioned migrations
- Automatic relationship management reduces manual foreign-key handling

### Why OpenAI Assistants API for Summarization?
- The architecture supports *multiple summaries per transcript* using *different prompts*
- Assistants API allows stateful, template-based workflows with system instructions embedded in the assistant definition
- Direct GPT fallback (`summarise_text()`) is available but Assistants are the primary path

### Why Soft Deletes for Prompts?
- Soft-delete preserves referential integrity; summaries linked to deleted prompts remain queryable
- Enables restore functionality without losing audit trails

### Why Chunking Audio?
- OpenAI Whisper API has 25 MB limit
- Most voice messages are <2 min; chunking allows processing longer recordings without truncation
- Preserves context by overlapping chunk boundaries (not yet implemented but architectural foundation exists)

## Challenges & Solutions

**Challenge: OpenAI API Rate Limits**
- Issue: Multiple concurrent uploads could exceed rate limits
- Current State: No retry logic or backoff implemented
- Mitigation Path: Client should handle 429 responses; server could implement exponential backoff

**Challenge: Large Audio File Processing**
- Issue: Whisper API has 25 MB file size limit and practical duration limits
- Solution: Automatic chunking strategy splits files into 2-minute segments before transcription

**Challenge: Audio File Storage**
- Issue: Temporary files are created during processing
- Solution: Immediate cleanup in `finally` block; files are not persisted long-term (only metadata stored)

**Challenge: Unique Summary Constraint**
- Issue: Preventing duplicate summaries for the same (user, transcript, prompt) tuple
- Solution: Database unique constraint enforces this; API doesn't re-summarize if record exists

**Challenge: Async Summarization**
- Issue: GPT summarization and Assistant polling are blocking calls
- Current State: No background job queue; requests are synchronous
- Architectural Note: Service layer is isolated; adding Celery/task queue would require minimal routing changes

## Installation

### Prerequisites
- Python 3.9+
- FFmpeg (required by Pydub for audio handling)
- PostgreSQL or MySQL
- OpenAI API key (for Whisper and GPT models)

### System Dependencies
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg -y

# Windows (via Chocolatey)
choco install ffmpeg
```

### Python Setup
```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Unix/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Database Setup
```bash
# Apply migrations
alembic upgrade head
```

### Environment Variables
Create a `.env` file in the project root:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/voice_summary
# or for MySQL:
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/voice_summary

# OpenAI
OPENAI_API_KEY=sk-...

# Security
SECRET_KEY=your-secret-key-here-min-32-chars
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | SQLAlchemy connection string (PostgreSQL or MySQL) |
| `OPENAI_API_KEY` | Yes | OpenAI API key for Whisper and GPT models |
| `SECRET_KEY` | Yes | HS256 signing key for JWT tokens (minimum 32 characters) |

**Notes:**
- Never commit `.env` to version control; use `.env.example` as a template
- `SECRET_KEY` should be cryptographically random in production

## Running Locally

### Start the Development Server
```bash
# With Uvicorn (default)
uvicorn app.main:app --reload

# Or with FastAPI CLI
fastapi run app/main.py

# Server will be available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
# ReDoc at http://localhost:8000/redoc
```

### Database Migrations
```bash
# Create a new migration (auto-detects changes)
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

### Testing Authentication
In Swagger UI (`/docs`):
1. Click "Authorize"
2. Use `/auth/loginSwagger` endpoint to get token
3. Paste token in Authorize dialog
4. Make authenticated requests

## Deployment

The API is containerizable and suitable for cloud deployment. Key considerations:

**Docker Support** (not yet in repository)
- Base image: `python:3.11-slim`
- Expose port 8000
- Run: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

**Environment Configuration**
- All secrets via environment variables (no hardcoding)
- Database URL must point to production database
- CORS origins should be restricted to frontend domain

**Database Migration Strategy**
- Run `alembic upgrade head` during deployment
- Migrations are safe to run multiple times (idempotent)

**Reverse Proxy** (Recommended)
- Use Nginx or Caddy in front of Uvicorn
- Handles HTTPS, compression, rate limiting
- Uvicorn listens on localhost:8000 only

**Monitoring**
- Health endpoint: `GET /health?include_db=true`
- Returns 503 if database unavailable
- Suitable for Kubernetes/Docker health checks

## Future Improvements

**Performance**
- Implement async database queries (SQLAlchemy 2.0 async mode)
- Add Redis caching for prompt lists and frequent queries
- Implement background job queue (Celery) for long-running summarizations

**Audio Processing**
- Implement chunking with overlap to preserve context across boundaries
- Support additional audio formats (WAV, M4A, OGG) beyond MP3
- Add audio preprocessing (noise reduction, normalization)

**Summarization**
- Admin dashboard for monitoring summary quality and prompt effectiveness
- A/B testing framework for comparing different prompts
- Fallback mechanism if primary summarization fails (retry with backup prompt)

**API**
- Batch upload endpoint (process multiple files in single request)
- Webhook support for completion notifications
- Export/download summaries as PDF or formatted text
- Rate limiting per user (prevent abuse)

**Database**
- Add soft delete for transcriptions and summaries (preserve audit trail)
- Archive old records to cold storage
- Add full-text search on transcription results

**Infrastructure**
- Add distributed tracing (OpenTelemetry)
- Implement structured logging (JSON format)
- Metrics collection (Prometheus)
- Alert on high API error rates

<!-- 
## License

No license specified. Please add a `LICENSE` file to the repository (e.g., MIT, Apache 2.0, or proprietary). -->
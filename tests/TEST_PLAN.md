# Test Plan — Voice Summary API

## Test Layers

### 1. Core Tests (`tests/test_core/`)
| Test | What it verifies |
|------|------------------|
| `test_security.py` | Password hashing round-trip, JWT create/decode, invalid token rejection |
| `test_exceptions.py` | Exception attributes (code, message, status_code), hierarchy |

### 2. Repository Tests (`tests/test_repositories/`)
| Test | What it verifies |
|------|------------------|
| `test_user_repo.py` | Create user, get by email, get by id, get_or_404 raises |
| `test_transcription_repo.py` | Create, list by user, cascading relationships |
| `test_prompt_repo.py` | CRUD, list active vs all, soft delete |
| `test_summary_repo.py` | Create, list by transcription, find existing, unique constraint |

### 3. Service Tests (`tests/test_services/`) — Mocked dependencies
| Test | What it verifies |
|------|------------------|
| `test_auth_service.py` | Register success, duplicate email, login success, wrong password |
| `test_audio_service.py` | Upload+transcribe success, upload+summarize, summarize existing, provider failure rollback |
| `test_prompt_service.py` | CRUD, soft-delete, restore |

### 4. API Integration Tests (`tests/test_api/`) — TestClient + test DB
| Test | What it verifies |
|------|------------------|
| `test_health.py` | GET /health with/without DB check |
| `test_auth.py` | POST register, login, loginSwagger, GET /me |
| `test_audio.py` | Upload, list, get summaries, summarize (with mocked AI) |
| `test_prompt.py` | Admin CRUD, user list, soft-delete flow |

### 5. Provider Tests (`tests/test_providers/`)
| Test | What it verifies |
|------|------------------|
| `test_factory.py` | Provider selection based on AI_PROVIDER config |

---

## Fixtures (`conftest.py`)

### Shared
- `test_db` — In-memory SQLite or MySQL test DB with all tables
- `db_session` — Scoped session per test
- `client` — FastAPI TestClient
- `auth_headers` — JWT token for authenticated requests
- `admin_headers` — JWT token for admin requests

### Mocks
- `mock_provider` — Async mock of AIProvider
- `mock_audio_file` — Bytes of a minimal valid audio file

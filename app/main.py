# app/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.auth import auth_router
from app.api import upload  # assuming upload.py is here

from app.db.database import check_db_connection

app = FastAPI(
    title="Voice Summary API",
    version="0.1.0",
    description="Upload voice messages and get summaries using Whisper and GPT",
)

# Optional: CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (don't add prefix here since it's already in the module)
app.include_router(auth_router.router)
app.include_router(
    upload.router, prefix="/audio", tags=["audio"]
)  # or adjust as needed


@app.get("/health", summary="System Health Check")
async def health_check(include_db: bool = True):
    """
    Comprehensive system health check endpoint that verifies:
    - API service availability
    - Database connectivity (optional)

    Parameters:
        include_db (bool): Whether to check database connection (default: True)

    Returns:
        dict: Status report with these possible keys:
            - api: API service status
            - database: Database connection status (if checked)
            - timestamp: Time of the check

    Examples:
        Basic check (API only):
        {'api': '✅ Service is operational', 'timestamp': '2023-01-01T12:00:00'}

        Full check (API + DB):
        {
            'api': '✅ Service is operational',
            'database': '✅ Database connection successful',
            'timestamp': '2023-01-01T12:00:00'
        }

        Error case:
        {
            'api': '✅ Service is operational',
            'database': '❌ Database connection failed: [error details]',
            'timestamp': '2023-01-01T12:00:00'
        }
    """
    from datetime import datetime, timezone

    response = {
        "api": "✅ Service is operational",
        "timestamp": datetime.now(timezone.utc).isoformat()

    }

    if include_db:
        try:
            db_status = check_db_connection()
            response["database"] = db_status["message"]
        except HTTPException as e:
            response["database"] = f"❌ {e.detail['message']}"
        except Exception as e:
            response["database"] = f"❌ Unexpected error: {str(e)}"

    return response

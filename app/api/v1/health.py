"""Health check endpoint."""

from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone

from app.db.database import check_db_connection

router = APIRouter(tags=["system"])


@router.get("/health", summary="System Health Check")
async def health_check(include_db: bool = Query(True)):
    response = {
        "api": "✅ Service is operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if include_db:
        try:
            db_status = check_db_connection()
            response["database"] = db_status["message"]
        except Exception as e:
            response["database"] = f"❌ Database connection failed: {str(e)}"
    return response


@router.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

# app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth import auth_router
from app.api import upload  # assuming upload.py is here

from app.auth.dependencies import get_current_user_email


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


@app.get("/me")
def read_me(user_email: str = Depends(get_current_user_email)):
    return {"email": user_email}

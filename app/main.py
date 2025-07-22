from fastapi import Depends
from app.auth.dependencies import get_current_user
from fastapi import FastAPI
from app.db.database import Base, engine
from app.models import user
from app.auth import auth_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router.router)

@app.get("/")
def root():
    return {"msg": "Voice summarizer backend with auth"}

@app.get("/me")
def read_me(user_email: str = Depends(get_current_user)):
    return {"email": user_email}
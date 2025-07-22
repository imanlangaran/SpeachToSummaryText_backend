from fastapi import FastAPI
from app.db.database import Base, engine
from app.models import user

app = FastAPI()

# Auto-create tables (only for dev!)
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"msg": "Voice summarizer backend (SQLite) is running"}

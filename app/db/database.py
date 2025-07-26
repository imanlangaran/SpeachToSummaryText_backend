from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection():
    """
    Checks the database connection status.

    Returns:
        dict: A status message indicating database connection status.
        Raises HTTPException if connection fails.

    Example:
        Successful: {'status': 'success', 'message': '✅ Database connection successful'}
        Failed: Raises HTTPException with 503 status code
    """
    try:
        # Create a new database session
        db = SessionLocal()
        # Execute a simple SQL query to verify connection
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "success", "message": "✅ Database connection successful"}
    except Exception as e:
        # Log the error (you might want to add proper logging here)
        error_msg = f"Database connection failed: {str(e)}"
        raise HTTPException(
            status_code=503, detail={"status": "error", "message": error_msg}
        )

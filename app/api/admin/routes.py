from fastapi import APIRouter
from .prompt import router as promptRouter

adminRoute = APIRouter(prefix='/admin', tags=['admin'])
  
adminRoute.include_router(promptRouter)
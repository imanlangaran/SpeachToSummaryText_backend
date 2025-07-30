from fastapi import APIRouter
from .prompt import router as promptRouter

clientRoute = APIRouter(prefix='/user', tags=['user'])
  
clientRoute.include_router(promptRouter)
from fastapi import APIRouter
from .prompt import router as promptRouter
from .audio import router as audioRouter

clientRoute = APIRouter(prefix='/user', tags=['user'])
  
clientRoute.include_router(promptRouter)
clientRoute.include_router(audioRouter)
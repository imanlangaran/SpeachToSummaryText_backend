from fastapi import APIRouter
from .prompt import router as promptRouter

adminRoute = APIRouter(prefix='/admin', tags=['admin'])

@adminRoute.get('/')
def check():
  return {
    'success' : 'true',
    'data' : 'this is health ckeck for admin route'
  }
  
adminRoute.include_router(promptRouter)
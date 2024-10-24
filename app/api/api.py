from fastapi import APIRouter
from app.api.endpoints import auth, tasks

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tasks.router, prefix="/task", tags=["tasks"])

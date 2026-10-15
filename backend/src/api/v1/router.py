from fastapi import APIRouter
from src.modules.users.router import router as user_router
api_router = APIRouter()
api_router.include_router(user_router)


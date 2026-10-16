from fastapi import APIRouter
from src.modules.users.router import router as user_router
from src.modules.exercises.router import router as exercise_router
from src.modules.workouts.router import workout_router as workout_router
from src.modules.workouts.router import set_router as set_router

api_router = APIRouter()
api_router.include_router(user_router)
api_router.include_router(exercise_router)

api_router.include_router(workout_router)
api_router.include_router(set_router)

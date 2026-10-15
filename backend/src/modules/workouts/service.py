from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from .schemas import WorkoutCreate
from .models import Workout


async def create_workout(
    session: AsyncSession,
    workouts_in: WorkoutCreate,
    user_id: int,
):
    new_workout = Workout(
        title=workouts_in.title,
        workout_date=workouts_in.workout_date,
        notes=workouts_in.notes,
        user_id=user_id,
    )
    session.add(new_workout)
    await session.commit()
    await session.refresh(new_workout)
    return new_workout


async def get_workout(session: AsyncSession, user_id: int, workout_id: int):
    pass

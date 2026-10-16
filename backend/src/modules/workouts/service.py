from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy.orm import joinedload, selectinload

from .schemas import WorkoutCreate, WorkoutUpdate
from .models import Workout, WorkoutSet


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
    query = (
        select(Workout)
        .options(selectinload(Workout.sets))
        .where(Workout.id == new_workout.id)
    )
    result = await session.execute(query)
    workout_with_sets = result.scalars().first()

    return workout_with_sets


async def get_workout(session: AsyncSession, user_id: int, workout_id: int):
    query = (
        select(Workout)
        .options(selectinload(Workout.sets).joinedload(WorkoutSet.exercise))
        .where(
            Workout.id == workout_id,
            Workout.user_id == user_id,
        )
    )

    result = await session.execute(query)
    workout = result.scalar_one_or_none()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тренировка не найдена"
        )

    return workout


async def update_workout(
    session: AsyncSession, user_id: int, workout_id: int, workout_in: WorkoutUpdate
):
    query = select(Workout).where(Workout.id == workout_id, Workout.user_id == user_id)
    result = await session.execute(query)
    workout = result.scalars().first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренировка не найдена или у вас нет прав на его изменение",
        )

    update_data = workout_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(workout, key, value)

    await session.commit()
    query = (
        select(Workout)
        .options(selectinload(Workout.sets))
        .where(Workout.id == workout_id)
    )
    result = await session.execute(query)
    workout_with_sets = result.scalars().first()
    return workout

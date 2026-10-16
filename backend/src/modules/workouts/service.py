from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy.orm import joinedload, selectinload
from datetime import date
from .schemas import WorkoutCreate, WorkoutUpdate, WorkoutSetCreate, WorkoutSetUpdate
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


async def get_workouts_list(
    session: AsyncSession, user_id: int, date_from: date | None, date_to: date | None
):
    query = (
        select(Workout)
        .options(selectinload(Workout.sets).joinedload(WorkoutSet.exercise))
        .where(Workout.user_id == user_id)
    )

    if date_from is not None:
        query = query.where(Workout.workout_date >= date_from)
    if date_to is not None:
        query = query.where(Workout.workout_date <= date_to)

    query = query.order_by(Workout.workout_date.desc(), Workout.id.desc())

    result = await session.execute(query)
    workouts = result.scalars().all()

    if not workouts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Тренировки не найдены"
        )

    return workouts


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


async def delete_workout(session: AsyncSession, workout_id: int, user_id: int):
    query = select(Workout).where(Workout.id == workout_id, Workout.user_id == user_id)
    result = await session.execute(query)
    workout = result.scalars().first()

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тренироовка не найдена или у вас нет прав на его удаление",
        )

    await session.delete(workout)
    await session.commit()


async def create_workout_set(
    session: AsyncSession, user_id: int, workout_id: int, set_in: WorkoutSetCreate
):
    new_workout_set = WorkoutSet(
        workout_id=workout_id,
        exercise_id=set_in.exercise_id,
        set_number=set_in.set_number,
        reps=set_in.reps,
        extra_weight=set_in.extra_weight,
        is_warmup=set_in.is_warmup,
    )
    session.add(new_workout_set)
    await session.commit()
    query = (
        select(Workout)
        .options(selectinload(Workout.sets).joinedload(WorkoutSet.exercise))
        .where(Workout.id == workout_id)
    )
    result = await session.execute(query)
    workout_with_sets = result.scalars().first()

    return workout_with_sets


async def update_workout_set(
    session: AsyncSession, set_id: int, set_in: WorkoutSetUpdate, user_id: int
):
    query = (
        select(WorkoutSet)
        .join(WorkoutSet.workout)
        .where(
            WorkoutSet.id == set_id,
            Workout.user_id == user_id,
        )
    )
    result = await session.execute(query)
    db_set = result.scalars().first()

    if not db_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подход не найден или у вас нет прав на его изменение",
        )

    update_data = set_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_set, key, value)

    await session.commit()

    refresh_query = (
        select(WorkoutSet)
        .options(joinedload(WorkoutSet.exercise))
        .where(WorkoutSet.id == set_id)
    )
    refresh_result = await session.execute(refresh_query)
    updated_set = refresh_result.scalars().first()

    return updated_set


async def delete_workout_set(session: AsyncSession, set_id: int, user_id: int):
    query = (
        select(WorkoutSet)
        .join(WorkoutSet.workout)
        .where(
            WorkoutSet.id == set_id,
            Workout.user_id == user_id,
        )
    )
    result = await session.execute(query)
    db_set = result.scalars().first()

    if not db_set:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сет не найдена или у вас нет прав на его удаление",
        )

    await session.delete(db_set)
    await session.commit()

from fastapi import HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from sqlalchemy.orm import joinedload, selectinload
from .models import Exercise, MuscleGroup
from .schemas import ExerciseCreate, ExerciseUpdate
from src.modules.workouts.models import Workout, WorkoutSet


async def get_filtered_exercises(
    session: AsyncSession,
    user_id: int,
    muscle_group: MuscleGroup | None = None,
    is_bodyweight: bool | None = None,
    is_own_exercise: bool | None = None,
    search: str | None = None,
):
    query = select(Exercise)

    if is_own_exercise is True:
        query = query.where(Exercise.user_id == user_id)
    elif is_own_exercise is False:
        query = query.where(Exercise.user_id.is_(None))
    else:
        query = query.where(
            or_(Exercise.user_id.is_(None), Exercise.user_id == user_id)
        )

    if muscle_group is not None:
        query = query.where(Exercise.muscle_group == muscle_group)

    if is_bodyweight is not None:
        query = query.where(Exercise.is_bodyweight == is_bodyweight)

    if search:
        query = query.where(Exercise.name.ilike(f"%{search}%"))

    result = await session.execute(query)
    return result.scalars().all()


async def get_last_exercise_performance(
    session: AsyncSession, exercise_id: int, user_id: int
):
    last_workout_subquery = (
        select(Workout.id)
        .join(Workout.sets)
        .where(Workout.user_id == user_id, WorkoutSet.exercise_id == exercise_id)
        .order_by(Workout.workout_date.desc(), Workout.id.desc())
        .limit(1)
        .scalar_subquery()
    )

    query = (
        select(WorkoutSet)
        .options(joinedload(WorkoutSet.exercise))
        .where(
            WorkoutSet.workout_id == last_workout_subquery,
            WorkoutSet.exercise_id == exercise_id,
        )
        .order_by(WorkoutSet.set_number)
    )

    result = await session.execute(query)
    last_sets = result.scalars().all()

    return last_sets


async def create_custom_exercise(
    session: AsyncSession, exercise_in: ExerciseCreate, user_id: int
):
    new_exercise = Exercise(
        name=exercise_in.name,
        muscle_group=exercise_in.muscle_group,
        is_bodyweight=exercise_in.is_bodyweight,
        user_id=user_id,
    )
    session.add(new_exercise)
    await session.commit()
    await session.refresh(new_exercise)
    return new_exercise


async def update_custom_exercise(
    session: AsyncSession, exercise_id: int, exercise_in: ExerciseUpdate, user_id: int
):
    query = select(Exercise).where(
        Exercise.id == exercise_id, Exercise.user_id == user_id
    )
    result = await session.execute(query)
    exercise = result.scalars().first()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Упражнение не найдено или у вас нет прав на его изменение",
        )

    update_data = exercise_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(exercise, key, value)

    await session.commit()
    await session.refresh(exercise)
    return exercise


async def delete_custom_exercise(session: AsyncSession, exercise_id: int, user_id: int):
    query = select(Exercise).where(
        Exercise.id == exercise_id, Exercise.user_id == user_id
    )
    result = await session.execute(query)
    exercise = result.scalars().first()

    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Упражнение не найдено или у вас нет прав на его удаление",
        )

    await session.delete(exercise)
    await session.commit()

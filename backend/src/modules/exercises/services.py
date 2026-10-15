from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Exercise, MuscleGroup
from .schemas import ExerciseCreate


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

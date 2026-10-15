from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db_helper import db_helper
from src.modules.users.dependencies import get_current_user

from .models import Exercise, MuscleGroup
from .schemas import ExerciseCreate, ExerciseResponse

router = APIRouter(tags=["Exercises"])
SessionDep = Annotated[AsyncSession, Depends(db_helper.session_dependency)]


@router.get(
    "/exercises", response_model=list[ExerciseResponse], status_code=status.HTTP_200_OK
)
@router.get(
    "/exercises", response_model=list[ExerciseResponse], status_code=status.HTTP_200_OK
)
async def get_exercises(
    session: SessionDep,
    muscle_group: MuscleGroup | None = Query(None, description="Фильтр по группе мышц"),
    is_bodyweight: bool | None = Query(
        None, description="Только со своим весом (true) или только с железом (false)"
    ),
    is_own_exercise: bool | None = Query(None, description="Собственные упражнения"),
    search: str | None = Query(None, description="Поиск по части названия"),
    user_id: int = Depends(get_current_user),
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


@router.post(
    "/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED
)
async def create_exercise(
    session: SessionDep,
    exercise_in: ExerciseCreate,
    user_id: int = Depends(get_current_user),
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

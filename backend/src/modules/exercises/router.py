from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db_helper import db_helper
from fastapi import Query
from fastapi import Query

from .models import Exercise, MuscleGroup
from .schemas import ExerciseList

router = APIRouter(tags=["Exercises"])
SessionDep = Annotated[AsyncSession, Depends(db_helper.session_dependency)]



@router.get(
    "/exercises", response_model=list[ExerciseList], status_code=status.HTTP_200_OK
)
async def get_exercises(
    session: SessionDep,
    muscle_group: MuscleGroup | None = Query(None, description="Фильтр по группе мышц"),
    is_bodyweight: bool | None = Query(
        None, description="Только со своим весом (true) или только с железом (false)"
    ),
    search: str | None = Query(None, description="Поиск по части названия"),
):
    query = select(Exercise).where(Exercise.user_id.is_(None))

    if muscle_group is not None:
        query = query.where(Exercise.muscle_group == muscle_group)

    if is_bodyweight is not None:
        query = query.where(Exercise.is_bodyweight == is_bodyweight)

    if search:
        query = query.where(Exercise.name.ilike(f"%{search}%"))

    result = await session.execute(query)
    return result.scalars().all()

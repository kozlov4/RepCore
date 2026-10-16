from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db_helper import db_helper
from src.modules.users.dependencies import get_current_user

from .models import Exercise, MuscleGroup
from .schemas import ExerciseCreate, ExerciseResponse, ExerciseUpdate
from src.modules.workouts.schemas import WorkoutSetResponse
from . import services

router = APIRouter(tags=["Exercises"])
SessionDep = Annotated[AsyncSession, Depends(db_helper.session_dependency)]


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
    return await services.get_filtered_exercises(
        session=session,
        muscle_group=muscle_group,
        is_bodyweight=is_bodyweight,
        is_own_exercise=is_own_exercise,
        search=search,
        user_id=user_id,
    )


@router.get(
    "/exercises/{exercise_id}/last-performance",
    response_model=list[WorkoutSetResponse],
    status_code=status.HTTP_200_OK,
)
async def get_last_exercise(
    session: SessionDep, exercise_id: int, user_id: int = Depends(get_current_user)
):
    return await services.get_last_exercise_performance(
        session=session, exercise_id=exercise_id, user_id=user_id
    )


@router.post(
    "/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED
)
async def create_exercise(
    session: SessionDep,
    exercise_in: ExerciseCreate,
    user_id: int = Depends(get_current_user),
):
    return await services.create_custom_exercise(
        session=session, exercise_in=exercise_in, user_id=user_id
    )


@router.patch(
    "/exercises/{exercise_id}",
    response_model=ExerciseResponse,
    status_code=status.HTTP_200_OK,
)
async def update_exercise(
    exercise_id: int,
    exercise_in: ExerciseUpdate,
    session: SessionDep,
    user_id: int = Depends(get_current_user),
):
    return await services.update_custom_exercise(
        session=session,
        exercise_id=exercise_id,
        exercise_in=exercise_in,
        user_id=user_id,
    )


@router.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(
    exercise_id: int,
    session: SessionDep,
    user_id: int = Depends(get_current_user),
):
    await services.delete_custom_exercise(
        session=session, exercise_id=exercise_id, user_id=user_id
    )

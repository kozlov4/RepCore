import datetime
from typing import Annotated
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db_helper import db_helper
from src.modules.users.dependencies import get_current_user

from .schemas import (
    WorkoutResponse,
    WorkoutCreate,
    WorkoutSetUpdate,
    WorkoutUpdate,
    WorkoutSetCreate,
    WorkoutSetResponse,
)
from . import service

workout_router = APIRouter(tags=["Workouts"])

set_router = APIRouter(tags=["Sets"])

SessionDep = Annotated[AsyncSession, Depends(db_helper.session_dependency)]


@workout_router.get(
    "/workouts/{workout_id}",
    response_model=WorkoutResponse,
    status_code=status.HTTP_200_OK,
)
async def get_workout(
    session: SessionDep,
    workout_id: int,
    user_id: int = Depends(get_current_user),
):
    return await service.get_workout(
        session=session,
        user_id=user_id,
        workout_id=workout_id,
    )


@workout_router.get(
    "/workouts",
    response_model=list[WorkoutResponse],
    status_code=status.HTTP_200_OK,
)
async def get_workouts_list(
    session: SessionDep,
    user_id: int = Depends(get_current_user),
    date_from: date | None = Query(
        default=None,
        description="Фильтр: начальная дата диапазона (включительно), формат YYYY-MM-DD",
        examples=["2026-10-01"],
    ),
    date_to: date | None = Query(
        default=None,
        description="Фильтр: конечная дата диапазона (включительно), формат YYYY-MM-DD",
        examples=["2026-10-16"],
    ),
):
    return await service.get_workouts_list(
        session=session,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )


@workout_router.post(
    "/workouts", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED
)
async def create_workout(
    session: SessionDep,
    workouts_in: WorkoutCreate,
    user_id: int = Depends(get_current_user),
):
    return await service.create_workout(
        session=session, workouts_in=workouts_in, user_id=user_id
    )


@set_router.post(
    "/workouts/{workout_id}/sets",
    response_model=WorkoutResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workout_set(
    session: SessionDep,
    workout_id: int,
    set_in: WorkoutSetCreate,
    user_id: int = Depends(get_current_user),
):
    return await service.create_workout_set(
        session=session, set_in=set_in, user_id=user_id, workout_id=workout_id
    )


@workout_router.patch(
    "/workouts/{workout_id}",
    response_model=WorkoutResponse,
    status_code=status.HTTP_200_OK,
)
async def update_workout(
    workout_id: int,
    workout_in: WorkoutUpdate,
    session: SessionDep,
    user_id: int = Depends(get_current_user),
):
    return await service.update_workout(
        session=session,
        workout_id=workout_id,
        workout_in=workout_in,
        user_id=user_id,
    )


@set_router.patch(
    "/sets/{set_id}",
    response_model=WorkoutSetResponse,
    status_code=status.HTTP_200_OK,
)
async def update_workout_set(
    set_id: int,
    set_in: WorkoutSetUpdate,
    session: SessionDep,
    user_id: int = Depends(get_current_user),
):
    return await service.update_workout_set(
        session=session,
        set_id=set_id,
        set_in=set_in,
        user_id=user_id,
    )


@workout_router.delete("/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: int,
    session: SessionDep,
    user_id: int = Depends(get_current_user),
):
    await service.delete_workout(
        session=session, workout_id=workout_id, user_id=user_id
    )


@set_router.delete("/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_set(
    set_id: int,
    session: SessionDep,
    user_id: int = Depends(get_current_user),
):
    await service.delete_workout_set(session=session, set_id=set_id, user_id=user_id)

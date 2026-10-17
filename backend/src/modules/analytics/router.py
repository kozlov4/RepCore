from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db_helper import db_helper
from src.modules.users.dependencies import get_current_user

from . import schemas, service

SessionDep = Annotated[AsyncSession, Depends(db_helper.session_dependency)]
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/records",
    response_model=list[schemas.RecordResponse],
    status_code=status.HTTP_200_OK,
)
async def get_records(
    session: SessionDep,
    user_id: int = Depends(get_current_user),
):
    return await service.get_user_records(session=session, user_id=user_id)


@router.get(
    "/exercises/{exercise_id}/chart",
    response_model=list[schemas.ChartDataPoint],
    status_code=status.HTTP_200_OK,
)
async def get_exercise_chart(
    exercise_id: int,
    session: SessionDep,
    user_id: int = Depends(get_current_user),
):
    return await service.get_exercise_chart_data(
        session=session, user_id=user_id, exercise_id=exercise_id
    )


@router.get(
    "/summary", response_model=schemas.SummaryResponse, status_code=status.HTTP_200_OK
)
async def get_summary(
    session: SessionDep,
    user_id: int = Depends(get_current_user),
    period: schemas.SummaryPeriod = Query(
        default=schemas.SummaryPeriod.week,
        description="Aggregation period: week, month, year, all_time",
    ),
):
    return await service.get_activity_summary(
        session=session, user_id=user_id, period=period
    )

from datetime import date, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.workouts.models import Workout, WorkoutSet
from src.modules.exercises.models import Exercise
from .schemas import SummaryPeriod


async def get_user_records(session: AsyncSession, user_id: int):
    query = (
        select(
            Exercise.id.label("exercise_id"),
            Exercise.name.label("exercise_name"),
            func.max(WorkoutSet.extra_weight).label("max_weight"),
            func.max(WorkoutSet.reps).label("max_reps"),
            func.count(WorkoutSet.id).label("total_working_sets"),
        )
        .select_from(WorkoutSet)
        .join(Exercise, Exercise.id == WorkoutSet.exercise_id)
        .join(Workout, Workout.id == WorkoutSet.workout_id)
        .where(
            Workout.user_id == user_id,
            WorkoutSet.is_warmup == False,
        )
        .group_by(Exercise.id, Exercise.name)
        .order_by(Exercise.name)
    )

    result = await session.execute(query)
    return result.mappings().all()


async def get_exercise_chart_data(
    session: AsyncSession, user_id: int, exercise_id: int
):
    query = (
        select(
            Workout.workout_date,
            func.max(WorkoutSet.extra_weight).label("max_weight"),
            func.sum(WorkoutSet.reps).label("total_reps"),
            func.count(WorkoutSet.id).label("total_sets"),
        )
        .select_from(WorkoutSet)
        .join(Workout, Workout.id == WorkoutSet.workout_id)
        .where(
            Workout.user_id == user_id,
            WorkoutSet.exercise_id == exercise_id,
            WorkoutSet.is_warmup == False,
        )
        .group_by(Workout.workout_date)
        .order_by(Workout.workout_date)
    )

    result = await session.execute(query)
    return result.mappings().all()


async def get_activity_summary(
    session: AsyncSession, user_id: int, period: SummaryPeriod
):
    today = date.today()
    start_date = None

    if period == SummaryPeriod.week:
        start_date = today - timedelta(days=7)
    elif period == SummaryPeriod.month:
        start_date = today - timedelta(days=30)
    elif period == SummaryPeriod.year:
        start_date = today - timedelta(days=365)

    query = (
        select(
            func.count(func.distinct(Workout.id)).label("total_workouts"),
            func.count(WorkoutSet.id).label("total_sets"),
            func.coalesce(func.sum(WorkoutSet.reps), 0).label("total_reps"),
        )
        .select_from(Workout)
        .outerjoin(WorkoutSet, Workout.id == WorkoutSet.workout_id)
        .where(Workout.user_id == user_id)
    )

    if start_date:
        query = query.where(Workout.workout_date >= start_date)

    result = await session.execute(query)
    return result.mappings().first()

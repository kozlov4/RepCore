from datetime import date
from enum import Enum
from pydantic import BaseModel


class SummaryPeriod(str, Enum):
    week = "week"
    month = "month"
    year = "year"
    all_time = "all_time"


class RecordResponse(BaseModel):
    exercise_id: int
    exercise_name: str
    max_weight: float
    max_reps: int
    total_working_sets: int


class ChartDataPoint(BaseModel):
    workout_date: date
    max_weight: float
    total_reps: int
    total_sets: int


class SummaryResponse(BaseModel):
    total_workouts: int
    total_sets: int
    total_reps: int

import datetime
from pydantic import BaseModel

from src.modules.exercises.schemas import ExerciseResponse


class WorkoutSetCreate(BaseModel):
    exercise_id: int
    set_number: int
    reps: int
    extra_weight: float = 0.0
    is_warmup: bool = False


class WorkoutSetUpdate(BaseModel):
    exercise_id: int | None = None
    set_number: int | None = None
    reps: int | None = None
    extra_weight: float | None = None
    is_warmup: bool | None = None


class WorkoutSetResponse(BaseModel):
    id: int
    set_number: int
    reps: int
    extra_weight: float
    is_warmup: bool

    exercise: ExerciseResponse

    class Config:
        from_attributes = True


class WorkoutCreate(BaseModel):
    title: str
    workout_date: datetime.date
    notes: str | None = None


class WorkoutUpdate(BaseModel):
    title: str | None = None
    workout_date: datetime.date | None = None
    notes: str | None = None


class WorkoutResponse(BaseModel):
    id: int
    title: str
    workout_date: datetime.date
    notes: str | None = None

    sets: list[WorkoutSetResponse] = []

    class Config:
        from_attributes = True

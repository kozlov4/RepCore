import datetime

from pydantic import BaseModel


class WorkoutResponse(BaseModel):
    id: int
    title: str
    workout_date: datetime.date
    notes: None | str = None

    class Config:
        from_attributes = True


class WorkoutCreate(BaseModel):
    title: str
    workout_date: datetime.date
    notes: str | None = None

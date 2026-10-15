from pydantic import BaseModel
from .models import MuscleGroup


class ExerciseCreate(BaseModel):
    name: str
    muscle_group: MuscleGroup
    is_bodyweight: bool = False


class ExerciseResponse(BaseModel):
    id: int
    name: str
    muscle_group: MuscleGroup
    is_bodyweight: bool

    class Config:

        from_attributes = True


class ExerciseUpdate(BaseModel):
    name: str | None = None
    muscle_group: MuscleGroup | None = None
    is_bodyweight: bool | None = None

from pydantic import BaseModel
from .models import MuscleGroup

class ExerciseList(BaseModel):
    id: int
    name: str
    muscle_group: MuscleGroup
    is_bodyweight: bool

    class Config:
        from_attributes = True

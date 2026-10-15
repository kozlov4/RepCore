import enum

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from src.core.base import Base


class MuscleGroup(str, enum.Enum):
    BACK = "back"
    CHEST = "chest"
    SHOULDERS = "shoulders"
    ARMS = "arms"
    LEGS = "legs"
    CORE = "core"


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    muscle_group: Mapped[MuscleGroup] = mapped_column(Enum(MuscleGroup), index=True)

    is_bodyweight: Mapped[bool] = mapped_column(Boolean, default=False)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True
    )

import datetime

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.base import Base

from src.modules.exercises.models import Exercise


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), index=True
    )

    title: Mapped[str] = mapped_column(String(100))
    workout_date: Mapped[datetime.date] = mapped_column(
        Date, default=datetime.date.today, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    sets: Mapped[list[WorkoutSet]] = relationship(
        back_populates="workout", cascade="all, delete-orphan"
    )


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workout_id: Mapped[int] = mapped_column(
        ForeignKey("workouts.id", ondelete="CASCADE"), index=True
    )
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"), index=True
    )

    set_number: Mapped[int] = mapped_column(
        Integer
    )
    reps: Mapped[int] = mapped_column(Integer)
    extra_weight: Mapped[float] = mapped_column(
        Float, default=0.0
    )
    is_warmup: Mapped[bool] = mapped_column(Boolean, default=False)

    workout: Mapped[Workout] = relationship(back_populates="sets")

    exercise: Mapped[Exercise] = relationship()

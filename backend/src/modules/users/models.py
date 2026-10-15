from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hash_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

    verification_token: Mapped[EmailVerification] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    # noinspection PyUnresolvedReferences
    workouts: Mapped[list[Workout]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # noinspection PyUnresolvedReferences
    custom_exercises: Mapped[list[Exercise]] = relationship(
        cascade="all, delete-orphan"
    )


class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE")
    )
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)

    user: Mapped[User] = relationship(back_populates="verification_token")

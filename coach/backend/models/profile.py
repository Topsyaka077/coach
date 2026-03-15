from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fitness_level: Mapped[str] = mapped_column(String, nullable=False)
    primary_goal: Mapped[str] = mapped_column(String, nullable=False)
    goals_detail: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    weekly_hours: Mapped[float] = mapped_column(Float, nullable=False)
    rest_days: Mapped[list] = mapped_column(JSON, nullable=False)
    extra_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

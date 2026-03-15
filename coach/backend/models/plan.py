from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    plan_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    generation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

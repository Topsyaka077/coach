import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.log import WorkoutLog
from models.plan import TrainingPlan
from models.profile import UserProfile


async def build_context(session: AsyncSession) -> dict:
    profile_result = await session.execute(
        select(UserProfile).limit(1)
    )
    profile = profile_result.scalar_one_or_none()

    plan_result = await session.execute(
        select(TrainingPlan).order_by(TrainingPlan.created_at.desc()).limit(1)
    )
    current_plan = plan_result.scalar_one_or_none()

    cutoff = datetime.date.today() - datetime.timedelta(days=7)
    logs_result = await session.execute(
        select(WorkoutLog)
        .where(WorkoutLog.date >= cutoff)
        .order_by(WorkoutLog.date.desc())
    )
    recent_logs = list(logs_result.scalars().all())

    return {
        "profile": profile,
        "current_plan": current_plan,
        "recent_logs": recent_logs,
    }

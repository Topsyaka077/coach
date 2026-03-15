import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from agent.context import build_context
from models.log import WorkoutLog
from models.plan import TrainingPlan
from models.profile import UserProfile


async def test_empty_db(session: AsyncSession):
    ctx = await build_context(session)
    assert ctx["profile"] is None
    assert ctx["current_plan"] is None
    assert ctx["recent_logs"] == []


async def test_with_profile(session: AsyncSession, sample_profile: UserProfile):
    ctx = await build_context(session)
    assert ctx["profile"] is not None
    assert ctx["profile"].name == "Alice"


async def test_returns_latest_plan(session: AsyncSession):
    old_plan = TrainingPlan(
        week_start_date=datetime.date(2026, 2, 1),
        plan_data={"day": "old"},
        created_at=datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc),
    )
    new_plan = TrainingPlan(
        week_start_date=datetime.date(2026, 3, 1),
        plan_data={"day": "new"},
        created_at=datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc),
    )
    session.add_all([old_plan, new_plan])
    await session.commit()

    ctx = await build_context(session)
    assert ctx["current_plan"].plan_data == {"day": "new"}


async def test_recent_logs_within_7_days(session: AsyncSession):
    today = datetime.date.today()
    recent = WorkoutLog(
        date=today - datetime.timedelta(days=3),
        workout_type="run",
        feeling="good",
    )
    old = WorkoutLog(
        date=today - datetime.timedelta(days=10),
        workout_type="swim",
        feeling="ok",
    )
    session.add_all([recent, old])
    await session.commit()

    ctx = await build_context(session)
    assert len(ctx["recent_logs"]) == 1
    assert ctx["recent_logs"][0].workout_type == "run"


async def test_logs_ordered_desc(session: AsyncSession):
    today = datetime.date.today()
    log1 = WorkoutLog(
        date=today - datetime.timedelta(days=2),
        workout_type="run",
        feeling="good",
    )
    log2 = WorkoutLog(
        date=today - datetime.timedelta(days=1),
        workout_type="bike",
        feeling="great",
    )
    log3 = WorkoutLog(
        date=today,
        workout_type="swim",
        feeling="ok",
    )
    session.add_all([log1, log2, log3])
    await session.commit()

    ctx = await build_context(session)
    types = [log.workout_type for log in ctx["recent_logs"]]
    assert types == ["swim", "bike", "run"]

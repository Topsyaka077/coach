import datetime
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent.executor import execute_tool
from models.log import WorkoutLog
from models.plan import TrainingPlan
from models.profile import UserProfile


async def test_get_profile_empty(session: AsyncSession):
    result = await execute_tool("get_profile", {}, session)
    assert result == "No profile set up yet."


async def test_get_profile_with_data(session: AsyncSession, sample_profile):
    result = await execute_tool("get_profile", {}, session)
    data = json.loads(result)
    assert data["name"] == "Alice"
    assert data["age"] == 30
    assert data["fitness_level"] == "intermediate"
    assert data["primary_goal"] == "run a marathon"
    assert data["weekly_hours"] == 6.0
    assert data["rest_days"] == ["Monday", "Friday"]


async def test_get_current_plan_empty(session: AsyncSession):
    result = await execute_tool("get_current_plan", {}, session)
    assert result == "No training plan exists yet."


async def test_get_current_plan_with_data(session: AsyncSession, sample_plan):
    result = await execute_tool("get_current_plan", {}, session)
    data = json.loads(result)
    assert "monday" in data["plan_data"]
    assert data["week_start_date"] == str(datetime.date.today())


async def test_get_recent_logs_empty(session: AsyncSession):
    result = await execute_tool("get_recent_logs", {}, session)
    assert result == "No workouts logged in this period."


async def test_get_recent_logs_default_days(session: AsyncSession, sample_log):
    result = await execute_tool("get_recent_logs", {}, session)
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["workout_type"] == "easy_run"


async def test_get_recent_logs_custom_days(session: AsyncSession):
    today = datetime.date.today()
    log = WorkoutLog(
        date=today - datetime.timedelta(days=5),
        workout_type="run",
        feeling="good",
    )
    session.add(log)
    await session.commit()

    result_3 = await execute_tool("get_recent_logs", {"days": 3}, session)
    assert result_3 == "No workouts logged in this period."

    result_7 = await execute_tool("get_recent_logs", {"days": 7}, session)
    data = json.loads(result_7)
    assert len(data) == 1


async def test_log_workout(session: AsyncSession):
    result = await execute_tool("log_workout", {
        "date": "2026-03-01",
        "workout_type": "tempo_run",
        "distance_km": 10.0,
        "duration_minutes": 50,
        "feeling": "great",
        "notes": "Negative splits",
    }, session)

    assert "tempo_run" in result
    assert "2026-03-01" in result
    assert "great" in result

    row = (await session.execute(select(WorkoutLog))).scalar_one()
    assert row.source == "agent"
    assert row.distance_km == 10.0
    assert row.notes == "Negative splits"


async def test_log_workout_minimal(session: AsyncSession):
    result = await execute_tool("log_workout", {
        "date": "2026-03-02",
        "workout_type": "yoga",
        "feeling": "ok",
    }, session)

    assert "yoga" in result
    row = (await session.execute(select(WorkoutLog))).scalar_one()
    assert row.distance_km is None
    assert row.duration_minutes is None


async def test_update_plan_creates_new(session: AsyncSession):
    result = await execute_tool("update_plan", {
        "updated_plan": {"monday": "rest", "tuesday": "run"},
        "reason": "Initial plan",
    }, session)

    assert "Initial plan" in result
    row = (await session.execute(select(TrainingPlan))).scalar_one()
    assert row.plan_data == {"monday": "rest", "tuesday": "run"}


async def test_update_plan_modifies_existing(session: AsyncSession, sample_plan):
    new_plan = {"monday": "easy run", "tuesday": "rest"}
    result = await execute_tool("update_plan", {
        "updated_plan": new_plan,
        "reason": "User requested lighter week",
    }, session)

    assert "User requested lighter week" in result
    row = (await session.execute(select(TrainingPlan))).scalar_one()
    assert row.plan_data == new_plan


async def test_generate_plan(session: AsyncSession):
    result = await execute_tool("generate_plan", {}, session)
    assert result == "GENERATE_PLAN_REQUESTED"


async def test_unknown_tool(session: AsyncSession):
    result = await execute_tool("nonexistent_tool", {}, session)
    assert result == "Unknown tool: nonexistent_tool"

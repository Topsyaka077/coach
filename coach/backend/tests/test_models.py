import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.log import WorkoutLog
from models.plan import TrainingPlan
from models.profile import UserProfile


async def test_create_user_profile(session: AsyncSession):
    profile = UserProfile(
        name="Bob",
        fitness_level="beginner",
        primary_goal="lose weight",
        weekly_hours=3.0,
        rest_days=["Saturday", "Sunday"],
    )
    session.add(profile)
    await session.commit()

    result = await session.execute(select(UserProfile))
    row = result.scalar_one()
    assert row.name == "Bob"
    assert row.fitness_level == "beginner"
    assert row.primary_goal == "lose weight"
    assert row.weekly_hours == 3.0
    assert row.rest_days == ["Saturday", "Sunday"]
    assert row.age is None
    assert row.goals_detail is None
    assert row.extra_notes is None


async def test_profile_nullable_fields(session: AsyncSession):
    profile = UserProfile(
        name="Carol",
        age=25,
        fitness_level="advanced",
        primary_goal="ultra marathon",
        goals_detail={"distance": "100km"},
        weekly_hours=12.0,
        rest_days=["Monday"],
        extra_notes="Experienced trail runner",
    )
    session.add(profile)
    await session.commit()

    result = await session.execute(select(UserProfile))
    row = result.scalar_one()
    assert row.age == 25
    assert row.goals_detail == {"distance": "100km"}
    assert row.extra_notes == "Experienced trail runner"


async def test_create_training_plan(session: AsyncSession):
    plan = TrainingPlan(
        week_start_date=datetime.date(2026, 3, 2),
        plan_data={"monday": "rest", "tuesday": "run 5km"},
        generation_notes="Test plan",
    )
    session.add(plan)
    await session.commit()

    result = await session.execute(select(TrainingPlan))
    row = result.scalar_one()
    assert row.week_start_date == datetime.date(2026, 3, 2)
    assert row.plan_data == {"monday": "rest", "tuesday": "run 5km"}
    assert row.generation_notes == "Test plan"


async def test_training_plan_nullable_notes(session: AsyncSession):
    plan = TrainingPlan(
        week_start_date=datetime.date.today(),
        plan_data={"monday": "rest"},
    )
    session.add(plan)
    await session.commit()

    result = await session.execute(select(TrainingPlan))
    row = result.scalar_one()
    assert row.generation_notes is None


async def test_create_workout_log(session: AsyncSession):
    log = WorkoutLog(
        date=datetime.date(2026, 3, 1),
        workout_type="intervals",
        distance_km=8.0,
        duration_minutes=45,
        feeling="great",
        notes="Hit all targets",
    )
    session.add(log)
    await session.commit()

    result = await session.execute(select(WorkoutLog))
    row = result.scalar_one()
    assert row.date == datetime.date(2026, 3, 1)
    assert row.workout_type == "intervals"
    assert row.distance_km == 8.0
    assert row.duration_minutes == 45
    assert row.feeling == "great"
    assert row.notes == "Hit all targets"


async def test_workout_log_source_default(session: AsyncSession):
    log = WorkoutLog(
        date=datetime.date.today(),
        workout_type="easy_run",
        feeling="ok",
    )
    session.add(log)
    await session.commit()

    result = await session.execute(select(WorkoutLog))
    row = result.scalar_one()
    assert row.source == "manual"


async def test_workout_log_nullable_fields(session: AsyncSession):
    log = WorkoutLog(
        date=datetime.date.today(),
        workout_type="yoga",
        feeling="good",
    )
    session.add(log)
    await session.commit()

    result = await session.execute(select(WorkoutLog))
    row = result.scalar_one()
    assert row.distance_km is None
    assert row.duration_minutes is None
    assert row.notes is None


async def test_json_fields_roundtrip(session: AsyncSession):
    profile = UserProfile(
        name="Dan",
        fitness_level="beginner",
        primary_goal="stay active",
        goals_detail={"targets": [1, 2, 3], "nested": {"key": "value"}},
        weekly_hours=2.0,
        rest_days=["Monday", "Wednesday", "Friday"],
    )
    session.add(profile)
    await session.commit()

    result = await session.execute(select(UserProfile))
    row = result.scalar_one()
    assert row.goals_detail == {"targets": [1, 2, 3], "nested": {"key": "value"}}
    assert row.rest_days == ["Monday", "Wednesday", "Friday"]

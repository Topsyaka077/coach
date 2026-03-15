import datetime
from unittest.mock import patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database import Base, get_db
from models.log import WorkoutLog
from models.plan import TrainingPlan
from models.profile import UserProfile


@pytest.fixture
async def engine():
    eng = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest.fixture
async def session(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as sess:
        yield sess
        await sess.rollback()


@pytest.fixture
def client(session):
    from fastapi.testclient import TestClient
    from main import app

    async def _override_get_db():
        yield session

    app.dependency_overrides[get_db] = _override_get_db

    with patch("main.run_migrations"):
        with TestClient(app) as c:
            yield c

    app.dependency_overrides.clear()


@pytest.fixture
async def sample_profile(session: AsyncSession) -> UserProfile:
    profile = UserProfile(
        name="Alice",
        age=30,
        fitness_level="intermediate",
        primary_goal="run a marathon",
        goals_detail={"target_time": "4:00:00"},
        weekly_hours=6.0,
        rest_days=["Monday", "Friday"],
        extra_notes="Prefer morning runs",
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


@pytest.fixture
async def sample_plan(session: AsyncSession) -> TrainingPlan:
    plan = TrainingPlan(
        week_start_date=datetime.date.today(),
        plan_data={
            "monday": "rest",
            "tuesday": "easy run 5km",
            "wednesday": "intervals",
            "thursday": "easy run 5km",
            "friday": "rest",
            "saturday": "long run 15km",
            "sunday": "recovery jog 3km",
        },
        generation_notes="Initial plan for marathon prep",
    )
    session.add(plan)
    await session.commit()
    await session.refresh(plan)
    return plan


@pytest.fixture
async def sample_log(session: AsyncSession) -> WorkoutLog:
    log = WorkoutLog(
        date=datetime.date.today(),
        workout_type="easy_run",
        distance_km=5.0,
        duration_minutes=30,
        feeling="good",
        notes="Felt strong",
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log

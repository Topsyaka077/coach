import datetime
from unittest.mock import MagicMock

from agent.prompt import build_system_prompt


def _make_profile(**overrides):
    defaults = dict(
        name="Alice",
        age=30,
        fitness_level="intermediate",
        primary_goal="run a marathon",
        goals_detail=None,
        weekly_hours=6.0,
        rest_days=["Monday", "Friday"],
        extra_notes=None,
    )
    defaults.update(overrides)
    mock = MagicMock(**defaults)
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def _make_plan(**overrides):
    defaults = dict(
        week_start_date=datetime.date(2026, 3, 2),
        plan_data={"monday": "rest", "tuesday": "run"},
        generation_notes=None,
    )
    defaults.update(overrides)
    mock = MagicMock(**defaults)
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def _make_log(**overrides):
    defaults = dict(
        date=datetime.date(2026, 3, 1),
        workout_type="easy_run",
        distance_km=5.0,
        duration_minutes=30,
        feeling="good",
        notes=None,
    )
    defaults.update(overrides)
    mock = MagicMock(**defaults)
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def test_empty_context():
    ctx = {"profile": None, "current_plan": None, "recent_logs": []}
    prompt = build_system_prompt(ctx)
    assert "No profile yet" in prompt
    assert "No plan yet" in prompt
    assert "No recent activity" in prompt


def test_prompt_includes_date():
    ctx = {"profile": None, "current_plan": None, "recent_logs": []}
    prompt = build_system_prompt(ctx)
    assert str(datetime.date.today()) in prompt


def test_prompt_includes_tool_instructions():
    ctx = {"profile": None, "current_plan": None, "recent_logs": []}
    prompt = build_system_prompt(ctx)
    assert "log_workout" in prompt
    assert "update_plan" in prompt
    assert "generate_plan" in prompt


def test_prompt_with_profile():
    profile = _make_profile(extra_notes="Morning runner")
    ctx = {"profile": profile, "current_plan": None, "recent_logs": []}
    prompt = build_system_prompt(ctx)
    assert "Alice" in prompt
    assert "intermediate" in prompt
    assert "run a marathon" in prompt
    assert "Morning runner" in prompt
    assert "No profile yet" not in prompt


def test_prompt_with_plan():
    plan = _make_plan(generation_notes="Week 1 plan")
    ctx = {"profile": None, "current_plan": plan, "recent_logs": []}
    prompt = build_system_prompt(ctx)
    assert "2026-03-02" in prompt
    assert "rest" in prompt
    assert "Week 1 plan" in prompt
    assert "No plan yet" not in prompt


def test_prompt_with_logs():
    logs = [
        _make_log(distance_km=5.0, duration_minutes=30, notes="Felt good"),
        _make_log(date=datetime.date(2026, 2, 28), workout_type="intervals",
                  distance_km=None, duration_minutes=45, notes=None),
    ]
    ctx = {"profile": None, "current_plan": None, "recent_logs": logs}
    prompt = build_system_prompt(ctx)
    assert "easy_run" in prompt
    assert "5.0 km" in prompt
    assert "30 min" in prompt
    assert "Felt good" in prompt
    assert "intervals" in prompt
    assert "45 min" in prompt
    assert "No recent activity" not in prompt


def test_prompt_with_goals_detail():
    profile = _make_profile(goals_detail={"target_time": "4:00:00"})
    ctx = {"profile": profile, "current_plan": None, "recent_logs": []}
    prompt = build_system_prompt(ctx)
    assert "target_time" in prompt

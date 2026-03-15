import datetime
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.log import WorkoutLog
from models.plan import TrainingPlan
from models.profile import UserProfile


async def execute_tool(
    tool_name: str, tool_input: dict, session: AsyncSession
) -> str:
    if tool_name == "get_profile":
        return await _get_profile(session)
    elif tool_name == "get_current_plan":
        return await _get_current_plan(session)
    elif tool_name == "get_recent_logs":
        return await _get_recent_logs(tool_input, session)
    elif tool_name == "log_workout":
        return await _log_workout(tool_input, session)
    elif tool_name == "update_plan":
        return await _update_plan(tool_input, session)
    elif tool_name == "generate_plan":
        return _generate_plan(tool_input)
    else:
        return f"Unknown tool: {tool_name}"


async def _get_profile(session: AsyncSession) -> str:
    result = await session.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()
    if profile is None:
        return "No profile set up yet."
    return json.dumps({
        "name": profile.name,
        "age": profile.age,
        "fitness_level": profile.fitness_level,
        "primary_goal": profile.primary_goal,
        "goals_detail": profile.goals_detail,
        "weekly_hours": profile.weekly_hours,
        "rest_days": profile.rest_days,
        "extra_notes": profile.extra_notes,
    })


async def _get_current_plan(session: AsyncSession) -> str:
    result = await session.execute(
        select(TrainingPlan).order_by(TrainingPlan.created_at.desc()).limit(1)
    )
    plan = result.scalar_one_or_none()
    if plan is None:
        return "No training plan exists yet."
    return json.dumps({
        "week_start_date": str(plan.week_start_date),
        "plan_data": plan.plan_data,
        "generation_notes": plan.generation_notes,
    })


async def _get_recent_logs(tool_input: dict, session: AsyncSession) -> str:
    days = tool_input.get("days", 7)
    cutoff = datetime.date.today() - datetime.timedelta(days=days)
    result = await session.execute(
        select(WorkoutLog)
        .where(WorkoutLog.date >= cutoff)
        .order_by(WorkoutLog.date.desc())
    )
    logs = result.scalars().all()
    if not logs:
        return "No workouts logged in this period."
    return json.dumps([
        {
            "date": str(log.date),
            "workout_type": log.workout_type,
            "distance_km": log.distance_km,
            "duration_minutes": log.duration_minutes,
            "feeling": log.feeling,
            "notes": log.notes,
            "source": log.source,
        }
        for log in logs
    ])


async def _log_workout(tool_input: dict, session: AsyncSession) -> str:
    log = WorkoutLog(
        date=datetime.date.fromisoformat(tool_input["date"]),
        workout_type=tool_input["workout_type"],
        distance_km=tool_input.get("distance_km"),
        duration_minutes=tool_input.get("duration_minutes"),
        feeling=tool_input["feeling"],
        notes=tool_input.get("notes"),
        source="agent",
    )
    session.add(log)
    await session.commit()
    return f"Workout logged: {log.workout_type} on {log.date}, feeling {log.feeling}"


async def _update_plan(tool_input: dict, session: AsyncSession) -> str:
    result = await session.execute(
        select(TrainingPlan).order_by(TrainingPlan.created_at.desc()).limit(1)
    )
    plan = result.scalar_one_or_none()

    if plan is None:
        plan = TrainingPlan(
            week_start_date=datetime.date.today(),
            plan_data=tool_input["updated_plan"],
            generation_notes=tool_input["reason"],
        )
        session.add(plan)
    else:
        plan.plan_data = tool_input["updated_plan"]
        plan.generation_notes = tool_input["reason"]

    await session.commit()
    return f"Plan updated: {tool_input['reason']}"


def _generate_plan(tool_input: dict) -> str:
    return "GENERATE_PLAN_REQUESTED"

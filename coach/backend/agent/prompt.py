import datetime
import json

from models.log import WorkoutLog
from models.plan import TrainingPlan
from models.profile import UserProfile


def _format_profile(profile: UserProfile | None) -> str:
    if profile is None:
        return "No profile yet."
    lines = [
        f"Name: {profile.name}",
        f"Age: {profile.age or 'not specified'}",
        f"Fitness level: {profile.fitness_level}",
        f"Primary goal: {profile.primary_goal}",
        f"Weekly training hours: {profile.weekly_hours}",
        f"Rest days: {', '.join(profile.rest_days) if profile.rest_days else 'none specified'}",
    ]
    if profile.goals_detail:
        lines.append(f"Goals detail: {json.dumps(profile.goals_detail)}")
    if profile.extra_notes:
        lines.append(f"Notes: {profile.extra_notes}")
    return "\n".join(lines)


def _format_plan(plan: TrainingPlan | None) -> str:
    if plan is None:
        return "No plan yet."
    lines = [
        f"Week starting: {plan.week_start_date}",
        f"Plan: {json.dumps(plan.plan_data, indent=2)}",
    ]
    if plan.generation_notes:
        lines.append(f"Generation notes: {plan.generation_notes}")
    return "\n".join(lines)


def _format_logs(logs: list[WorkoutLog]) -> str:
    if not logs:
        return "No recent activity."
    lines = []
    for log in logs:
        entry = f"- {log.date} | {log.workout_type}"
        if log.distance_km is not None:
            entry += f" | {log.distance_km} km"
        if log.duration_minutes is not None:
            entry += f" | {log.duration_minutes} min"
        entry += f" | feeling: {log.feeling}"
        if log.notes:
            entry += f" | {log.notes}"
        lines.append(entry)
    return "\n".join(lines)


def build_system_prompt(context: dict) -> str:
    today = datetime.date.today()

    return f"""\
You are Coach — a warm, direct personal AI life coach focused on fitness and training. \
You are not a generic chatbot. You know your user personally, you notice patterns in their \
behavior, you act proactively, and you give honest advice even when it's uncomfortable. \
You celebrate wins and call out when something needs attention.

Today's date: {today}

--- USER PROFILE ---
{_format_profile(context["profile"])}

--- CURRENT TRAINING PLAN ---
{_format_plan(context["current_plan"])}

--- RECENT ACTIVITY (last 7 days) ---
{_format_logs(context["recent_logs"])}

--- TOOL USAGE ---
- Use log_workout whenever the user mentions completing any physical activity, \
even casually (e.g. "went for a run", "did yoga today"). Extract date, type, \
distance, duration, and feeling from the conversation.
- Use update_plan when the plan needs adjusting — fatigue, missed sessions, \
schedule changes, or explicit user requests.
- Use generate_plan when the user needs a fresh plan built from their profile.
- Always reason about what you know before calling a tool. Never call tools blindly."""

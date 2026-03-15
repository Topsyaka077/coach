TOOLS = [
    {
        "name": "get_profile",
        "description": "Get user name, goals, fitness level, preferences",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_current_plan",
        "description": "Get this week's training plan",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_recent_logs",
        "description": "Get workout logs for past N days",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "integer",
                    "description": "Number of past days to retrieve logs for",
                    "default": 7,
                },
            },
            "required": [],
        },
    },
    {
        "name": "log_workout",
        "description": "Record a completed workout from conversation",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Date of the workout (YYYY-MM-DD)",
                },
                "workout_type": {
                    "type": "string",
                    "description": "Type of workout (e.g. easy_run, long_run, intervals, rest)",
                },
                "distance_km": {
                    "type": "number",
                    "description": "Distance covered in kilometers",
                },
                "duration_minutes": {
                    "type": "integer",
                    "description": "Duration of the workout in minutes",
                },
                "feeling": {
                    "type": "string",
                    "enum": ["great", "good", "ok", "tired", "very_tired"],
                    "description": "How the user felt during/after the workout",
                },
                "notes": {
                    "type": "string",
                    "description": "Additional notes about the workout",
                },
            },
            "required": ["date", "workout_type", "feeling"],
        },
    },
    {
        "name": "update_plan",
        "description": (
            "Modify the training plan. Use when user reports fatigue, "
            "misses sessions, or requests changes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "updated_plan": {
                    "type": "object",
                    "description": "The modified training plan data",
                },
                "reason": {
                    "type": "string",
                    "description": "Why the plan is being updated",
                },
            },
            "required": ["updated_plan", "reason"],
        },
    },
    {
        "name": "generate_plan",
        "description": "Create a brand new training plan from user's profile and goals",
        "input_schema": {
            "type": "object",
            "properties": {
                "notes": {
                    "type": "string",
                    "description": "Optional guidance or constraints for plan generation",
                },
            },
            "required": [],
        },
    },
]

TOOL_NAMES = [t["name"] for t in TOOLS]

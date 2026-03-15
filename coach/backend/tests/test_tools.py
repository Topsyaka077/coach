from agent.tools import TOOL_NAMES, TOOLS

EXPECTED_NAMES = [
    "get_profile",
    "get_current_plan",
    "get_recent_logs",
    "log_workout",
    "update_plan",
    "generate_plan",
]


def test_tools_count():
    assert len(TOOLS) == 6


def test_tool_names():
    assert TOOL_NAMES == EXPECTED_NAMES


def test_each_tool_has_required_keys():
    for tool in TOOLS:
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        assert tool["input_schema"]["type"] == "object"
        assert "properties" in tool["input_schema"]


def test_get_profile_schema():
    tool = TOOLS[0]
    assert tool["name"] == "get_profile"
    assert tool["input_schema"]["properties"] == {}


def test_get_current_plan_schema():
    tool = TOOLS[1]
    assert tool["name"] == "get_current_plan"
    assert tool["input_schema"]["properties"] == {}


def test_get_recent_logs_schema():
    tool = TOOLS[2]
    assert tool["name"] == "get_recent_logs"
    props = tool["input_schema"]["properties"]
    assert "days" in props
    assert props["days"]["type"] == "integer"
    assert props["days"]["default"] == 7


def test_log_workout_schema():
    tool = TOOLS[3]
    assert tool["name"] == "log_workout"
    schema = tool["input_schema"]
    assert set(schema["required"]) == {"date", "workout_type", "feeling"}
    assert schema["properties"]["feeling"]["enum"] == [
        "great", "good", "ok", "tired", "very_tired"
    ]
    assert schema["properties"]["date"]["type"] == "string"
    assert schema["properties"]["distance_km"]["type"] == "number"
    assert schema["properties"]["duration_minutes"]["type"] == "integer"


def test_update_plan_schema():
    tool = TOOLS[4]
    assert tool["name"] == "update_plan"
    schema = tool["input_schema"]
    assert set(schema["required"]) == {"updated_plan", "reason"}
    assert schema["properties"]["updated_plan"]["type"] == "object"
    assert schema["properties"]["reason"]["type"] == "string"


def test_generate_plan_schema():
    tool = TOOLS[5]
    assert tool["name"] == "generate_plan"
    schema = tool["input_schema"]
    assert schema["required"] == []
    assert "notes" in schema["properties"]
    assert schema["properties"]["notes"]["type"] == "string"

from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from agent.loop import run_agent_loop


class AsyncIteratorMock:
    def __init__(self, items):
        self._items = list(items)
        self._index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._index >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._index]
        self._index += 1
        return item


def _text_block(text: str):
    block = MagicMock()
    block.type = "text"
    block.text = text
    return block


def _tool_use_block(tool_id: str, name: str, tool_input: dict):
    block = MagicMock()
    block.type = "tool_use"
    block.id = tool_id
    block.name = name
    block.input = tool_input
    return block


def _make_response(content, stop_reason="end_turn"):
    response = MagicMock()
    response.content = content
    response.stop_reason = stop_reason
    return response


def _make_text_event(text: str):
    event = MagicMock()
    event.type = "text"
    event.text = text
    return event


@patch("agent.loop.build_context", new_callable=AsyncMock)
@patch("agent.loop.build_system_prompt")
async def test_non_streaming_text_response(
    mock_prompt, mock_context, session: AsyncSession
):
    mock_context.return_value = {"profile": None, "current_plan": None, "recent_logs": []}
    mock_prompt.return_value = "You are Coach."

    response = _make_response([_text_block("Hello! How can I help?")])

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=response)

    with patch("agent.loop.anthropic.AsyncAnthropic", return_value=mock_client):
        chunks = []
        async for chunk in run_agent_loop("hi", [], session, stream=False):
            chunks.append(chunk)

    assert chunks == ["Hello! How can I help?"]


@patch("agent.loop.build_context", new_callable=AsyncMock)
@patch("agent.loop.build_system_prompt")
async def test_streaming_text_response(
    mock_prompt, mock_context, session: AsyncSession
):
    mock_context.return_value = {"profile": None, "current_plan": None, "recent_logs": []}
    mock_prompt.return_value = "You are Coach."

    text_events = [_make_text_event("Hello"), _make_text_event(" world")]
    final_message = _make_response([_text_block("Hello world")])

    stream_body = AsyncIteratorMock(text_events)
    stream_body.get_final_message = AsyncMock(return_value=final_message)

    mock_stream = MagicMock()
    mock_stream.__aenter__ = AsyncMock(return_value=stream_body)
    mock_stream.__aexit__ = AsyncMock(return_value=False)

    mock_client = AsyncMock()
    mock_client.messages.stream = MagicMock(return_value=mock_stream)

    with patch("agent.loop.anthropic.AsyncAnthropic", return_value=mock_client):
        chunks = []
        async for chunk in run_agent_loop("hi", [], session, stream=True):
            chunks.append(chunk)

    assert chunks == ["Hello", " world"]


@patch("agent.loop.execute_tool", new_callable=AsyncMock)
@patch("agent.loop.build_context", new_callable=AsyncMock)
@patch("agent.loop.build_system_prompt")
async def test_tool_call_then_text(
    mock_prompt, mock_context, mock_execute, session: AsyncSession
):
    mock_context.return_value = {"profile": None, "current_plan": None, "recent_logs": []}
    mock_prompt.return_value = "You are Coach."
    mock_execute.return_value = "No profile set up yet."

    tool_response = _make_response(
        [_tool_use_block("tool_1", "get_profile", {})],
        stop_reason="tool_use",
    )
    text_response = _make_response([_text_block("You don't have a profile yet.")])

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(side_effect=[tool_response, text_response])

    with patch("agent.loop.anthropic.AsyncAnthropic", return_value=mock_client):
        chunks = []
        async for chunk in run_agent_loop("show profile", [], session, stream=False):
            chunks.append(chunk)

    assert chunks == ["You don't have a profile yet."]
    mock_execute.assert_called_once_with("get_profile", {}, session)
    assert mock_client.messages.create.call_count == 2


@patch("agent.loop.execute_tool", new_callable=AsyncMock)
@patch("agent.loop.build_context", new_callable=AsyncMock)
@patch("agent.loop.build_system_prompt")
async def test_max_loop_limit(
    mock_prompt, mock_context, mock_execute, session: AsyncSession
):
    mock_context.return_value = {"profile": None, "current_plan": None, "recent_logs": []}
    mock_prompt.return_value = "You are Coach."
    mock_execute.return_value = "done"

    tool_response = _make_response(
        [_tool_use_block("tool_1", "get_profile", {})],
        stop_reason="tool_use",
    )

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=tool_response)

    with (
        patch("agent.loop.anthropic.AsyncAnthropic", return_value=mock_client),
        patch.dict("os.environ", {"MAX_AGENT_LOOPS": "3"}),
    ):
        chunks = []
        async for chunk in run_agent_loop("loop forever", [], session, stream=False):
            chunks.append(chunk)

    assert chunks == ["I've reached my reasoning limit for this turn. Please try again."]
    assert mock_client.messages.create.call_count == 3

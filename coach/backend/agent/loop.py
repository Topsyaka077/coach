import json
import os
from collections.abc import AsyncIterator

import anthropic
from sqlalchemy.ext.asyncio import AsyncSession

from agent.context import build_context
from agent.executor import execute_tool
from agent.prompt import build_system_prompt
from agent.tools import TOOLS


async def run_agent_loop(
    message: str,
    history: list[dict],
    session: AsyncSession,
    stream: bool = True,
) -> AsyncIterator[str]:
    context = await build_context(session)
    system = build_system_prompt(context)
    messages = history + [{"role": "user", "content": message}]

    client = anthropic.AsyncAnthropic()
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
    max_loops = int(os.getenv("MAX_AGENT_LOOPS", "8"))

    for _ in range(max_loops):
        if stream:
            text_chunks: list[str] = []

            async with client.messages.stream(
                model=model,
                max_tokens=1024,
                system=system,
                messages=messages,
                tools=TOOLS,
            ) as s:
                async for event in s:
                    if event.type == "text":
                        text_chunks.append(event.text)

                response = await s.get_final_message()
        else:
            response = await client.messages.create(
                model=model,
                max_tokens=1024,
                system=system,
                messages=messages,
                tools=TOOLS,
            )

        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]

        if not tool_use_blocks:
            if stream:
                for chunk in text_chunks:
                    yield chunk
            else:
                text = "".join(
                    b.text for b in response.content if b.type == "text"
                )
                yield text
            return

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in tool_use_blocks:
            result = await execute_tool(block.name, block.input, session)
            result_str = json.dumps(result) if not isinstance(result, str) else result
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result_str,
            })

        messages.append({"role": "user", "content": tool_results})

    yield "I've reached my reasoning limit for this turn. Please try again."

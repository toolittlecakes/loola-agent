"""Minimal async coding agent SDK.

    async with OpenAICompatibleLLM(base_url, api_key, model) as llm, Bash() as bash:
        agent = Agent(llm, Toolbox([bash]))
        async for event in agent.send("fix the failing test"):
            ...  # render / persist events; the last one is RunFinished
"""
from .agent import (SYSTEM_PROMPT, Agent, AssistantMessage, Event, RunFinished, ToolResult, ToolStarted,
                    UserMessage, build_context)
from .llm import LLM, Completion, LLMError, OpenAICompatibleLLM, Usage
from .tools import Bash, Tool, Toolbox

__all__ = ["SYSTEM_PROMPT", "Agent", "AssistantMessage", "Bash", "Completion", "Event", "LLM", "LLMError",
           "OpenAICompatibleLLM", "RunFinished", "Tool", "ToolResult", "ToolStarted", "Toolbox", "Usage",
           "UserMessage", "build_context"]

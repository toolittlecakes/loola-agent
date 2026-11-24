"""Minimal async coding agent SDK.

    async with OpenAICompatibleLLM(base_url, api_key, model) as llm, Bash() as bash:
        agent = Agent(llm, Toolbox([bash], deferred=more_tools))
        async for event in agent.send("fix the failing test"):
            ...  # render / persist events; the last one is RunFinished
"""
from .agent import SYSTEM_PROMPT, Agent
from .compaction import CompactionError, CompactionPolicy
from .events import (AssistantMessage, Compaction, Event, RunFinished, ToolResult, ToolStarted, UserMessage,
                     build_context)
from .bash import Bash
from .catalog import DummyTool, load_catalog
from .llm import LLM, Completion, LLMError, OpenAICompatibleLLM, Usage
from .skills import Skill, load_skills, skills_prompt
from .tools import Tool, Toolbox

__all__ = ["SYSTEM_PROMPT", "Agent", "AssistantMessage", "Bash", "Compaction", "CompactionError", "CompactionPolicy", "Completion", "DummyTool", "Event", "LLM",
           "LLMError", "OpenAICompatibleLLM", "RunFinished", "Skill", "Tool", "ToolResult", "ToolStarted", "Toolbox", "Usage",
           "UserMessage", "build_context", "load_catalog", "load_skills", "skills_prompt"]

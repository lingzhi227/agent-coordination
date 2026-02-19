"""
Unified trace building and persistence.

All coordination patterns use build_trace() + save_trace() to produce
a consistent JSON format for debugging and analysis.

Trace schema v2.0 adds:
  - backend info per step (codex / claude_code / gemini)
  - thinking blocks (extended thinking / reasoning)
  - session_messages (complete normalized messages from native session files)
  - session_file path for each step
"""

import json
from datetime import datetime, timezone

from src.backends import DEFAULT_MODELS, Backend
from src.agent import AgentResult
from src.base import CoordinatorResult


SCHEMA_VERSION = "2.0"


def _build_step(step: AgentResult, step_index: int) -> dict:
    """Convert a single AgentResult into the unified step dict."""
    t = step.trace
    return {
        "agent_name": step.agent_name,
        "step_label": step.step_label or "",
        "step_index": step_index,
        "elapsed_seconds": round(step.elapsed, 2),
        "backend": t.backend if t else "",
        "model": t.model if t else None,
        "system_prompt": t.system_prompt if t else "",
        "user_prompt": t.user_prompt if t else "",
        "context": t.context if t else None,
        "full_prompt": t.full_prompt if t else "",
        "thinking": t.thinking if t else [],
        "tool_calls": t.tool_calls if t else [],
        "tool_results": t.tool_results if t else [],
        "web_searches": t.web_searches if t else [],
        "command_executions": t.command_executions if t else [],
        "session_messages": (
            [m.to_dict() for m in t.session_messages] if t else []
        ),
        "session_file": t.session_file if t else None,
        "raw_events": t.raw_events if t else [],
        "output": t.output if t else (step.output or ""),
        "usage": t.usage if t else None,
        "error": t.error if t else step.error,
    }


def build_trace(
    result: CoordinatorResult,
    task: str,
    *,
    pattern: str = "",
    model: str = "",
) -> dict:
    """Build a unified trace dict from a CoordinatorResult.

    Args:
        result: The coordinator result containing steps and metadata.
        task: The original task string.
        pattern: Coordination pattern name (auto-detected from
                 result.metadata["pattern"] if not provided).
        model: Model name (defaults to codex model for backward compat).
    """
    pat = pattern or result.metadata.get("pattern", "")
    mdl = model or DEFAULT_MODELS[Backend.CODEX]

    steps = [_build_step(s, i) for i, s in enumerate(result.steps)]

    # Collect unique backends used across all steps
    backends_used = sorted({
        s.trace.backend for s in result.steps
        if s.trace and s.trace.backend
    })

    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": mdl,
            "pattern": pat,
            "task": task,
            "total_elapsed_seconds": round(result.elapsed, 2),
            "total_steps": len(steps),
            "success": result.success,
            "backends_used": backends_used,
        },
        "steps": steps,
    }


def save_trace(trace: dict, path: str) -> None:
    """Write a trace dict to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False, default=str)

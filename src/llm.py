"""
LLM wrapper using local Codex CLI.

Calls `codex exec --json` as a subprocess, parses the JSONL stream,
and returns the final assistant answer.
"""

import json
import subprocess
from dataclasses import dataclass, field

DEFAULT_MODEL = "gpt-5.2-codex"


@dataclass
class LLMResponse:
    text: str
    reasoning: list[str] = field(default_factory=list)
    usage: dict | None = None
    error: str | None = None
    events: list[dict] = field(default_factory=list)  # every raw JSONL event


def call(prompt: str, *, model: str = DEFAULT_MODEL) -> LLMResponse:
    """Send a prompt to Codex CLI and return the response."""
    cmd = ["codex", "exec", "--json", "--model", model, prompt]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    reasoning: list[str] = []
    assistant_texts: list[str] = []
    events: list[dict] = []
    usage = None
    error = None

    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Store every raw event for tracing
        events.append(event)

        etype = event.get("type")
        item = event.get("item", {})

        if etype == "item.completed":
            if item.get("type") == "reasoning" and item.get("text"):
                reasoning.append(item["text"])
            elif item.get("type") == "agent_message" and item.get("text"):
                assistant_texts.append(item["text"])

        elif etype == "turn.completed":
            usage = event.get("usage")

        elif etype in ("error", "turn.failed"):
            err = event.get("error", {})
            error = err.get("message") if isinstance(err, dict) else event.get("message", str(err))

    proc.wait()

    stderr_out = proc.stderr.read().strip()
    if proc.returncode != 0 and not error:
        error = stderr_out or f"codex exited with code {proc.returncode}"

    final_text = assistant_texts[-1] if assistant_texts else ""

    return LLMResponse(
        text=final_text,
        reasoning=reasoning,
        usage=usage,
        error=error,
        events=events,
    )

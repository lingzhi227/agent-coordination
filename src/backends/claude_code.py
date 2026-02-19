"""
Claude Code CLI backend.

Invokes `claude -p --output-format stream-json` and extracts the complete
trace from the native session file at ~/.claude/projects/{slug}/{uuid}.jsonl.

Session file format (from life-long-memory/src/parsers/claude_code.py):
  Each line: {"type": "user"|"assistant"|"progress"|..., "timestamp": str,
              "sessionId": str, "message": {"role": str, "content": [...]}}
  Content block types:
    {"type": "thinking", "thinking": "..."}     → extended thinking
    {"type": "text", "text": "..."}             → text output
    {"type": "tool_use", "name": "...", "input": {...}} → tool call
    {"type": "tool_result", "content": "..."}   → tool result
"""

import json
import subprocess
import time
from pathlib import Path

from src.backends import LLMResponse, TraceMessage
from src.backends.session_utils import (
    read_jsonl,
    truncate,
    wait_for_session_file,
)

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"


def call_claude_code(
    prompt: str,
    *,
    model: str = "claude-sonnet-4-6",
    full_auto: bool = False,
) -> LLMResponse:
    """Send a prompt to Claude Code CLI and return the response with full trace."""
    cmd = ["claude", "-p", "--output-format", "stream-json", "--verbose", "--model", model]
    if full_auto:
        cmd.append("--dangerously-skip-permissions")

    # Record time before execution to find new session file
    start_mtime = time.time() - 1  # 1s buffer

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Send prompt via stdin (safer for long prompts)
    proc.stdin.write(prompt)
    proc.stdin.close()

    # Parse stream-json stdout for immediate answer
    assistant_texts: list[str] = []
    raw_events: list[dict] = []
    usage = None
    error = None
    session_id = None

    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        raw_events.append(event)
        etype = event.get("type", "")

        if etype == "system" and event.get("subtype") == "init":
            session_id = event.get("session_id")

        elif etype == "assistant":
            message = event.get("message", {})
            content = message.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text = block.get("text", "")
                        if text:
                            assistant_texts.append(text)
            u = message.get("usage")
            if u:
                usage = u

        elif etype == "result":
            result_text = event.get("result", "")
            if result_text and not assistant_texts:
                assistant_texts.append(result_text)
            if event.get("is_error"):
                error = result_text
            if not session_id:
                session_id = event.get("session_id")

        elif etype == "error":
            error = event.get("error", {}).get("message", str(event))

    proc.wait()

    stderr_out = proc.stderr.read().strip()
    if proc.returncode != 0 and not error:
        error = stderr_out or f"claude exited with code {proc.returncode}"

    final_text = assistant_texts[-1] if assistant_texts else ""

    # --- Extract complete trace from session file ---
    thinking, tool_calls, tool_results, session_messages = [], [], [], []
    session_file = None

    sf = _find_session_file(session_id, start_mtime)
    if sf:
        session_file = str(sf)
        thinking, tool_calls, tool_results, session_messages = (
            _parse_claude_code_session(sf)
        )

    return LLMResponse(
        text=final_text,
        thinking=thinking,
        tool_calls=tool_calls,
        tool_results=tool_results,
        raw_events=raw_events,
        session_messages=session_messages,
        session_file=session_file,
        usage=usage,
        error=error,
        model=model,
        backend="claude_code",
    )


def _find_session_file(
    session_id: str | None,
    start_mtime: float,
) -> Path | None:
    """Find the Claude Code session JSONL file.

    First tries to match by session_id, then falls back to newest file.
    """
    if not CLAUDE_PROJECTS_DIR.exists():
        return None

    # If we know the session ID, search for the exact file
    if session_id:
        for project_dir in CLAUDE_PROJECTS_DIR.iterdir():
            if not project_dir.is_dir():
                continue
            candidate = project_dir / f"{session_id}.jsonl"
            if candidate.exists():
                return candidate

    # Fallback: find newest JSONL file across all projects
    return wait_for_session_file(
        CLAUDE_PROJECTS_DIR, "*.jsonl", start_mtime, timeout=5.0,
    )


def _parse_claude_code_session(
    file_path: Path,
) -> tuple[list[str], list[dict], list[dict], list[TraceMessage]]:
    """Parse a Claude Code session JSONL file for complete trace.

    Adapted from life-long-memory/src/parsers/claude_code.py.

    Returns:
        (thinking, tool_calls, tool_results, session_messages)
    """
    records = read_jsonl(file_path)

    thinking: list[str] = []
    tool_calls: list[dict] = []
    tool_results: list[dict] = []
    messages: list[TraceMessage] = []

    for rec in records:
        rec_type = rec.get("type", "")
        ts_str = rec.get("timestamp", "")

        # Skip non-message types
        if rec_type in ("file-history-snapshot", "queue-operation", "progress"):
            continue

        message = rec.get("message", {})
        if not message:
            continue

        content = message.get("content", "")

        if rec_type == "user":
            _parse_user_content(content, ts_str, messages, tool_results)

        elif rec_type == "assistant":
            _parse_assistant_content(
                content, ts_str, messages, thinking, tool_calls,
            )

    return thinking, tool_calls, tool_results, messages


def _parse_user_content(
    content: str | list | dict,
    ts_str: str,
    messages: list[TraceMessage],
    tool_results: list[dict],
) -> None:
    """Parse user message content blocks."""
    if isinstance(content, str):
        if content.strip():
            messages.append(TraceMessage(
                role="user",
                content_type="text",
                content=content,
                timestamp=ts_str,
            ))
        return

    if isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type", "")

            if item_type == "text":
                text = item.get("text", "")
                if text.strip():
                    messages.append(TraceMessage(
                        role="user",
                        content_type="text",
                        content=text,
                        timestamp=ts_str,
                    ))

            elif item_type == "tool_result":
                result_content = item.get("content", "")
                if isinstance(result_content, list):
                    parts = []
                    for block in result_content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            parts.append(block.get("text", ""))
                    result_content = "\n".join(parts)
                result_text = truncate(str(result_content))
                tool_results.append({
                    "tool_use_id": item.get("tool_use_id"),
                    "output": result_text,
                })
                messages.append(TraceMessage(
                    role="tool",
                    content_type="tool_result",
                    content=result_text,
                    timestamp=ts_str,
                ))


def _parse_assistant_content(
    content: str | list | dict,
    ts_str: str,
    messages: list[TraceMessage],
    thinking: list[str],
    tool_calls: list[dict],
) -> None:
    """Parse assistant message content blocks."""
    if isinstance(content, str):
        if content.strip():
            messages.append(TraceMessage(
                role="assistant",
                content_type="text",
                content=content,
                timestamp=ts_str,
            ))
        return

    if isinstance(content, list):
        for item in content:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type", "")

            if item_type == "text":
                text = item.get("text", "")
                if text.strip():
                    messages.append(TraceMessage(
                        role="assistant",
                        content_type="text",
                        content=text,
                        timestamp=ts_str,
                    ))

            elif item_type == "thinking":
                text = item.get("thinking", "")
                if text.strip():
                    thinking.append(text)
                    messages.append(TraceMessage(
                        role="assistant",
                        content_type="thinking",
                        content=text,
                        timestamp=ts_str,
                    ))

            elif item_type == "tool_use":
                name = item.get("name", "")
                inp = item.get("input", {})
                inp_str = json.dumps(inp) if isinstance(inp, dict) else str(inp)
                tc = {
                    "id": item.get("id"),
                    "name": name,
                    "input": inp,
                }
                tool_calls.append(tc)
                messages.append(TraceMessage(
                    role="assistant",
                    content_type="tool_call",
                    content=truncate(inp_str, 500),
                    tool_name=name,
                    tool_input=inp_str,
                    timestamp=ts_str,
                ))

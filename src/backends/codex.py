"""
Codex CLI backend.

Invokes `codex exec --json` and extracts the complete trace from
the native session file at ~/.codex/sessions/{y}/{m}/{d}/rollout-*.jsonl.

Session file format (from life-long-memory/src/parsers/codex.py):
  Each line: {"timestamp": str, "type": str, "payload": {...}}
  Types: session_meta, turn_context, response_item, event_msg
  response_item payloads: message, reasoning, function_call,
                          function_call_output, custom_tool_call, custom_tool_call_output
"""

import json
import subprocess
import time
from pathlib import Path

from src.backends import LLMResponse, TraceMessage
from src.backends.session_utils import (
    find_newest_file,
    read_jsonl,
    truncate,
    wait_for_session_file,
)

CODEX_SESSION_DIR = Path.home() / ".codex" / "sessions"


def call_codex(
    prompt: str,
    *,
    model: str = "gpt-5.2-codex",
    full_auto: bool = False,
) -> LLMResponse:
    """Send a prompt to Codex CLI and return the response with full trace."""
    cmd = ["codex", "exec", "--json", "--model", model]
    if full_auto:
        cmd.extend(["--full-auto", "--skip-git-repo-check", "--ephemeral"])
    cmd.append(prompt)

    # Record time before execution to find new session file
    start_mtime = time.time() - 1  # 1s buffer

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Parse stdout JSONL stream for immediate answer
    assistant_texts: list[str] = []
    raw_events: list[dict] = []
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

        raw_events.append(event)
        etype = event.get("type")
        item = event.get("item", {})

        if etype == "item.completed":
            itype = item.get("type")
            if itype == "agent_message" and item.get("text"):
                assistant_texts.append(item["text"])
        elif etype == "turn.completed":
            usage = event.get("usage")
        elif etype in ("error", "turn.failed"):
            err = event.get("error", {})
            error = (
                err.get("message") if isinstance(err, dict)
                else event.get("message", str(err))
            )

    proc.wait()

    stderr_out = proc.stderr.read().strip()
    if proc.returncode != 0 and not error:
        error = stderr_out or f"codex exited with code {proc.returncode}"

    final_text = assistant_texts[-1] if assistant_texts else ""

    # --- Extract complete trace from session file ---
    thinking, tool_calls, tool_results, session_messages = [], [], [], []
    session_file = None

    sf = wait_for_session_file(
        CODEX_SESSION_DIR, "rollout-*.jsonl", start_mtime, timeout=5.0,
    )
    if sf:
        session_file = str(sf)
        thinking, tool_calls, tool_results, session_messages = _parse_codex_session(sf)

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
        backend="codex",
    )


def _parse_codex_session(
    file_path: Path,
) -> tuple[list[str], list[dict], list[dict], list[TraceMessage]]:
    """Parse a Codex session JSONL file for complete trace.

    Adapted from life-long-memory/src/parsers/codex.py.

    Returns:
        (thinking, tool_calls, tool_results, session_messages)
    """
    records = read_jsonl(file_path)

    thinking: list[str] = []
    tool_calls: list[dict] = []
    tool_results: list[dict] = []
    messages: list[TraceMessage] = []

    for rec in records:
        ts_str = rec.get("timestamp", "")
        rec_type = rec.get("type", "")
        payload = rec.get("payload", {})

        if rec_type == "response_item":
            ptype = payload.get("type", "")

            if ptype == "message":
                role = payload.get("role", "user")
                content_parts = payload.get("content", [])
                text_parts = []
                for part in content_parts:
                    if isinstance(part, dict):
                        t = part.get("text", "")
                        if t:
                            text_parts.append(t)
                    elif isinstance(part, str):
                        text_parts.append(part)
                text = "\n".join(text_parts)
                if text:
                    messages.append(TraceMessage(
                        role=role,
                        content_type="text",
                        content=text,
                        timestamp=ts_str,
                    ))

            elif ptype == "reasoning":
                summary_parts = payload.get("summary", [])
                text_parts = []
                for part in summary_parts:
                    if isinstance(part, dict):
                        text_parts.append(part.get("text", ""))
                text = "\n".join(text_parts)
                if text:
                    thinking.append(text)
                    messages.append(TraceMessage(
                        role="assistant",
                        content_type="thinking",
                        content=text,
                        timestamp=ts_str,
                    ))

            elif ptype == "function_call":
                name = payload.get("name", "")
                args = payload.get("arguments", "")
                call_id = payload.get("call_id", "")
                tc = {"name": name, "arguments": args, "call_id": call_id}
                tool_calls.append(tc)
                messages.append(TraceMessage(
                    role="assistant",
                    content_type="tool_call",
                    content=truncate(args, 500),
                    tool_name=name,
                    tool_input=args,
                    timestamp=ts_str,
                ))

            elif ptype == "function_call_output":
                output = payload.get("output", "")
                call_id = payload.get("call_id", "")
                tr = {"call_id": call_id, "output": truncate(output)}
                tool_results.append(tr)
                messages.append(TraceMessage(
                    role="tool",
                    content_type="tool_result",
                    content=truncate(output),
                    timestamp=ts_str,
                ))

            elif ptype == "custom_tool_call":
                name = payload.get("name", "")
                inp = str(payload.get("input", ""))
                call_id = payload.get("call_id", "")
                tc = {"name": name, "input": inp, "call_id": call_id}
                tool_calls.append(tc)
                messages.append(TraceMessage(
                    role="assistant",
                    content_type="tool_call",
                    content=truncate(inp, 500),
                    tool_name=name,
                    tool_input=inp,
                    timestamp=ts_str,
                ))

            elif ptype == "custom_tool_call_output":
                output = str(payload.get("output", ""))
                tr = {"output": truncate(output)}
                tool_results.append(tr)
                messages.append(TraceMessage(
                    role="tool",
                    content_type="tool_result",
                    content=truncate(output),
                    timestamp=ts_str,
                ))

        elif rec_type == "event_msg":
            payload_type = payload.get("type", "")
            if payload_type == "user_message":
                text = payload.get("message", "")
                if text:
                    messages.append(TraceMessage(
                        role="user",
                        content_type="text",
                        content=text,
                        timestamp=ts_str,
                    ))

    return thinking, tool_calls, tool_results, messages

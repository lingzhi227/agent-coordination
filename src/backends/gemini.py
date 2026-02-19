"""
Gemini CLI backend.

Invokes the Gemini CLI and extracts the complete trace from the native
session file at ~/.gemini/tmp/{projectHash}/chats/session-*.json.

Session file format (from life-long-memory/src/parsers/gemini.py):
  Single JSON object:
    {"sessionId": str, "projectHash": str, "messages": [...]}
  Message types: "user", "gemini", "info"
  Gemini messages contain:
    thoughts: [{subject, description}]    → thinking
    toolCalls: [{name, args, result}]     → tool calls + results
    content: str                          → text output
"""

import hashlib
import json
import subprocess
import time
from pathlib import Path

from src.backends import LLMResponse, TraceMessage
from src.backends.session_utils import (
    read_json,
    truncate,
    wait_for_session_file,
)

GEMINI_TMP_DIR = Path.home() / ".gemini" / "tmp"


def call_gemini(
    prompt: str,
    *,
    model: str = "gemini-2.5-pro",
    full_auto: bool = False,
) -> LLMResponse:
    """Send a prompt to Gemini CLI and return the response with full trace."""
    cmd = ["gemini"]
    if model:
        cmd.extend(["--model", model])
    if full_auto:
        cmd.append("--sandbox")

    # Record time before execution to find new session file
    start_mtime = time.time() - 1  # 1s buffer

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Send prompt via stdin
    proc.stdin.write(prompt)
    proc.stdin.close()

    stdout_text = proc.stdout.read()
    proc.wait()

    stderr_out = proc.stderr.read().strip()
    error = None
    if proc.returncode != 0:
        error = stderr_out or f"gemini exited with code {proc.returncode}"

    final_text = stdout_text.strip()

    # --- Extract complete trace from session file ---
    thinking, tool_calls, tool_results, session_messages = [], [], [], []
    session_file = None
    usage = None
    detected_model = None

    sf = wait_for_session_file(
        GEMINI_TMP_DIR, "session-*.json", start_mtime, timeout=5.0,
    )
    if sf:
        session_file = str(sf)
        result = _parse_gemini_session(sf)
        thinking = result["thinking"]
        tool_calls = result["tool_calls"]
        tool_results = result["tool_results"]
        session_messages = result["messages"]
        usage = result["usage"]
        detected_model = result["model"]
        # Use session file content as final text if stdout was empty
        if not final_text and result["final_text"]:
            final_text = result["final_text"]

    return LLMResponse(
        text=final_text,
        thinking=thinking,
        tool_calls=tool_calls,
        tool_results=tool_results,
        raw_events=[],  # Gemini doesn't stream JSONL events
        session_messages=session_messages,
        session_file=session_file,
        usage=usage,
        error=error,
        model=detected_model or model,
        backend="gemini",
    )


def _parse_gemini_session(file_path: Path) -> dict:
    """Parse a Gemini session JSON file for complete trace.

    Adapted from life-long-memory/src/parsers/gemini.py.

    Returns dict with: thinking, tool_calls, tool_results, messages,
                       usage, model, final_text
    """
    data = read_json(file_path)
    if not data:
        return _empty_result()

    raw_messages = data.get("messages", [])
    if not raw_messages:
        return _empty_result()

    thinking: list[str] = []
    tool_calls: list[dict] = []
    tool_results: list[dict] = []
    messages: list[TraceMessage] = []
    total_tokens = 0
    model = None
    final_text = ""

    for msg in raw_messages:
        if not isinstance(msg, dict):
            continue

        msg_type = msg.get("type", "")
        ts_str = msg.get("timestamp", "")

        if msg_type == "user":
            text = _extract_user_text(msg)
            if text:
                messages.append(TraceMessage(
                    role="user",
                    content_type="text",
                    content=text,
                    timestamp=ts_str,
                ))

        elif msg_type == "gemini":
            if not model:
                model = msg.get("model")

            # Token accounting
            tokens = msg.get("tokens", {})
            if tokens:
                total_tokens += tokens.get("total", 0)

            # Thinking / thoughts
            for thought in msg.get("thoughts", []):
                desc = thought.get("description", "")
                subject = thought.get("subject", "")
                thought_text = f"{subject}: {desc}" if subject else desc
                if thought_text:
                    thinking.append(thought_text)
                    messages.append(TraceMessage(
                        role="assistant",
                        content_type="thinking",
                        content=thought_text,
                        timestamp=ts_str,
                    ))

            # Tool calls
            for tc in msg.get("toolCalls", []):
                tool_name = tc.get("name", "")
                args = tc.get("args", {})
                result = tc.get("result", "")
                status = tc.get("status", "")
                if tool_name:
                    args_str = json.dumps(args) if isinstance(args, dict) else str(args)
                    tool_calls.append({
                        "name": tool_name,
                        "args": args,
                        "status": status,
                    })
                    messages.append(TraceMessage(
                        role="assistant",
                        content_type="tool_call",
                        content=truncate(args_str, 500),
                        tool_name=tool_name,
                        tool_input=args_str,
                        timestamp=ts_str,
                    ))

                    # Tool result
                    result_text = (
                        json.dumps(result) if not isinstance(result, str)
                        else result
                    )
                    tool_results.append({
                        "name": tool_name,
                        "output": truncate(result_text),
                    })
                    messages.append(TraceMessage(
                        role="tool",
                        content_type="tool_result",
                        content=truncate(result_text),
                        timestamp=ts_str,
                    ))

            # Main text content
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip():
                final_text = content  # Last gemini message is the final answer
                messages.append(TraceMessage(
                    role="assistant",
                    content_type="text",
                    content=content,
                    timestamp=ts_str,
                ))

        elif msg_type == "info":
            content = msg.get("content", "")
            text = ""
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text = " ".join(
                    item.get("text", "") for item in content
                    if isinstance(item, dict)
                )
            if text.strip():
                messages.append(TraceMessage(
                    role="system",
                    content_type="text",
                    content=text,
                    timestamp=ts_str,
                ))

    usage_dict = {"total_tokens": total_tokens} if total_tokens else None

    return {
        "thinking": thinking,
        "tool_calls": tool_calls,
        "tool_results": tool_results,
        "messages": messages,
        "usage": usage_dict,
        "model": model,
        "final_text": final_text,
    }


def _extract_user_text(msg: dict) -> str:
    """Extract text from a user message's content field."""
    content = msg.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                t = item.get("text", "")
                if t:
                    parts.append(t)
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return ""


def _empty_result() -> dict:
    return {
        "thinking": [],
        "tool_calls": [],
        "tool_results": [],
        "messages": [],
        "usage": None,
        "model": None,
        "final_text": "",
    }

"""
Shared utilities for session file discovery and parsing.

Used by all three backends to find and read native session files
after CLI execution.
"""

import json
import time
from pathlib import Path


def read_jsonl(file_path: Path) -> list[dict]:
    """Read a JSONL file, skipping malformed lines."""
    lines = []
    with open(file_path, "r", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                lines.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return lines


def read_json(file_path: Path) -> dict | None:
    """Read a JSON file, returning None on error."""
    try:
        data = json.loads(file_path.read_text(errors="replace"))
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, OSError):
        return None


def find_newest_file(
    directory: Path,
    pattern: str,
    after_mtime: float,
) -> Path | None:
    """Find the newest file matching glob pattern created after the given time.

    Args:
        directory: Root directory to search recursively.
        pattern: Glob pattern (e.g. "*.jsonl", "session-*.json").
        after_mtime: Only consider files modified after this unix timestamp.

    Returns:
        Path to the newest matching file, or None.
    """
    if not directory.exists():
        return None
    candidates = []
    for f in directory.rglob(pattern):
        if f.is_file() and f.stat().st_mtime > after_mtime:
            candidates.append(f)
    if not candidates:
        return None
    return max(candidates, key=lambda f: f.stat().st_mtime)


def truncate(text: str, max_len: int = 2000) -> str:
    """Truncate text, adding ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "...[truncated]"


def wait_for_session_file(
    directory: Path,
    pattern: str,
    after_mtime: float,
    timeout: float = 10.0,
    poll_interval: float = 0.5,
) -> Path | None:
    """Wait for a new session file to appear after CLI execution.

    Some CLIs flush the session file slightly after the process exits.
    This polls for up to `timeout` seconds.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = find_newest_file(directory, pattern, after_mtime)
        if result is not None:
            # Give the file a moment to finish writing
            time.sleep(0.2)
            return result
        time.sleep(poll_interval)
    return None

"""
Multi-backend LLM support: Codex CLI, Claude Code, Gemini CLI.

Each backend invokes the CLI subprocess, then reads the native session
file for the complete faithful trace (thinking, tool calls, tool results).
Trace extraction methods adapted from life-long-memory parsers.
"""

from enum import Enum
from dataclasses import dataclass, field


class Backend(str, Enum):
    CODEX = "codex"
    CLAUDE_CODE = "claude_code"
    GEMINI = "gemini"


DEFAULT_BACKEND = Backend.CODEX

DEFAULT_MODELS = {
    Backend.CODEX: "gpt-5.2-codex",
    Backend.CLAUDE_CODE: "claude-sonnet-4-6",
    Backend.GEMINI: "gemini-2.5-pro",
}


@dataclass
class TraceMessage:
    """Normalized message extracted from a native session file.

    Provides a unified representation across all three CLIs:
    - Claude Code JSONL: thinking blocks, tool_use, tool_result, text
    - Codex JSONL: reasoning, function_call, function_call_output, message
    - Gemini JSON: thoughts, toolCalls, content
    """

    role: str  # user | assistant | tool | system
    content_type: str  # text | thinking | tool_call | tool_result
    content: str
    tool_name: str | None = None
    tool_input: str | None = None
    timestamp: str = ""

    def to_dict(self) -> dict:
        d = {
            "role": self.role,
            "content_type": self.content_type,
            "content": self.content,
        }
        if self.tool_name:
            d["tool_name"] = self.tool_name
        if self.tool_input:
            d["tool_input"] = self.tool_input
        if self.timestamp:
            d["timestamp"] = self.timestamp
        return d


@dataclass
class LLMResponse:
    """Unified response from any backend.

    Contains both the immediate answer (text) and the complete trace
    extracted from the native session file.
    """

    text: str
    thinking: list[str] = field(default_factory=list)
    tool_calls: list[dict] = field(default_factory=list)
    tool_results: list[dict] = field(default_factory=list)
    raw_events: list[dict] = field(default_factory=list)
    session_messages: list[TraceMessage] = field(default_factory=list)
    session_file: str | None = None
    usage: dict | None = None
    error: str | None = None
    model: str | None = None
    backend: str = ""

    @property
    def reasoning(self) -> list[str]:
        """Alias for thinking (backward compat with codex-only code)."""
        return self.thinking

    @property
    def events(self) -> list[dict]:
        """Alias for raw_events (backward compat)."""
        return self.raw_events


def call(
    prompt: str,
    *,
    backend: Backend | str = DEFAULT_BACKEND,
    model: str = "",
    full_auto: bool = False,
) -> LLMResponse:
    """Dispatch a prompt to the appropriate CLI backend.

    Args:
        prompt: The full prompt string to send.
        backend: Which CLI to use (codex, claude_code, gemini).
        model: Model name. Defaults to backend-specific default.
        full_auto: Enable autonomous mode (web search, commands, etc.).

    Returns:
        LLMResponse with text answer and complete session trace.
    """
    if isinstance(backend, str):
        backend = Backend(backend)

    resolved_model = model or DEFAULT_MODELS[backend]

    if backend == Backend.CODEX:
        from src.backends.codex import call_codex
        return call_codex(prompt, model=resolved_model, full_auto=full_auto)
    elif backend == Backend.CLAUDE_CODE:
        from src.backends.claude_code import call_claude_code
        return call_claude_code(prompt, model=resolved_model, full_auto=full_auto)
    elif backend == Backend.GEMINI:
        from src.backends.gemini import call_gemini
        return call_gemini(prompt, model=resolved_model, full_auto=full_auto)
    else:
        raise ValueError(f"Unknown backend: {backend}")

"""
Base Agent class for all coordination patterns.

An agent has a role (system-level description of what it does) and can
process a task by sending a prompt to the LLM via a configurable backend
(Codex CLI, Claude Code, or Gemini CLI).
"""

import time
from dataclasses import dataclass, field

from src.backends import Backend, DEFAULT_MODELS, LLMResponse, TraceMessage
from src.backends import call as backend_call


@dataclass
class AgentTrace:
    """Full trace of a single agent invocation for debugging / logging.

    Includes both the immediate execution data and the complete trace
    extracted from the CLI's native session file.
    """

    system_prompt: str = ""
    user_prompt: str = ""
    context: str | None = None
    full_prompt: str = ""
    # Thinking / reasoning blocks (from session file)
    thinking: list[str] = field(default_factory=list)
    # Tool calls and results (from session file)
    tool_calls: list[dict] = field(default_factory=list)
    tool_results: list[dict] = field(default_factory=list)
    # Raw events from stdout stream (backend-specific)
    raw_events: list[dict] = field(default_factory=list)
    # Complete normalized messages from session file
    session_messages: list[TraceMessage] = field(default_factory=list)
    # Path to the native session file
    session_file: str | None = None
    # Extracted web searches and command executions (Codex-specific)
    web_searches: list[dict] = field(default_factory=list)
    command_executions: list[dict] = field(default_factory=list)
    # Final output and metadata
    output: str = ""
    usage: dict | None = None
    error: str | None = None
    backend: str = ""
    model: str | None = None

    @property
    def reasoning(self) -> list[str]:
        """Alias for thinking (backward compat)."""
        return self.thinking

    def to_dict(self) -> dict:
        return {
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "context": self.context,
            "full_prompt": self.full_prompt,
            "thinking": self.thinking,
            "tool_calls": self.tool_calls,
            "tool_results": self.tool_results,
            "raw_events": self.raw_events,
            "session_messages": [m.to_dict() for m in self.session_messages],
            "session_file": self.session_file,
            "web_searches": self.web_searches,
            "command_executions": self.command_executions,
            "output": self.output,
            "usage": self.usage,
            "error": self.error,
            "backend": self.backend,
            "model": self.model,
        }


@dataclass
class AgentResult:
    agent_name: str
    output: str
    error: str | None = None
    trace: AgentTrace | None = None
    elapsed: float = 0.0
    step_label: str = ""


@dataclass
class Agent:
    name: str
    role: str  # describes what this agent does, injected into every prompt
    instruction: str = ""  # agent-specific sub-question or assignment
    full_auto: bool = False  # enable autonomous mode (web search / commands)
    backend: Backend | str = Backend.CODEX  # which CLI to use
    model: str = ""  # model override (defaults to backend-specific default)

    def __repr__(self) -> str:
        return f"Agent({self.name!r}, backend={self.backend!r})"

    def run(self, task: str, context: str = "") -> AgentResult:
        """Execute a task with optional context from previous steps."""
        system_prompt = f"You are: {self.role}"
        parts = [system_prompt]
        if context:
            parts.append(f"Context from previous work:\n{context}")
        user_prompt = f"Task:\n{task}"
        parts.append(user_prompt)
        if self.instruction:
            parts.append(f"Your specific assignment:\n{self.instruction}")

        prompt = "\n\n".join(parts)
        t0 = time.time()
        resp: LLMResponse = backend_call(
            prompt,
            backend=self.backend,
            model=self.model,
            full_auto=self.full_auto,
        )
        elapsed = time.time() - t0

        # Extract web_search and command_execution events (Codex-specific)
        web_searches: list[dict] = []
        command_executions: list[dict] = []
        for ev in resp.raw_events:
            item = ev.get("item", {})
            etype = ev.get("type", "")
            itype = item.get("type", "")
            if etype == "item.completed" and itype == "web_search":
                web_searches.append({
                    "id": item.get("id"),
                    "query": item.get("query", ""),
                    "results": item.get("results", []),
                })
            elif etype == "item.completed" and itype == "command_execution":
                command_executions.append({
                    "id": item.get("id"),
                    "command": item.get("command", ""),
                    "output": (item.get("aggregated_output") or "")[:2000],
                    "exit_code": item.get("exit_code"),
                })

        trace = AgentTrace(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context or None,
            full_prompt=prompt,
            thinking=resp.thinking,
            tool_calls=resp.tool_calls,
            tool_results=resp.tool_results,
            raw_events=resp.raw_events,
            session_messages=resp.session_messages,
            session_file=resp.session_file,
            web_searches=web_searches,
            command_executions=command_executions,
            output=resp.text,
            usage=resp.usage,
            error=resp.error,
            backend=resp.backend,
            model=resp.model,
        )

        return AgentResult(
            agent_name=self.name,
            output=resp.text,
            error=resp.error,
            trace=trace,
            elapsed=elapsed,
        )

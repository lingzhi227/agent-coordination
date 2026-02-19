"""
Base Agent class for all coordination patterns.

An agent has a role (system-level description of what it does) and can
process a task by sending a prompt to the LLM.
"""

from dataclasses import dataclass, field
from src import llm


@dataclass
class AgentTrace:
    """Full trace of a single agent invocation for debugging / logging."""
    system_prompt: str = ""
    user_prompt: str = ""
    context: str | None = None
    full_prompt: str = ""
    reasoning: list[str] = field(default_factory=list)
    tool_calls: list[dict] = field(default_factory=list)
    tool_results: list[dict] = field(default_factory=list)
    raw_events: list[dict] = field(default_factory=list)
    output: str = ""
    usage: dict | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "context": self.context,
            "full_prompt": self.full_prompt,
            "reasoning": self.reasoning,
            "tool_calls": self.tool_calls,
            "tool_results": self.tool_results,
            "raw_events": self.raw_events,
            "output": self.output,
            "usage": self.usage,
            "error": self.error,
        }


@dataclass
class AgentResult:
    agent_name: str
    output: str
    error: str | None = None
    trace: AgentTrace | None = None


@dataclass
class Agent:
    name: str
    role: str  # describes what this agent does, injected into every prompt

    def __repr__(self) -> str:
        return f"Agent({self.name!r})"

    def run(self, task: str, context: str = "") -> AgentResult:
        """Execute a task with optional context from previous steps."""
        system_prompt = f"You are: {self.role}"
        parts = [system_prompt]
        if context:
            parts.append(f"Context from previous work:\n{context}")
        user_prompt = f"Task:\n{task}"
        parts.append(user_prompt)

        prompt = "\n\n".join(parts)
        resp = llm.call(prompt)

        trace = AgentTrace(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            context=context or None,
            full_prompt=prompt,
            reasoning=resp.reasoning,
            tool_calls=resp.tool_calls,
            tool_results=resp.tool_results,
            raw_events=resp.raw_events,
            output=resp.text,
            usage=resp.usage,
            error=resp.error,
        )

        return AgentResult(
            agent_name=self.name,
            output=resp.text,
            error=resp.error,
            trace=trace,
        )

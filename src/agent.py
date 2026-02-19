"""
Base Agent class for all coordination patterns.

An agent has a role (system-level description of what it does) and can
process a task by sending a prompt to the LLM.
"""

import time
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
    web_searches: list[dict] = field(default_factory=list)
    command_executions: list[dict] = field(default_factory=list)
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
            "web_searches": self.web_searches,
            "command_executions": self.command_executions,
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
    elapsed: float = 0.0
    step_label: str = ""


@dataclass
class Agent:
    name: str
    role: str  # describes what this agent does, injected into every prompt
    instruction: str = ""  # agent-specific sub-question or assignment
    full_auto: bool = False  # enable --full-auto for web search / command execution

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
        if self.instruction:
            parts.append(f"Your specific assignment:\n{self.instruction}")

        prompt = "\n\n".join(parts)
        t0 = time.time()
        resp = llm.call(prompt, full_auto=self.full_auto)
        elapsed = time.time() - t0

        # Extract web_search and command_execution events
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
            reasoning=resp.reasoning,
            tool_calls=resp.tool_calls,
            tool_results=resp.tool_results,
            raw_events=resp.raw_events,
            web_searches=web_searches,
            command_executions=command_executions,
            output=resp.text,
            usage=resp.usage,
            error=resp.error,
        )

        return AgentResult(
            agent_name=self.name,
            output=resp.text,
            error=resp.error,
            trace=trace,
            elapsed=elapsed,
        )

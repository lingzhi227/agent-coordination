"""
Base Agent class for all coordination patterns.

An agent has a role (system-level description of what it does) and can
process a task by sending a prompt to the LLM.
"""

from dataclasses import dataclass, field
from src import llm


@dataclass
class AgentResult:
    agent_name: str
    output: str
    error: str | None = None


@dataclass
class Agent:
    name: str
    role: str  # describes what this agent does, injected into every prompt

    def __repr__(self) -> str:
        return f"Agent({self.name!r})"

    def run(self, task: str, context: str = "") -> AgentResult:
        """Execute a task with optional context from previous steps."""
        parts = [f"You are: {self.role}"]
        if context:
            parts.append(f"Context from previous work:\n{context}")
        parts.append(f"Task:\n{task}")

        prompt = "\n\n".join(parts)
        resp = llm.call(prompt)

        return AgentResult(
            agent_name=self.name,
            output=resp.text,
            error=resp.error,
        )

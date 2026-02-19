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
    trace: dict | None = None  # full execution trace for debugging


@dataclass
class Agent:
    name: str
    role: str  # describes what this agent does, injected into every prompt

    def run(self, task: str, context: str = "") -> AgentResult:
        """Execute a task with optional context from previous steps."""
        system_prompt = f"You are: {self.role}"
        parts = [system_prompt]
        if context:
            parts.append(f"Context from previous work:\n{context}")
        parts.append(f"Task:\n{task}")

        prompt = "\n\n".join(parts)
        resp = llm.call(prompt)

        # Build structured trace
        trace = {
            "agent_name": self.name,
            "system_prompt": system_prompt,
            "user_prompt": task,
            "context": context or None,
            "full_prompt": prompt,
            "reasoning": resp.reasoning,
            "events": resp.events,
            "usage": resp.usage,
            "final_output": resp.text,
            "error": resp.error,
        }

        return AgentResult(
            agent_name=self.name,
            output=resp.text,
            error=resp.error,
            trace=trace,
        )

"""
Coordinator abstract base class and unified result type.

All coordination patterns (pipeline, plan-execute, parallel, etc.)
inherit from Coordinator and return CoordinatorResult.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from src.agent import AgentResult


@dataclass
class CoordinatorResult:
    """Unified result type for all coordination patterns."""

    steps: list[AgentResult] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    elapsed: float = 0.0

    @property
    def final_output(self) -> str:
        return self.steps[-1].output if self.steps else ""

    @property
    def success(self) -> bool:
        return all(s.error is None for s in self.steps)

    @property
    def errors(self) -> list[str]:
        return [
            f"{s.agent_name}: {s.error}" for s in self.steps if s.error is not None
        ]


class Coordinator(ABC):
    """Base class for all coordination patterns."""

    def __init__(self, name: str):
        self.name = name

    def run(self, task: str) -> CoordinatorResult:
        """Public interface — delegates to _run() and records elapsed time."""
        start = time.time()
        result = self._run(task)
        result.elapsed = time.time() - start
        return result

    @abstractmethod
    def _run(self, task: str) -> CoordinatorResult:
        """Subclasses implement their coordination logic here."""
        ...

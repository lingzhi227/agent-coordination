"""
A2A-inspired task envelope for graph execution.

Provides the in-process equivalent of A2A's Task lifecycle,
tracking state and provenance as data flows through the graph.
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum

from src.agent import AgentResult


class TaskState(str, Enum):
    """A2A task lifecycle states."""

    SUBMITTED = "submitted"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskEnvelope:
    """Message flowing along graph edges.

    Maps A2A concepts to lightweight in-process equivalents:
    - task_id: unique per node execution
    - context_id: unique per graph run (shared across all envelopes)
    - parent_task_ids: provenance — which upstream tasks produced this
    """

    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    context_id: str = ""
    parent_task_ids: list[str] = field(default_factory=list)
    task: str = ""
    context: str = ""
    state: TaskState = TaskState.SUBMITTED
    node_id: str = ""
    result: AgentResult | None = None

    def mark_working(self) -> None:
        self.state = TaskState.WORKING

    def mark_completed(self, result: AgentResult) -> None:
        self.state = TaskState.COMPLETED
        self.result = result

    def mark_failed(self, result: AgentResult) -> None:
        self.state = TaskState.FAILED
        self.result = result

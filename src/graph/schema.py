"""
Graph schema dataclasses.

Defines the declarative graph structure: nodes (agents), edges (data flow),
and their configuration. Maps A2A protocol concepts to lightweight in-process
equivalents.
"""

from dataclasses import dataclass, field
from enum import Enum


class ContextPolicy(str, Enum):
    """How context is passed along an edge."""

    REPLACE = "replace"
    ACCUMULATE = "accumulate"
    AGGREGATE = "aggregate"
    NONE = "none"


class ExpandMode(str, Enum):
    """How a dynamic node expands its output into downstream executions."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


@dataclass
class LLMCallDef:
    """Configuration for a dynamic node's LLM call."""

    backend: str = "codex"
    prompt: str = ""
    model: str = ""
    full_auto: bool = False


@dataclass
class NodeDef:
    """Definition of a single node (agent) in the graph."""

    id: str
    role: str = ""
    backend: str = "codex"
    model: str = ""
    full_auto: bool = False
    instruction: str = ""
    type: str = "agent"
    expand: ExpandMode | None = None
    llm_call: LLMCallDef | None = None
    transform: str = ""


@dataclass
class EdgeDef:
    """Definition of a directed edge (data flow) in the graph."""

    source: str
    target: str
    context_policy: ContextPolicy = ContextPolicy.REPLACE


@dataclass
class GraphDef:
    """Complete graph definition."""

    name: str
    nodes: dict[str, NodeDef] = field(default_factory=dict)
    edges: list[EdgeDef] = field(default_factory=list)

    @property
    def entry_nodes(self) -> list[str]:
        return [e.target for e in self.edges if e.source == "_input"]

    @property
    def exit_nodes(self) -> list[str]:
        return [e.source for e in self.edges if e.target == "_output"]

    def upstream(self, node_id: str) -> list[EdgeDef]:
        return [e for e in self.edges if e.target == node_id]

    def downstream(self, node_id: str) -> list[EdgeDef]:
        return [e for e in self.edges if e.source == node_id]

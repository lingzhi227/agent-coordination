"""
Graph-based agent coordination.

Provides a single declarative graph engine that unifies pipeline,
parallel, plan-execute, and arbitrary topologies.

Usage (YAML):
    from src.graph import load_graph, GraphExecutor
    graph = load_graph("graphs/pipeline.yaml")
    executor = GraphExecutor(graph)
    result = executor.run("Your task here")

Usage (programmatic):
    from src.graph import pipeline, parallel, plan_execute
    executor = pipeline([agent1, agent2, agent3])
    result = executor.run("Your task here")
"""

from src.graph.schema import (
    ContextPolicy,
    EdgeDef,
    ExpandMode,
    GraphDef,
    LLMCallDef,
    NodeDef,
)
from src.graph.envelope import TaskEnvelope, TaskState
from src.graph.loader import load_graph, parse_graph
from src.graph.executor import GraphExecutor

from src.agent import Agent
from src.backends import Backend


def pipeline(agents: list[Agent]) -> GraphExecutor:
    """Build a linear pipeline graph from a list of agents.

    Each agent's output replaces the context for the next agent.

    Args:
        agents: Ordered list of agents to chain.

    Returns:
        GraphExecutor ready to run.
    """
    nodes = {}
    edges = []

    for agent in agents:
        backend_val = (
            agent.backend if isinstance(agent.backend, str)
            else agent.backend.value
        )
        nodes[agent.name] = NodeDef(
            id=agent.name,
            role=agent.role,
            backend=backend_val,
            model=agent.model,
            full_auto=agent.full_auto,
            instruction=agent.instruction,
        )

    # _input -> first agent
    edges.append(EdgeDef(source="_input", target=agents[0].name))

    # Chain agents with replace policy
    for i in range(len(agents) - 1):
        edges.append(EdgeDef(
            source=agents[i].name,
            target=agents[i + 1].name,
            context_policy=ContextPolicy.REPLACE,
        ))

    # Last agent -> _output
    edges.append(EdgeDef(source=agents[-1].name, target="_output"))

    graph = GraphDef(name="pipeline", nodes=nodes, edges=edges)
    return GraphExecutor(graph)


def parallel(
    workers: list[Agent],
    synthesizer: Agent | None = None,
) -> GraphExecutor:
    """Build a parallel fan-out/fan-in graph.

    All workers receive the task concurrently. If a synthesizer is
    provided, all worker outputs are aggregated and fed to it.

    Args:
        workers: Agents to run in parallel.
        synthesizer: Optional agent to combine results.

    Returns:
        GraphExecutor ready to run.
    """
    nodes = {}
    edges = []

    for agent in workers:
        backend_val = (
            agent.backend if isinstance(agent.backend, str)
            else agent.backend.value
        )
        nodes[agent.name] = NodeDef(
            id=agent.name,
            role=agent.role,
            backend=backend_val,
            model=agent.model,
            full_auto=agent.full_auto,
            instruction=agent.instruction,
        )
        edges.append(EdgeDef(source="_input", target=agent.name))

    if synthesizer:
        backend_val = (
            synthesizer.backend if isinstance(synthesizer.backend, str)
            else synthesizer.backend.value
        )
        nodes[synthesizer.name] = NodeDef(
            id=synthesizer.name,
            role=synthesizer.role,
            backend=backend_val,
            model=synthesizer.model,
            full_auto=synthesizer.full_auto,
            instruction=synthesizer.instruction,
        )
        for agent in workers:
            edges.append(EdgeDef(
                source=agent.name,
                target=synthesizer.name,
                context_policy=ContextPolicy.AGGREGATE,
            ))
        edges.append(EdgeDef(source=synthesizer.name, target="_output"))
    else:
        for agent in workers:
            edges.append(EdgeDef(source=agent.name, target="_output"))

    graph = GraphDef(name="parallel", nodes=nodes, edges=edges)
    return GraphExecutor(graph)


def plan_execute(
    executor_agent: Agent,
    planning_backend: str = "codex",
) -> GraphExecutor:
    """Build a plan-execute graph with dynamic expansion.

    A planner LLM call breaks the task into subtasks, then the executor
    agent runs them sequentially with accumulating context.

    Args:
        executor_agent: Agent that executes each subtask.
        planning_backend: Backend for the planning LLM call.

    Returns:
        GraphExecutor ready to run.
    """
    backend_val = (
        executor_agent.backend if isinstance(executor_agent.backend, str)
        else executor_agent.backend.value
    )
    nodes = {
        "planner": NodeDef(
            id="planner",
            type="dynamic",
            expand=ExpandMode.SEQUENTIAL,
            llm_call=LLMCallDef(
                backend=planning_backend,
                prompt=(
                    "Break the following task into 2-5 concrete subtasks. "
                    "Return ONLY a JSON array of strings, no other text.\n\n"
                    "Task: {{task}}"
                ),
            ),
            transform="parse_list",
        ),
        "executor": NodeDef(
            id="executor",
            role=executor_agent.role,
            backend=backend_val,
            model=executor_agent.model,
            full_auto=executor_agent.full_auto,
            instruction=executor_agent.instruction,
        ),
    }

    edges = [
        EdgeDef(source="_input", target="planner"),
        EdgeDef(
            source="planner",
            target="executor",
            context_policy=ContextPolicy.ACCUMULATE,
        ),
        EdgeDef(source="executor", target="_output"),
    ]

    graph = GraphDef(name="plan-execute", nodes=nodes, edges=edges)
    return GraphExecutor(graph)


__all__ = [
    # Core types
    "GraphDef",
    "NodeDef",
    "EdgeDef",
    "LLMCallDef",
    "ContextPolicy",
    "ExpandMode",
    # A2A envelope
    "TaskEnvelope",
    "TaskState",
    # Loading
    "load_graph",
    "parse_graph",
    # Execution
    "GraphExecutor",
    # Factory functions
    "pipeline",
    "parallel",
    "plan_execute",
]

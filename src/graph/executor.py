"""
Graph executor — the single engine for all coordination patterns.

Executes a GraphDef by topologically sorting nodes, running them
with the appropriate context policies, and handling dynamic expansion.
"""

import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.agent import Agent, AgentResult
from src.backends import call as backend_call
from src.base import Coordinator, CoordinatorResult
from src.logging import StepLogger
from src.graph.envelope import TaskEnvelope, TaskState
from src.graph.schema import ContextPolicy, ExpandMode, GraphDef, NodeDef
from src.graph.transforms import get_transform


class GraphExecutor(Coordinator):
    """Execute an arbitrary agent graph.

    Supports linear pipelines, parallel fan-out/fan-in, dynamic expansion
    (plan-execute), and any combination thereof — all driven by a single
    declarative GraphDef.
    """

    def __init__(self, graph: GraphDef):
        super().__init__(graph.name)
        self.graph = graph

    def _run(self, task: str) -> CoordinatorResult:
        """Execute the graph with parallel group detection."""
        log = StepLogger(self.name)
        context_id = uuid.uuid4().hex[:12]
        steps: list[AgentResult] = []

        order = _topo_sort(self.graph)
        groups = _parallel_groups(self.graph, order)
        log.info(f"execution plan: {' -> '.join([str(g) for g in groups])}")

        completed: dict[str, list[TaskEnvelope]] = {}
        step_counter = 0
        total = len(order)
        failed = False

        for group in groups:
            if failed:
                break

            if len(group) == 1:
                node_id = group[0]
                node = self.graph.nodes[node_id]

                # Handle dynamic nodes (plan-execute pattern)
                if node.type == "dynamic":
                    expanded = self._run_dynamic(
                        node, task,
                        _get_upstream_envelopes(
                            self.graph, node_id, task, context_id, completed,
                        ),
                        context_id, log,
                    )
                    completed[node_id] = expanded
                    for env in expanded:
                        if env.result:
                            steps.append(env.result)
                    continue

                # Regular node
                upstream_envelopes = _get_upstream_envelopes(
                    self.graph, node_id, task, context_id, completed,
                )
                context = _build_context(
                    self.graph.upstream(node_id), completed,
                )

                step_counter += 1
                log.start(step_counter, total, node_id)

                agent = _node_to_agent(node)
                result = agent.run(task, context=context)
                result.step_label = node_id
                steps.append(result)

                env = _make_envelope(
                    context_id, task, context, node_id, upstream_envelopes,
                )

                if result.error:
                    log.error(step_counter, total, node_id, result.error)
                    env.mark_failed(result)
                    completed[node_id] = [env]
                    failed = True
                    break

                log.done(step_counter, total, node_id, len(result.output))
                env.mark_completed(result)
                completed[node_id] = [env]

            else:
                # Parallel group — run concurrently
                log.info(f"parallel group: {group}")

                def run_node(nid: str) -> tuple[str, AgentResult, TaskEnvelope]:
                    n = self.graph.nodes[nid]
                    ue = _get_upstream_envelopes(
                        self.graph, nid, task, context_id, completed,
                    )
                    ctx = _build_context(self.graph.upstream(nid), completed)
                    a = _node_to_agent(n)
                    r = a.run(task, context=ctx)
                    r.step_label = nid
                    e = _make_envelope(context_id, task, ctx, nid, ue)
                    if r.error:
                        e.mark_failed(r)
                    else:
                        e.mark_completed(r)
                    return nid, r, e

                with ThreadPoolExecutor(max_workers=len(group)) as pool:
                    futures = {
                        pool.submit(run_node, nid): nid for nid in group
                    }
                    for future in as_completed(futures):
                        nid, result, env = future.result()
                        step_counter += 1
                        steps.append(result)
                        completed[nid] = [env]

                        if result.error:
                            log.error(step_counter, total, nid, result.error)
                            failed = True
                        else:
                            log.done(
                                step_counter, total, nid, len(result.output),
                            )

        return CoordinatorResult(
            steps=steps,
            metadata={"pattern": "graph", "graph_name": self.graph.name},
        )

    def _run_dynamic(
        self,
        node: NodeDef,
        task: str,
        upstream_envelopes: list[TaskEnvelope],
        context_id: str,
        log: StepLogger,
    ) -> list[TaskEnvelope]:
        """Execute a dynamic node: LLM call -> parse -> expand downstream."""
        llm = node.llm_call
        prompt = llm.prompt.replace("{{task}}", task)

        log.info(f"dynamic node {node.id!r}: calling LLM...")
        resp = backend_call(
            prompt,
            backend=llm.backend,
            model=llm.model,
            full_auto=llm.full_auto,
        )

        # Apply transform
        transform = get_transform(node.transform or "parse_list")
        items = transform(resp.text)
        log.info(f"dynamic node {node.id!r}: expanded to {len(items)} items")

        # Find downstream node(s) for this dynamic node
        downstream_edges = self.graph.downstream(node.id)
        downstream_ids = [
            e.target for e in downstream_edges if e.target != "_output"
        ]

        if not downstream_ids:
            # Dynamic node outputs directly — wrap items as envelopes
            envelopes = []
            for item in items:
                env = TaskEnvelope(
                    context_id=context_id,
                    task=item,
                    node_id=node.id,
                )
                env.state = TaskState.COMPLETED
                envelopes.append(env)
            return envelopes

        # Execute downstream node for each expanded item
        target_id = downstream_ids[0]
        target_node = self.graph.nodes[target_id]
        agent = _node_to_agent(target_node)

        # Determine context policy from the edge
        edge_policy = downstream_edges[0].context_policy
        envelopes: list[TaskEnvelope] = []
        context = ""

        if node.expand == ExpandMode.SEQUENTIAL:
            for i, item in enumerate(items):
                log.start(i + 1, len(items), f"{target_id} ({item[:50]})")
                result = agent.run(item, context=context)
                result.step_label = f"{target_id}-{i+1}"

                env = TaskEnvelope(
                    context_id=context_id,
                    task=item,
                    context=context,
                    node_id=target_id,
                )

                if result.error:
                    log.error(i + 1, len(items), target_id, result.error)
                    env.mark_failed(result)
                    envelopes.append(env)
                    break

                log.done(i + 1, len(items), target_id, len(result.output))
                env.mark_completed(result)
                envelopes.append(env)

                # Update context per policy
                if edge_policy == ContextPolicy.ACCUMULATE:
                    context += f"\n\nCompleted: {item}\nResult: {result.output}"
                elif edge_policy == ContextPolicy.REPLACE:
                    context = result.output

        elif node.expand == ExpandMode.PARALLEL:
            def run_item(item: str, idx: int):
                r = agent.run(item, context="")
                r.step_label = f"{target_id}-{idx+1}"
                e = TaskEnvelope(
                    context_id=context_id, task=item, node_id=target_id,
                )
                if r.error:
                    e.mark_failed(r)
                else:
                    e.mark_completed(r)
                return e

            with ThreadPoolExecutor(max_workers=len(items)) as pool:
                futures = [
                    pool.submit(run_item, item, i)
                    for i, item in enumerate(items)
                ]
                for future in as_completed(futures):
                    envelopes.append(future.result())

        return envelopes


# ── Helpers ──────────────────────────────────────────────────────────


def _node_to_agent(node: NodeDef) -> Agent:
    """Convert a NodeDef to an Agent instance."""
    return Agent(
        name=node.id,
        role=node.role,
        instruction=node.instruction,
        full_auto=node.full_auto,
        backend=node.backend,
        model=node.model,
    )


def _make_envelope(
    context_id: str,
    task: str,
    context: str,
    node_id: str,
    upstream_envelopes: list[TaskEnvelope],
) -> TaskEnvelope:
    """Create a new TaskEnvelope with provenance."""
    return TaskEnvelope(
        context_id=context_id,
        task=task,
        context=context,
        node_id=node_id,
        parent_task_ids=[e.task_id for e in upstream_envelopes],
    )


def _get_upstream_envelopes(
    graph: GraphDef,
    node_id: str,
    task: str,
    context_id: str,
    completed: dict[str, list[TaskEnvelope]],
) -> list[TaskEnvelope]:
    """Collect upstream envelopes for a node."""
    envelopes: list[TaskEnvelope] = []
    for edge in graph.upstream(node_id):
        if edge.source == "_input":
            env = TaskEnvelope(
                context_id=context_id,
                task=task,
                node_id="_input",
            )
            env.state = TaskState.COMPLETED
            envelopes.append(env)
        elif edge.source in completed:
            envelopes.extend(completed[edge.source])
    return envelopes


def _build_context(
    edges: list,
    completed: dict[str, list[TaskEnvelope]],
) -> str:
    """Build context string based on edge policies."""
    if not edges:
        return ""

    # Gather upstream outputs grouped by source
    source_outputs: dict[str, list[str]] = {}
    for edge in edges:
        if edge.source == "_input":
            continue
        if edge.source in completed:
            outputs = []
            for env in completed[edge.source]:
                if env.result and env.result.output:
                    outputs.append(env.result.output)
            if outputs:
                source_outputs[edge.source] = outputs

    if not source_outputs:
        return ""

    # Use the first non-_input edge's policy as representative
    policy = ContextPolicy.REPLACE
    for edge in edges:
        if edge.source != "_input":
            policy = edge.context_policy
            break

    if policy == ContextPolicy.NONE:
        return ""

    if policy == ContextPolicy.REPLACE:
        # Use the last upstream output only
        all_outputs = []
        for outputs in source_outputs.values():
            all_outputs.extend(outputs)
        return all_outputs[-1] if all_outputs else ""

    if policy == ContextPolicy.ACCUMULATE:
        # Build growing context from all upstream envelopes
        parts = []
        for source_id, outputs in source_outputs.items():
            if source_id in completed:
                for env in completed[source_id]:
                    if env.result and env.result.output:
                        label = env.task[:80] if env.task else env.node_id
                        parts.append(
                            f"Completed: {label}\nResult: {env.result.output}"
                        )
        return "\n\n".join(parts)

    if policy == ContextPolicy.AGGREGATE:
        # Collect all upstream outputs, joined with labels
        all_parts = []
        for source_id, outputs in source_outputs.items():
            for output in outputs:
                all_parts.append(f"[{source_id}]:\n{output}")
        return "\n\n---\n\n".join(all_parts)

    return ""


def _topo_sort(graph: GraphDef) -> list[str]:
    """Topological sort of graph nodes (Kahn's algorithm)."""
    in_degree: dict[str, int] = {nid: 0 for nid in graph.nodes}
    adjacency: dict[str, list[str]] = {nid: [] for nid in graph.nodes}

    for edge in graph.edges:
        if edge.source in graph.nodes and edge.target in graph.nodes:
            adjacency[edge.source].append(edge.target)
            in_degree[edge.target] += 1

    queue = [nid for nid in graph.nodes if in_degree[nid] == 0]
    order: list[str] = []

    while queue:
        queue.sort()  # Deterministic ordering
        node = queue.pop(0)
        order.append(node)
        for neighbor in adjacency[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return order


def _parallel_groups(
    graph: GraphDef, order: list[str],
) -> list[list[str]]:
    """Group topologically sorted nodes into parallel execution groups.

    Nodes whose dependencies are all satisfied at the same time can run
    concurrently.
    """
    done: set[str] = set()
    groups: list[list[str]] = []
    remaining = list(order)

    while remaining:
        ready = []
        for nid in remaining:
            deps = {
                e.source for e in graph.upstream(nid)
                if e.source != "_input" and e.source in graph.nodes
            }
            if deps <= done:
                ready.append(nid)

        if not ready:
            break

        groups.append(ready)
        done.update(ready)
        for nid in ready:
            remaining.remove(nid)

    return groups

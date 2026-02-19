"""
YAML graph loading and validation.

Parses YAML graph definitions into GraphDef dataclasses,
validates references, detects cycles, and checks dynamic node config.
"""

import yaml

from src.graph.schema import (
    ContextPolicy,
    EdgeDef,
    ExpandMode,
    GraphDef,
    LLMCallDef,
    NodeDef,
)


def load_graph(path: str) -> GraphDef:
    """Load a graph definition from a YAML file.

    Args:
        path: Path to the YAML file.

    Returns:
        Validated GraphDef ready for execution.

    Raises:
        ValueError: If the graph definition is invalid.
        FileNotFoundError: If the YAML file doesn't exist.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return parse_graph(data)


def parse_graph(data: dict) -> GraphDef:
    """Parse a raw dict (from YAML or Python) into a validated GraphDef."""
    name = data.get("name", "unnamed")

    # Parse nodes
    nodes: dict[str, NodeDef] = {}
    for node_id, node_data in data.get("nodes", {}).items():
        nodes[node_id] = _parse_node(node_id, node_data)

    # Parse edges
    edges: list[EdgeDef] = []
    for edge_data in data.get("edges", []):
        edges.append(_parse_edge(edge_data))

    graph = GraphDef(name=name, nodes=nodes, edges=edges)
    _validate(graph)
    return graph


def _parse_node(node_id: str, data: dict) -> NodeDef:
    """Parse a single node definition."""
    llm_call = None
    if "llm_call" in data:
        lc = data["llm_call"]
        llm_call = LLMCallDef(
            backend=lc.get("backend", "codex"),
            prompt=lc.get("prompt", ""),
            model=lc.get("model", ""),
            full_auto=lc.get("full_auto", False),
        )

    expand = None
    if "expand" in data:
        expand = ExpandMode(data["expand"])

    return NodeDef(
        id=node_id,
        role=data.get("role", ""),
        backend=data.get("backend", "codex"),
        model=data.get("model", ""),
        full_auto=data.get("full_auto", False),
        instruction=data.get("instruction", ""),
        type=data.get("type", "agent"),
        expand=expand,
        llm_call=llm_call,
        transform=data.get("transform", ""),
    )


def _parse_edge(data: dict) -> EdgeDef:
    """Parse a single edge definition."""
    policy_str = data.get("context_policy", "replace")
    return EdgeDef(
        source=data["from"],
        target=data["to"],
        context_policy=ContextPolicy(policy_str),
    )


def _validate(graph: GraphDef) -> None:
    """Validate graph structure.

    Checks:
    1. All edge references point to existing nodes (or _input/_output)
    2. No cycles in the graph
    3. Dynamic nodes have required llm_call config
    4. At least one entry and one exit node
    """
    valid_ids = set(graph.nodes.keys()) | {"_input", "_output"}

    # Check edge references
    for edge in graph.edges:
        if edge.source not in valid_ids:
            raise ValueError(f"Edge references unknown source: {edge.source!r}")
        if edge.target not in valid_ids:
            raise ValueError(f"Edge references unknown target: {edge.target!r}")

    # Check entry/exit nodes exist
    if not graph.entry_nodes:
        raise ValueError("Graph has no entry nodes (no edges from _input)")
    if not graph.exit_nodes:
        raise ValueError("Graph has no exit nodes (no edges to _output)")

    # Check dynamic nodes
    for node_id, node in graph.nodes.items():
        if node.type == "dynamic":
            if not node.llm_call:
                raise ValueError(
                    f"Dynamic node {node_id!r} requires an llm_call definition"
                )
            if not node.expand:
                raise ValueError(
                    f"Dynamic node {node_id!r} requires an expand mode "
                    "(sequential or parallel)"
                )

    # Cycle detection (DFS on non-special nodes)
    adjacency: dict[str, list[str]] = {nid: [] for nid in graph.nodes}
    for edge in graph.edges:
        if edge.source in graph.nodes and edge.target in graph.nodes:
            adjacency[edge.source].append(edge.target)

    UNVISITED, IN_STACK, DONE = 0, 1, 2
    state: dict[str, int] = {nid: UNVISITED for nid in graph.nodes}

    def dfs(node: str) -> None:
        state[node] = IN_STACK
        for neighbor in adjacency[node]:
            if state[neighbor] == IN_STACK:
                raise ValueError(
                    f"Cycle detected in graph: ... -> {node} -> {neighbor} -> ..."
                )
            if state[neighbor] == UNVISITED:
                dfs(neighbor)
        state[node] = DONE

    for nid in graph.nodes:
        if state[nid] == UNVISITED:
            dfs(nid)

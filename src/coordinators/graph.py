"""
Graph Coordinator — convenience wrapper for loading and running graphs.

Accepts either a YAML path or a GraphDef, delegates to GraphExecutor.
"""

from src.graph.executor import GraphExecutor
from src.graph.loader import load_graph
from src.graph.schema import GraphDef


class GraphCoordinator(GraphExecutor):
    """Coordinator backed by a declarative graph (YAML or programmatic).

    Extends GraphExecutor with the ability to load from a YAML path.

    Usage:
        coord = GraphCoordinator("graphs/pipeline.yaml")
        result = coord.run("Your task here")

        # Or from a GraphDef:
        coord = GraphCoordinator(graph_def)
        result = coord.run("Your task here")
    """

    def __init__(self, source: str | GraphDef):
        if isinstance(source, str):
            graph_def = load_graph(source)
        else:
            graph_def = source
        super().__init__(graph_def)

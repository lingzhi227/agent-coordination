"""
Pipeline Coordinator.

Agent1 -> Agent2 -> Agent3 -> ... -> AgentN

Each agent receives the previous agent's output as context.
"""

from src.agent import Agent
from src.base import Coordinator, CoordinatorResult
from src.context import run_chain
from src.logging import StepLogger


class PipelineCoordinator(Coordinator):
    def __init__(self, agents: list[Agent]):
        super().__init__("pipeline")
        self.agents = agents

    def _run(self, task: str) -> CoordinatorResult:
        log = StepLogger(self.name)
        tasks = [task] * len(self.agents)
        steps = run_chain(self.agents, tasks, log, accumulate=False)
        return CoordinatorResult(steps=steps)

"""
Plan-Execute Coordinator.

A planner (LLM call) breaks a task into subtasks, then an executor agent
carries them out sequentially with accumulating context.
"""

from src import llm
from src.agent import Agent
from src.base import Coordinator, CoordinatorResult
from src.context import run_chain
from src.logging import StepLogger
from src.parsing import parse_list_response


class PlanExecuteCoordinator(Coordinator):
    def __init__(self, executor: Agent):
        super().__init__("plan-execute")
        self.executor = executor

    def _run(self, task: str) -> CoordinatorResult:
        log = StepLogger(self.name)

        # Generate plan
        log.info("generating plan...")
        plan = self._generate_plan(task)

        log.info(f"plan has {len(plan)} steps:")
        for i, step in enumerate(plan):
            print(f"  {i + 1}. {step}")

        # Execute plan
        steps = run_chain(
            [self.executor], plan, log, accumulate=True,
        )

        return CoordinatorResult(
            steps=steps,
            metadata={"plan": plan},
        )

    @staticmethod
    def _generate_plan(task: str) -> list[str]:
        prompt = (
            "Break the following task into 2-5 concrete subtasks. "
            "Return ONLY a JSON array of strings, no other text.\n\n"
            f"Task: {task}"
        )
        resp = llm.call(prompt)
        return parse_list_response(resp.text)

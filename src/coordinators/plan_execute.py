"""
Plan-Execute Coordinator.

A planner (LLM call) breaks a task into subtasks, then an executor agent
carries them out sequentially with accumulating context.
"""

from src.backends import Backend, call as backend_call
from src.agent import Agent
from src.base import Coordinator, CoordinatorResult
from src.context import run_chain
from src.logging import StepLogger
from src.parsing import parse_list_response


class PlanExecuteCoordinator(Coordinator):
    def __init__(
        self,
        executor: Agent,
        planning_backend: Backend | str | None = None,
    ):
        super().__init__("plan-execute")
        self.executor = executor
        # Use executor's backend for planning by default
        self.planning_backend = planning_backend or executor.backend

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
        for i, step in enumerate(steps):
            step.step_label = f"step-{i+1}"

        return CoordinatorResult(
            steps=steps,
            metadata={"plan": plan, "pattern": "plan-execute"},
        )

    def _generate_plan(self, task: str) -> list[str]:
        prompt = (
            "Break the following task into 2-5 concrete subtasks. "
            "Return ONLY a JSON array of strings, no other text.\n\n"
            f"Task: {task}"
        )
        resp = backend_call(prompt, backend=self.planning_backend)
        return parse_list_response(resp.text)

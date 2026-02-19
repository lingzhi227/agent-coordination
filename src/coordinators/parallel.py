"""
Parallel Coordinator with Central Store.

Multiple agents work concurrently on independent subtasks.
A synthesizer agent combines all results.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

from src import llm
from src.agent import Agent, AgentResult
from src.base import Coordinator, CoordinatorResult
from src.logging import StepLogger
from src.parsing import parse_list_response


@dataclass
class CentralStore:
    """Thread-safe central storage for agent results."""

    results: dict[str, AgentResult] = field(default_factory=dict)

    def put(self, key: str, result: AgentResult):
        self.results[key] = result

    def get_all(self) -> dict[str, AgentResult]:
        return dict(self.results)

    def summary(self) -> str:
        parts = []
        for key, r in self.results.items():
            parts.append(f"[{key}] ({r.agent_name}):\n{r.output}")
        return "\n\n---\n\n".join(parts)


class ParallelCoordinator(Coordinator):
    def __init__(
        self,
        workers: list[Agent],
        synthesizer: Agent | None = None,
        subtasks: list[str] | None = None,
    ):
        super().__init__("parallel")
        self.workers = workers
        self.synthesizer = synthesizer
        self.subtasks = subtasks

    def _run(self, task: str) -> CoordinatorResult:
        log = StepLogger(self.name)
        store = CentralStore()

        # Split task into subtasks (or use pre-defined ones)
        if self.subtasks is not None:
            log.info(f"using {len(self.subtasks)} pre-defined subtasks...")
            subtasks = list(self.subtasks)
        else:
            log.info(f"splitting task for {len(self.workers)} agents...")
            subtasks = self._split_task(task, len(self.workers))

        if len(subtasks) < len(self.workers):
            subtasks.extend(
                ["continue the remaining work"] * (len(self.workers) - len(subtasks))
            )

        log.info("subtasks:")
        for i, st in enumerate(subtasks):
            print(f"  {i + 1}. {st}")

        # Execute in parallel
        all_steps: list[AgentResult] = []

        def run_agent(
            agent: Agent, subtask: str, key: str,
        ) -> tuple[str, AgentResult]:
            print(f"  [{key}] {agent.name}: starting...")
            r = agent.run(subtask)
            print(f"  [{key}] {agent.name}: done ({len(r.output)} chars)")
            return key, r

        log.info("executing in parallel...")
        with ThreadPoolExecutor(max_workers=len(self.workers)) as pool:
            futures = {
                pool.submit(run_agent, agent, subtask, f"worker-{i+1}"): i
                for i, (agent, subtask) in enumerate(zip(self.workers, subtasks))
            }
            for future in as_completed(futures):
                key, agent_result = future.result()
                store.put(key, agent_result)
                all_steps.append(agent_result)

        # Synthesize
        if self.synthesizer and store.results:
            log.info("synthesizing results...")
            all_context = store.summary()
            synth_result = self.synthesizer.run(
                f"Synthesize the following parallel results into a coherent answer for: {task}",
                context=all_context,
            )
            all_steps.append(synth_result)
            synthesis = synth_result.output
            log.info(f"synthesis done ({len(synthesis)} chars)")
        else:
            synthesis = store.summary()

        return CoordinatorResult(
            steps=all_steps,
            metadata={"store": store, "synthesis": synthesis},
        )

    @staticmethod
    def _split_task(task: str, n: int) -> list[str]:
        prompt = (
            f"Split the following task into exactly {n} independent subtasks "
            "that can be done in parallel. "
            "Return ONLY a JSON array of strings, no other text.\n\n"
            f"Task: {task}"
        )
        resp = llm.call(prompt)
        items = parse_list_response(resp.text)
        return items[:n]

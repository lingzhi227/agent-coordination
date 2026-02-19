"""
Pattern 3: Parallel Execution with Central Store

Multiple agents run in parallel on independent subtasks.
Results are collected in a central store.
A final synthesizer agent reads all results and produces the output.

  [Agent1(subtask1)] ──┐
  [Agent2(subtask2)] ──┼──> CentralStore ──> Synthesizer -> final output
  [Agent3(subtask3)] ──┘
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from src.agent import Agent, AgentResult
from src import llm


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


@dataclass
class ParallelResult:
    store: CentralStore = field(default_factory=CentralStore)
    synthesis: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def final_output(self) -> str:
        return self.synthesis

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def _split_task(task: str, n: int) -> list[str]:
    """Ask the LLM to split a task into N independent subtasks."""
    prompt = (
        f"Split the following task into exactly {n} independent subtasks "
        "that can be done in parallel. "
        "Return ONLY a JSON array of strings, no other text.\n\n"
        f"Task: {task}"
    )
    resp = llm.call(prompt)
    text = resp.text.strip()

    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        return json.loads(text[start : end + 1])

    lines = [line.strip("- ").strip() for line in text.splitlines() if line.strip()]
    return lines[:n]


def run(
    agents: list[Agent],
    task: str,
    synthesizer: Agent | None = None,
) -> ParallelResult:
    """Run agents in parallel, collect results, then synthesize."""
    result = ParallelResult()

    # Split task into subtasks
    print(f"[coordinator] splitting task for {len(agents)} agents...")
    subtasks = _split_task(task, len(agents))

    if len(subtasks) < len(agents):
        subtasks.extend(["continue the remaining work"] * (len(agents) - len(subtasks)))

    print(f"[coordinator] subtasks:")
    for i, st in enumerate(subtasks):
        print(f"  {i + 1}. {st}")

    # Execute in parallel
    def run_agent(agent: Agent, subtask: str, key: str) -> tuple[str, AgentResult]:
        print(f"  [{key}] {agent.name}: starting...")
        r = agent.run(subtask)
        print(f"  [{key}] {agent.name}: done ({len(r.output)} chars)")
        return key, r

    print("[coordinator] executing in parallel...")
    with ThreadPoolExecutor(max_workers=len(agents)) as pool:
        futures = {
            pool.submit(run_agent, agent, subtask, f"worker-{i+1}"): i
            for i, (agent, subtask) in enumerate(zip(agents, subtasks))
        }
        for future in as_completed(futures):
            key, agent_result = future.result()
            result.store.put(key, agent_result)
            if agent_result.error:
                result.errors.append(f"{key}: {agent_result.error}")

    # Synthesize
    if synthesizer and result.store.results:
        print("[synthesizer] combining results...")
        all_context = result.store.summary()
        synth_result = synthesizer.run(
            f"Synthesize the following parallel results into a coherent answer for: {task}",
            context=all_context,
        )
        result.synthesis = synth_result.output
        if synth_result.error:
            result.errors.append(f"synthesizer: {synth_result.error}")
        print(f"[synthesizer] done ({len(result.synthesis)} chars)")
    else:
        result.synthesis = result.store.summary()

    return result

"""
Pattern 2: Plan-Execute

A planner agent breaks a task into subtasks, then executor agents
carry them out one by one. The planner sees all completed results
and can adjust remaining steps.

  Planner -> [subtask1, subtask2, ...]
  Executor(subtask1) -> result1
  Executor(subtask2, context=result1) -> result2
  ...
"""

import json
from dataclasses import dataclass, field
from src.agent import Agent, AgentResult
from src import llm


@dataclass
class PlanExecuteResult:
    plan: list[str] = field(default_factory=list)
    step_results: list[AgentResult] = field(default_factory=list)

    @property
    def final_output(self) -> str:
        outputs = [r.output for r in self.step_results if r.output]
        return "\n\n---\n\n".join(outputs)

    @property
    def success(self) -> bool:
        return all(r.error is None for r in self.step_results)


def _generate_plan(task: str) -> list[str]:
    """Ask the LLM to break a task into ordered subtasks."""
    prompt = (
        "Break the following task into 2-5 concrete subtasks. "
        "Return ONLY a JSON array of strings, no other text.\n\n"
        f"Task: {task}"
    )
    resp = llm.call(prompt)
    text = resp.text.strip()

    # Try to extract JSON array from response
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        return json.loads(text[start : end + 1])

    # Fallback: split by newlines
    return [line.strip("- ").strip() for line in text.splitlines() if line.strip()]


def run(executor: Agent, task: str) -> PlanExecuteResult:
    """Plan subtasks, then execute them sequentially with accumulating context."""
    print("[planner] generating plan...")
    plan = _generate_plan(task)
    result = PlanExecuteResult(plan=plan)

    print(f"[planner] plan has {len(plan)} steps:")
    for i, step in enumerate(plan):
        print(f"  {i + 1}. {step}")

    completed_context = ""

    for i, subtask in enumerate(plan):
        step_label = f"[executor step {i + 1}/{len(plan)}]"
        print(f"{step_label} {subtask}")

        step_result = executor.run(subtask, context=completed_context)
        result.step_results.append(step_result)

        if step_result.error:
            print(f"{step_label} ERROR - {step_result.error}")
            break

        print(f"{step_label} done ({len(step_result.output)} chars)")
        completed_context += f"\n\nCompleted: {subtask}\nResult: {step_result.output}"

    return result

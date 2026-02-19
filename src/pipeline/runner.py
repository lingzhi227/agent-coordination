"""
Pattern 1: Pipeline

Agent1 -> Agent2 -> Agent3 -> ... -> AgentN

Each agent receives the previous agent's output as context.
The final agent's output is the pipeline result.
"""

from dataclasses import dataclass, field
from src.agent import Agent, AgentResult


@dataclass
class PipelineResult:
    steps: list[AgentResult] = field(default_factory=list)

    @property
    def final_output(self) -> str:
        return self.steps[-1].output if self.steps else ""

    @property
    def success(self) -> bool:
        return all(s.error is None for s in self.steps)


def run(agents: list[Agent], task: str) -> PipelineResult:
    """Run agents sequentially, piping each output to the next."""
    result = PipelineResult()
    context = ""

    for i, agent in enumerate(agents):
        step_label = f"[step {i + 1}/{len(agents)}] {agent.name}"
        print(f"{step_label}: starting...")

        step_result = agent.run(task, context=context)
        result.steps.append(step_result)

        if step_result.error:
            print(f"{step_label}: ERROR - {step_result.error}")
            break

        print(f"{step_label}: done ({len(step_result.output)} chars)")
        context = step_result.output

    return result

"""
Sequential execution with context chaining.

Shared by pipeline (accumulate=False) and plan-execute (accumulate=True).
"""

from src.agent import Agent, AgentResult
from src.logging import StepLogger


def run_chain(
    agents: list[Agent],
    tasks: list[str],
    log: StepLogger,
    *,
    accumulate: bool = False,
) -> list[AgentResult]:
    """Run agents sequentially, passing context forward.

    Args:
        agents: Agents to execute. If len(agents) < len(tasks), the last agent
                is reused for remaining tasks (plan-execute pattern).
        tasks: One task string per step.
        log: Logger for progress output.
        accumulate: If False (pipeline), context = previous output only.
                    If True (plan-execute), context grows with each step.

    Returns:
        List of AgentResult for each completed step.
    """
    results: list[AgentResult] = []
    context = ""
    total = len(tasks)

    for i, task in enumerate(tasks):
        agent = agents[i] if i < len(agents) else agents[-1]
        step_num = i + 1

        log.start(step_num, total, agent.name)

        step_result = agent.run(task, context=context)
        results.append(step_result)

        if step_result.error:
            log.error(step_num, total, agent.name, step_result.error)
            break

        log.done(step_num, total, agent.name, len(step_result.output))

        if accumulate:
            context += f"\n\nCompleted: {task}\nResult: {step_result.output}"
        else:
            context = step_result.output

    return results

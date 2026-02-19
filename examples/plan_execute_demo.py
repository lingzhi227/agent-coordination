#!/usr/bin/env python3
"""
Demo: Plan-Execute coordination pattern.

A planner breaks the task into subtasks, then an executor agent
handles them sequentially with accumulating context.
"""

import sys
sys.path.insert(0, ".")

from src.agent import Agent
from src.plan_execute.runner import run


def main():
    executor = Agent(
        name="executor",
        role="You are a skilled software engineer. Complete the assigned subtask thoroughly. Use the context of previously completed work to stay consistent.",
    )

    task = "Design a simple REST API for a todo-list app: define the endpoints, data models, and write example request/response for each endpoint"

    print(f"=== Plan-Execute Demo ===")
    print(f"Task: {task}")
    print()

    result = run(executor, task)

    print(f"\n{'='*60}")
    print(f"Plan-Execute {'succeeded' if result.success else 'FAILED'}")
    print(f"Plan steps: {len(result.plan)}")
    print(f"Completed: {len(result.step_results)}")
    print(f"\nFinal output:\n{result.final_output}")


if __name__ == "__main__":
    main()

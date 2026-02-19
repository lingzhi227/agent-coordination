#!/usr/bin/env python3
"""
Demo: Parallel execution with central store coordination pattern.

Multiple agents work on independent subtasks concurrently.
A synthesizer combines all results.
"""

import sys
sys.path.insert(0, ".")

from src.agent import Agent
from src.coordinators import ParallelCoordinator


def main():
    workers = [
        Agent(
            name="backend-expert",
            role="You are a backend architecture expert. Focus on server-side design, APIs, and databases.",
        ),
        Agent(
            name="frontend-expert",
            role="You are a frontend architecture expert. Focus on UI components, state management, and user experience.",
        ),
        Agent(
            name="devops-expert",
            role="You are a DevOps expert. Focus on deployment, CI/CD, monitoring, and infrastructure.",
        ),
    ]

    synthesizer = Agent(
        name="tech-lead",
        role="You are a tech lead. Combine the inputs from backend, frontend, and devops experts into a coherent, unified technical plan.",
    )

    task = "Design the architecture for a real-time collaborative document editor"

    print(f"=== Parallel Execution Demo ===")
    print(f"Task: {task}")
    print(f"Workers: {', '.join(a.name for a in workers)}")
    print()

    coordinator = ParallelCoordinator(workers, synthesizer=synthesizer)
    result = coordinator.run(task)

    store = result.metadata["store"]
    print(f"\n{'='*60}")
    print(f"Parallel {'succeeded' if result.success else 'FAILED'}")
    print(f"Workers completed: {len(store.results)}")
    print(f"Elapsed: {result.elapsed:.1f}s")
    print(f"\nSynthesized output:\n{result.metadata['synthesis']}")


if __name__ == "__main__":
    main()

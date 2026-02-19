#!/usr/bin/env python3
"""
Demo: Pipeline coordination pattern.

Example: Research -> Draft -> Review pipeline for writing an article.
"""

import sys
sys.path.insert(0, ".")

from src.agent import Agent
from src.coordinators import PipelineCoordinator


def main():
    agents = [
        Agent(
            name="researcher",
            role="You are a research agent. Gather key facts and data points about the given topic. Output a structured list of findings.",
        ),
        Agent(
            name="writer",
            role="You are a writer agent. Using the research provided as context, write a clear and concise draft article. Keep it under 500 words.",
        ),
        Agent(
            name="reviewer",
            role="You are a review agent. Review the draft for accuracy, clarity, and completeness. Output the final polished version with any corrections.",
        ),
    ]

    task = "Write a brief article about how multi-agent AI systems coordinate work"

    print(f"=== Pipeline Demo ===")
    print(f"Task: {task}")
    print(f"Agents: {' -> '.join(a.name for a in agents)}")
    print()

    coordinator = PipelineCoordinator(agents)
    result = coordinator.run(task)

    print(f"\n{'='*60}")
    print(f"Pipeline {'succeeded' if result.success else 'FAILED'}")
    print(f"Steps completed: {len(result.steps)}")
    print(f"Elapsed: {result.elapsed:.1f}s")
    print(f"\nFinal output:\n{result.final_output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Integration test: verify the graph engine replicates all three coordination patterns.

Runs each pattern using both:
  1. The programmatic API (factory functions)
  2. YAML graph definitions

All agents use claude_code backend (Claude Sonnet) for testing.
"""

import os
import sys
import time

# Allow nested Claude Code sessions (we're running inside Claude Code)
os.environ.pop("CLAUDECODE", None)

sys.path.insert(0, ".")

from src.agent import Agent
from src.graph import (
    GraphExecutor,
    load_graph,
    parse_graph,
    pipeline,
    parallel,
    plan_execute,
)
from src.coordinators.graph import GraphCoordinator

BACKEND = "claude_code"
MODEL = "haiku"

# Use deliberately short tasks to keep cost/time low
PIPELINE_TASK = "List 3 benefits of unit testing in software development"
PARALLEL_TASK = "What are the key considerations when designing a REST API?"
PLAN_EXEC_TASK = "Outline the steps to set up a basic Python web server with Flask"


def header(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def check(label: str, condition: bool, detail: str = ""):
    status = "PASS" if condition else "FAIL"
    msg = f"  [{status}] {label}"
    if detail:
        msg += f"  ({detail})"
    print(msg)
    return condition


# ── 1. Pipeline ──────────────────────────────────────────────────────

def test_pipeline_programmatic():
    header("Pipeline — Programmatic API")

    agents = [
        Agent(name="researcher", role="You are a research agent. List key facts about the topic.", backend=BACKEND, model=MODEL),
        Agent(name="writer", role="You are a writer. Rewrite the research as a concise paragraph.", backend=BACKEND, model=MODEL),
        Agent(name="reviewer", role="You are a reviewer. Polish the text for clarity and return the final version.", backend=BACKEND, model=MODEL),
    ]

    executor = pipeline(agents)
    print(f"Graph: {executor.graph.name}")
    print(f"Nodes: {list(executor.graph.nodes.keys())}")
    print(f"Edges: {len(executor.graph.edges)}")
    print(f"Entry: {executor.graph.entry_nodes}")
    print(f"Exit:  {executor.graph.exit_nodes}")
    print()

    t0 = time.time()
    result = executor.run(PIPELINE_TASK)
    elapsed = time.time() - t0

    passed = all([
        check("result is successful", result.success, f"errors={result.errors}"),
        check("3 steps completed", len(result.steps) == 3, f"got {len(result.steps)}"),
        check("steps in correct order", [s.step_label for s in result.steps] == ["researcher", "writer", "reviewer"]),
        check("each step has output", all(len(s.output) > 0 for s in result.steps)),
        check("final_output is non-empty", len(result.final_output) > 50, f"{len(result.final_output)} chars"),
        check("metadata has graph pattern", result.metadata.get("pattern") == "graph"),
    ])

    print(f"\n  Elapsed: {elapsed:.1f}s")
    print(f"  Step outputs: {[len(s.output) for s in result.steps]} chars")
    print(f"  Final output preview: {result.final_output[:200]}...")
    return passed, result


def test_pipeline_yaml():
    header("Pipeline — YAML (via GraphCoordinator)")

    # Build a test YAML that uses claude_code for all nodes
    yaml_data = {
        "name": "test-pipeline",
        "nodes": {
            "researcher": {
                "role": "You are a research agent. List key facts about the topic.",
                "backend": BACKEND,
                "model": MODEL,
            },
            "writer": {
                "role": "You are a writer. Rewrite the research as a concise paragraph.",
                "backend": BACKEND,
                "model": MODEL,
            },
            "reviewer": {
                "role": "You are a reviewer. Polish the text and return the final version.",
                "backend": BACKEND,
                "model": MODEL,
            },
        },
        "edges": [
            {"from": "_input", "to": "researcher"},
            {"from": "researcher", "to": "writer", "context_policy": "replace"},
            {"from": "writer", "to": "reviewer", "context_policy": "replace"},
            {"from": "reviewer", "to": "_output"},
        ],
    }

    graph_def = parse_graph(yaml_data)
    executor = GraphExecutor(graph_def)

    t0 = time.time()
    result = executor.run(PIPELINE_TASK)
    elapsed = time.time() - t0

    passed = all([
        check("result is successful", result.success),
        check("3 steps completed", len(result.steps) == 3, f"got {len(result.steps)}"),
        check("final_output is non-empty", len(result.final_output) > 50),
    ])

    print(f"\n  Elapsed: {elapsed:.1f}s")
    print(f"  Final output preview: {result.final_output[:200]}...")
    return passed, result


# ── 2. Parallel ──────────────────────────────────────────────────────

def test_parallel_programmatic():
    header("Parallel — Programmatic API")

    workers = [
        Agent(name="backend_expert", role="You are a backend expert. Give 2-3 key backend considerations.", backend=BACKEND, model=MODEL),
        Agent(name="frontend_expert", role="You are a frontend expert. Give 2-3 key frontend considerations.", backend=BACKEND, model=MODEL),
    ]
    synth = Agent(name="synthesizer", role="You are a tech lead. Combine expert inputs into a unified summary.", backend=BACKEND, model=MODEL)

    executor = parallel(workers, synthesizer=synth)
    print(f"Graph: {executor.graph.name}")
    print(f"Nodes: {list(executor.graph.nodes.keys())}")
    print(f"Entry: {executor.graph.entry_nodes}")
    print(f"Exit:  {executor.graph.exit_nodes}")
    print()

    t0 = time.time()
    result = executor.run(PARALLEL_TASK)
    elapsed = time.time() - t0

    step_labels = [s.step_label for s in result.steps]

    passed = all([
        check("result is successful", result.success, f"errors={result.errors}"),
        check("3 steps completed", len(result.steps) == 3, f"got {len(result.steps)}"),
        check("both experts ran", "backend_expert" in step_labels and "frontend_expert" in step_labels),
        check("synthesizer ran last", result.steps[-1].step_label == "synthesizer"),
        check("each step has output", all(len(s.output) > 0 for s in result.steps)),
        check("final_output is non-empty", len(result.final_output) > 50, f"{len(result.final_output)} chars"),
    ])

    print(f"\n  Elapsed: {elapsed:.1f}s")
    print(f"  Step labels: {step_labels}")
    print(f"  Step outputs: {[len(s.output) for s in result.steps]} chars")
    print(f"  Final output preview: {result.final_output[:200]}...")
    return passed, result


def test_parallel_yaml():
    header("Parallel — YAML (via parse_graph)")

    yaml_data = {
        "name": "test-parallel",
        "nodes": {
            "backend_expert": {
                "role": "You are a backend expert. Give 2-3 key backend considerations.",
                "backend": BACKEND,
                "model": MODEL,
            },
            "frontend_expert": {
                "role": "You are a frontend expert. Give 2-3 key frontend considerations.",
                "backend": BACKEND,
                "model": MODEL,
            },
            "synthesizer": {
                "role": "You are a tech lead. Combine expert inputs into a unified summary.",
                "backend": BACKEND,
                "model": MODEL,
            },
        },
        "edges": [
            {"from": "_input", "to": "backend_expert", "context_policy": "none"},
            {"from": "_input", "to": "frontend_expert", "context_policy": "none"},
            {"from": "backend_expert", "to": "synthesizer", "context_policy": "aggregate"},
            {"from": "frontend_expert", "to": "synthesizer", "context_policy": "aggregate"},
            {"from": "synthesizer", "to": "_output"},
        ],
    }

    graph_def = parse_graph(yaml_data)
    executor = GraphExecutor(graph_def)

    t0 = time.time()
    result = executor.run(PARALLEL_TASK)
    elapsed = time.time() - t0

    passed = all([
        check("result is successful", result.success),
        check("3 steps completed", len(result.steps) == 3, f"got {len(result.steps)}"),
        check("synthesizer has aggregated context", result.steps[-1].step_label == "synthesizer"),
        check("final_output is non-empty", len(result.final_output) > 50),
    ])

    print(f"\n  Elapsed: {elapsed:.1f}s")
    print(f"  Final output preview: {result.final_output[:200]}...")
    return passed, result


# ── 3. Plan-Execute ──────────────────────────────────────────────────

def test_plan_execute_programmatic():
    header("Plan-Execute — Programmatic API")

    executor_agent = Agent(
        name="executor",
        role="You are a skilled engineer. Complete the assigned subtask. Be concise (2-3 sentences).",
        backend=BACKEND,
        model=MODEL,
    )

    executor = plan_execute(executor_agent, planning_backend=BACKEND)
    print(f"Graph: {executor.graph.name}")
    print(f"Nodes: {list(executor.graph.nodes.keys())}")
    print(f"Dynamic node: planner (expand=sequential)")
    print()

    t0 = time.time()
    result = executor.run(PLAN_EXEC_TASK)
    elapsed = time.time() - t0

    passed = all([
        check("result is successful", result.success, f"errors={result.errors}"),
        check("at least 2 steps completed", len(result.steps) >= 2, f"got {len(result.steps)}"),
        check("each step has output", all(len(s.output) > 0 for s in result.steps)),
        check("final_output is non-empty", len(result.final_output) > 20, f"{len(result.final_output)} chars"),
    ])

    print(f"\n  Elapsed: {elapsed:.1f}s")
    print(f"  Steps: {len(result.steps)}")
    print(f"  Step labels: {[s.step_label for s in result.steps]}")
    print(f"  Final output preview: {result.final_output[:200]}...")
    return passed, result


def test_plan_execute_yaml():
    header("Plan-Execute — YAML (via parse_graph)")

    yaml_data = {
        "name": "test-plan-execute",
        "nodes": {
            "planner": {
                "type": "dynamic",
                "expand": "sequential",
                "llm_call": {
                    "backend": BACKEND,
                    "model": MODEL,
                    "prompt": (
                        "Break the following task into 2-3 concrete subtasks. "
                        "Return ONLY a JSON array of strings, no other text.\n\n"
                        "Task: {{task}}"
                    ),
                },
                "transform": "parse_list",
            },
            "executor": {
                "role": "You are a skilled engineer. Complete the assigned subtask. Be concise (2-3 sentences).",
                "backend": BACKEND,
                "model": MODEL,
            },
        },
        "edges": [
            {"from": "_input", "to": "planner"},
            {"from": "planner", "to": "executor", "context_policy": "accumulate"},
            {"from": "executor", "to": "_output"},
        ],
    }

    graph_def = parse_graph(yaml_data)
    executor = GraphExecutor(graph_def)

    t0 = time.time()
    result = executor.run(PLAN_EXEC_TASK)
    elapsed = time.time() - t0

    passed = all([
        check("result is successful", result.success),
        check("at least 2 steps completed", len(result.steps) >= 2, f"got {len(result.steps)}"),
        check("final_output is non-empty", len(result.final_output) > 20),
    ])

    print(f"\n  Elapsed: {elapsed:.1f}s")
    print(f"  Steps: {len(result.steps)}")
    print(f"  Final output preview: {result.final_output[:200]}...")
    return passed, result


# ── Main ─────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  Graph Engine Integration Tests — All Three Patterns")
    print(f"  Backend: {BACKEND} | Model: {MODEL}")
    print("=" * 70)

    results = {}
    all_passed = True

    tests = [
        ("pipeline-programmatic", test_pipeline_programmatic),
        ("pipeline-yaml", test_pipeline_yaml),
        ("parallel-programmatic", test_parallel_programmatic),
        ("parallel-yaml", test_parallel_yaml),
        ("plan-execute-programmatic", test_plan_execute_programmatic),
        ("plan-execute-yaml", test_plan_execute_yaml),
    ]

    for name, test_fn in tests:
        try:
            passed, result = test_fn()
            results[name] = {"passed": passed, "steps": len(result.steps)}
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"\n  [FAIL] Exception: {e}")
            import traceback
            traceback.print_exc()
            results[name] = {"passed": False, "error": str(e)}
            all_passed = False

    # Summary
    header("SUMMARY")
    for name, info in results.items():
        status = "PASS" if info.get("passed") else "FAIL"
        extra = f"steps={info['steps']}" if "steps" in info else f"error={info.get('error', '?')}"
        print(f"  [{status}] {name}  ({extra})")

    print(f"\n  Overall: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

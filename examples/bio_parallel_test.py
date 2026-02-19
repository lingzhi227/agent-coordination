#!/usr/bin/env python3
"""
Test: Parallel biology research with Codex GPT-5.2 web search.

Generates a set of real biology / genomics / protein-function questions,
spins up one agent per question (each uses Codex's built-in web search),
runs them all in parallel, and writes every agent's raw answer into a
single Markdown report file.
"""

import os
import sys
import datetime
from pathlib import Path

sys.path.insert(0, ".")

from src.agent import Agent
from src.coordinators import ParallelCoordinator
from src.tracing import build_trace, save_trace

# ---------------------------------------------------------------------------
# Real biology / genomics / protein-function questions
# ---------------------------------------------------------------------------
QUESTIONS = [
    (
        "crispr-cas13d",
        "What are the latest advances (2024-2025) in CRISPR-Cas13d RNA editing "
        "for treating neurodegenerative diseases? Summarize key papers, clinical "
        "trials, and remaining delivery challenges."
    ),
    (
        "alphafold3-ppi",
        "How does AlphaFold 3 improve prediction of protein-protein interactions "
        "compared to AlphaFold 2? Describe the architectural changes, new training "
        "data, and benchmark results on recent CASP/CAPRI targets."
    ),
    (
        "single-cell-spatial",
        "What are the current state-of-the-art spatial transcriptomics methods "
        "(e.g., MERFISH, Visium HD, Stereo-seq) and how are they being combined "
        "with single-cell RNA-seq to build whole-organ cell atlases?"
    ),
    (
        "tp53-gof-mutations",
        "Explain the gain-of-function mechanisms of TP53 missense mutations "
        "(R175H, R248W, R273H) in cancer. What are the newest therapeutic "
        "strategies targeting mutant p53, including molecular glues and "
        "PROTACs reported in 2024-2025?"
    ),
    (
        "long-read-pangenome",
        "How are long-read sequencing technologies (PacBio HiFi, ONT) being "
        "used to build the human pangenome reference? Summarize the HPRC "
        "achievements, structural variant discovery, and clinical implications."
    ),
]


def main():
    # One researcher agent per question, each instructed to use web search
    agents = []
    subtasks = []

    for tag, question in QUESTIONS:
        agents.append(
            Agent(
                name=f"researcher-{tag}",
                role=(
                    "You are an expert molecular biology and genomics researcher. "
                    "Use your web search tool to find the most recent and authoritative "
                    "information. Cite specific papers, preprints, and data where possible. "
                    "Write a thorough, well-structured answer in Markdown format."
                ),
            )
        )
        subtasks.append(question)

    task = "Research the following independent biology / genomics questions in parallel."

    print("=" * 70)
    print("  Parallel Biology Research Test  —  Codex GPT-5.2 + Web Search")
    print("=" * 70)
    print(f"Questions: {len(QUESTIONS)}")
    for i, (tag, q) in enumerate(QUESTIONS, 1):
        print(f"  Q{i} [{tag}]: {q[:80]}...")
    print()

    # Run parallel — no synthesizer; we want raw answers stacked
    coordinator = ParallelCoordinator(agents, subtasks=subtasks)
    result = coordinator.run(task)

    # -----------------------------------------------------------------------
    # Build the Markdown report
    # -----------------------------------------------------------------------
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# Parallel Biology Research Report",
        f"",
        f"**Generated:** {now}  ",
        f"**Model:** gpt-5.2-codex  ",
        f"**Mode:** parallel ({len(QUESTIONS)} agents)  ",
        f"**Status:** {'All succeeded' if result.success else 'Some errors — see below'}",
        f"",
        "---",
        "",
    ]

    # Stack each agent's answer verbatim
    store = result.metadata["store"]
    for i, (tag, question) in enumerate(QUESTIONS, 1):
        key = f"worker-{i}"
        agent_result = store.results.get(key)
        lines.append(f"## Q{i}: {tag}")
        lines.append("")
        lines.append(f"**Question:** {question}")
        lines.append("")
        if agent_result is None:
            lines.append("*No result returned.*")
        elif agent_result.error:
            lines.append(f"**Error:** {agent_result.error}")
            lines.append("")
            lines.append(agent_result.output or "*empty*")
        else:
            lines.append(agent_result.output)
        lines.append("")
        lines.append("---")
        lines.append("")

    # Errors summary (if any)
    if result.errors:
        lines.append("## Errors")
        lines.append("")
        for err in result.errors:
            lines.append(f"- {err}")
        lines.append("")

    report = "\n".join(lines)

    # Write Markdown report
    base = os.path.join("outputs", "parallel")
    os.makedirs(base, exist_ok=True)
    existing = [int(d) for d in os.listdir(base) if d.isdigit()]
    next_num = max(existing, default=0) + 1
    out_dir = Path(base) / str(next_num)
    out_dir.mkdir()

    md_path = out_dir / "bio_parallel_report.md"
    md_path.write_text(report, encoding="utf-8")

    # -----------------------------------------------------------------------
    # Build and write trace JSON
    # -----------------------------------------------------------------------
    trace_path = out_dir / "bio_parallel_trace.json"
    trace = build_trace(result, task=task)
    save_trace(trace, str(trace_path))

    print(f"\n{'=' * 70}")
    print(f"Report written to: {md_path.resolve()}")
    print(f"Trace written to:  {trace_path.resolve()}")
    print(f"Total workers completed: {len(store.results)}")
    print(f"Elapsed: {result.elapsed:.1f}s")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.success}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()

# agent-coordination

Three multi-agent coordination patterns, using Codex CLI (gpt-5.2-codex) as the LLM backend.

## Patterns

### 1. Pipeline
```
Agent1 -> Agent2 -> Agent3 -> ... -> AgentN
```
Each agent's output feeds into the next as context. Good for sequential workflows like research -> draft -> review.

### 2. Plan-Execute
```
Planner -> [subtask1, subtask2, ...] -> Executor(each)
```
A planner LLM call breaks the task into steps, then an executor agent handles them one by one with accumulating context.

### 3. Parallel + Central Store
```
[Worker1] ──┐
[Worker2] ──┼──> Store ──> Synthesizer
[Worker3] ──┘
```
Workers run concurrently on independent subtasks. Results go to a central store. A synthesizer combines everything.

## Usage

```bash
# Pipeline
python examples/pipeline_demo.py

# Plan-Execute
python examples/plan_execute_demo.py

# Parallel
python examples/parallel_demo.py
```

## Requirements

- Python 3.11+
- [Codex CLI](https://github.com/openai/codex) installed and authenticated

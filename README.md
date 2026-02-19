# agent-coordination

Three multi-agent coordination patterns with multi-backend support:
**Codex CLI**, **Claude Code**, and **Gemini CLI**.

Each backend captures the **complete faithful trace** from native session files,
including thinking/reasoning blocks, tool calls, tool results, and raw events.
Trace extraction methods adapted from [life-long-memory](../life-long-memory) parsers.

## Backends

| Backend | CLI Command | Session File Location | Trace Contents |
|---------|------------|----------------------|----------------|
| **Codex** | `codex exec --json` | `~/.codex/sessions/{y}/{m}/{d}/rollout-*.jsonl` | reasoning, function_call, function_call_output |
| **Claude Code** | `claude -p --output-format stream-json` | `~/.claude/projects/{slug}/{uuid}.jsonl` | thinking blocks, tool_use, tool_result |
| **Gemini** | `gemini` | `~/.gemini/tmp/{hash}/chats/session-*.json` | thoughts, toolCalls, content |

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

```python
from src.agent import Agent
from src.backends import Backend
from src.coordinators import PipelineCoordinator

# Each agent can use a different backend
agents = [
    Agent(name="researcher", role="...", backend=Backend.CLAUDE_CODE, full_auto=True),
    Agent(name="analyst", role="...", backend=Backend.CODEX, full_auto=True),
    Agent(name="writer", role="...", backend=Backend.GEMINI),
]

coordinator = PipelineCoordinator(agents)
result = coordinator.run("Your task here")

# Trace includes complete session data from each backend's native files
from src.tracing import build_trace, save_trace
trace = build_trace(result, task="Your task here")
save_trace(trace, "trace.json")
```

```bash
# Pipeline demo
python tests/examples/pipeline_demo.py

# Plan-Execute demo
python tests/examples/plan_execute_demo.py

# Parallel demo
python tests/examples/parallel_demo.py
```

## Trace Schema (v2.0)

Each step in the trace contains:

| Field | Description |
|-------|-------------|
| `backend` | Which CLI was used (codex / claude_code / gemini) |
| `model` | Model name used for this step |
| `thinking` | Reasoning/thinking blocks from the model |
| `tool_calls` | All tool invocations with arguments |
| `tool_results` | Tool execution results |
| `session_messages` | Complete normalized messages from native session file |
| `session_file` | Path to the original session file for full replay |
| `raw_events` | Raw stdout events from CLI execution |

## Requirements

- Python 3.11+
- At least one CLI installed and authenticated:
  - [Codex CLI](https://github.com/openai/codex) for Codex backend
  - [Claude Code](https://claude.com/claude-code) for Claude Code backend
  - [Gemini CLI](https://github.com/google-gemini/gemini-cli) for Gemini backend

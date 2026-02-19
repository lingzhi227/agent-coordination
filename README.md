# agent-coordination

Graph-based multi-agent coordination with **A2A protocol** concepts and multi-backend support:
**Codex CLI**, **Claude Code**, and **Gemini CLI**.

Declare agents as **nodes** and data flow as **edges** in a single graph definition.
The graph engine handles execution order, parallelism, dynamic expansion, and context passing.
All three classic patterns (pipeline, parallel, plan-execute) are special cases of the graph.

## Graph-Based Coordination

### YAML Definition

```yaml
name: article-pipeline

nodes:
  researcher:
    role: "You are a research agent..."
    backend: codex
    full_auto: true
  writer:
    role: "You are a writer agent..."
    backend: claude_code
  reviewer:
    role: "You are a review agent..."
    backend: gemini

edges:
  - from: _input
    to: researcher
  - from: researcher
    to: writer
    context_policy: replace
  - from: writer
    to: reviewer
    context_policy: replace
  - from: reviewer
    to: _output
```

```python
from src.graph import load_graph, GraphExecutor

graph = load_graph("graphs/pipeline.yaml")
executor = GraphExecutor(graph)
result = executor.run("Write an article about quantum computing")
```

### Programmatic API (No YAML Required)

```python
from src.agent import Agent
from src.backends import Backend
from src.graph import pipeline, parallel, plan_execute

# Pipeline
agents = [
    Agent(name="researcher", role="...", backend=Backend.CODEX),
    Agent(name="writer", role="...", backend=Backend.CLAUDE_CODE),
    Agent(name="reviewer", role="...", backend=Backend.GEMINI),
]
executor = pipeline(agents)
result = executor.run("Your task here")

# Parallel fan-out/fan-in
workers = [
    Agent(name="backend_expert", role="...", backend=Backend.CODEX),
    Agent(name="frontend_expert", role="...", backend=Backend.CLAUDE_CODE),
]
synth = Agent(name="synthesizer", role="Combine expert inputs.", backend=Backend.GEMINI)
executor = parallel(workers, synthesizer=synth)
result = executor.run("Design architecture for...")

# Plan-Execute (dynamic expansion)
exec_agent = Agent(name="executor", role="Complete the subtask.", backend=Backend.CLAUDE_CODE)
executor = plan_execute(exec_agent, planning_backend="codex")
result = executor.run("Build a REST API for...")
```

### Context Policies

Edges carry a `context_policy` that controls how data flows between nodes:

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `replace` | Downstream gets only upstream output | Pipeline stages |
| `accumulate` | Context grows with each step | Plan-execute sequential tasks |
| `aggregate` | All upstream outputs collected/joined | Parallel → synthesizer |
| `none` | No context passed, only the task | Independent parallel workers |

### A2A Protocol Mapping

The graph engine uses [A2A](https://google.github.io/A2A/) vocabulary internally:

| A2A Concept | Implementation |
|-------------|---------------|
| Agent Card | `NodeDef` in YAML (name, role, backend) |
| Task | `TaskEnvelope` dataclass flowing along edges |
| TaskState | `submitted → working → completed/failed` per node |
| Message | Context + task strings passed to `Agent.run()` |
| Artifact | `AgentResult.output` — the tangible product |
| contextId | UUID per graph execution run |

### Dynamic Nodes (Plan-Execute)

Nodes with `type: dynamic` call an LLM to expand the task into subtasks:

```yaml
nodes:
  planner:
    type: dynamic
    expand: sequential    # or "parallel"
    llm_call:
      backend: codex
      prompt: "Break this into 2-5 subtasks. Return JSON array.\nTask: {{task}}"
    transform: parse_list
```

## Backends

| Backend | CLI Command | Session File Location |
|---------|------------|----------------------|
| **Codex** | `codex exec --json` | `~/.codex/sessions/{y}/{m}/{d}/rollout-*.jsonl` |
| **Claude Code** | `claude -p --output-format stream-json` | `~/.claude/projects/{slug}/{uuid}.jsonl` |
| **Gemini** | `gemini` | `~/.gemini/tmp/{hash}/chats/session-*.json` |

Each backend captures the **complete faithful trace** from native session files,
including thinking/reasoning blocks, tool calls, tool results, and raw events.

## Classic Patterns (Backward Compatible)

The original coordinator classes remain available:

```python
from src.coordinators import PipelineCoordinator, ParallelCoordinator, PlanExecuteCoordinator
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

## Requirements

- Python 3.11+
- `pyyaml>=6.0` (for YAML graph loading)
- At least one CLI installed and authenticated:
  - [Codex CLI](https://github.com/openai/codex) for Codex backend
  - [Claude Code](https://claude.com/claude-code) for Claude Code backend
  - [Gemini CLI](https://github.com/google-gemini/gemini-cli) for Gemini backend

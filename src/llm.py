"""
LLM wrapper — backward-compatible shim over src.backends.

The actual backend implementations live in src/backends/.
This module preserves the original call() interface for existing code.
"""

from src.backends import (
    Backend,
    DEFAULT_MODELS,
    LLMResponse,
    call as _call,
)

DEFAULT_MODEL = DEFAULT_MODELS[Backend.CODEX]
DEFAULT_BACKEND = Backend.CODEX


def call(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    full_auto: bool = False,
    backend: Backend | str = DEFAULT_BACKEND,
) -> LLMResponse:
    """Send a prompt to the LLM and return the response.

    Backward compatible: defaults to Codex CLI.
    New code should use src.backends.call() directly.
    """
    return _call(prompt, backend=backend, model=model, full_auto=full_auto)

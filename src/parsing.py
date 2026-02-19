"""
Shared JSON array parsing for LLM responses.

Used by plan-execute (plan generation) and parallel (task splitting)
to extract structured lists from LLM output.
"""

import json


def parse_list_response(text: str) -> list[str]:
    """Extract a list of strings from an LLM response.

    Tries JSON array first, falls back to newline splitting.
    """
    text = text.strip()

    # Try to extract JSON array
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    # Fallback: split by newlines, strip list markers
    return [line.strip("- ").strip() for line in text.splitlines() if line.strip()]

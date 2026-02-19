"""
Transform functions for dynamic node output parsing.

Reuses src/parsing.py for the heavy lifting.
"""

from src.parsing import parse_list_response

# Registry of available transforms
TRANSFORMS: dict[str, callable] = {
    "parse_list": parse_list_response,
}


def get_transform(name: str) -> callable:
    """Look up a transform function by name."""
    if name not in TRANSFORMS:
        raise ValueError(
            f"Unknown transform: {name!r}. "
            f"Available: {list(TRANSFORMS.keys())}"
        )
    return TRANSFORMS[name]

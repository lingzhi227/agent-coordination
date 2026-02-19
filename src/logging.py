"""
Unified step logging for all coordination patterns.
"""


class StepLogger:
    """Consistent log output for coordinator steps."""

    def __init__(self, name: str):
        self.name = name

    def info(self, msg: str):
        print(f"[{self.name}] {msg}")

    def start(self, step: int, total: int, label: str):
        print(f"[{self.name} step {step}/{total}] {label}: starting...")

    def done(self, step: int, total: int, label: str, chars: int):
        print(f"[{self.name} step {step}/{total}] {label}: done ({chars} chars)")

    def error(self, step: int, total: int, label: str, err: str):
        print(f"[{self.name} step {step}/{total}] {label}: ERROR - {err}")

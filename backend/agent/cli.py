"""Anchor CLI - talk to the agent from the terminal.

Useful for demos without spinning up the web UI.

Run:  python -m agent.cli
"""
from __future__ import annotations

from ..memory.client import get_bank_id
from .loop import run_loop


def main() -> None:
    bank_id = get_bank_id()
    print("Anchor - Caregiver Memory Agent (type 'quit' to exit)\n")
    while True:
        try:
            message = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not message:
            continue
        if message.lower() in {"quit", "exit"}:
            break
        result = run_loop(bank_id, message)
        print(f"anchor> {result['answer']}")
        if result["risk"]:
            print(f"  [RISK FLAGGED] {result['risk_reason']}")


if __name__ == "__main__":
    main()

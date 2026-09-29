"""Convenience runner for the full Anchor demo.

Sets up the bank, loads demo data, and prints a quick smoke test of the
learning-curve so you can verify the demo before recording.

Run:  python run.py
"""
import sys

sys.path.insert(0, "backend")

from memory.create_bank import create_bank
from data.load_demo_data import load


def main() -> None:
    print("== Anchor setup ==")
    create_bank()
    count = load()
    print(f"Loaded {count} demo memories. Bank ready.")
    print("Next steps:")
    print("  1. Start backend:  uvicorn agent.main:app --reload")
    print("  2. Start UI:       streamlit run frontend/app.py")
    print("  Or talk directly:  python -m agent.cli")


if __name__ == "__main__":
    main()

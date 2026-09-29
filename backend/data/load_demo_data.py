"""Load the synthetic caregiver dataset into a Hindsight memory bank.

Run:  python -m data.load_demo_data
"""
from __future__ import annotations

from ..memory.client import get_bank_id, retain_batch
from .synthetic import generate


def load(bank_id: str | None = None, verbose: bool = True) -> int:
    bank_id = bank_id or get_bank_id()
    items = generate()
    retain_batch(bank_id, items, document_id="demo_history_3weeks")
    if verbose:
        print(f"[anchor] loaded {len(items)} demo memories into bank '{bank_id}'")
    return len(items)


if __name__ == "__main__":
    load()

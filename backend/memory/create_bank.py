"""Create and configure the Anchor memory bank.

This is where Hindsight's memory *personality* is set:

- mission:      natural-language identity telling Hindsight what knowledge to
                prioritize and how to reason.
- directives:   hard rules the agent MUST follow (safety guardrails).
- disposition:  soft traits influencing reasoning style.

For a caregiver health agent we want high empathy (the human is stressed) and
high skepticism (we must not give false reassurance or miss a risk). Literalism
is kept moderate so the agent can reason about vague symptoms like "dizzy".

Run:  python -m memory.create_bank
"""
from __future__ import annotations

from .client import get_client, get_bank_id

MISSION = (
    "I am Anchor, a memory-powered health navigator for a family caregiver "
    "looking after an aging parent. My job is to remember the parent's full "
    "medical journey - symptoms, medications, lab results, doctor notes and "
    "daily observations - across weeks and months. I surface patterns and "
    "contradictions over time, prepare clear one-page briefs for doctor "
    "visits, and help the caregiver make confident, informed decisions. "
    "I prioritize safety and clarity over convenience."
)

DIRECTIVES = [
    "Always flag potential drug interactions when a new medication or dose "
    "appears alongside an existing one, especially blood thinners.",
    "Never give medical dosage advice or prescribe anything. Recommend "
    "contacting the right provider instead.",
    "Always cite the memories (symptoms, dates, provider names) that back up "
    "any concern you raise.",
    "If information is missing or uncertain, say so clearly rather than "
    "guessing. Do not reassure without evidence.",
    "Treat all personal health information as confidential. Never repeat "
    "unrelated details.",
]

DISPOSITION = {
    "skepticism": 4,  # 1 trusting -> 5 skeptical (don't over-reassure)
    "literalism": 3,  # 1 flexible -> 5 literal (reason about vague symptoms)
    "empathy": 5,     # 1 detached -> 5 empathetic (caregiver is stressed)
}


def _add_directives(client, bank_id: str) -> bool:
    """Persist directives, tolerating client API differences between versions.

    Returns True only if every directive was added.
    """
    if not hasattr(client, "directives"):
        return False
    added = 0
    for directive in DIRECTIVES:
        try:
            client.directives.add(bank_id=bank_id, directive=directive)
            added += 1
        except TypeError:
            # Some client versions name the kwarg `text` instead.
            try:
                client.directives.add(bank_id=bank_id, text=directive)
                added += 1
            except Exception as exc:  # noqa: BLE001
                print(f"[anchor] directive skipped ({exc})")
        except Exception as exc:  # noqa: BLE001
            print(f"[anchor] directive skipped ({exc})")
    return added == len(DIRECTIVES)


def create_bank(bank_id: str | None = None) -> None:
    """Create/update the Anchor memory bank with mission, directives, disposition."""
    bank_id = bank_id or get_bank_id()
    client = get_client()
    client.create_bank(
        bank_id=bank_id,
        name="Anchor - Caregiver Medical Memory",
        mission=MISSION,
        disposition=DISPOSITION,
    )
    if not _add_directives(client, bank_id):
        # Fallback: some client versions accept directives on create_bank.
        try:
            client.create_bank(
                bank_id=bank_id,
                name="Anchor - Caregiver Medical Memory",
                mission=MISSION,
                directives=DIRECTIVES,
                disposition=DISPOSITION,
            )
        except TypeError as exc:
            print(f"[anchor] warning: directives not persisted ({exc}); "
                  "add them via the Hindsight control plane.")
    print(f"[anchor] bank '{bank_id}' configured.")


if __name__ == "__main__":
    create_bank()

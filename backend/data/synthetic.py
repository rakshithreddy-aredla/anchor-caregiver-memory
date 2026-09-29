"""Synthetic caregiver dataset generator.

The #1 tip in the competition brief: "the thing that makes your project look
real is the data." This generates three weeks of realistic medical history for
a fictional family so the demo can show the learning curve and the Catch.

It builds a believable story arc:

- Week 1-2: Mom's baseline (BP ~130/80, walks daily, takes Warfarin).
- Day ~12:  New cardiologist starts Metoprolol for BP, doubles the dose on
            day 14.
- Day 14+: BP climbs (165/92), Mom reports dizziness.
- This is the exact scenario Anchor should catch.

Output is a list of retain-batch items (content + timestamp + context) ready
to load into Hindsight via memory.client.retain_batch.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

# Family / care-recipient profile (fictional but realistic)
PARENT = {
    "name": "Margaret Chen",
    "age": 78,
    "diagnoses": ["atrial fibrillation", "hypertension", "mild osteoarthritis"],
    "baseline_bp": "130/80",
    "daily": "walks 20 minutes, sleeps 7 hours",
}

MEDS = [
    "Warfarin 5mg once daily (blood thinner)",
    "Lisinopril 10mg daily (BP)",
    "Atorvastatin 20mg nightly (cholesterol)",
]

# The narrative arc we want the agent to learn and ultimately "catch".
STORY = [
    # (day_offset, content, context)
    (0, "Margaret started her day, BP 128/78, felt well. Walked 20 minutes.",
     "daily observation"),
    (1, "BP 131/82 at breakfast. No complaints.", "daily observation"),
    (2, "BP 129/80. Took Warfarin 5mg at 8am as usual.", "medication"),
    (3, "Slight joint stiffness in the morning, eased after walking.",
     "daily observation"),
    (4, "BP 132/84. Appetite normal.", "daily observation"),
    (5, "Visited Dr. Patel, her cardiologist. Routine check, no changes.",
     "doctor visit"),
    (6, "BP 130/81. Felt energetic, went for a longer walk.", "daily observation"),
    (7, "BP 127/78. No new symptoms.", "daily observation"),
    (8, "BP 131/83. Complained of mild morning stiffness only.", "daily observation"),
    (9, "BP 130/82. Normal day, took all meds on time.", "medication"),
    (10, "BP 128/79. Feeling well.", "daily observation"),
    (11, "BP 133/85 - slightly higher than baseline. Noted.", "daily observation"),
    (12, "Saw Dr. Patel. Blood pressure trending up; started Metoprolol 25mg "
          "once daily for hypertension. Added to existing meds.",
     "doctor visit / medication change"),
    (13, "BP 138/88 after starting Metoprolol. Slight fatigue.", "daily observation"),
    (14, "Dr. Patel doubled Metoprolol to 50mg daily because BP was still "
          "elevated. Warfarin unchanged.", "medication change"),
    (15, "BP 152/90 this morning - noticeably higher. Margaret felt dizzy "
          "after standing up.", "symptom"),
    (16, "BP 158/92. Reported lightheadedness twice today.", "symptom"),
    (17, "BP 165/92 - highest reading. Dizzy spells continue, especially "
          "after standing. Taking Metoprolol 50mg + Warfarin 5mg.",
     "symptom / medication"),
]

# Mapped provider contact (for the brief).
PROVIDERS = [
    "Dr. Anita Patel, Cardiologist - (555) 010-2233",
    "Dr. James Okafor, Primary Care - (555) 010-8899",
]


def generate(start: datetime | None = None) -> list[dict]:
    """Generate the full dataset as retain-batch items with datetime timestamps.

    Timestamps are datetime objects per Hindsight's documented retain contract
    (``timestamp=datetime(...)``), so temporal recall works correctly.
    """
    start = start or datetime(2026, 9, 1, 8, 0, 0)
    items: list[dict] = []

    # Provider contact + base profile first so recall has context.
    items.append({
        "content": f"{PARENT['name']}, age {PARENT['age']}, diagnoses: "
                   f"{', '.join(PARENT['diagnoses'])}. Baseline BP "
                   f"{PARENT['baseline_bp']}. {PARENT['daily']}.",
        "context": "profile",
        "timestamp": start,
    })
    for m in MEDS:
        items.append({
            "content": f"{PARENT['name']} takes {m}.",
            "context": "medication baseline",
            "timestamp": start,
        })
    for p in PROVIDERS:
        items.append({
            "content": p,
            "context": "provider contact",
            "timestamp": start,
        })

    # The narrative arc.
    for offset, content, context in STORY:
        ts = start + timedelta(days=offset)
        items.append({
            "content": f"{PARENT['name']}, day +{offset}: {content}",
            "context": context,
            "timestamp": ts,
        })
    return items


# Written next to this module so the default path works regardless of cwd.
DEFAULT_JSONL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "demo_data.jsonl"
)


def to_jsonl(path: str | None = None) -> None:
    """Write the dataset to JSONL (timestamps serialized as ISO strings)."""
    path = path or DEFAULT_JSONL_PATH
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    items = generate()
    with open(path, "w", encoding="utf-8") as fh:
        for it in items:
            row = dict(it)
            ts = row.get("timestamp")
            if isinstance(ts, datetime):
                row["timestamp"] = ts.isoformat()
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"[anchor] wrote {len(items)} demo memories to {path}")


if __name__ == "__main__":
    to_jsonl()

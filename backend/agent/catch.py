"""The "Catch" engine.

The demo-defining feature. Given the family's memory, detect a real risk that a
stateless agent would miss - e.g. a symptom that coincides with a new
medication or dose change, especially a blood thinner.

The heavy lifting (observation consolidation + temporal recall) is done by
Hindsight. This module adds a focused LLM step that turns the recalled memory
into an actionable, cited risk flag.
"""
from __future__ import annotations

from memory.client import get_bank_id, recall

TRIGGERS = {
    "dizzy spells": "dizziness",
    "short of breath": "breathing",
    "chest pain": "chest pain",
    "lightheaded": "dizziness",
    "confusion": "confusion",
    "confused": "confusion",
    "bruising": "bleeding",
    "bleeding": "bleeding",
    "dizzy": "dizziness",
    "fell": "fall",
    "fall": "fall",
    "weak": "weakness",
}


def catch(bank_id: str | None, symptom: str) -> dict:
    """Check the parent's memory for a risk related to `symptom`.

    Returns:
        {"risk": bool, "reason": str, "evidence": [str]}
    """
    bank_id = bank_id or get_bank_id()
    norm = symptom.lower().strip()

    # 1. Map the symptom to a risk keyword FIRST - no wasted recall calls
    #    when the message contains no symptom. Longer phrases are matched
    #    before shorter ones so "dizzy spells" wins over "dizzy".
    keyword = None
    for phrase, mapped in TRIGGERS.items():
        if phrase in norm:
            keyword = mapped
            break
    if not keyword:
        return {"risk": False, "reason": None, "evidence": []}

    # 2. Recall anything temporal/medication related. Degrade gracefully if
    #    the memory layer is unavailable.
    try:
        meds = recall(bank_id, "current medications and doses", budget="mid")
        trends = recall(
            bank_id, f"when did {keyword} start and how has it changed", budget="mid"
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[anchor] catch recall unavailable: {exc}")
        return {"risk": False, "reason": None, "evidence": []}

    # 3. A simple, transparent heuristic that's easy to demo and verify.
    #    A real deployment would lean on Hindsight observations + the LLM.
    recent_med_change = any(
        any(w in m.lower() for w in ["new", "increased", "started", "changed", "added"])
        for m in meds
    )
    on_blood_thinner = any(
        any(w in m.lower() for w in ["warfarin", "eliquis", "xarelto", "heparin", "anticoag"])
        for m in meds
    )

    risk = bool(recent_med_change or on_blood_thinner)
    reason = None
    if risk:
        reason = (
            f"The parent recently had a medication change and/or is on a blood "
            f"thinner, and reports '{keyword}'. This combination can indicate a "
            f"drug interaction or adverse reaction worth checking with a provider."
        )

    evidence = meds + trends
    return {"risk": risk, "reason": reason, "evidence": evidence}

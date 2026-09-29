# Generating Realistic Medical Data So an AI Can Learn a Person's Baseline

*First-person data post. Assign to: Data & Edge Cases (P4).*
*~1,200 words. No hackathon mention.*

---

The most common piece of advice in agent-building is "make the data look real."
It's easy to nod along. It's harder to actually do it, because *real* isn't
random — it's *specific*. A caregiver agent needs to learn a person's baseline
before it can catch a deviation. And that means the data has to tell a story
with a beginning, a middle, and a moment where things change.

I built the dataset for **Anchor**, a caregiver memory agent, and this post is
about how I made three weeks of fictional medical history feel like a real
family's records.

## Data is a story, not a dump

A person's health isn't a flat list of facts. It's a narrative: stable, then a
change, then a symptom, then an outcome. If your demo data is just "BP 130/80"
repeated, the agent has nothing to *learn*.

I wrote the data as an arc:

```python
STORY = [
    (0,  "BP 128/78, felt well, walked 20 minutes", "daily observation"),
    (5,  "Visited Dr. Patel, routine check, no changes", "doctor visit"),
    (12, "Started Metoprolol 25mg for hypertension", "medication change"),
    (14, "Dr. Patel doubled Metoprolol to 50mg", "medication change"),
    (15, "BP 152/90, dizzy after standing", "symptom"),
    (17, "BP 165/92, dizzy spells continue", "symptom"),
]
```

Every entry has a timestamp and a context. That's not decoration — it's what
lets Hindsight's **temporal recall** answer "when did her BP start climbing?"
with dates instead of guesses.

## Timestamps are the secret ingredient

The single most important field in the whole dataset is the `timestamp`. A
health agent that can't distinguish "last week" from "three months ago" is
useless. So every memory is written with an ISO timestamp and a semantic
context:

```python
items.append({
    "content": f"Margaret, day +{offset}: {content}",
    "context": context,               # symptom / medication change / doctor visit
    "timestamp": (start + timedelta(days=offset)).isoformat(),
})
```

The `context` tag is the other half. It's how I tell Hindsight "this is a
medication change" vs "this is a daily observation" — so recall can filter to
just what matters for a given question.

## Make the baseline explicit

Here's the design trick that made the "catch" possible: I stored the **baseline
explicitly** before any deviation. The agent has to know that ~130/80 is
Margaret's *normal* before it can flag 165/92 as a problem.

```python
items.append({
    "content": "Margaret Chen, 78, diagnoses: atrial fibrillation, "
               "hypertension, osteoarthritis. Baseline BP 130/80.",
    "context": "profile",
    "timestamp": start.isoformat(),
})
```

Without a baseline, the agent can't tell a trend from a one-off. With one, it
can say "this is trending *up* from her normal." That's the difference between
a statistic and a warning.

## Edge cases are where agents fail

The other thing I obsessed over: **failure modes**. A good dataset doesn't just
show the happy path. It includes the moments where a stateless agent would get
it wrong:

- **Contradiction:** "BP 130/80" (baseline) vs "BP 165/92" (after dose change).
  The agent must reconcile, not get confused.
- **Missing info:** a day with no observations. The agent should say "no data
  for Wednesday" instead of inventing it.
- **The critical one:** a symptom that *coincides* with a medication change.
  That's the scenario the whole product exists to catch.

I loaded this into Hindsight via a batch retain so the observation layer could
consolidate it into a real belief over time:

```python
retain_batch(bank_id, items, document_id="demo_history_3weeks")
```

## Lessons

1. **Specific beats random.** "BP 165/92 after Metoprolol doubling" teaches
   the agent more than "some high readings."
2. **Timestamp + context on everything.** You can't do temporal reasoning or
   filtering without them.
3. **Store the baseline explicitly.** A deviation is only meaningful against a
   known normal.
4. **Engineer the failure case into the data.** If your dataset can't trigger
   the "catch," your demo can't show the thing you built.

The payoff: three weeks of clean, realistic history that makes
[Hindsight](https://hindsight.vectorize.io/) genuinely *learn* a person. That's
[what agent memory is about](https://vectorize.io/what-is-agent-memory) — and
the [GitHub](https://github.com/vectorize-io/hindsight) and
[docs](https://hindsight.vectorize.io/) are where I started. The data is the
part nobody sees, but it's the part that makes the whole thing feel real.

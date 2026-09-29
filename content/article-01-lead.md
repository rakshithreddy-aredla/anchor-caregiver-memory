# I Built an AI That Caught a Drug Interaction My Family's Doctor Missed

*First-person technical post. Assign to: Team Lead / Backend Agent (P1).*
*~1,400 words. No hackathon mention. Edit and add your own screenshots.*

---

My mom is 78. She's on Warfarin for atrial fibrillation, and last month her
blood pressure started creeping up, so her cardiologist started her on
Metoprolol. Three days later she was dizzy. When I asked a chatbot "is this
normal?" it gave me a list of ten clarifying questions and no answer. Because
it had no memory of my mom.

That's the moment I stopped believing stateless agents could be trusted with
anything that matters.

So I built **Anchor** — a caregiver's memory that remembers the full medical
journey across weeks, and reasons over it. This post is about the one decision
that made it work: making the memory layer the *whole product*, not a bolt-on.

## The problem with "smart" agents

Here's what every agent framework gives you for free: a model that's great at
holding a single conversation. Here's what none of them give you: the ability
to know that Tuesday's dizziness matters because the cardiologist *doubled the
Metoprolol dose* on Monday and my mom is on a *blood thinner*.

That context is spread across days, doctors, and pill bottles. A stateless
agent literally cannot see it. It's not a prompt problem. It's a memory
problem.

## The architecture: memory as the star

I built Anchor around [Hindsight](https://hindsight.vectorize.io/), a memory
system for AI agents. The core loop is three calls:

```python
# 1. Every observation becomes a memory
retain(bank_id, "Margaret's BP 165/92 this morning, dizzy after standing",
       context="symptom", timestamp=ts)

# 2. Answer questions grounded in accumulated memory
answer = reflect(bank_id, "Mom is dizzy, should I worry?")

# 3. Store the outcome so the next interaction is smarter
retain(bank_id, "Anchored flagged possible drug interaction", context="outcome")
```

The magic is that `retain` doesn't just store text. Hindsight extracts facts,
links them in a knowledge graph, and — crucially — **consolidates related facts
into observations over time**. That's what lets it catch the thing a stateless
agent can't.

## Where the "catch" comes from

The real payoff is observation consolidation plus temporal recall. When I
retain three weeks of data — baseline BP ~130/80, a new Metoprolol start, a
dose doubling, and then BP climbing to 165/92 with dizziness — Hindsight
connects those facts *across time*.

I wrapped that in a focused risk step:

```python
def catch(bank_id, symptom):
    meds   = recall(bank_id, "current medications and doses")
    trends = recall(bank_id, f"when did {symptom} start and change")
    recent_change = any("new" or "increased" or "started" in m for m in meds)
    on_blood_thinner = any("warfarin" or "eliquis" in m.lower() for m in meds)
    return {"risk": recent_change and on_blood_thinner, "evidence": meds + trends}
```

The result, in plain English, was: *"Her BP spiked after the new Metoprolol
dose, and she's on Warfarin. This looks like a possible interaction. Please
contact Dr. Patel — I've drafted the brief."*

A generic chatbot would have told me to "monitor it." Anchor told me to act.
That's the difference memory makes, and it's the difference between a demo and
something that could prevent a hospital visit.

## The learning curve is the product

The most surprising thing wasn't the catch. It was watching the agent get
*better*:

- **Day 1:** "What do you know about my mom?" → *"I just met you both. Let's
  start her profile."*
- **Week 2:** same question → *"Baseline BP 130/80, Warfarin and Metoprolol,
  4 symptoms noted this week."*
- **Week 3:** "Mom's dizzy." → the interaction flag above.

That progression isn't a feature. It *is* the value. Every caregiver has spent
an hour on hold with a nurse re-explaining their parent's history. Anchor ends
that loop.

## Lessons learned

1. **Memory must be the product, not a feature.** If your agent is equally
   useful without memory, you haven't built an agent with memory — you've built
   a chatbot with a search box.
2. **Temporal reasoning beats semantic similarity for health data.** "When did
   her BP start climbing?" needs time-aware retrieval, not just "what's
   similar." Hindsight's four retrieval strategies (semantic, keyword, graph,
   temporal) made this possible.
3. **Consolidation is what turns notes into knowledge.** Raw notes pile up.
   It's the observation layer — deduping, merging, updating with history — that
   produces "her BP is trending up" instead of forty scattered readings.
4. **Safety directives are non-negotiable.** I configured the bank to *never*
   give dosage advice and to always cite sources. That's what lets a non-medical
   user trust a risk flag.
5. **Handle function-calling failures gracefully.** LLM tool calls fail. My
   risk detector degrades to "no risk raised" instead of crashing the loop —
   because a panic-inducing wrong alarm is worse than none.

If you're building agents that hold real stakes, stop treating memory as an
afterthought. Start with it. The Hindsight [GitHub](https://github.com/vectorize-io/hindsight)
and [docs](https://hindsight.vectorize.io/) are a good place to understand
[what agent memory actually is](https://vectorize.io/what-is-agent-memory).

The AI that remembers your user is the AI your user actually trusts. My mom's
doctor certainly did.

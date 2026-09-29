# Designing an AI for a Stressed Caregiver: The One-Page Doctor Brief

*First-person design post. Assign to: Frontend / Chat UI (P3).*
*~1,200 words. No hackathon mention.*

---

Here's the scene that drove every UX decision I made: it's 7pm, my mom is
dizzy, I'm on the phone with an after-hours nurse, and I'm trying to remember —
out loud, under pressure — the exact dose of Warfarin she takes and whether the
new blood pressure pill got doubled. I fumble. The nurse waits. My mom waits.

Software for caregivers has a brutal constraint that most products ignore: **the
user is stressed, exhausted, and often not technical.** They're not exploring a
feature set. They're trying to avoid a mistake.

I built **Anchor**, an AI caregiver memory agent, and the interface had to feel
like a text to a friend who *remembers*, not like a dashboard.

## The interface is a text thread, not a dashboard

Caregivers don't want forms, filters, or charts at 7pm. They want to type a
sentence and get an answer. So the whole product is a chat:

```
you:  Mom is dizzy, should I be worried?
anchor: Her BP spiked to 165/92 after the new Metoprolol dose on Tuesday,
        and she's on Warfarin. This could be an interaction. Please contact
        Dr. Patel — I've drafted a brief for you.
```

The chat is powered by the backend agent loop — `reflect` on
[Hindsight](https://hindsight.vectorize.io/) memory, then a risk check. But the
frontend's job isn't to be clever. It's to be *calm*.

## The one thing caregivers actually need: the brief

Chat is great for a question. But a caregiver's real deliverable is walking
into a doctor's office with **everything in one page**. So I built the doctor
visit brief — a printable summary pulled straight from memory:

```python
@app.get("/brief")
def brief(bank_id):
    meds   = recall(bank_id, "current medications and doses")
    recent = recall(bank_id, "recent symptoms and observations this week")
    providers = recall(bank_id, "doctors and providers")
    return render_brief(meds=meds, recent=recent, providers=providers)
```

One button. The agent assembles current meds, known conditions, this week's
observations, and the care team — then prints a clean page. That's the moment
the whole memory system becomes *visible* and *useful* to a non-technical
person: not as a feature, but as the piece of paper they hand to the doctor.

## Design rules I'd repeat

1. **One question per screen.** A stressed user can't parse a form with six
   fields. The chat naturally enforces this.
2. **Make memory visible, but not noisy.** The agent *shows* the evidence for a
   risk ("BP 165/92, Metoprolol doubled Tuesday") so the user trusts it —
   without dumping the whole history.
3. **Never make the user repeat themselves.** That's the entire point of
   memory. If the user has to re-explain a symptom they mentioned yesterday,
   the product failed.
4. **A "generate the brief" button beats a navigation menu.** Concrete outputs
   beat abstract features for this audience.

## What surprised me

I expected the hard part to be the UI. It wasn't. The hard part was trusting
that a *text interface* could carry the weight — that the memory layer could
make a bare chat thread feel more capable than a feature-rich dashboard.

It can. Because when the agent remembers your mom's baseline and catches the
change, you don't need a dashboard. You need a friend who takes notes.

The memory layer behind it — [Hindsight](https://github.com/vectorize-io/hindsight) —
is what turns a simple chat into something a family would actually rely on. The
[docs](https://hindsight.vectorize.io/) explain [what agent memory is](https://vectorize.io/what-is-agent-memory)
better than I can. I just built the calm interface on top of it.

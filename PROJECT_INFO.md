# Anchor — Project Info Sheet

## One-liner
**Anchor** is a memory-powered health navigator for caregivers of aging parents.
It remembers the full medical journey across weeks using
[Hindsight](https://github.com/vectorize-io/hindsight) so families never repeat
their loved one's story — and catches drug-interaction risks a stateless
chatbot would miss.

## Problem
Caregivers manage scattered info (meds, symptoms, labs, doctor calls) and must
re-tell their parent's history under stress. Stateless chatbots forget
everything, so they can't connect a Tuesday symptom to a Monday dose change.
1 in 5 caregivers reports a medication error. 53M+ unpaid caregivers in the US.

## Key features
- **Persistent medical memory** — symptoms, meds, labs, doctor notes,
  observations, all retained with timestamps
- **The "Catch" engine** — detects contradictions across time (new med +
  existing med + symptom = risk)
- **Temporal recall** — "what changed this week vs last week?" via Hindsight's
  4-way TEMPR retrieval (semantic / keyword / graph / temporal)
- **Doctor-visit brief** — one-click printable page generated from memory
- **Safety by design** — flags interactions, never gives dosage advice, cites
  sources; message length validated; graceful degradation when memory is down

## Tech stack
| Layer | Tech |
|---|---|
| Memory | **Hindsight** (retain / recall / reflect) — Cloud or open-source |
| LLM | Groq (`gpt-oss-120b` / `qwen3-32b`) |
| Backend | FastAPI + Python 3.12 |
| Frontend | Streamlit chat UI + brief |
| Tests | pytest (36 regression tests, CI on GitHub Actions) |
| Data | Synthetic 3-week caregiver history |

## The demo (the "wow")
- **Day 1:** "What do you know about my mom?" → *"I just met you both."*
- **Week 2:** → *"Baseline BP 130/80, Warfarin + Metoprolol, 4 symptoms this
  week."*
- **Week 3:** "Mom's dizzy." → *"BP spiked to 165/92 after the new Metoprolol
  dose, and she's on Warfarin. Possible interaction — contact Dr. Patel, I've
  drafted the brief."*

## How Hindsight memory is used
- `retain()` — every observation, doctor note, med change, symptom stored as
  world/experience facts with timestamps
- Observation consolidation — scattered facts merged into durable, grounded
  beliefs (the "learning curve")
- `recall()` — TEMPR 4-way search (semantic, keyword, graph, temporal)
- `reflect()` — disposition-aware answers (empathy 5, skepticism 4) governed by
  mission + safety directives
- Mental models — family-curated baseline ("BP ~130/80, walks daily")

## Run it
```bash
pip install -r backend/requirements.txt
cp .env.example .env   # set HINDSIGHT_BASE_URL / HINDSIGHT_API_KEY / GROQ_API_KEY
python run.py          # create bank + load demo data
cd backend && uvicorn agent.main:app --reload
streamlit run frontend/app.py   # from repo root
```

## Team (6 roles)
1. Team Lead / Backend Agent
2. Hindsight Memory Architect
3. Frontend / Chat UI
4. Data & Edge Cases
5. Demo & Video Lead
6. Content & Pitch Lead

## Repo layout
```
backend/agent/     loop, catch engine, FastAPI app, CLI
backend/memory/    Hindsight bank config + client wrapper
backend/data/      synthetic dataset + loader
backend/tests/     36 regression tests
frontend/          Streamlit chat + doctor brief
content/           article drafts, LinkedIn/Reddit posts, video script
docs/              content plan + submission checklist
```

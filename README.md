# Anchor — The Caregiver's Memory

> **The AI that never forgets what your family member told the doctor.**

Anchor is a memory-powered health navigator for caregivers of aging parents. It uses
[Hindsight](https://github.com/vectorize-io/hindsight) — a state-of-the-art agent memory
system — to remember the full medical journey: symptoms, medications, lab results, doctor
conversations, and daily observations. So a family never repeats their loved one's story to
a new doctor, nurse, or insurer — and Anchor catches problems (drug interactions, worsening
trends, missed follow-ups) before they become emergencies.

## Why memory is the whole product

Stateless chatbots forget everything between sessions. For a caregiver, that's not just
annoying — it's dangerous. When Dad's blood pressure spikes, the agent needs to know he
started a new Metoprolol dose on Tuesday, that he's on Warfarin, and that his BP has been
climbing all week. A generic chatbot can't hold that context. Anchor can, because **every
interaction is retained in a Hindsight memory bank** and recalled during reasoning.

Read more about [what agent memory is](https://vectorize.io/what-is-agent-memory) and how
[Hindsight](https://hindsight.vectorize.io/) makes it work.

## Features

- **Persistent medical memory** — symptoms, meds, labs, doctor notes, observations, all
  retained across weeks with timestamps.
- **The "Catch" engine** — Hindsight's observation consolidation detects contradictions
  across time (new med + existing med + symptom = risk) that a stateless agent would miss.
- **Temporal recall** — answers "what changed since last week?" using Hindsight's TEMPR
  4-way retrieval (semantic, keyword, graph, temporal).
- **Doctor-visit brief** — generates a one-page printable summary pulled from memory.
- **Safety by design** — directives flag drug interactions, never give dosage advice, and
  always cite sources. PII is redacted.

## Architecture

```
[Frontend] WhatsApp-style chat (Streamlit / FastAPI web UI)
     │
[Backend] FastAPI — the agent loop
     │
     ├── Hindsight Cloud (memory)  ← THE STAR
     │     ├── retain()   → store observations, notes, meds, labs
     │     ├── recall()   → TEMPR 4-way search (semantic/keyword/graph/temporal)
     │     └── reflect()  → disposition-aware, memory-grounded answers
     │
     └── LLM: Groq (gpt-oss-120b / qwen3-32b) with function calling
             (with robust error handling)
```

## Quick Start

### 1. Set up Hindsight

Use Hindsight Cloud ([ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io)) — use
promo code `MEMHACK99` for $50 free credits — or run the open-source Docker image:

```bash
export OPENAI_API_KEY=sk-xxx
export HINDSIGHT_API_LLM_API_KEY=$OPENAI_API_KEY

docker run -it --pull always --name hindsight --restart unless-stopped \
  --shm-size=1g -p 8888:8888 -p 9999:9999 \
  -e HINDSIGHT_API_LLM_API_KEY=$OPENAI_API_KEY \
  -v $HOME/.hindsight-docker:/home/hindsight/.pg0 \
  ghcr.io/vectorize-io/hindsight:latest
```

### 2. Install the client

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and set:

```bash
HINDSIGHT_BASE_URL=http://localhost:8888   # or your Cloud URL
HINDSIGHT_API_KEY=your-key-here
GROQ_API_KEY=your-groq-key
```

### 4. Create the memory bank

```bash
python -m memory.create_bank
```

### 5. Load the synthetic dataset (for the demo)

```bash
python -m data.load_demo_data
```

### 6. Run the agent

```bash
python -m agent.main
```

Then open the chat UI and ask:

> "Mom is dizzy, should I be worried?"

Watch Anchor recall three weeks of history, catch the drug-interaction risk, and draft a
doctor-visit brief.

## Project Layout

```
anchor/
├── backend/
│   ├── agent/
│   │   ├── main.py            # FastAPI app + agent loop
│   │   ├── loop.py            # reflect -> LLM -> retain cycle
│   │   └── catch.py           # The "Catch" risk-detection engine
│   ├── memory/
│   │   ├── create_bank.py     # mission / directives / disposition / mental models
│   │   └── client.py          # Hindsight client wrapper (retain/recall/reflect)
│   ├── data/
│   │   ├── synthetic.py       # realistic 3-week caregiver dataset generator
│   │   └── load_demo_data.py  # retain_batch into Hindsight
│   └── requirements.txt
├── frontend/
│   └── app.py                 # Streamlit chat UI + doctor brief
├── content/                   # articles, posts, scripts (see docs)
└── docs/
    ├── CONTENT_PLAN.md
    └── SUBMISSION_CHECKLIST.md
```

## Tech Stack

- **Memory:** Hindsight Cloud / open-source (retain, recall, reflect)
- **LLM:** Groq (`gpt-oss-120b`, `qwen3-32b`) via OpenAI-compatible API
- **Backend:** FastAPI + Python
- **Frontend:** Streamlit (fast, clean, demo-ready)
- **Data:** Synthetic caregiver history (realistic names, meds, BP readings, doctor notes)

## License

MIT

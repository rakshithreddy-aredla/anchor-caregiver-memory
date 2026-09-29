# Anchor — Content & Submission Plan (6-Person Team)

This doc is the single source of truth for who does what, what to publish, and
how to submit. Follow it top to bottom.

## Mandatory — do THIS first (all 6 members)

1. **Profile Review Form** (every member MUST complete, or the team is not
   reviewed): https://forms.gle/AXWnanWsEEir6xSP9
2. Register on **Hindsight Cloud** (https://ui.hindsight.vectorize.io) and add
   promo code `MEMHACK99` for $50 credits (billing section).
3. Create the GitHub repo from this folder and invite all 6 members.

## Final Submission form (ONE per team — team lead fills it)
https://forms.gle/cD7fCnPnkdVm2sH78
Requires: Email, Phone, Team Name, all member names, GitHub/Drive link,
LinkedIn post URL, Article URL, Video URL, Reddit Post URL, + feedback.

## Role assignments

| # | Role | Deliverables |
|---|---|---|
| P1 | Team Lead / Backend Agent | Final submission owner; backend loop; chat endpoint |
| P2 | Hindsight Memory Architect | memory/create_bank.py; bank config deep-dive |
| P3 | Frontend / Chat UI | frontend/app.py; doctor brief UI |
| P4 | Data & Edge Cases | data/synthetic.py; load demo data; edge cases |
| P5 | Demo & Video Lead | Record + edit demo video; thumbnail; upload YouTube |
| P6 | Content & Pitch Lead | Article drafts, LinkedIn posts, Reddit post, README |

## What to build (already scaffolded in this repo)

- `backend/memory/` — Hindsight bank config + client wrapper
- `backend/agent/` — loop, catch engine, FastAPI app, CLI
- `backend/data/` — synthetic 3-week caregiver dataset
- `frontend/app.py` — Streamlit chat + doctor brief

Run order:
```
pip install -r backend/requirements.txt
python -m memory.create_bank        # configure bank (mission/directives/disposition)
python -m data.load_demo_data       # load 3 weeks of history
uvicorn agent.main:app --reload     # backend on :8000
streamlit run frontend/app.py       # UI
```

## Content deliverables (per the content guide)

### Per team member (all 6):
- **1 Article** (800-1500 words) — drafts in `content/article-0X-*.md`. Each
  member edits/personalizes their own and publishes to a public link
  (Medium / Dev.to / Hashnode / Substack / LinkedIn Articles).
- **1 Social post** — LinkedIn post in `content/linkedin-post.md`. Post article
  URL as first comment, Hindsight GitHub as second comment.

### Per team (1):
- **1 Video** — script in `content/video-script.md`, thumbnail prompt in
  `content/thumbnail-prompt.md`. Upload public to YouTube.

### Team-wide:
- **1 Reddit post** — `content/reddit-post.md`. Link post on r/llmdevs,
  r/sideproject, r/aiagents, or r/aimemory.

## Content rules (read carefully — disqualifiers)
- **NEVER mention "hackathon"** in any article title/body or social post
  (including hashtags).
- Every article must embed these 3 links with natural anchor text:
  - Hindsight GitHub: https://github.com/vectorize-io/hindsight
  - Hindsight docs: https://hindsight.vectorize.io/
  - Vectorize agent memory: https://vectorize.io/what-is-agent-memory
- Articles must be public and linkable.

## Timeline (compressed — today is the deadline)
1. **Hour 0-1:** all 6 fill Profile form; create repo; register Hindsight Cloud.
2. **Hour 1-6:** backend agent loop + memory bank + demo data working end-to-end.
3. **Hour 6-12:** frontend UI + brief; start recording video.
4. **Hour 12-20:** publish articles + LinkedIn posts; record/edit/upload video.
5. **Hour 20-24:** Reddit post; fill final submission form; verify checklist.

## Verify the learning curve works before recording
Demo the 3 snapshots so the "catch" is honest:
- Day 1: "What do you know about my mom?" → generic
- Week 2: recalls baseline + meds
- Week 3: "Mom's dizzy." → catches the drug-interaction risk

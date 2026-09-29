# Anchor — Demo Video Script (~3 min, 1080p screen recording + voiceover)
# Assign to: Demo & Video Lead (P5). Record with OBS/Loom. No hackathon mention.

# ---- 1. Intro (30 sec) ----
NARRATION:
"Hi, I'm [NAME]. I built Anchor — an AI that remembers a family's medical
journey across weeks, so a caregiver never has to re-explain their parent's
history, and catches problems before they become emergencies."

ON SCREEN:
- You on camera (optional) then a clean title card: "Anchor — The Caregiver's
  Memory"
- Show the repo/README briefly.

# ---- 2. The problem (30 sec) ----
NARRATION:
"Here's the problem. A caregiver manages scattered info: meds, symptoms, lab
results, doctor calls. Ask a normal chatbot about it and look what happens —"

ON SCREEN:
- Open a plain chatbot, type: "Mom is dizzy, should I be worried?"
- It responds with generic, forgetful text ("I don't have context..."). Narrate
  the failure: it doesn't know your mom, her meds, or her baseline.

# ---- 3. The demo: learning curve + the catch (2 min) ----
NARRATION:
"Now Anchor. It uses Hindsight for memory. Every observation is retained. Watch
the learning curve — same question, different days."

ON SCREEN:
- Show the chat UI (frontend/app.py).
- Day 1: type "What do you know about my mom?" → "I just met you both."
- Week 2: same question → "Baseline BP 130/80, Warfarin + Metoprolol, 4
  symptoms this week."
- Point to the memory bank: show that these are REAL retained memories
  (backend/memory/client.py retain()).

NARRATION:
"Now the moment it earns its keep. Three weeks in —"

ON SCREEN:
- Type: "Mom is dizzy, should I be worried?"
- The agent recalls the trend: BP spiked to 165/92 after the Metoprolol dose
  was doubled on Tuesday, and she's on Warfarin. It flags a possible drug
  interaction and recommends contacting Dr. Patel.
- This is the "catch" — backend/agent/catch.py. Show the recall() calls and the
  risk flagging.

NARRATION:
"And one click turns that memory into something useful —"

ON SCREEN:
- Click "Generate brief" (frontend/app.py GET /brief).
- Show the clean one-page doctor brief: meds, conditions, this week's
  observations, care team.

# ---- 4. Wrap up (30 sec) ----
NARRATION:
"What surprised me: the same code answered Day 1, Week 2, and Week 3
differently — not because I changed the model, but because Hindsight's memory
changed. That's the real value of agent memory: it gets better every single
interaction. A generic chatbot would have said 'monitor it.' Anchor told us to
act."

ON SCREEN:
- Side-by-side: generic chatbot vs Anchor.
- End card: "Anchor — the AI that never forgets. Built on Hindsight."
  + link to the GitHub repo.

# ---- 5 High-performing YouTube titles ----
1. "AI Caught a Drug Interaction My Family's Doctor Missed"
2. "I Built an AI That Remembers Your Parent's Health — And It Just Saved Mine"
3. "Why Your Chatbot Forgets: Building an Agent With Real Memory"
4. "The AI Caregiver That Learns Your Mom's Baseline in 3 Weeks"
5. "Memory-Powered AI vs Stateless Chatbot — The Difference Is Life-Saving"

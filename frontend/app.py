"""Anchor - Streamlit chat UI.

WhatsApp-style chat for a caregiver plus a one-page doctor-visit brief.

Run:  streamlit run frontend/app.py
"""
from __future__ import annotations

import os
import sys

import requests
import streamlit as st

# Allow running from the repo root while importing backend modules.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

API_URL = os.getenv("ANCHOR_API_URL", "http://localhost:8000")

st.set_page_config(page_title="Anchor - Caregiver Memory", page_icon="🫀", layout="wide")

st.title("🫀 Anchor — The Caregiver's Memory")
st.caption("An AI that remembers your family member's full medical journey.")

# ---- Chat state ----
if "messages" not in st.session_state:
    st.session_state.messages = []


def send(message: str) -> None:
    """Post a message to the backend and append the reply."""
    st.session_state.messages.append({"role": "user", "content": message})
    try:
        resp = requests.post(
            f"{API_URL}/chat",
            json={"message": message},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        reply = data["answer"]
        if data.get("risk"):
            reply += f"\n\n🚨 **Risk flagged:** {data['risk_reason']}"
        st.session_state.messages.append({"role": "assistant", "content": reply})
    except Exception as exc:  # noqa: BLE001
        st.session_state.messages.append(
            {"role": "assistant", "content": f"(backend unreachable: {exc})"}
        )


# ---- Chat panel ----
col_chat, col_brief = st.columns([3, 2])

with col_chat:
    st.subheader("💬 Caregiver chat")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask about your parent, e.g. 'Mom is dizzy, should I worry?'")
    if prompt:
        send(prompt)
        st.rerun()

    with st.expander("Try these prompts"):
        st.write("• 'Mom is dizzy, should I be worried?'")
        st.write("• 'What's changed with Mom's blood pressure this week?'")
        st.write("• 'What medications is she on right now?'")

# ---- Doctor brief panel ----
with col_brief:
    st.subheader("📄 Doctor-visit brief")
    if st.button("Generate brief", type="primary"):
        try:
            resp = requests.get(f"{API_URL}/brief", timeout=60)
            resp.raise_for_status()
            st.markdown(resp.json()["brief"])
        except Exception as exc:  # noqa: BLE001
            st.error(f"Could not generate brief: {exc}")

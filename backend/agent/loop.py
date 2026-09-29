"""The Anchor agent loop.

Flow for each caregiver message:

1. reflect()   -> Hindsight grounds the answer in the family's memory,
                  applying mission, directives and disposition.
2. LLM         -> an optional structured step (function calling) used for
                  risk detection and for drafting the doctor brief.
3. retain()    -> the conversation outcome is stored back into memory so the
                  agent gets smarter with every interaction.

This is the "learning curve": interaction 1 is generic, interaction 20 knows
the parent's baseline and can catch things a stateless agent would miss.
"""
from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from memory.client import get_bank_id, reflect, retain

load_dotenv()

_SYSTEM = (
    "You are the reasoning layer of Anchor, a caregiver health navigator. "
    "You receive memory-grounded context from Hindsight plus the caregiver's "
    "message. Produce a short, warm, plain-English reply. If a drug "
    "interaction risk exists, say so and recommend contacting the provider. "
    "Never give dosage advice. Cite specific memories when you raise concern."
)


def _llm() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )


def _model() -> str:
    return os.getenv("GROQ_MODEL", "gpt-oss-120b")


def run_loop(user_message: str, bank_id: str | None = None,
             context: str | None = None) -> dict:
    """Handle one caregiver message and return an answer + risk summary.

    Returns:
        {"answer": str, "risk": bool, "risk_reason": str | None}
    """
    bank_id = bank_id or get_bank_id()

    # 1. Memory-grounded reasoning via Hindsight reflect().
    try:
        grounded = reflect(bank_id, user_message, context=context)
    except Exception as exc:  # noqa: BLE001 - surface gracefully to UI
        grounded = f"(memory unavailable: {exc})"

    # 2. Structured risk detection via LLM function calling.
    risk_reason = _detect_risk(bank_id, user_message, grounded)

    # 3. Compose the final answer.
    try:
        final = _compose_answer(grounded, risk_reason)
    except Exception:  # noqa: BLE001
        final = grounded

    # 4. Retain the outcome so the agent learns.
    try:
        retain(
            bank_id,
            f"Caregiver asked: {user_message}. Anchor replied and "
            f"{'flagged a possible risk: ' + risk_reason if risk_reason else 'gave guidance.'}",
            context="caregiver interaction",
            metadata={"risk": bool(risk_reason)},
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[anchor] retain failed: {exc}")

    return {
        "answer": final,
        "risk": bool(risk_reason),
        "risk_reason": risk_reason,
    }


def _detect_risk(bank_id: str, user_message: str, grounded: str) -> str | None:
    """Use LLM function calling to decide whether a risk should be raised.

    Robust to function-calling errors: any failure degrades to None (no risk
    raised) rather than crashing the whole loop.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "report_risk",
                "description": "Report a possible health/safety risk for the parent.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "risk": {
                            "type": "boolean",
                            "description": "True if a real risk (e.g. drug interaction, "
                                           "worsening trend) is indicated.",
                        },
                        "reason": {
                            "type": "string",
                            "description": "Plain-English reason grounded in memory.",
                        },
                    },
                    "required": ["risk", "reason"],
                },
            },
        }
    ]
    try:
        resp = _llm().chat.completions.create(
            model=_model(),
            messages=[
                {"role": "system",
                 "content": "You flag possible medical risks from the context."},
                {"role": "user", "content": f"CAREGIVER: {user_message}\nMEMORY: {grounded}"},
            ],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "report_risk"}},
        )
        tool_calls = resp.choices[0].message.tool_calls
        if not tool_calls:
            # Model ignored tool_choice; treat as "no risk" rather than crash.
            return None
        args = json.loads(tool_calls[0].function.arguments)
        if args.get("risk"):
            return args.get("reason")
        return None
    except Exception as exc:  # noqa: BLE001
        print(f"[anchor] risk detection degraded: {exc}")
        return None


def _compose_answer(grounded: str, risk_reason: str | None) -> str:
    """Final, warm reply. Falls back to the grounded text on LLM failure."""
    risk_line = (
        f"\n\nI want to flag something important: {risk_reason}. "
        "Please contact the relevant provider. I can draft a summary for you."
        if risk_reason
        else ""
    )
    return f"{grounded}{risk_line}"

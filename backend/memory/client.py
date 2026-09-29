"""Hindsight client wrapper for Anchor.

Thin, typed wrapper around the Hindsight Python client so the rest of the
app talks to a single module. Exposes the three core operations:

- retain:   store a memory (observation, doctor note, med change, symptom)
- recall:   search memories (TEMPR 4-way: semantic / keyword / graph / temporal)
- reflect:  memory-grounded, disposition-aware answer generation

Hindsight docs: https://hindsight.vectorize.io/
"""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()


@lru_cache(maxsize=1)
def get_client() -> Hindsight:
    """Return a cached Hindsight client from environment variables.

    Cached so every retain/recall/reflect reuses one connection pool instead
    of constructing a new client per call. Tests can reset via
    ``get_client.cache_clear()``.
    """
    base_url = os.getenv("HINDSIGHT_BASE_URL", "http://localhost:8888")
    api_key = os.getenv("HINDSIGHT_API_KEY")
    if api_key:
        return Hindsight(base_url=base_url, api_key=api_key)
    return Hindsight(base_url=base_url)


def get_bank_id() -> str:
    """Return the default memory bank id for this app."""
    return os.getenv("BANK_ID", "anchor_family_demo")


def retain(bank_id: str, content: str, *, context: str | None = None,
           timestamp=None, metadata: dict | None = None,
           document_id: str | None = None) -> None:
    """Store a memory in the given bank."""
    client = get_client()
    client.retain(
        bank_id=bank_id,
        content=content,
        context=context,
        timestamp=timestamp,
        metadata=metadata or {},
        document_id=document_id,
        retain_async=False,
    )


def retain_batch(bank_id: str, items: list[dict], *,
                 document_id: str | None = None) -> None:
    """Store many memories at once (used for loading demo history)."""
    client = get_client()
    client.retain_batch(
        bank_id=bank_id,
        items=items,
        document_id=document_id,
        retain_async=False,
    )


def recall(bank_id: str, query: str, *, types: list[str] | None = None,
           max_tokens: int = 4096, budget: str = "high",
           include_chunks: bool = False) -> list[str]:
    """Search memories and return the matched memory texts."""
    client = get_client()
    response = client.recall(
        bank_id=bank_id,
        query=query,
        types=types,
        max_tokens=max_tokens,
        budget=budget,
        include_chunks=include_chunks,
    )
    # Some server versions return results=None when nothing matches.
    return [r.text for r in (response.results or [])]


def reflect(bank_id: str, query: str, *, context: str | None = None,
            budget: str = "high") -> str:
    """Generate a memory-grounded, disposition-aware answer."""
    client = get_client()
    answer = client.reflect(
        bank_id=bank_id,
        query=query,
        context=context,
        budget=budget,
    )
    return answer.text

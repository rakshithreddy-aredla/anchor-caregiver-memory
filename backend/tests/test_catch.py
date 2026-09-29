"""Regression tests for the Catch engine (agent/catch.py).

Mocks the Hindsight recall (network boundary) - the engine's logic is tested
purely against canned memory results.
"""
from unittest.mock import patch

from agent.catch import TRIGGERS, catch

BLOOD_THINNER_MEDS = [
    "Margaret Chen takes Warfarin 5mg once daily (blood thinner).",
    "Dr. Patel started Metoprolol 50mg daily.",
]
PLAIN_MEDS = ["Margaret Chen takes Atorvastatin 20mg nightly."]


class TestCatchHappyPath:
    def test_flags_risk_for_symptom_with_blood_thinner(self):
        """Symptom + blood thinner in memory -> risk flagged with a reason."""
        with patch("agent.catch.recall") as mock_recall:
            mock_recall.side_effect = [BLOOD_THINNER_MEDS, []]
            result = catch(bank_id="b", symptom="Mom is dizzy, should I worry?")
        assert result["risk"] is True
        assert result["reason"] is not None
        assert "dizziness" in result["reason"]

    def test_no_risk_for_symptom_with_plain_meds(self):
        """Symptom but no blood thinner / med change -> no risk flagged."""
        with patch("agent.catch.recall") as mock_recall:
            mock_recall.side_effect = [PLAIN_MEDS, []]
            result = catch(bank_id="b", symptom="Mom feels dizzy")
        assert result["risk"] is False
        assert result["reason"] is None

    def test_evidence_combines_meds_and_trends(self):
        """Evidence list is the concatenation of med and trend recall results."""
        trends = ["BP 165/92 on day +17"]
        with patch("agent.catch.recall") as mock_recall:
            mock_recall.side_effect = [BLOOD_THINNER_MEDS, trends]
            result = catch(bank_id="b", symptom="dizzy")
        assert result["evidence"] == BLOOD_THINNER_MEDS + trends


class TestCatchBoundaries:
    def test_no_symptom_keyword_short_circuits_without_recalling(self):
        """Message with no symptom keyword -> no risk AND no recall calls."""
        with patch("agent.catch.recall") as mock_recall:
            result = catch(bank_id="b", symptom="What a lovely day")
        assert result == {"risk": False, "reason": None, "evidence": []}
        mock_recall.assert_not_called()

    def test_empty_meds_means_no_risk(self):
        """Empty medication memory -> both heuristics false -> no risk."""
        with patch("agent.catch.recall") as mock_recall:
            mock_recall.side_effect = [[], []]
            result = catch(bank_id="b", symptom="dizzy")
        assert result["risk"] is False

    def test_recall_failure_degrades_gracefully(self):
        """Hindsight unavailable -> returns a no-risk result, does not raise."""
        with patch("agent.catch.recall", side_effect=ConnectionError("down")):
            result = catch(bank_id="b", symptom="dizzy")
        assert result["risk"] is False
        assert result["reason"] is None
        assert result["evidence"] == []


class TestTriggerOrdering:
    def test_longer_phrases_listed_before_shorter_prefixes(self):
        """'dizzy spells' must be matched before 'dizzy' (prefix shadowing)."""
        phrases = list(TRIGGERS.keys())
        assert phrases.index("dizzy spells") < phrases.index("dizzy")

    def test_dizzy_spells_maps_to_dizziness(self):
        assert TRIGGERS["dizzy spells"] == "dizziness"

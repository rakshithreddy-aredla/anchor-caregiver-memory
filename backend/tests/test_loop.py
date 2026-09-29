"""Regression tests for the agent loop (agent/loop.py).

Mocks the Hindsight and LLM boundaries (network) - the loop's composition,
degradation, and retention behavior are tested in isolation.
"""
from unittest.mock import MagicMock, patch

from agent.loop import _detect_risk, run_loop


def _fake_tool_response(risk: bool, reason: str = "possible interaction"):
    """Build a fake OpenAI tool-calling response."""
    message = MagicMock()
    message.tool_calls = [MagicMock()]
    message.tool_calls[0].function.arguments = (
        f'{{"risk": {"true" if risk else "false"}, "reason": "{reason}"}}'
    )
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message = message
    return response


class TestRunLoop:
    def test_returns_answer_and_no_risk_when_detection_clears(self):
        """Happy path: reflect answers, detection finds no risk."""
        with patch("agent.loop.reflect", return_value="She is stable."), \
             patch("agent.loop._detect_risk", return_value=None), \
             patch("agent.loop.retain") as mock_retain:
            result = run_loop("How is Mom?", bank_id="b")
        assert result["answer"] == "She is stable."
        assert result["risk"] is False
        assert result["risk_reason"] is None
        mock_retain.assert_called_once()

    def test_risk_reason_merged_into_result(self):
        """Detection raising a risk -> result carries risk=True + reason."""
        with patch("agent.loop.reflect", return_value="She is stable."), \
             patch("agent.loop._detect_risk", return_value="interaction risk"), \
             patch("agent.loop.retain"):
            result = run_loop("Mom is dizzy", bank_id="b")
        assert result["risk"] is True
        assert result["risk_reason"] == "interaction risk"

    def test_reflect_failure_still_returns_an_answer(self):
        """Hindsight down -> graceful fallback text, loop does not crash."""
        with patch("agent.loop.reflect", side_effect=ConnectionError("down")), \
             patch("agent.loop._detect_risk", return_value=None), \
             patch("agent.loop.retain"):
            result = run_loop("How is Mom?", bank_id="b")
        assert "memory unavailable" in result["answer"]
        assert result["risk"] is False

    def test_retain_failure_does_not_crash_loop(self):
        """Retain raising -> logged, result still returned."""
        with patch("agent.loop.reflect", return_value="ok"), \
             patch("agent.loop._detect_risk", return_value=None), \
             patch("agent.loop.retain", side_effect=RuntimeError("write failed")):
            result = run_loop("How is Mom?", bank_id="b")
        assert result["answer"] == "ok"

    def test_bank_id_defaults_when_none(self):
        """bank_id=None -> falls back to the configured default bank."""
        with patch("agent.loop.get_bank_id", return_value="default-bank"), \
             patch("agent.loop.reflect", return_value="ok") as mock_reflect, \
             patch("agent.loop._detect_risk", return_value=None), \
             patch("agent.loop.retain") as mock_retain:
            run_loop("How is Mom?")
        assert mock_reflect.call_args.args[0] == "default-bank"
        assert mock_retain.call_args.args[0] == "default-bank"


class TestDetectRisk:
    def test_returns_reason_when_tool_reports_risk(self):
        with patch("agent.loop._llm") as mock_llm:
            mock_llm.return_value.chat.completions.create.return_value = (
                _fake_tool_response(risk=True, reason="drug interaction")
            )
            assert _detect_risk("b", "Mom is dizzy", "context") == "drug interaction"

    def test_returns_none_when_tool_clears_risk(self):
        with patch("agent.loop._llm") as mock_llm:
            mock_llm.return_value.chat.completions.create.return_value = (
                _fake_tool_response(risk=False)
            )
            assert _detect_risk("b", "How is Mom?", "context") is None

    def test_degrades_to_none_when_no_tool_call_returned(self):
        """Model ignored tool_choice (tool_calls=None) -> None, not a crash."""
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.tool_calls = None
        with patch("agent.loop._llm") as mock_llm:
            mock_llm.return_value.chat.completions.create.return_value = response
            assert _detect_risk("b", "Mom is dizzy", "context") is None

    def test_degrades_to_none_when_llm_raises(self):
        """LLM unavailable/function-calling error -> None, loop continues."""
        with patch("agent.loop._llm", side_effect=RuntimeError("no key")):
            assert _detect_risk("b", "Mom is dizzy", "context") is None

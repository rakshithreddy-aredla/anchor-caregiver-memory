"""Regression tests for the CLI (agent/cli.py).

Guards the argument order of run_loop: the user message must come first.
"""
from unittest.mock import patch

from agent import cli


class TestCli:
    def test_run_loop_receives_message_first_then_bank_id(self):
        """Regression: run_loop(bank_id, message) swapped args after the
        signature was reordered to (user_message, bank_id)."""
        with patch("agent.cli.get_bank_id", return_value="default-bank"), \
             patch("agent.cli.run_loop") as mock_loop, \
             patch("builtins.input", side_effect=["How is Mom?", "quit"]), \
             patch("builtins.print"):
            cli.main()
        assert mock_loop.call_args.args == ("How is Mom?", "default-bank")

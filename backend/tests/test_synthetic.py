"""Regression tests for the synthetic dataset (data/synthetic.py)."""
import json
from datetime import datetime

from data.synthetic import DEFAULT_JSONL_PATH, PARENT, generate, to_jsonl


class TestGenerate:
    def test_items_have_datetime_timestamps(self):
        """Timestamps must be datetime objects per Hindsight's retain contract."""
        items = generate()
        assert all(isinstance(it["timestamp"], datetime) for it in items)

    def test_items_have_content_and_context(self):
        items = generate()
        assert all(it["content"] and it["context"] for it in items)

    def test_baseline_stored_before_deviations(self):
        """Profile + meds come first so the agent can learn the baseline."""
        items = generate()
        assert items[0]["context"] == "profile"
        assert PARENT["baseline_bp"] in items[0]["content"]

    def test_story_arc_ends_on_the_catch(self):
        """The final entry is the BP spike + dizziness scenario to catch."""
        items = generate()
        last = items[-1]
        assert "165/92" in last["content"]
        assert "dizzy" in last["content"].lower()

    def test_timestamps_are_monotonically_increasing(self):
        """Temporal recall requires ordered timestamps."""
        items = generate()
        ts = [it["timestamp"] for it in items]
        assert ts == sorted(ts)

    def test_custom_start_date_is_respected(self):
        items = generate(start=datetime(2025, 1, 1, 8, 0, 0))
        assert items[0]["timestamp"] == datetime(2025, 1, 1, 8, 0, 0)


class TestToJsonl:
    def test_writes_jsonl_with_iso_timestamps(self, tmp_path):
        path = tmp_path / "demo.jsonl"
        to_jsonl(str(path))
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == len(generate())
        row = json.loads(lines[0])
        # JSONL serializes datetime as an ISO string.
        assert isinstance(row["timestamp"], str)
        datetime.fromisoformat(row["timestamp"])

    def test_default_path_writes_next_to_module(self):
        """Default path must resolve relative to the module, not cwd."""
        assert DEFAULT_JSONL_PATH.endswith("demo_data.jsonl")

    def test_creates_missing_parent_dirs(self, tmp_path):
        path = tmp_path / "nested" / "dir" / "demo.jsonl"
        to_jsonl(str(path))
        assert path.exists()

from __future__ import annotations

from goodcode.gui.session_stats import SessionStats


def test_record_accumulates_runs_and_finds() -> None:
    session = SessionStats()

    session.record(file_name="a.py", finding_count=3, category_count=2)
    session.record(file_name="b.py", finding_count=1, category_count=1)

    assert session.runs == 2
    assert session.total_finds == 4
    assert session.last.file_name == "b.py"


def test_history_keeps_only_most_recent_eight_entries() -> None:
    session = SessionStats()

    for i in range(10):
        session.record(file_name=f"file{i}.py", finding_count=1, category_count=1)

    assert len(session.history) == 8
    assert session.history[0].file_name == "file9.py"


def test_reset_clears_all_state() -> None:
    session = SessionStats()
    session.record(file_name="a.py", finding_count=3, category_count=2)

    session.reset()

    assert session.runs == 0
    assert session.total_finds == 0
    assert session.history == []
    assert session.last is None

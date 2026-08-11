from __future__ import annotations

from goodcode.gui import rankings
from goodcode.gui.session_stats import SessionStats


def test_leaderboard_places_me_by_score_among_sample_ranks() -> None:
    session = SessionStats()
    session.record(file_name="a.py", finding_count=200, category_count=6)

    board = rankings.leaderboard(session)
    me = next(row for row in board if row.get("me"))

    assert me["rank"] == 1
    assert me["tier"] == "t-king"
    assert len(board) == len(rankings.SAMPLE_RANKS) + 1


def test_leaderboard_me_defaults_to_last_place_with_no_scans() -> None:
    session = SessionStats()

    board = rankings.leaderboard(session)
    me = next(row for row in board if row.get("me"))

    assert me["finds"] == 0
    assert me["rank"] == len(board)


def test_tier_of_matches_thresholds() -> None:
    assert rankings.tier_of(0) == "t-new"
    assert rankings.tier_of(25) == "t-pro"
    assert rankings.tier_of(90) == "t-elite"
    assert rankings.tier_of(120) == "t-king"


def test_next_tier_gap_counts_down_to_next_threshold() -> None:
    assert rankings.next_tier_gap(0) == 25
    assert rankings.next_tier_gap(24) == 1
    assert rankings.next_tier_gap(25) == 65
    assert rankings.next_tier_gap(120) is None

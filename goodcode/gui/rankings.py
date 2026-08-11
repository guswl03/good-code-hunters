from __future__ import annotations

from goodcode.gui.session_stats import SessionStats

SAMPLE_RANKS: list[dict] = [
    {"name": "hoxy_secure", "team": "SecOps 스터디", "finds": 128, "cats": 6},
    {"name": "ast_walker", "team": "코드리뷰 길드", "finds": 111, "cats": 6},
    {"name": "saltnpepper", "team": "백엔드 4팀", "finds": 97, "cats": 5},
    {"name": "compare_dgst", "team": "플랫폼 보안", "finds": 74, "cats": 5},
    {"name": "yaml_safe", "team": "데브옵스", "finds": 61, "cats": 4},
    {"name": "pbkdf2_kim", "team": "신입 부트캠프", "finds": 43, "cats": 4},
    {"name": "subproc_lee", "team": "QA 자동화", "finds": 28, "cats": 3},
    {"name": "newbie_park", "team": "학생 개발자", "finds": 12, "cats": 2},
]

TIER_LABELS = {
    "t-new": "신입",
    "t-pro": "정예",
    "t-elite": "특급",
    "t-king": "검거왕",
}

_TIER_THRESHOLDS = (120, "t-king"), (90, "t-elite"), (25, "t-pro")


def tier_of(finds: int) -> str:
    for threshold, tier in _TIER_THRESHOLDS:
        if finds >= threshold:
            return tier
    return "t-new"


def next_tier_gap(finds: int) -> int | None:
    for threshold in (25, 90, 120):
        if threshold > finds:
            return threshold - finds
    return None


def leaderboard(session: SessionStats) -> list[dict]:
    last = session.last
    me = {
        "me": True,
        "name": "나 (이번 세션)",
        "team": last.file_name if last else "아직 분석 기록 없음",
        "finds": session.total_finds,
        "cats": last.category_count if last else 0,
    }

    rows = [dict(row) for row in SAMPLE_RANKS] + [me]
    rows.sort(key=lambda row: (-row["finds"], -row["cats"]))
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
        row["tier"] = tier_of(row["finds"])
    return rows

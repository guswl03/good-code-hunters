from __future__ import annotations

from goodcode.gui.rulebook_data import CATEGORY_LABELS, RULES


def test_rulebook_only_lists_implemented_rules() -> None:
    assert [rule["id"] for rule in RULES] == ["GOOD004", "GOOD005", "GOOD006"]


def test_every_rule_has_a_known_category_label() -> None:
    for rule in RULES:
        assert rule["category"] in CATEGORY_LABELS


def test_every_rule_has_good_and_bad_examples() -> None:
    for rule in RULES:
        assert rule["good"]
        assert rule["bad"]
        assert rule["ref"]

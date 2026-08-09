from __future__ import annotations

from collections.abc import Iterable

from goodcode.rules.base import Rule

_REGISTERED_RULES: list[Rule] = []


def register_rule(rule: Rule) -> None:
    _REGISTERED_RULES.append(rule)


def replace_rules(rules: Iterable[Rule]) -> None:
    _REGISTERED_RULES.clear()
    _REGISTERED_RULES.extend(rules)


def get_registered_rules() -> list[Rule]:
    return list(_REGISTERED_RULES)
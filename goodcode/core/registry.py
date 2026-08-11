from __future__ import annotations

from collections.abc import Iterable

from goodcode.rules.base import Rule
from goodcode.rules.constant_time import ConstantTimeComparisonRule
from goodcode.rules.password_hashing import PasswordHashingRule
from goodcode.rules.secure_random import SecureRandomnessRule
from goodcode.rules.sql import ParameterizedSqlQueryRule
from goodcode.rules.subprocess_rule import SaferSubprocessInvocationRule
from goodcode.rules.yaml_safe_load import SafeYamlDeserializationRule


# ===
# 만든 이유: production의 scan_file()이 별도 설정 없이 P0 규칙 6개를 항상 실행해야 한다.
# 코드 설명: 각 호출마다 새 Rule 객체를 만들어 테스트에서 변경된 Registry를 안전하게 복구한다.
# ===
def _default_rules() -> list[Rule]:
    return [
        ParameterizedSqlQueryRule(),
        SecureRandomnessRule(),
        PasswordHashingRule(),
        ConstantTimeComparisonRule(),
        SaferSubprocessInvocationRule(),
        SafeYamlDeserializationRule(),
    ]


_REGISTERED_RULES: list[Rule] = _default_rules()


def register_rule(rule: Rule) -> None:
    if any(registered.rule_id == rule.rule_id for registered in _REGISTERED_RULES):
        return
    _REGISTERED_RULES.append(rule)


def replace_rules(rules: Iterable[Rule]) -> None:
    _REGISTERED_RULES.clear()
    _REGISTERED_RULES.extend(rules)


def get_registered_rules() -> list[Rule]:
    return list(_REGISTERED_RULES)


def reset_rules() -> None:
    # ===
    # 만든 이유: 단위 테스트가 Registry를 교체한 뒤에도 기본 P0 상태를 결정적으로 복원해야 한다.
    # 코드 설명: GOOD001부터 GOOD006까지 새 객체로 전체 목록을 교체한다.
    # ===
    replace_rules(_default_rules())

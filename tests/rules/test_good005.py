import ast
from pathlib import Path

from goodcode.core.import_resolver import build_import_alias_context
from goodcode.core.source import SourceHelper
from goodcode.rules.subprocess_rule import SaferSubprocessInvocationRule

FIXTURES = Path(__file__).parents[1] / "fixtures" / "good005"


# ===
# 만든 이유: 리스트 인자와 shell 미사용을 모두 만족할 때만 GOOD005가 생성되는지 검증한다.
# 코드 설명: 안전 호출과 shell=True 문자열 호출을 각각 Positive/Negative fixture로 비교한다.
# ===
def test_good005_detects_list_arguments_without_shell() -> None:
    findings = _scan_fixture("positive.py")
    assert len(findings) == 1
    assert findings[0].rule_id == "GOOD005"


def test_good005_ignores_string_command_with_shell() -> None:
    assert _scan_fixture("negative.py") == []


def _scan_fixture(name: str):
    source_text = (FIXTURES / name).read_text(encoding="utf-8")
    tree = ast.parse(source_text)
    return SaferSubprocessInvocationRule(name).check(
        tree,
        SourceHelper(source_text),
        build_import_alias_context(tree),
    )

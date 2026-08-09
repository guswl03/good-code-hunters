import ast
from pathlib import Path

from goodcode.core.import_resolver import build_import_alias_context
from goodcode.core.source import SourceHelper
from goodcode.rules.constant_time import ConstantTimeComparisonRule

FIXTURES = Path(__file__).parents[1] / "fixtures" / "good004"


# ===
# 만든 이유: GOOD004가 명확한 Positive만 탐지하고 일반 비교를 오탐하지 않는지 고정한다.
# 코드 설명: fixture를 AST로만 읽어 Rule 결과의 ID, 파일, evidence를 검증한다.
# ===
def test_good004_detects_compare_digest_alias() -> None:
    findings = _scan_fixture("positive.py")
    assert len(findings) == 1
    assert findings[0].rule_id == "GOOD004"
    assert findings[0].file == "positive.py"
    assert "compare_digest" in findings[0].evidence


def test_good004_ignores_normal_equality() -> None:
    assert _scan_fixture("negative.py") == []


def _scan_fixture(name: str):
    source_text = (FIXTURES / name).read_text(encoding="utf-8")
    tree = ast.parse(source_text)
    return ConstantTimeComparisonRule(name).check(
        tree,
        SourceHelper(source_text),
        build_import_alias_context(tree),
    )

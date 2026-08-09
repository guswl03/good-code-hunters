import ast
from pathlib import Path

from goodcode.core.import_resolver import build_import_alias_context
from goodcode.core.source import SourceHelper
from goodcode.rules.yaml_safe_load import SafeYamlDeserializationRule

FIXTURES = Path(__file__).parents[1] / "fixtures" / "good006"


# ===
# 만든 이유: GOOD006이 safe_load alias만 찾고 yaml.load를 긍정 근거로 오탐하지 않게 한다.
# 코드 설명: yaml 패키지를 실행하거나 import하지 않고 AST fixture만 분석한다.
# ===
def test_good006_detects_safe_load_symbol_alias() -> None:
    findings = _scan_fixture("positive.py")
    assert len(findings) == 1
    assert findings[0].rule_id == "GOOD006"


def test_good006_ignores_yaml_load() -> None:
    assert _scan_fixture("negative.py") == []


def _scan_fixture(name: str):
    source_text = (FIXTURES / name).read_text(encoding="utf-8")
    tree = ast.parse(source_text)
    return SafeYamlDeserializationRule(name).check(
        tree,
        SourceHelper(source_text),
        build_import_alias_context(tree),
    )

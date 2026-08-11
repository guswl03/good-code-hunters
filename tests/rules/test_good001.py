import ast
from pathlib import Path

from goodcode.core.import_resolver import build_import_alias_context
from goodcode.core.source import SourceHelper
from goodcode.rules.sql import ParameterizedSqlQueryRule

FIXTURES = Path(__file__).parents[1] / "fixtures" / "good001"


def test_good001_detects_supported_parameterized_queries() -> None:
    findings = _scan_fixture("positive.py")

    assert len(findings) == 3
    assert [finding.rule_id for finding in findings] == ["GOOD001"] * 3
    assert [finding.line for finding in findings] == [2, 3, 4]
    assert [finding.column for finding in findings] == [5, 5, 5]
    assert all(finding.file == "positive.py" for finding in findings)
    assert all(finding.name == "Parameterized SQL Query" for finding in findings)
    assert all(finding.category == "injection-prevention" for finding in findings)
    assert all(finding.confidence == "HIGH" for finding in findings)
    assert all("parameterized query" in finding.message for finding in findings)
    assert "WHERE id = ?" in findings[0].evidence
    assert "VALUES (%s)" in findings[1].evidence
    assert "name = :name" in findings[2].evidence


def test_good001_ignores_assembled_and_non_parameterized_sql() -> None:
    assert _scan_fixture("negative.py") == []


def _scan_fixture(name: str):
    source_text = (FIXTURES / name).read_text(encoding="utf-8")
    tree = ast.parse(source_text)
    return ParameterizedSqlQueryRule(name).check(
        tree,
        SourceHelper(source_text),
        build_import_alias_context(tree),
    )

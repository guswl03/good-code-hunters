from __future__ import annotations

from pathlib import Path

from goodcode.core.models import (
    GOOD_PATTERNS_FOUND,
    NO_GOOD_PATTERNS_FOUND,
    PARSE_ERROR,
    READ_ERROR,
    Finding,
)
from goodcode.core.registry import replace_rules
from goodcode.core.service import scan_file


class UnsortedRule:
    rule_id = "TEST999"

    def check(self, tree, source, imports):
        return [
            Finding(
                rule_id="B",
                name="Rule B",
                category="tests",
                confidence="HIGH",
                file="sample.py",
                line=10,
                column=2,
                evidence="z()",
                message="later",
            ),
            Finding(
                rule_id="A",
                name="Rule A",
                category="tests",
                confidence="HIGH",
                file="sample.py",
                line=5,
                column=3,
                evidence="b()",
                message="first",
            ),
            Finding(
                rule_id="A",
                name="Rule A",
                category="tests",
                confidence="HIGH",
                file="sample.py",
                line=5,
                column=1,
                evidence="a()",
                message="sorted",
            ),
        ]


def test_scan_file_returns_empty_findings_for_plain_python(tmp_path: Path) -> None:
    replace_rules([])
    target = tmp_path / "sample.py"
    target.write_text("value = 1\n", encoding="utf-8")

    result = scan_file(str(target))

    assert result.target == str(target)
    assert result.status == NO_GOOD_PATTERNS_FOUND
    assert result.findings == []
    assert result.warnings == []


def test_scan_file_sorts_findings_deterministically(tmp_path: Path) -> None:
    replace_rules([UnsortedRule()])
    target = tmp_path / "sample.py"
    target.write_text("value = 1\n", encoding="utf-8")

    result = scan_file(str(target))

    assert result.status == GOOD_PATTERNS_FOUND
    assert [(f.line, f.column, f.rule_id) for f in result.findings] == [
        (5, 1, "A"),
        (5, 3, "A"),
        (10, 2, "B"),
    ]


def test_scan_file_returns_parse_error_status(tmp_path: Path) -> None:
    replace_rules([])
    target = tmp_path / "broken.py"
    target.write_text("def broken(:\n", encoding="utf-8")

    result = scan_file(str(target))

    assert result.status == PARSE_ERROR
    assert result.findings == []
    assert result.warnings


def test_scan_file_returns_read_error_status_for_missing_file(tmp_path: Path) -> None:
    replace_rules([])

    result = scan_file(str(tmp_path / "missing.py"))

    assert result.status == READ_ERROR
    assert result.findings == []
    assert result.warnings


def test_scan_file_returns_read_error_status_for_non_python_input(tmp_path: Path) -> None:
    replace_rules([])
    target = tmp_path / "sample.txt"
    target.write_text("value = 1\n", encoding="utf-8")

    result = scan_file(str(target))

    assert result.status == READ_ERROR
    assert result.findings == []
    assert result.warnings == [f"Expected a .py file: {target}"]


def test_scan_file_does_not_execute_target_code(tmp_path: Path, monkeypatch) -> None:
    replace_rules([])
    target = tmp_path / "side_effect.py"
    marker = tmp_path / "SHOULD_NOT_EXIST.txt"

    target.write_text(
        "from pathlib import Path\n"
        "Path('SHOULD_NOT_EXIST.txt').write_text('executed', encoding='utf-8')\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    scan_file(str(target))

    assert not marker.exists()
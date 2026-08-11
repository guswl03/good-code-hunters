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


class WrongFileRule:
    rule_id = "TEST001"

    def __init__(self, finding_file: str = "") -> None:
        self.finding_file = finding_file

    def check(self, tree, source, imports):
        return [
            Finding(
                rule_id=self.rule_id,
                name="Path Test Rule",
                category="tests",
                confidence="HIGH",
                file=self.finding_file,
                line=1,
                column=0,
                evidence="value = 1",
                message="path test",
            )
        ]


def test_scan_file_returns_empty_findings_for_plain_python(
    tmp_path: Path,
) -> None:
    replace_rules([])

    target = tmp_path / "sample.py"
    target.write_text("value = 1\n", encoding="utf-8")

    result = scan_file(str(target))

    assert result.target == str(target)
    assert result.status == NO_GOOD_PATTERNS_FOUND
    assert result.findings == []
    assert result.warnings == []


def test_scan_file_sorts_findings_deterministically(
    tmp_path: Path,
) -> None:
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


def test_scan_file_sets_current_path_on_every_finding(
    tmp_path: Path,
) -> None:
    replace_rules([WrongFileRule(finding_file="")])

    target = tmp_path / "current.py"
    target.write_text("value = 1\n", encoding="utf-8")

    result = scan_file(str(target))

    assert result.status == GOOD_PATTERNS_FOUND
    assert result.target == str(target)
    assert [finding.file for finding in result.findings] == [str(target)]


def test_scan_file_overrides_wrong_rule_path(
    tmp_path: Path,
) -> None:
    replace_rules([WrongFileRule(finding_file="old.py")])

    target = tmp_path / "current.py"
    target.write_text("value = 1\n", encoding="utf-8")

    result = scan_file(str(target))

    assert result.status == GOOD_PATTERNS_FOUND
    assert result.findings[0].file == str(target)


def test_consecutive_scans_do_not_mix_finding_paths(
    tmp_path: Path,
) -> None:
    replace_rules([WrongFileRule(finding_file="stale.py")])

    first = tmp_path / "first.py"
    second = tmp_path / "second.py"

    first.write_text("first_value = 1\n", encoding="utf-8")
    second.write_text("second_value = 2\n", encoding="utf-8")

    first_result = scan_file(str(first))
    second_result = scan_file(str(second))

    assert [finding.file for finding in first_result.findings] == [str(first)]
    assert [finding.file for finding in second_result.findings] == [str(second)]

    # 두 번째 분석이 끝난 뒤에도 첫 번째 결과의 경로가 유지되어야 한다.
    assert first_result.findings[0].file == str(first)


def test_scan_file_returns_parse_error_status(
    tmp_path: Path,
) -> None:
    replace_rules([])

    target = tmp_path / "broken.py"
    target.write_text("def broken(:\n", encoding="utf-8")

    result = scan_file(str(target))

    assert result.target == str(target)
    assert result.status == PARSE_ERROR
    assert result.findings == []
    assert result.warnings


def test_scan_file_returns_read_error_status_for_missing_file(
    tmp_path: Path,
) -> None:
    replace_rules([])

    target = tmp_path / "missing.py"
    result = scan_file(str(target))

    assert result.target == str(target)
    assert result.status == READ_ERROR
    assert result.findings == []
    assert result.warnings


def test_scan_file_returns_read_error_for_invalid_utf8(tmp_path: Path) -> None:
    replace_rules([])
    target = tmp_path / "invalid_utf8.py"
    target.write_bytes(b"\xff\xfe\x00")

    result = scan_file(str(target))

    assert result.target == str(target)
    assert result.status == READ_ERROR
    assert result.findings == []
    assert result.warnings


def test_scan_file_returns_read_error_status_for_non_python_input(
    tmp_path: Path,
) -> None:
    replace_rules([])

    target = tmp_path / "sample.txt"
    target.write_text("value = 1\n", encoding="utf-8")

    result = scan_file(str(target))

    assert result.target == str(target)
    assert result.status == READ_ERROR
    assert result.findings == []
    assert result.warnings == [f"Expected a .py file: {target}"]


def test_scan_file_does_not_execute_target_code(
    tmp_path: Path,
    monkeypatch,
) -> None:
    replace_rules([])

    target = tmp_path / "side_effect.py"
    marker = tmp_path / "SHOULD_NOT_EXIST.txt"

    target.write_text(
        "from pathlib import Path\n"
        "Path('SHOULD_NOT_EXIST.txt').write_text("
        "'executed', encoding='utf-8'"
        ")\n",
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)
    result = scan_file(str(target))

    assert result.status == NO_GOOD_PATTERNS_FOUND
    assert not marker.exists()

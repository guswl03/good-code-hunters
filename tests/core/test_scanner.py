from pathlib import Path

from goodcode.core.models import Finding
from goodcode.core.registry import replace_rules
from goodcode.core.service import scan_file


class UnsortedRule:
    rule_id = "TEST999"

    def check(self, tree, source, imports):
        return [
            Finding(rule_id="B", line=10, code="z()", message="later"),
            Finding(rule_id="A", line=5, code="b()", message="first"),
            Finding(rule_id="A", line=5, code="a()", message="sorted"),
        ]


def test_scan_file_returns_empty_findings_for_plain_python(tmp_path: Path) -> None:
    replace_rules([])
    target = tmp_path / "sample.py"
    target.write_text("value = 1\n", encoding="utf-8")

    result = scan_file(str(target))

    assert result.findings == []


def test_scan_file_sorts_findings_deterministically(tmp_path: Path) -> None:
    replace_rules([UnsortedRule()])
    target = tmp_path / "sample.py"
    target.write_text("value = 1\n", encoding="utf-8")

    result = scan_file(str(target))

    assert [(f.line, f.rule_id, f.code) for f in result.findings] == [
        (5, "A", "a()"),
        (5, "A", "b()"),
        (10, "B", "z()"),
    ]


def test_scan_file_does_not_execute_target_code(tmp_path: Path) -> None:
    replace_rules([])
    target = tmp_path / "side_effect.py"
    marker = tmp_path / "SHOULD_NOT_EXIST.txt"

    target.write_text(
        "from pathlib import Path\n"
        "Path('SHOULD_NOT_EXIST.txt').write_text('executed', encoding='utf-8')\n",
        encoding="utf-8",
    )

    scan_file(str(target))

    assert not marker.exists()
from __future__ import annotations

import ast
from pathlib import Path

from goodcode.core.import_resolver import build_import_alias_context
from goodcode.core.models import (
    GOOD_PATTERNS_FOUND,
    NO_GOOD_PATTERNS_FOUND,
    PARSE_ERROR,
    READ_ERROR,
    Finding,
    ScanResult,
)
from goodcode.core.registry import get_registered_rules
from goodcode.core.source import SourceHelper


def read_python_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sorted_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda item: (item.line, item.column, item.rule_id))


def scan_path(path: Path) -> ScanResult:
    try:
        source = read_python_source(path)
    except OSError as exc:
        return ScanResult(
            findings=[],
            target=str(path),
            status=READ_ERROR,
            warnings=[str(exc)],
        )

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        warning = f"Line {exc.lineno}: {exc.msg}" if exc.lineno else exc.msg
        return ScanResult(
            findings=[],
            target=str(path),
            status=PARSE_ERROR,
            warnings=[warning],
        )

    source_helper = SourceHelper(source=source)
    imports = build_import_alias_context(tree)

    findings: list[Finding] = []
    for rule in get_registered_rules():
        findings.extend(rule.check(tree=tree, source=source_helper, imports=imports))

    sorted_findings = _sorted_findings(findings)
    status = GOOD_PATTERNS_FOUND if sorted_findings else NO_GOOD_PATTERNS_FOUND

    return ScanResult(
        findings=sorted_findings,
        target=str(path),
        status=status,
        warnings=[],
    )
from __future__ import annotations

import ast
from pathlib import Path

from goodcode.core.import_resolver import build_import_alias_context
from goodcode.core.models import Finding, ScanResult
from goodcode.core.registry import get_registered_rules
from goodcode.core.source import SourceHelper


def read_python_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sorted_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda item: (item.line, item.rule_id, item.code))


def scan_path(path: Path) -> ScanResult:
    source = read_python_source(path)
    tree = ast.parse(source, filename=str(path))
    source_helper = SourceHelper(source=source)
    imports = build_import_alias_context(tree)

    findings: list[Finding] = []
    for rule in get_registered_rules():
        findings.extend(rule.check(tree=tree, source=source_helper, imports=imports))

    return ScanResult(
        target_file=str(path),
        findings=_sorted_findings(findings),
    )
from __future__ import annotations

import ast
from dataclasses import replace
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


def _with_current_file(findings: list[Finding], path: Path) -> list[Finding]:
    # ===
    # 만든 이유: Rule이 빈 경로나 이전 분석 경로를 반환해도 현재 분석 파일 경로를 보장하기 위해 필요하다.
    # 코드 설명: frozen Finding을 직접 변경하지 않고 file 필드만 현재 분석 경로로 바꾼 복사본을 생성한다.
    # ===
    current_file = str(path)
    return [replace(finding, file=current_file) for finding in findings]


def _sorted_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(
        findings,
        key=lambda item: (item.line, item.column, item.rule_id),
    )


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
        findings.extend(
            rule.check(
                tree=tree,
                source=source_helper,
                imports=imports,
            )
        )

    # ===
    # 만든 이유: Registry에서 재사용되는 Rule의 Finding에 빈 경로나 이전 경로가 남는 문제를 방지하기 위해 필요하다.
    # 코드 설명: 모든 Rule 결과를 현재 분석 파일 경로로 정규화한 뒤 기존 정렬 순서를 적용한다.
    # ===
    normalized_findings = _with_current_file(findings, path)
    sorted_findings = _sorted_findings(normalized_findings)

    status = (
        GOOD_PATTERNS_FOUND
        if sorted_findings
        else NO_GOOD_PATTERNS_FOUND
    )

    return ScanResult(
        findings=sorted_findings,
        target=str(path),
        status=status,
        warnings=[],
    )
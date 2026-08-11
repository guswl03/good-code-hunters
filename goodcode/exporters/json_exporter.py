from __future__ import annotations

import json
from pathlib import Path

from goodcode.core.models import ScanResult


# ===
# 만든 이유: GUI와 테스트가 같은 안정적인 JSON 계약을 사용하도록 변환 책임을 한곳에 모은다.
# 코드 설명: ScanResult를 PRD 순서의 사전으로 바꾸고 Finding 개수와 카테고리 개수를 계산한다.
# ===
def scan_result_to_dict(result: ScanResult) -> dict[str, object]:
    findings = [
        {
            "rule_id": finding.rule_id,
            "name": finding.name,
            "category": finding.category,
            "confidence": finding.confidence,
            "line": finding.line,
            "column": finding.column,
            "evidence": finding.evidence,
            "message": finding.message,
        }
        for finding in result.findings
    ]
    categories = {finding.category for finding in result.findings}

    return {
        "schema_version": result.schema_version,
        "tool_version": result.tool_version,
        "target": result.target,
        "status": result.status,
        "summary": {
            "findings": len(result.findings),
            "categories": len(categories),
        },
        "findings": findings,
        "warnings": list(result.warnings),
    }


# ===
# 만든 이유: 파일 저장 전에도 GUI나 테스트가 동일한 JSON 문자열을 사용할 수 있게 한다.
# 코드 설명: 한글을 그대로 보존하고 들여쓰기와 마지막 줄바꿈을 고정해 결과를 결정적으로 만든다.
# ===
def scan_result_to_json(result: ScanResult) -> str:
    return json.dumps(
        scan_result_to_dict(result),
        ensure_ascii=False,
        indent=2,
    ) + "\n"


# ===
# 만든 이유: GUI는 저장 경로만 선택하고 실제 UTF-8 파일 저장은 독립 Exporter에 맡겨야 한다.
# 코드 설명: 기존 폴더 안의 지정 경로에 JSON을 쓰고 저장된 Path를 호출자에게 돌려준다.
# ===
def export_scan_result(result: ScanResult, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.write_text(scan_result_to_json(result), encoding="utf-8")
    return path

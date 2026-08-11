from __future__ import annotations

import json
from pathlib import Path

from goodcode.core.models import GOOD_PATTERNS_FOUND, Finding, ScanResult
from goodcode.exporters.json_exporter import (
    export_scan_result,
    scan_result_to_dict,
    scan_result_to_json,
)

GOLDEN = Path(__file__).parent / "golden" / "scan_result.json"


# ===
# 만든 이유: Exporter 변경으로 발표 및 연동용 JSON 계약이 조용히 깨지는 일을 방지한다.
# 코드 설명: 고정 ScanResult를 직렬화한 문자열을 저장소의 Golden JSON과 완전히 비교한다.
# ===
def test_scan_result_json_matches_golden_file() -> None:
    assert scan_result_to_json(_sample_result()) == GOLDEN.read_text(encoding="utf-8")


# ===
# 만든 이유: GUI가 선택한 경로에 UTF-8 JSON이 실제로 저장되는지 검증한다.
# 코드 설명: 임시 경로에 저장한 뒤 반환 경로와 다시 읽은 JSON 데이터를 확인한다.
# ===
def test_export_scan_result_writes_utf8_json(tmp_path: Path) -> None:
    output = tmp_path / "결과.json"

    saved_path = export_scan_result(_sample_result(), output)

    assert saved_path == output
    assert json.loads(output.read_text(encoding="utf-8")) == scan_result_to_dict(
        _sample_result()
    )


# ===
# 만든 이유: Finding이 여러 개여도 중복 카테고리를 한 번만 집계하는지 고정한다.
# 코드 설명: 샘플의 두 Finding이 같은 카테고리이므로 summary categories는 1이어야 한다.
# ===
def test_scan_result_summary_counts_unique_categories() -> None:
    exported = scan_result_to_dict(_sample_result())

    assert exported["summary"] == {"findings": 2, "categories": 1}


def _sample_result() -> ScanResult:
    return ScanResult(
        target="sample.py",
        status=GOOD_PATTERNS_FOUND,
        findings=[
            Finding(
                rule_id="GOOD004",
                name="Constant-Time Secret Comparison",
                category="cryptography",
                confidence="HIGH",
                file="sample.py",
                line=4,
                column=4,
                evidence="hmac.compare_digest(received, expected)",
                message="비밀값 비교에 일정 시간 비교 함수를 사용하고 있습니다.",
            ),
            Finding(
                rule_id="GOOD004",
                name="Constant-Time Secret Comparison",
                category="cryptography",
                confidence="HIGH",
                file="sample.py",
                line=8,
                column=4,
                evidence="hmac.compare_digest(left, right)",
                message="비밀값 비교에 일정 시간 비교 함수를 사용하고 있습니다.",
            ),
        ],
        warnings=[],
    )

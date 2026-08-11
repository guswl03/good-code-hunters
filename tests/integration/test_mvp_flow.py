from __future__ import annotations

import json
from pathlib import Path

from goodcode.core.models import GOOD_PATTERNS_FOUND
from goodcode.core.registry import reset_rules
from goodcode.core.service import scan_file
from goodcode.exporters import export_scan_result, scan_result_to_dict

PROJECT_ROOT = Path(__file__).parents[2]
DEMO_GOOD = PROJECT_ROOT / "examples" / "demo_good.py"
EXPECTED_RULE_IDS = {f"GOOD{index:03d}" for index in range(1, 7)}


# ===
# 만든 이유: 네 팀원의 결과물이 public scan_file 경로에서 실제로 연결되는지 한 번에 검증한다.
# 코드 설명: 기본 Registry로 데모를 두 번 분석하고 6개 Rule, 경로, 결정성, JSON 계약을 확인한다.
# ===
def test_complete_mvp_scan_and_export_flow(tmp_path: Path) -> None:
    reset_rules()

    first = scan_file(str(DEMO_GOOD))
    second = scan_file(str(DEMO_GOOD))

    assert first.status == GOOD_PATTERNS_FOUND
    assert {finding.rule_id for finding in first.findings} == EXPECTED_RULE_IDS
    assert {finding.file for finding in first.findings} == {str(DEMO_GOOD)}
    assert scan_result_to_dict(first) == scan_result_to_dict(second)

    output = tmp_path / "demo-good.json"
    export_scan_result(first, output)
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["target"] == str(DEMO_GOOD)
    assert payload["summary"]["findings"] == len(first.findings)
    assert {item["rule_id"] for item in payload["findings"]} == EXPECTED_RULE_IDS


# ===
# 만든 이유: P0 Rule이 실제 등록된 production 경로에서도 대상 코드 실행 금지를 보장해야 한다.
# 코드 설명: 실행되면 파일을 만드는 소스를 scan_file로 분석하고 side effect가 없음을 확인한다.
# ===
def test_complete_mvp_scan_never_executes_target(tmp_path: Path) -> None:
    reset_rules()
    marker = tmp_path / "SHOULD_NOT_EXIST.txt"
    target = tmp_path / "no_execution.py"
    target.write_text(
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('executed', encoding='utf-8')\n"
        "import secrets\n"
        "token = secrets.token_hex(16)\n",
        encoding="utf-8",
    )

    result = scan_file(str(target))

    assert result.status == GOOD_PATTERNS_FOUND
    assert {finding.rule_id for finding in result.findings} == {"GOOD002"}
    assert not marker.exists()

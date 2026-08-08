from goodcode.core.models import Finding, ScanResult


def test_scan_result_to_dict_is_json_friendly() -> None:
    result = ScanResult(
        target_file="sample.py",
        findings=[
            Finding(
                rule_id="GOOD002",
                line=3,
                code="token = secrets.token_hex(16)",
                message="uses secrets",
            )
        ],
    )

    assert result.to_dict()["target_file"] == "sample.py"
    assert result.to_dict()["findings"][0]["rule_id"] == "GOOD002"
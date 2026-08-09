from goodcode.core.models import GOOD_PATTERNS_FOUND, Finding, ScanResult


def test_scan_result_to_dict_is_json_friendly() -> None:
    result = ScanResult(
        findings=[
            Finding(
                rule_id="GOOD002",
                name="Cryptographically Secure Randomness",
                category="cryptography",
                confidence="HIGH",
                file="sample.py",
                line=3,
                column=1,
                evidence="token = secrets.token_hex(16)",
                message="uses secrets",
            )
        ],
        target="sample.py",
        status=GOOD_PATTERNS_FOUND,
        warnings=[],
    )

    assert result.to_dict() == {
        "schema_version": "1.0",
        "tool_version": "0.1.0",
        "target": "sample.py",
        "status": "GOOD_PATTERNS_FOUND",
        "findings": [
            {
                "rule_id": "GOOD002",
                "name": "Cryptographically Secure Randomness",
                "category": "cryptography",
                "confidence": "HIGH",
                "file": "sample.py",
                "line": 3,
                "column": 1,
                "evidence": "token = secrets.token_hex(16)",
                "message": "uses secrets",
            }
        ],
        "warnings": [],
    }
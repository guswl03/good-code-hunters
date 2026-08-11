import ast
from pathlib import Path

from goodcode.core.import_resolver import build_import_alias_context
from goodcode.core.source import SourceHelper
from goodcode.rules.secure_random import SecureRandomnessRule

FIXTURES = Path(__file__).parents[1] / "fixtures" / "good002"


def test_good002_detects_secrets_apis_and_aliases() -> None:
    findings = _scan_fixture("positive.py")

    assert len(findings) == 7
    assert [finding.rule_id for finding in findings] == ["GOOD002"] * 7
    assert [finding.line for finding in findings] == list(range(9, 16))
    assert [finding.column for finding in findings] == [9] * 7
    assert all(finding.file == "positive.py" for finding in findings)
    assert all(
        finding.name == "Cryptographically Secure Randomness"
        for finding in findings
    )
    assert all(finding.category == "cryptography" for finding in findings)
    assert all(finding.confidence == "HIGH" for finding in findings)
    assert all("secrets API" in finding.message for finding in findings)
    assert any("sec.token_hex" in finding.evidence for finding in findings)
    assert any("make_token" in finding.evidence for finding in findings)
    assert any("SystemRandom" in finding.evidence for finding in findings)


def test_good002_ignores_random_and_same_named_user_function() -> None:
    assert _scan_fixture("negative.py") == []


def _scan_fixture(name: str):
    source_text = (FIXTURES / name).read_text(encoding="utf-8")
    tree = ast.parse(source_text)
    return SecureRandomnessRule(name).check(
        tree,
        SourceHelper(source_text),
        build_import_alias_context(tree),
    )

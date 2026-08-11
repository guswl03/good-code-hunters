import ast
from pathlib import Path

from goodcode.core.import_resolver import build_import_alias_context
from goodcode.core.source import SourceHelper
from goodcode.rules.password_hashing import PasswordHashingRule

FIXTURES = Path(__file__).parents[1] / "fixtures" / "good003"


def test_good003_detects_password_hashing_apis_and_argon2_instance() -> None:
    findings = _scan_fixture("positive.py")

    assert len(findings) == 5
    assert [finding.rule_id for finding in findings] == ["GOOD003"] * 5
    assert [finding.line for finding in findings] == [9, 10, 17, 18, 20]
    assert all(finding.column > 0 for finding in findings)
    assert all(finding.file == "positive.py" for finding in findings)
    assert all(finding.name == "Password Hashing / KDF" for finding in findings)
    assert all(finding.category == "credential-protection" for finding in findings)
    assert all(finding.confidence == "HIGH" for finding in findings)
    assert all("Password Hash/KDF API" in finding.message for finding in findings)
    assert any("pbkdf2_hmac" in finding.evidence for finding in findings)
    assert any("scrypt" in finding.evidence for finding in findings)
    assert any("bcrypt.hashpw" in finding.evidence for finding in findings)
    assert any("bcrypt_hashpw" in finding.evidence for finding in findings)
    assert any("hasher.hash" in finding.evidence for finding in findings)


def test_good003_ignores_general_hashes_and_same_named_functions() -> None:
    assert _scan_fixture("negative.py") == []


def _scan_fixture(name: str):
    source_text = (FIXTURES / name).read_text(encoding="utf-8")
    tree = ast.parse(source_text)
    return PasswordHashingRule(name).check(
        tree,
        SourceHelper(source_text),
        build_import_alias_context(tree),
    )

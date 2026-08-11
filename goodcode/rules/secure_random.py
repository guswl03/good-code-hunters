from __future__ import annotations

import ast

from goodcode.core.import_resolver import ImportAliasContext
from goodcode.core.models import Finding
from goodcode.core.source import SourceHelper

SECURE_RANDOM_APIS = {
    "secrets.SystemRandom",
    "secrets.choice",
    "secrets.randbelow",
    "secrets.token_bytes",
    "secrets.token_hex",
    "secrets.token_urlsafe",
}


# ===
# 만든 이유: 보안용 난수 생성에 적합한 secrets API 사용을 긍정 근거로 찾는다.
# 코드 설명: ImportAliasContext로 실제 secrets import가 확인되는 정확한 API 호출만 반환한다.
# ===
class SecureRandomnessRule:
    rule_id = "GOOD002"

    def __init__(self, target_file: str = "") -> None:
        self.target_file = target_file

    def check(
        self,
        tree: ast.AST,
        source: SourceHelper,
        imports: ImportAliasContext,
    ) -> list[Finding]:
        findings: list[Finding] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if _resolved_imported_call_name(node.func, imports) not in SECURE_RANDOM_APIS:
                continue
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    name="Cryptographically Secure Randomness",
                    category="cryptography",
                    confidence="HIGH",
                    file=self.target_file,
                    line=node.lineno,
                    column=source.column_for_node(node),
                    evidence=source.snippet_for_node(node),
                    message="보안용 난수 생성에 적합한 secrets API를 사용하고 있습니다.",
                )
            )

        return findings


def _resolved_imported_call_name(
    node: ast.AST,
    imports: ImportAliasContext,
) -> str | None:
    if isinstance(node, ast.Name):
        return imports.resolve_name(node.id)
    if not isinstance(node, ast.Attribute):
        return None

    root: ast.AST = node
    while isinstance(root, ast.Attribute):
        root = root.value
    if not isinstance(root, ast.Name) or imports.resolve_name(root.id) is None:
        return None
    return imports.resolve_attribute_chain(node)

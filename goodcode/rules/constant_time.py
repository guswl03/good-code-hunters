from __future__ import annotations

import ast

from goodcode.core.import_resolver import ImportAliasContext
from goodcode.core.models import Finding
from goodcode.core.source import SourceHelper


# ===
# 만든 이유: 비밀값 비교에 일반 동등 비교 대신 일정 시간 비교 API를 사용한 근거를 찾기 위해 만든 규칙이다.
# 코드 설명: 호출 이름을 Alias Resolver로 정규화하고 hmac.compare_digest 호출만 HIGH 신뢰도로 반환한다.
# ===
class ConstantTimeComparisonRule:
    rule_id = "GOOD004"

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
            if _resolved_call_name(node.func, imports) != "hmac.compare_digest":
                continue
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    name="Constant-Time Secret Comparison",
                    category="cryptography",
                    confidence="HIGH",
                    file=self.target_file,
                    line=node.lineno,
                    column=source.column_for_node(node),
                    evidence=source.snippet_for_node(node),
                    message="비밀값 비교에 일정 시간 비교 함수 hmac.compare_digest()를 사용하고 있습니다.",
                )
            )
        return findings


# ===
# 만든 이유: import alias와 from-import를 같은 규칙 로직으로 처리하기 위해 호출 이름 해석을 분리했다.
# 코드 설명: Attribute 호출과 Name 호출을 공통 정규화 이름으로 변환한다.
# ===
def _resolved_call_name(node: ast.AST, imports: ImportAliasContext) -> str | None:
    if isinstance(node, ast.Attribute):
        return imports.resolve_attribute_chain(node)
    if isinstance(node, ast.Name):
        return imports.resolve_name(node.id) or node.id
    return None

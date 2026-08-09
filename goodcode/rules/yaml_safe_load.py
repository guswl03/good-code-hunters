from __future__ import annotations

import ast

from goodcode.core.import_resolver import ImportAliasContext
from goodcode.core.models import Finding
from goodcode.core.source import SourceHelper


# ===
# 만든 이유: 임의 객체 생성을 피하는 YAML 안전 역직렬화 API 사용 근거를 찾기 위해 만든 규칙이다.
# 코드 설명: 실제 yaml 패키지를 import하지 않고 AST의 yaml.safe_load 호출과 alias만 확인한다.
# ===
class SafeYamlDeserializationRule:
    rule_id = "GOOD006"

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
            if _resolved_call_name(node.func, imports) != "yaml.safe_load":
                continue
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    name="Safe YAML Deserialization",
                    category="deserialization",
                    confidence="HIGH",
                    file=self.target_file,
                    line=node.lineno,
                    column=source.column_for_node(node),
                    evidence=source.snippet_for_node(node),
                    message="YAML 역직렬화에 yaml.safe_load()를 사용하고 있습니다.",
                )
            )
        return findings


def _resolved_call_name(node: ast.AST, imports: ImportAliasContext) -> str | None:
    if isinstance(node, ast.Attribute):
        return imports.resolve_attribute_chain(node)
    if isinstance(node, ast.Name):
        return imports.resolve_name(node.id) or node.id
    return None

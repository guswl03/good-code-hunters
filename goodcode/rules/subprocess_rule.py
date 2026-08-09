from __future__ import annotations

import ast

from goodcode.core.import_resolver import ImportAliasContext
from goodcode.core.models import Finding
from goodcode.core.source import SourceHelper

SAFE_SUBPROCESS_CALLS = {
    "subprocess.run",
    "subprocess.Popen",
    "subprocess.check_call",
    "subprocess.check_output",
}


# ===
# 만든 이유: shell 문자열 실행보다 명령과 인자를 분리한 subprocess 호출을 긍정 근거로 찾기 위해 만든 규칙이다.
# 코드 설명: 지원 API, list/tuple 첫 인자, shell=True 미사용을 모두 만족할 때만 Finding을 만든다.
# ===
class SaferSubprocessInvocationRule:
    rule_id = "GOOD005"

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
            if _resolved_call_name(node.func, imports) not in SAFE_SUBPROCESS_CALLS:
                continue
            if not node.args or not isinstance(node.args[0], (ast.List, ast.Tuple)):
                continue
            if _uses_possible_shell(node):
                continue
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    name="Safer Subprocess Invocation",
                    category="process-security",
                    confidence="HIGH",
                    file=self.target_file,
                    line=node.lineno,
                    column=source.column_for_node(node),
                    evidence=source.snippet_for_node(node),
                    message="명령과 인자를 분리하고 shell 실행을 사용하지 않는 subprocess 호출입니다.",
                )
            )
        return findings


# ===
# 만든 이유: shell 사용 여부가 False라고 확정되지 않으면 Positive Evidence로 인정할 수 없다.
# 코드 설명: shell=False 또는 키워드 생략만 허용하고 True, 변수, **kwargs는 보수적으로 제외한다.
# ===
def _uses_possible_shell(node: ast.Call) -> bool:
    for keyword in node.keywords:
        if keyword.arg is None:
            return True
        if keyword.arg == "shell":
            return not (
                isinstance(keyword.value, ast.Constant)
                and keyword.value.value is False
            )
    return False


def _resolved_call_name(node: ast.AST, imports: ImportAliasContext) -> str | None:
    if isinstance(node, ast.Attribute):
        return imports.resolve_attribute_chain(node)
    if isinstance(node, ast.Name):
        return imports.resolve_name(node.id) or node.id
    return None

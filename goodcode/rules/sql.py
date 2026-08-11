from __future__ import annotations

import ast
import re

from goodcode.core.import_resolver import ImportAliasContext
from goodcode.core.models import Finding
from goodcode.core.source import SourceHelper

SUPPORTED_METHODS = {"execute", "executemany"}
SQL_PREFIX = re.compile(
    r"^\s*(?:SELECT|INSERT|UPDATE|DELETE|REPLACE|WITH)\b",
    re.IGNORECASE,
)
NAMED_PLACEHOLDER = re.compile(r"(?<!:):[A-Za-z_][A-Za-z0-9_]*")


# ===
# 만든 이유: SQL 문자열과 데이터를 분리해 전달하는 명확한 parameterized query 근거를 찾는다.
# 코드 설명: SQL literal, 지원 placeholder, 별도 parameter 인자를 모두 확인한 호출만 반환한다.
# ===
class ParameterizedSqlQueryRule:
    rule_id = "GOOD001"

    def __init__(self, target_file: str = "") -> None:
        self.target_file = target_file

    def check(
        self,
        tree: ast.AST,
        source: SourceHelper,
        imports: ImportAliasContext,
    ) -> list[Finding]:
        del imports
        findings: list[Finding] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not _is_parameterized_sql_call(node):
                continue
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    name="Parameterized SQL Query",
                    category="injection-prevention",
                    confidence="HIGH",
                    file=self.target_file,
                    line=node.lineno,
                    column=source.column_for_node(node),
                    evidence=source.snippet_for_node(node),
                    message="SQL 문장과 데이터를 분리하여 parameterized query로 전달하고 있습니다.",
                )
            )

        return findings


def _is_parameterized_sql_call(node: ast.Call) -> bool:
    if not isinstance(node.func, ast.Attribute):
        return False
    if node.func.attr not in SUPPORTED_METHODS or len(node.args) < 2:
        return False

    query_node, parameters_node = node.args[:2]
    if not isinstance(query_node, ast.Constant) or not isinstance(
        query_node.value, str
    ):
        return False
    if not _contains_parameter_value(parameters_node):
        return False

    query = query_node.value
    return bool(SQL_PREFIX.match(query)) and _has_supported_placeholder(query)


def _contains_parameter_value(node: ast.AST) -> bool:
    if isinstance(node, ast.Starred):
        return False
    if isinstance(node, ast.Constant) and node.value is None:
        return False
    if isinstance(node, (ast.List, ast.Set, ast.Tuple)):
        return bool(node.elts)
    if isinstance(node, ast.Dict):
        return bool(node.keys)
    return True


def _has_supported_placeholder(query: str) -> bool:
    searchable_query = _without_sql_literals_and_comments(query)
    return (
        "?" in searchable_query
        or re.search(r"(?<!%)%s", searchable_query) is not None
        or NAMED_PLACEHOLDER.search(searchable_query) is not None
    )


def _without_sql_literals_and_comments(query: str) -> str:
    result: list[str] = []
    index = 0
    quote: str | None = None

    while index < len(query):
        character = query[index]
        next_character = query[index + 1] if index + 1 < len(query) else ""

        if quote is not None:
            if character == quote and next_character == quote:
                result.extend((" ", " "))
                index += 2
                continue
            if character == quote:
                quote = None
            result.append("\n" if character == "\n" else " ")
            index += 1
            continue

        if character in {"'", '"'}:
            quote = character
            result.append(" ")
            index += 1
            continue
        if character == "-" and next_character == "-":
            end = query.find("\n", index + 2)
            if end == -1:
                result.extend(" " * (len(query) - index))
                break
            result.extend(" " * (end - index))
            index = end
            continue
        if character == "/" and next_character == "*":
            end = query.find("*/", index + 2)
            if end == -1:
                result.extend(" " * (len(query) - index))
                break
            comment = query[index : end + 2]
            result.extend("\n" if item == "\n" else " " for item in comment)
            index = end + 2
            continue

        result.append(character)
        index += 1

    return "".join(result)

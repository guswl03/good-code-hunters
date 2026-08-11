from __future__ import annotations

import ast

from goodcode.core.import_resolver import ImportAliasContext
from goodcode.core.models import Finding
from goodcode.core.source import SourceHelper

PASSWORD_HASH_APIS = {
    "bcrypt.hashpw",
    "hashlib.pbkdf2_hmac",
    "hashlib.scrypt",
}
PASSWORD_HASHER = "argon2.PasswordHasher"
SCOPE_NODES = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


# ===
# 만든 이유: 비밀번호 보호에 권장되는 Password Hash/KDF API 사용 근거를 찾는다.
# 코드 설명: 직접 API 호출과 제한적인 Argon2 PasswordHasher 인스턴스 패턴만 정적으로 확인한다.
# ===
class PasswordHashingRule:
    rule_id = "GOOD003"

    def __init__(self, target_file: str = "") -> None:
        self.target_file = target_file

    def check(
        self,
        tree: ast.AST,
        source: SourceHelper,
        imports: ImportAliasContext,
    ) -> list[Finding]:
        calls: dict[int, ast.Call] = {}

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            resolved_name = _resolved_imported_call_name(node.func, imports)
            if resolved_name in PASSWORD_HASH_APIS or _is_direct_argon2_hash_call(
                node, imports
            ):
                calls[id(node)] = node

        for node in _find_assigned_argon2_hash_calls(tree, imports):
            calls[id(node)] = node

        ordered_calls = sorted(
            calls.values(),
            key=lambda node: (node.lineno, source.column_for_node(node)),
        )
        return [self._finding_for(node, source) for node in ordered_calls]

    def _finding_for(self, node: ast.Call, source: SourceHelper) -> Finding:
        return Finding(
            rule_id=self.rule_id,
            name="Password Hashing / KDF",
            category="credential-protection",
            confidence="HIGH",
            file=self.target_file,
            line=node.lineno,
            column=source.column_for_node(node),
            evidence=source.snippet_for_node(node),
            message="비밀번호 보호에 적합한 Password Hash/KDF API를 사용하고 있습니다.",
        )


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


def _is_password_hasher_constructor(
    node: ast.AST,
    imports: ImportAliasContext,
) -> bool:
    return isinstance(node, ast.Call) and (
        _resolved_imported_call_name(node.func, imports) == PASSWORD_HASHER
    )


def _is_direct_argon2_hash_call(
    node: ast.Call,
    imports: ImportAliasContext,
) -> bool:
    return (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "hash"
        and _is_password_hasher_constructor(node.func.value, imports)
    )


def _find_assigned_argon2_hash_calls(
    tree: ast.AST,
    imports: ImportAliasContext,
) -> list[ast.Call]:
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    scopes = [node for node in ast.walk(tree) if isinstance(node, SCOPE_NODES)]
    calls: list[ast.Call] = []

    for scope in scopes:
        known_instances: set[str] = set()
        for statement in scope.body:
            for node in ast.walk(statement):
                if not isinstance(node, ast.Call):
                    continue
                if _enclosing_scope(node, parents) is not scope:
                    continue
                if _is_known_instance_hash_call(node, known_instances):
                    calls.append(node)
            _update_known_instances(statement, known_instances, imports)

    return calls


def _enclosing_scope(
    node: ast.AST,
    parents: dict[ast.AST, ast.AST],
) -> ast.AST | None:
    current: ast.AST | None = node
    while current is not None:
        if isinstance(current, SCOPE_NODES):
            return current
        current = parents.get(current)
    return None


def _is_known_instance_hash_call(node: ast.Call, instances: set[str]) -> bool:
    return (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "hash"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id in instances
    )


def _update_known_instances(
    statement: ast.stmt,
    instances: set[str],
    imports: ImportAliasContext,
) -> None:
    targets: list[ast.expr]
    value: ast.AST | None

    if isinstance(statement, ast.Assign):
        targets = statement.targets
        value = statement.value
    elif isinstance(statement, ast.AnnAssign):
        targets = [statement.target]
        value = statement.value
    elif isinstance(statement, ast.AugAssign):
        targets = [statement.target]
        value = None
    else:
        return

    names = [target.id for target in targets if isinstance(target, ast.Name)]
    for name in names:
        instances.discard(name)
    if value is not None and _is_password_hasher_constructor(value, imports):
        instances.update(names)

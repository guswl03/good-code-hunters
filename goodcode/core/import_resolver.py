from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ImportAliasContext:
    module_aliases: dict[str, str]
    symbol_aliases: dict[str, str]

    def resolve_name(self, name: str) -> str | None:
        if name in self.symbol_aliases:
            return self.symbol_aliases[name]
        if name in self.module_aliases:
            return self.module_aliases[name]
        return None

    def resolve_attribute_chain(self, node: ast.AST) -> str | None:
        parts: list[str] = []
        current: ast.AST | None = node

        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            root = self.resolve_name(current.id) or current.id
            parts.append(root)
            parts.reverse()
            return ".".join(parts)

        return None


def build_import_alias_context(tree: ast.AST) -> ImportAliasContext:
    module_aliases: dict[str, str] = {}
    symbol_aliases: dict[str, str] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                exposed = alias.asname or alias.name
                module_aliases[exposed] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name == "*":
                    continue
                exposed = alias.asname or alias.name
                symbol_aliases[exposed] = f"{node.module}.{alias.name}"

    return ImportAliasContext(
        module_aliases=dict(sorted(module_aliases.items())),
        symbol_aliases=dict(sorted(symbol_aliases.items())),
    )
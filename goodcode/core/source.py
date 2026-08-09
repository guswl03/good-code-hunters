from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceHelper:
    source: str

    def lines(self) -> list[str]:
        return self.source.splitlines()

    def line_text(self, line_number: int) -> str:
        lines = self.lines()
        if 1 <= line_number <= len(lines):
            return lines[line_number - 1].strip()
        return ""

    def column_for_node(self, node: ast.AST) -> int:
        return (getattr(node, "col_offset", 0) or 0) + 1

    def snippet_for_node(self, node: ast.AST) -> str:
        snippet = ast.get_source_segment(self.source, node)
        if snippet:
            return snippet.strip()

        line_number = getattr(node, "lineno", 0) or 0
        return self.line_text(line_number)
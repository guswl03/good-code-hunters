from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceHelper:
    source: str

    def line_text(self, line_number: int) -> str:
        lines = self.source.splitlines()
        if 1 <= line_number <= len(lines):
            return lines[line_number - 1].strip()
        return ""

    def snippet_for_node(self, node: ast.AST) -> str:
        snippet = ast.get_source_segment(self.source, node)
        if snippet:
            return snippet.strip()

        line_number = getattr(node, "lineno", 0) or 0
        return self.line_text(line_number)
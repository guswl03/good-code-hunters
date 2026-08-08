import ast

from goodcode.core.source import SourceHelper


def test_source_helper_falls_back_to_line_text_when_segment_missing() -> None:
    helper = SourceHelper(source="value = 1\nother = 2\n")
    node = ast.Name(id="value")
    node.lineno = 1

    assert helper.snippet_for_node(node) == "value = 1"
import ast

from goodcode.core.import_resolver import build_import_alias_context


def test_import_alias_context_resolves_modules_and_symbols() -> None:
    tree = ast.parse(
        "import secrets as sec\n"
        "from secrets import token_hex as make_token\n"
        "sec.token_hex(16)\n"
        "make_token(16)\n"
    )
    context = build_import_alias_context(tree)

    assert context.resolve_attribute_chain(tree.body[2].value.func) == "secrets.token_hex"
    assert context.resolve_name("make_token") == "secrets.token_hex"
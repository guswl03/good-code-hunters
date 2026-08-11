"""GUI package initialization.

Provides lazy access to the main window and result view classes to avoid circular import
issues during package import. Modules are imported only when accessed via attribute
lookup.
"""

from importlib import import_module
from typing import Any

__all__ = ["MainWindow", "ResultView"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module(f"goodcode.gui.{name.lower()}")
        return getattr(module, name)
    raise AttributeError(f"module 'goodcode.gui' has no attribute {name!r}")

from __future__ import annotations

import os
import sys
from pathlib import Path


def _configure_tk_libraries() -> None:
    if os.environ.get("TCL_LIBRARY") and os.environ.get("TK_LIBRARY"):
        return

    base_path = Path(sys.base_prefix)
    candidates = (
        (base_path / "tcl" / "tcl8.6", base_path / "tcl" / "tk8.6"),
        (base_path / "Library" / "lib" / "tcl8.6", base_path / "Library" / "lib" / "tk8.6"),
    )

    for tcl_path, tk_path in candidates:
        if tcl_path.exists() and tk_path.exists():
            os.environ.setdefault("TCL_LIBRARY", str(tcl_path))
            os.environ.setdefault("TK_LIBRARY", str(tk_path))
            return


_configure_tk_libraries()

from __future__ import annotations

import os
import sys
from pathlib import Path


def _configure_tk_libraries() -> None:
    base_path = Path(sys.base_prefix)
    candidates = (
        (base_path / "tcl" / "tcl8.6", base_path / "tcl" / "tk8.6"),
        (base_path / "Library" / "lib" / "tcl8.6", base_path / "Library" / "lib" / "tk8.6"),
    )

    for tcl_path, tk_path in candidates:
        if (tcl_path / "init.tcl").exists() and (tk_path / "tk.tcl").exists():
            os.environ["TCL_LIBRARY"] = str(tcl_path)
            os.environ["TK_LIBRARY"] = str(tk_path)
            return


_configure_tk_libraries()

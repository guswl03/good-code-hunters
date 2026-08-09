from __future__ import annotations

from pathlib import Path

from goodcode.core.models import READ_ERROR, ScanResult
from goodcode.core.scanner import scan_path


def scan_file(file_path: str) -> ScanResult:
    path = Path(file_path)
    if path.suffix != ".py":
        return ScanResult(
            findings=[],
            target=str(path),
            status=READ_ERROR,
            warnings=[f"Expected a .py file: {file_path}"],
        )
    return scan_path(path)
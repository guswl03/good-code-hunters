from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MAX_HISTORY = 8


@dataclass(frozen=True)
class ScanRecord:
    file_name: str
    finding_count: int
    category_count: int
    timestamp: float


@dataclass
class SessionStats:
    runs: int = 0
    total_finds: int = 0
    history: list[ScanRecord] = field(default_factory=list)

    def record(self, file_name: str, finding_count: int, category_count: int) -> None:
        """Record a scan run.

        Args:
            file_name: Name of the scanned file.
            finding_count: Number of findings detected.
            category_count: Number of distinct categories found.
        """
        self.runs += 1
        self.total_finds += finding_count
        self.history.insert(
            0,
            ScanRecord(
                file_name=file_name,
                finding_count=finding_count,
                category_count=category_count,
                timestamp=time.time(),
            ),
        )
        del self.history[MAX_HISTORY:]

    def reset(self) -> None:
        """Reset all statistics."""
        self.runs = 0
        self.total_finds = 0
        self.history.clear()

    @property
    def last(self) -> ScanRecord | None:
        """Return the most recent record or ``None`` if history is empty."""
        return self.history[0] if self.history else None

    def to_dict(self) -> dict[str, Any]:
        """Serialize the stats to a JSON‑serializable dict."""
        return {
            "runs": self.runs,
            "total_finds": self.total_finds,
            "history": [
                {
                    "file_name": r.file_name,
                    "finding_count": r.finding_count,
                    "category_count": r.category_count,
                    "timestamp": r.timestamp,
                }
                for r in self.history
            ],
        }

    def save(self, path: str | Path) -> None:
        """Save the current stats to *path* as JSON.

        The file is written with UTF‑8 encoding and a trailing newline.
        """
        Path(path).write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: str | Path) -> SessionStats:
        """Load stats from *path*.

        If the file does not exist or cannot be parsed, an empty ``SessionStats``
        instance is returned.
        """
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            stats = cls(runs=data.get("runs", 0), total_finds=data.get("total_finds", 0))
            for rec in data.get("history", []):
                stats.history.append(
                    ScanRecord(
                        file_name=rec.get("file_name", ""),
                        finding_count=rec.get("finding_count", 0),
                        category_count=rec.get("category_count", 0),
                        timestamp=rec.get("timestamp", time.time()),
                    )
                )
            return stats
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return cls()

from __future__ import annotations

import time
from dataclasses import dataclass, field

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
        self.runs = 0
        self.total_finds = 0
        self.history.clear()

    @property
    def last(self) -> ScanRecord | None:
        return self.history[0] if self.history else None

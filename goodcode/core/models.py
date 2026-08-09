from __future__ import annotations

from dataclasses import asdict, dataclass, field

SCAN_SCHEMA_VERSION = "1.0"
TOOL_VERSION = "0.1.0"

GOOD_PATTERNS_FOUND = "GOOD_PATTERNS_FOUND"
NO_GOOD_PATTERNS_FOUND = "NO_GOOD_PATTERNS_FOUND"
PARSE_ERROR = "PARSE_ERROR"
READ_ERROR = "READ_ERROR"


@dataclass(frozen=True, slots=True)
class Finding:
    rule_id: str
    name: str
    category: str
    confidence: str
    file: str
    line: int
    column: int
    evidence: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScanResult:
    findings: list[Finding]
    schema_version: str = SCAN_SCHEMA_VERSION
    tool_version: str = TOOL_VERSION
    target: str = ""
    status: str = NO_GOOD_PATTERNS_FOUND
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
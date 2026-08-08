from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class Finding:
    rule_id: str
    line: int
    code: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScanResult:
    target_file: str
    findings: list[Finding]

    def to_dict(self) -> dict[str, object]:
        return {
            "target_file": self.target_file,
            "findings": [finding.to_dict() for finding in self.findings],
        }
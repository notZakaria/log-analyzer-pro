from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from enum import StrEnum


class Severity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    UNKNOWN = "UNKNOWN"


@dataclass(slots=True)
class LogEntry:
    timestamp: str
    severity: Severity
    message: str
    normalized_message: str
    source_file: str
    line_number: int
    is_critical: bool = False


@dataclass(slots=True)
class AnalysisSummary:
    total_entries: int
    severity_counts: Counter[Severity] = field(default_factory=Counter)
    error_occurrences: Counter[str] = field(default_factory=Counter)
    critical_count: int = 0
    files_processed: int = 0

    @property
    def unique_error_count(self) -> int:
        return len(self.error_occurrences)


@dataclass(slots=True)
class ReportBundle:
    entries: list[LogEntry]
    summary: AnalysisSummary
    summary_text: str

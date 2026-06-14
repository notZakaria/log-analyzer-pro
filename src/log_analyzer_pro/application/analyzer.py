from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from log_analyzer_pro.domain.models import AnalysisSummary, LogEntry, Severity


class LogAnalysisService:
    """Compute metrics and filter structured log entries."""

    def summarize(self, entries: list[LogEntry], files_processed: int) -> AnalysisSummary:
        severity_counts = Counter(entry.severity for entry in entries)
        error_occurrences = Counter(
            entry.normalized_message for entry in entries if entry.severity is Severity.ERROR
        )
        critical_count = sum(1 for entry in entries if entry.is_critical)
        return AnalysisSummary(
            total_entries=len(entries),
            severity_counts=severity_counts,
            error_occurrences=error_occurrences,
            critical_count=critical_count,
            files_processed=files_processed,
        )

    def filter_entries(
        self,
        entries: Iterable[LogEntry],
        search_text: str = "",
        severities: set[Severity] | None = None,
        critical_only: bool = False,
    ) -> list[LogEntry]:
        normalized_query = search_text.casefold().strip()
        selected = severities or {Severity.ERROR, Severity.WARNING, Severity.INFO}
        filtered: list[LogEntry] = []

        for entry in entries:
            if entry.severity not in selected:
                continue
            if critical_only and not entry.is_critical:
                continue
            haystack = f"{entry.timestamp} {entry.message} {entry.source_file}".casefold()
            if normalized_query and normalized_query not in haystack:
                continue
            filtered.append(entry)

        return filtered

    def top_errors(self, summary: AnalysisSummary, limit: int = 10) -> list[tuple[str, int]]:
        return summary.error_occurrences.most_common(limit)

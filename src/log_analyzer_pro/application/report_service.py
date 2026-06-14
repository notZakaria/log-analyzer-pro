from __future__ import annotations

from collections import Counter

from log_analyzer_pro.domain.models import AnalysisSummary, LogEntry, ReportBundle, Severity


class ReportService:
    """Prepare export-friendly report data."""

    def build_report(self, entries: list[LogEntry], files_processed: int) -> ReportBundle:
        severity_counts = Counter(entry.severity for entry in entries)
        error_occurrences = Counter(
            entry.normalized_message for entry in entries if entry.severity is Severity.ERROR
        )
        summary = AnalysisSummary(
            total_entries=len(entries),
            severity_counts=severity_counts,
            error_occurrences=error_occurrences,
            critical_count=sum(1 for entry in entries if entry.is_critical),
            files_processed=files_processed,
        )
        return ReportBundle(
            entries=entries,
            summary=summary,
            summary_text=self.build_summary_text(summary),
        )

    def build_summary_text(self, summary: AnalysisSummary) -> str:
        error_count = summary.severity_counts.get(Severity.ERROR, 0)
        warning_count = summary.severity_counts.get(Severity.WARNING, 0)
        info_count = summary.severity_counts.get(Severity.INFO, 0)
        top_error_lines = [
            f"- {message[:90]} ({count} occurrences)"
            for message, count in summary.error_occurrences.most_common(5)
        ]
        if not top_error_lines:
            top_error_lines = ["- No error signatures were detected."]

        return "\n".join(
            [
                "Log Analyzer Pro Summary",
                f"Files processed: {summary.files_processed}",
                f"Total entries: {summary.total_entries}",
                f"Errors: {error_count}",
                f"Warnings: {warning_count}",
                f"Info: {info_count}",
                f"Critical errors: {summary.critical_count}",
                f"Unique error signatures: {summary.unique_error_count}",
                "",
                "Top recurring errors:",
                *top_error_lines,
            ]
        )

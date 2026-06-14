from __future__ import annotations

import logging
import re
from pathlib import Path

from log_analyzer_pro.domain.models import LogEntry, Severity


LOGGER = logging.getLogger(__name__)


class LogParserService:
    """Parse plain-text logs into structured records."""

    TIMESTAMP_PATTERNS = (
        re.compile(
            r"(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d{3,6})?)"
        ),
        re.compile(r"(?P<timestamp>\d{2}:\d{2}:\d{2}(?:[.,]\d{3,6})?)"),
    )
    SEVERITY_PATTERNS: dict[Severity, re.Pattern[str]] = {
        Severity.ERROR: re.compile(
            r"\b(error|err|fatal|exception|failed|panic|critical)\b",
            re.IGNORECASE,
        ),
        Severity.WARNING: re.compile(r"\b(warn|warning|deprecated|retry)\b", re.IGNORECASE),
        Severity.INFO: re.compile(r"\b(info|started|completed|passed|success)\b", re.IGNORECASE),
    }
    CRITICAL_PATTERN = re.compile(
        r"\b(critical|fatal|panic|segmentation fault|kernel panic|data loss|unrecoverable)\b",
        re.IGNORECASE,
    )
    COLLAPSE_TOKENS = (
        (re.compile(r"\b0x[0-9a-f]+\b", re.IGNORECASE), "<hex>"),
        (re.compile(r"\b\d+\b"), "<num>"),
        (re.compile(r"'[^']+'"), "'<value>'"),
        (re.compile(r'"[^"]+"'), '"<value>"'),
    )

    def parse_files(self, file_paths: list[str]) -> list[LogEntry]:
        entries: list[LogEntry] = []
        for file_path in file_paths:
            entries.extend(self.parse_file(file_path))
        return entries

    def parse_file(self, file_path: str) -> list[LogEntry]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Log file not found: {file_path}")

        LOGGER.info("Parsing log file: %s", path)
        parsed_entries: list[LogEntry] = []

        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line_number, raw_line in enumerate(handle, start=1):
                line = raw_line.strip()
                if not line:
                    continue

                severity = self._detect_severity(line)
                if severity is Severity.UNKNOWN:
                    continue

                timestamp = self._extract_timestamp(line)
                message = self._clean_message(line)
                normalized = self._normalize_message(message)
                parsed_entries.append(
                    LogEntry(
                        timestamp=timestamp,
                        severity=severity,
                        message=message,
                        normalized_message=normalized,
                        source_file=path.name,
                        line_number=line_number,
                        is_critical=bool(self.CRITICAL_PATTERN.search(line)),
                    )
                )

        LOGGER.info("Parsed %s entries from %s", len(parsed_entries), path.name)
        return parsed_entries

    def _extract_timestamp(self, line: str) -> str:
        for pattern in self.TIMESTAMP_PATTERNS:
            match = pattern.search(line)
            if match:
                return match.group("timestamp")
        return "N/A"

    def _detect_severity(self, line: str) -> Severity:
        for severity, pattern in self.SEVERITY_PATTERNS.items():
            if pattern.search(line):
                return severity
        return Severity.UNKNOWN

    def _clean_message(self, line: str) -> str:
        cleaned = line
        for pattern in self.TIMESTAMP_PATTERNS:
            cleaned = pattern.sub("", cleaned, count=1).strip(" -|[]")

        cleaned = re.sub(r"\b(ERROR|ERR|FATAL|EXCEPTION|FAILED|WARNING|WARN|INFO)\b[:\]-]*", "", cleaned, flags=re.IGNORECASE)
        return re.sub(r"\s{2,}", " ", cleaned).strip(" -|")

    def _normalize_message(self, message: str) -> str:
        normalized = message.lower()
        for pattern, replacement in self.COLLAPSE_TOKENS:
            normalized = pattern.sub(replacement, normalized)
        normalized = re.sub(r"\s{2,}", " ", normalized)
        return normalized.strip()

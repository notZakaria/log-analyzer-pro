from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from log_analyzer_pro.domain.models import ReportBundle, Severity


class PdfExporter:
    """Export the current analysis snapshot into a polished PDF report."""

    def export(self, report: ReportBundle, destination: str) -> Path:
        output_path = Path(destination)
        document = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=14 * mm,
            rightMargin=14 * mm,
            topMargin=14 * mm,
            bottomMargin=14 * mm,
        )

        styles = getSampleStyleSheet()
        title_style = styles["Heading1"]
        section_style = styles["Heading2"]
        body_style = ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            leading=14,
            spaceAfter=6,
        )

        elements = [
            Paragraph("Log Analyzer Pro Report", title_style),
            Spacer(1, 8),
            Paragraph(report.summary_text.replace("\n", "<br/>"), body_style),
            Spacer(1, 10),
            Paragraph("Severity Breakdown", section_style),
            self._build_severity_table(report),
            Spacer(1, 10),
            Paragraph("Top Error Signatures", section_style),
            self._build_errors_table(report),
            Spacer(1, 10),
            Paragraph("Detailed Log Entries", section_style),
            self._build_entries_table(report),
        ]

        document.build(elements)
        return output_path

    def _build_severity_table(self, report: ReportBundle) -> Table:
        data = [["Metric", "Value"]]
        data.extend(
            [
                ["Files processed", report.summary.files_processed],
                ["Total entries", report.summary.total_entries],
                ["Errors", report.summary.severity_counts.get(Severity.ERROR, 0)],
                ["Warnings", report.summary.severity_counts.get(Severity.WARNING, 0)],
                ["Info", report.summary.severity_counts.get(Severity.INFO, 0)],
                ["Critical errors", report.summary.critical_count],
            ]
        )
        return self._styled_table(data, [70 * mm, 30 * mm])

    def _build_errors_table(self, report: ReportBundle) -> Table:
        data = [["Error Signature", "Occurrences"]]
        top_errors = report.summary.error_occurrences.most_common(10)
        if not top_errors:
            data.append(["No recurring errors detected", 0])
        else:
            data.extend([[signature[:100], count] for signature, count in top_errors])
        return self._styled_table(data, [120 * mm, 30 * mm])

    def _build_entries_table(self, report: ReportBundle) -> Table:
        preview_limit = 40
        data = [["Timestamp", "Severity", "Source", "Line", "Message"]]
        for entry in report.entries[:preview_limit]:
            message = entry.message[:90] + ("..." if len(entry.message) > 90 else "")
            data.append(
                [entry.timestamp, entry.severity.value, entry.source_file, entry.line_number, message]
            )

        if len(report.entries) > preview_limit:
            data.append(
                [
                    "...",
                    "...",
                    "...",
                    "...",
                    f"Preview truncated. {len(report.entries) - preview_limit} additional entries are available in the Excel export.",
                ]
            )

        return self._styled_table(data, [28 * mm, 24 * mm, 28 * mm, 12 * mm, 78 * mm])

    def _styled_table(self, data: list[list[object]], column_widths: list[float]) -> Table:
        table = Table(data, colWidths=column_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3b5b")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("LEADING", (0, 0), (-1, -1), 10),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return table

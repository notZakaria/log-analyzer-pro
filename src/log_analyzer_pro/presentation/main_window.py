from __future__ import annotations

import logging
from pathlib import Path
from tkinter import BooleanVar, StringVar, filedialog, messagebox

import customtkinter as ctk

from log_analyzer_pro.application.analyzer import LogAnalysisService
from log_analyzer_pro.application.log_parser import LogParserService
from log_analyzer_pro.application.report_service import ReportService
from log_analyzer_pro.domain.models import AnalysisSummary, LogEntry, Severity
from log_analyzer_pro.infrastructure.exporters.excel_exporter import ExcelExporter
from log_analyzer_pro.infrastructure.exporters.pdf_exporter import PdfExporter
from log_analyzer_pro.presentation.theme_manager import ThemeManager
from log_analyzer_pro.presentation.widgets.chart_frame import ChartFrame
from log_analyzer_pro.presentation.widgets.log_table import LogTable


LOGGER = logging.getLogger(__name__)


class StatCard(ctk.CTkFrame):
    def __init__(self, master, title: str, accent: str) -> None:
        super().__init__(master, corner_radius=18)
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=accent,
        )
        self.value_label = ctk.CTkLabel(
            self,
            text="0",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.title_label.pack(anchor="w", padx=16, pady=(14, 4))
        self.value_label.pack(anchor="w", padx=16, pady=(0, 14))

    def set_value(self, value: int) -> None:
        self.value_label.configure(text=str(value))


class LogAnalyzerApp(ctk.CTk):
    """Main desktop application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Log Analyzer Pro")
        self.geometry("1500x920")
        self.minsize(1280, 760)

        self.parser_service = LogParserService()
        self.analysis_service = LogAnalysisService()
        self.report_service = ReportService()
        self.excel_exporter = ExcelExporter()
        self.pdf_exporter = PdfExporter()
        self.theme_manager = ThemeManager()

        self.loaded_files: list[str] = []
        self.all_entries: list[LogEntry] = []
        self.filtered_entries: list[LogEntry] = []
        self.current_summary = AnalysisSummary(total_entries=0)

        self.search_var = StringVar()
        self.error_var = BooleanVar(value=True)
        self.warning_var = BooleanVar(value=True)
        self.info_var = BooleanVar(value=True)
        self.critical_only_var = BooleanVar(value=False)
        self.theme_var = StringVar(value="Dark")

        self._build_layout()
        self._apply_theme()
        self._update_dashboard()

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.header_frame = ctk.CTkFrame(self, corner_radius=0, height=90)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Log Analyzer Pro",
            font=ctk.CTkFont(size=30, weight="bold"),
        )
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Multi-file log diagnostics for validation and test engineering teams",
            font=ctk.CTkFont(size=14),
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=24, pady=(18, 2))
        self.subtitle_label.grid(row=1, column=0, sticky="w", padx=24, pady=(0, 18))

        self.theme_switch = ctk.CTkSegmentedButton(
            self.header_frame,
            values=["Dark", "Light"],
            variable=self.theme_var,
            command=self._on_theme_change,
        )
        self.theme_switch.grid(row=0, column=1, rowspan=2, sticky="e", padx=24)

        self.toolbar = ctk.CTkFrame(self, corner_radius=18)
        self.toolbar.grid(row=1, column=0, sticky="ew", padx=18, pady=18)
        for index in range(8):
            self.toolbar.grid_columnconfigure(index, weight=1 if index == 7 else 0)

        self.load_button = ctk.CTkButton(self.toolbar, text="Load Log Files", command=self.load_files, width=150)
        self.summary_button = ctk.CTkButton(
            self.toolbar,
            text="Generate Summary",
            command=self._update_dashboard,
            width=150,
        )
        self.export_excel_button = ctk.CTkButton(
            self.toolbar,
            text="Export Excel",
            command=self.export_excel,
            width=130,
        )
        self.export_pdf_button = ctk.CTkButton(
            self.toolbar,
            text="Export PDF",
            command=self.export_pdf,
            width=120,
        )

        self.search_entry = ctk.CTkEntry(
            self.toolbar,
            textvariable=self.search_var,
            width=280,
            placeholder_text="Search logs, files, or timestamps...",
        )
        self.search_entry.bind("<KeyRelease>", lambda _event: self.apply_filters())

        self.error_check = ctk.CTkCheckBox(self.toolbar, text="Errors", variable=self.error_var, command=self.apply_filters)
        self.warning_check = ctk.CTkCheckBox(
            self.toolbar,
            text="Warnings",
            variable=self.warning_var,
            command=self.apply_filters,
        )
        self.info_check = ctk.CTkCheckBox(self.toolbar, text="Info", variable=self.info_var, command=self.apply_filters)
        self.critical_check = ctk.CTkCheckBox(
            self.toolbar,
            text="Critical Only",
            variable=self.critical_only_var,
            command=self.apply_filters,
        )
        self.clear_button = ctk.CTkButton(self.toolbar, text="Clear Filters", command=self.clear_filters, width=120)

        controls = [
            self.load_button,
            self.summary_button,
            self.export_excel_button,
            self.export_pdf_button,
            self.search_entry,
            self.error_check,
            self.warning_check,
            self.info_check,
            self.critical_check,
            self.clear_button,
        ]
        grid_positions = [
            (0, 0),
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (0, 6),
            (0, 7),
            (1, 5),
            (1, 6),
        ]
        for widget, (row, column) in zip(controls, grid_positions):
            widget.grid(row=row, column=column, padx=10, pady=10, sticky="w")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.content_frame.grid_columnconfigure(0, weight=3)
        self.content_frame.grid_columnconfigure(1, weight=2)
        self.content_frame.grid_rowconfigure(1, weight=1)

        self.stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.stats_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        for index in range(4):
            self.stats_frame.grid_columnconfigure(index, weight=1)

        self.total_card = StatCard(self.stats_frame, "Displayed Entries", "#38bdf8")
        self.error_card = StatCard(self.stats_frame, "Errors", "#ef4444")
        self.warning_card = StatCard(self.stats_frame, "Warnings", "#f59e0b")
        self.critical_card = StatCard(self.stats_frame, "Critical", "#f97316")

        for index, card in enumerate(
            [self.total_card, self.error_card, self.warning_card, self.critical_card]
        ):
            card.grid(row=0, column=index, sticky="ew", padx=(0 if index == 0 else 10, 0))

        self.log_table = LogTable(self.content_frame)
        self.log_table.grid(row=1, column=0, sticky="nsew", padx=(0, 12))

        self.right_panel = ctk.CTkFrame(self.content_frame, corner_radius=18)
        self.right_panel.grid(row=1, column=1, sticky="nsew")
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.summary_title = ctk.CTkLabel(
            self.right_panel,
            text="Summary Report",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        self.summary_title.grid(row=0, column=0, sticky="w", padx=18, pady=(18, 10))

        self.chart_frame = ChartFrame(self.right_panel)
        self.chart_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 14))

        self.summary_text = ctk.CTkTextbox(self.right_panel, wrap="word", corner_radius=14, height=220)
        self.summary_text.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        self.summary_text.configure(state="disabled")

        self.status_var = StringVar(value="Load one or more log files to begin.")
        self.status_label = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            anchor="w",
            font=ctk.CTkFont(size=13),
        )
        self.status_label.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 16))

    def load_files(self) -> None:
        file_paths = filedialog.askopenfilenames(
            title="Select log files",
            filetypes=[("Log files", "*.log *.txt"), ("All files", "*.*")],
        )
        if not file_paths:
            return

        try:
            self.loaded_files = list(file_paths)
            self.all_entries = self.parser_service.parse_files(self.loaded_files)
            self.status_var.set(
                f"Loaded {len(self.loaded_files)} file(s) with {len(self.all_entries)} detected entries."
            )
            self.apply_filters()
        except Exception as exc:
            LOGGER.exception("Failed to load files")
            messagebox.showerror("Load Failed", f"Unable to parse the selected files.\n\n{exc}")

    def apply_filters(self) -> None:
        selected_severities = {
            severity
            for severity, enabled in (
                (Severity.ERROR, self.error_var.get()),
                (Severity.WARNING, self.warning_var.get()),
                (Severity.INFO, self.info_var.get()),
            )
            if enabled
        }

        if not selected_severities:
            self.filtered_entries = []
        else:
            self.filtered_entries = self.analysis_service.filter_entries(
                self.all_entries,
                search_text=self.search_var.get(),
                severities=selected_severities,
                critical_only=self.critical_only_var.get(),
            )

        self._update_dashboard()

    def clear_filters(self) -> None:
        self.search_var.set("")
        self.error_var.set(True)
        self.warning_var.set(True)
        self.info_var.set(True)
        self.critical_only_var.set(False)
        self.apply_filters()

    def export_excel(self) -> None:
        if not self.filtered_entries:
            messagebox.showwarning("Nothing to Export", "Load logs and keep at least one visible entry.")
            return

        destination = filedialog.asksaveasfilename(
            title="Export Excel Report",
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook", "*.xlsx")],
        )
        if not destination:
            return

        try:
            report = self.report_service.build_report(self.filtered_entries, len(self.loaded_files))
            output_path = self.excel_exporter.export(report, destination)
            self.status_var.set(f"Excel report exported to {output_path}")
            messagebox.showinfo("Export Complete", f"Excel report saved to:\n{output_path}")
        except Exception as exc:
            LOGGER.exception("Excel export failed")
            messagebox.showerror("Export Failed", f"Unable to export Excel report.\n\n{exc}")

    def export_pdf(self) -> None:
        if not self.filtered_entries:
            messagebox.showwarning("Nothing to Export", "Load logs and keep at least one visible entry.")
            return

        destination = filedialog.asksaveasfilename(
            title="Export PDF Report",
            defaultextension=".pdf",
            filetypes=[("PDF Report", "*.pdf")],
        )
        if not destination:
            return

        try:
            report = self.report_service.build_report(self.filtered_entries, len(self.loaded_files))
            output_path = self.pdf_exporter.export(report, destination)
            self.status_var.set(f"PDF report exported to {output_path}")
            messagebox.showinfo("Export Complete", f"PDF report saved to:\n{output_path}")
        except Exception as exc:
            LOGGER.exception("PDF export failed")
            messagebox.showerror("Export Failed", f"Unable to export PDF report.\n\n{exc}")

    def _on_theme_change(self, mode: str) -> None:
        self.theme_manager.set_mode(mode)
        self._apply_theme()
        self._update_dashboard()

    def _apply_theme(self) -> None:
        palette = self.theme_manager.palette()
        self.configure(fg_color=palette["surface"])
        self.header_frame.configure(fg_color=palette["card"])
        self.toolbar.configure(fg_color=palette["card"])
        self.right_panel.configure(fg_color=palette["card"])
        self.summary_text.configure(fg_color=palette["card_alt"], text_color=palette["text"])
        self.title_label.configure(text_color=palette["text"])
        self.subtitle_label.configure(text_color=palette["muted"])
        self.summary_title.configure(text_color=palette["text"])
        self.status_label.configure(text_color=palette["muted"])

        for card in [self.total_card, self.error_card, self.warning_card, self.critical_card]:
            card.configure(fg_color=palette["card"])
            card.value_label.configure(text_color=palette["text"])

        self.log_table.apply_theme(self.theme_var.get())

    def _update_dashboard(self) -> None:
        entries = self.filtered_entries if self.loaded_files else []
        self.current_summary = self.analysis_service.summarize(entries, len(self.loaded_files))
        summary_text = self.report_service.build_summary_text(self.current_summary)

        self.total_card.set_value(self.current_summary.total_entries)
        self.error_card.set_value(self.current_summary.severity_counts.get(Severity.ERROR, 0))
        self.warning_card.set_value(self.current_summary.severity_counts.get(Severity.WARNING, 0))
        self.critical_card.set_value(self.current_summary.critical_count)

        self.log_table.populate(entries)
        self.chart_frame.render(self.current_summary, self.theme_var.get())

        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", summary_text)
        self.summary_text.configure(state="disabled")

        if self.loaded_files:
            active_filter = "critical only" if self.critical_only_var.get() else "all severities"
            self.status_var.set(
                f"Displaying {len(entries)} of {len(self.all_entries)} entries across {len(self.loaded_files)} file(s) using {active_filter}."
            )
        else:
            self.status_var.set("Load one or more log files to begin.")

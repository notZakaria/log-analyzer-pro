from __future__ import annotations

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from log_analyzer_pro.domain.models import AnalysisSummary, Severity


class ChartFrame(ctk.CTkFrame):
    """Render severity and recurring error charts."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, corner_radius=18, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.figure = Figure(figsize=(6.0, 4.5), dpi=100)
        self.severity_ax = self.figure.add_subplot(211)
        self.errors_ax = self.figure.add_subplot(212)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

    def render(self, summary: AnalysisSummary, appearance_mode: str) -> None:
        background = "#ffffff" if appearance_mode == "Light" else "#111827"
        foreground = "#0f172a" if appearance_mode == "Light" else "#f8fafc"
        grid = "#cbd5e1" if appearance_mode == "Light" else "#334155"

        self.figure.patch.set_facecolor(background)
        self.severity_ax.clear()
        self.errors_ax.clear()

        severities = [Severity.ERROR, Severity.WARNING, Severity.INFO]
        values = [summary.severity_counts.get(severity, 0) for severity in severities]
        colors = ["#ef4444", "#f59e0b", "#10b981"]

        self.severity_ax.bar([severity.value for severity in severities], values, color=colors)
        self.severity_ax.set_title("Severity Distribution", color=foreground, pad=10)
        self.severity_ax.set_facecolor(background)
        self.severity_ax.tick_params(colors=foreground)
        for spine in self.severity_ax.spines.values():
            spine.set_color(grid)
        self.severity_ax.grid(axis="y", color=grid, alpha=0.25)

        top_errors = summary.error_occurrences.most_common(5)
        labels = [error[:45] + ("..." if len(error) > 45 else "") for error, _ in top_errors]
        counts = [count for _, count in top_errors]

        if labels:
            self.errors_ax.barh(labels[::-1], counts[::-1], color="#38bdf8")
        self.errors_ax.set_title("Top Recurring Errors", color=foreground, pad=10)
        self.errors_ax.set_facecolor(background)
        self.errors_ax.tick_params(colors=foreground, labelsize=8)
        for spine in self.errors_ax.spines.values():
            spine.set_color(grid)
        self.errors_ax.grid(axis="x", color=grid, alpha=0.25)

        self.figure.tight_layout(h_pad=2)
        self.canvas.draw_idle()

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from log_analyzer_pro.domain.models import LogEntry


class LogTable(ctk.CTkFrame):
    """Structured log table with highlighting support."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, corner_radius=18, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        columns = ("timestamp", "severity", "source_file", "line_number", "message")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=18)
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("severity", text="Severity")
        self.tree.heading("source_file", text="Source File")
        self.tree.heading("line_number", text="Line")
        self.tree.heading("message", text="Message")

        self.tree.column("timestamp", width=140, anchor=tk.W)
        self.tree.column("severity", width=90, anchor=tk.CENTER)
        self.tree.column("source_file", width=140, anchor=tk.W)
        self.tree.column("line_number", width=70, anchor=tk.CENTER)
        self.tree.column("message", width=760, anchor=tk.W)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(12, 0), pady=12)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 12), pady=12)

        self._configure_tags()

    def apply_theme(self, appearance_mode: str) -> None:
        style = ttk.Style()
        style.theme_use("default")

        if appearance_mode == "Light":
            background = "#ffffff"
            text = "#0f172a"
            heading_bg = "#dbeafe"
            field_bg = "#f8fafc"
            selected_bg = "#bfdbfe"
        else:
            background = "#111827"
            text = "#f8fafc"
            heading_bg = "#1e3a8a"
            field_bg = "#0f172a"
            selected_bg = "#1d4ed8"

        style.configure(
            "Treeview",
            background=background,
            fieldbackground=field_bg,
            foreground=text,
            rowheight=28,
            borderwidth=0,
        )
        style.map("Treeview", background=[("selected", selected_bg)])
        style.configure(
            "Treeview.Heading",
            background=heading_bg,
            foreground=text,
            relief="flat",
            padding=8,
        )
        self._configure_tags()

    def populate(self, entries: list[LogEntry]) -> None:
        self.tree.delete(*self.tree.get_children())
        for entry in entries:
            tags = []
            if entry.is_critical:
                tags.append("critical")
            elif entry.severity.value == "ERROR":
                tags.append("error")
            elif entry.severity.value == "WARNING":
                tags.append("warning")
            else:
                tags.append("info")

            self.tree.insert(
                "",
                "end",
                values=(
                    entry.timestamp,
                    entry.severity.value,
                    entry.source_file,
                    entry.line_number,
                    entry.message,
                ),
                tags=tuple(tags),
            )

    def _configure_tags(self) -> None:
        self.tree.tag_configure("critical", background="#7f1d1d", foreground="#ffffff")
        self.tree.tag_configure("error", background="#3f1d1d", foreground="#fee2e2")
        self.tree.tag_configure("warning", background="#3b2f0e", foreground="#fef3c7")
        self.tree.tag_configure("info", background="", foreground="")

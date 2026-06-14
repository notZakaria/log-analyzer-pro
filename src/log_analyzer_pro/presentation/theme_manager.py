from __future__ import annotations

import customtkinter as ctk


class ThemeManager:
    """Centralize appearance mode decisions."""

    def __init__(self) -> None:
        self.mode = "Dark"
        ctk.set_default_color_theme("blue")
        ctk.set_appearance_mode(self.mode)

    def set_mode(self, mode: str) -> None:
        self.mode = mode.title()
        ctk.set_appearance_mode(self.mode)

    def palette(self) -> dict[str, str]:
        if self.mode == "Light":
            return {
                "surface": "#f8fafc",
                "card": "#ffffff",
                "card_alt": "#e2e8f0",
                "text": "#0f172a",
                "muted": "#475569",
                "accent": "#1d4ed8",
            }

        return {
            "surface": "#0b1120",
            "card": "#111827",
            "card_alt": "#1f2937",
            "text": "#f8fafc",
            "muted": "#94a3b8",
            "accent": "#38bdf8",
        }

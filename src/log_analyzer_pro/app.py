from __future__ import annotations

import logging

from log_analyzer_pro.infrastructure.logging_config import configure_logging
from log_analyzer_pro.presentation.main_window import LogAnalyzerApp


def run() -> None:
    configure_logging()
    logging.getLogger(__name__).info("Starting Log Analyzer Pro")
    app = LogAnalyzerApp()
    app.mainloop()

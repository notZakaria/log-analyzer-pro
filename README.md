# Log Analyzer Pro

Log Analyzer Pro is a production-style Python desktop application for test engineers and validation engineers who need to inspect large log files quickly, identify recurring issues, and export professional reports.

The project targets Python 3.12 and uses a clean, layered architecture with a modern `CustomTkinter` interface.

## Features

- Load one or multiple log files in `.log` or `.txt` format
- Detect `ERROR`, `WARNING`, and `INFO` messages
- Count recurring error signatures automatically
- Search and filter by severity, text, and critical-only mode
- Highlight critical errors in the results table
- Display severity statistics and recurring error charts
- Generate a live summary report for the current filtered view
- Export analysis results to Excel and PDF
- Switch between dark and light themes
- Keep parsing, analytics, exports, and UI separated for maintainability

## Folder Structure

```text
log-analyzer-pro/
  main.py
  requirements.txt
  README.md
  sample_logs/
    smoke_test.log
    regression_suite.log
    integration_run.log
  src/
    log_analyzer_pro/
      __init__.py
      app.py
      application/
        __init__.py
        analyzer.py
        log_parser.py
        report_service.py
      domain/
        __init__.py
        models.py
      infrastructure/
        __init__.py
        logging_config.py
        exporters/
          __init__.py
          excel_exporter.py
          pdf_exporter.py
      presentation/
        __init__.py
        main_window.py
        theme_manager.py
        widgets/
          __init__.py
          chart_frame.py
          log_table.py
```

## Installation

### 1. Clone the project

```powershell
cd your project path
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Run the application

```powershell
python main.py
```

## How to Use

1. Click `Load Log Files` and select one or more sample logs or your own logs.
2. Use the search box and severity filters to narrow the dataset.
3. Enable `Critical Only` to focus on the highest-risk events.
4. Review the statistics cards, charts, table, and summary panel.
5. Export the current filtered view to Excel or PDF.

## Architecture

The application follows a lightweight clean architecture:

- `domain` contains the core business entities and report models.
- `application` contains parsing, analytics, and summary-building logic.
- `infrastructure` contains logging and export implementations.
- `presentation` contains the CustomTkinter GUI and reusable widgets.

This keeps the parsing and reporting logic independent from the UI, which makes the project easier to extend and test.

## File-by-File Explanation

### Root Files

- `main.py`
  Launches the desktop app and ensures the `src` directory is available on `sys.path`.

- `requirements.txt`
  Lists the Python dependencies needed for the GUI, charts, Excel export, and PDF export.

- `README.md`
  Documents installation, usage, architecture, and file explanations.

### Source Package

- `src/log_analyzer_pro/__init__.py`
  Defines the package and version.

- `src/log_analyzer_pro/app.py`
  Application entry module that configures logging and starts the main window.

### Domain Layer

- `src/log_analyzer_pro/domain/models.py`
  Defines the severity enum, structured log entry model, summary model, and export bundle.

### Application Layer

- `src/log_analyzer_pro/application/log_parser.py`
  Parses raw text lines, extracts timestamps, detects severity, normalizes error signatures, and flags critical failures.

- `src/log_analyzer_pro/application/analyzer.py`
  Builds summary statistics, filters entries, and returns the top recurring error signatures.

- `src/log_analyzer_pro/application/report_service.py`
  Converts analysis results into export-ready summary text and report bundles.

### Infrastructure Layer

- `src/log_analyzer_pro/infrastructure/logging_config.py`
  Sets up rotating application logs for operational traceability and debugging.

- `src/log_analyzer_pro/infrastructure/exporters/excel_exporter.py`
  Exports summaries, detailed entries, and recurring error counts into a multi-sheet Excel workbook.

- `src/log_analyzer_pro/infrastructure/exporters/pdf_exporter.py`
  Creates a formatted PDF report with summary metrics, top errors, and a preview of detailed entries.

### Presentation Layer

- `src/log_analyzer_pro/presentation/main_window.py`
  Builds the main application window, toolbar, filters, cards, table, charts, theme switching, and export workflows.

- `src/log_analyzer_pro/presentation/theme_manager.py`
  Centralizes appearance mode changes and color palette decisions.

- `src/log_analyzer_pro/presentation/widgets/chart_frame.py`
  Embeds Matplotlib charts inside the CustomTkinter interface.

- `src/log_analyzer_pro/presentation/widgets/log_table.py`
  Provides a styled, scrollable log table with critical-error highlighting.

## Sample Logs

The `sample_logs/` folder includes ready-to-use files with repeated errors, warnings, info messages, and a critical failure so you can validate:

- multi-file loading
- recurring error counting
- search and filter behavior
- chart generation
- Excel and PDF exports

## Error Handling and Logging

- Invalid file selections are handled with dialog-based error messages.
- Parsing failures and export failures are logged and surfaced to the user.
- Application logs are written to `log-analyzer-pro/logs/log_analyzer_pro.log` at runtime.

## Notes

- The parser focuses on common plain-text log formats and severity keywords.
- PDF export includes a detailed preview and keeps the full dataset available through Excel for very large result sets.
- The exported reports reflect the current filtered view shown in the UI.

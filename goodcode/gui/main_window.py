from __future__ import annotations

import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from goodcode.core.models import (
    GOOD_PATTERNS_FOUND,
    NO_GOOD_PATTERNS_FOUND,
    PARSE_ERROR,
    READ_ERROR,
    ScanResult,
)
from goodcode.gui.result_view import ResultView


def _ensure_tk_library_paths() -> None:
    if os.environ.get("TCL_LIBRARY") and os.environ.get("TK_LIBRARY"):
        return

    base_path = Path(sys.base_prefix)
    candidates = (
        (base_path / "tcl" / "tcl8.6", base_path / "tcl" / "tk8.6"),
        (base_path / "Library" / "lib" / "tcl8.6", base_path / "Library" / "lib" / "tk8.6"),
    )

    for tcl_path, tk_path in candidates:
        if tcl_path.exists() and tk_path.exists():
            os.environ.setdefault("TCL_LIBRARY", str(tcl_path))
            os.environ.setdefault("TK_LIBRARY", str(tk_path))
            return


class MainWindow(tk.Tk):
    def __init__(self, scan_service) -> None:
        _ensure_tk_library_paths()
        super().__init__()
        self._scan_service = scan_service
        self._selected_file: str | None = None
        self._result: ScanResult | None = None

        self.title("Good Code Hunter")
        self.geometry("1220x760")
        self.minsize(1080, 680)
        self.configure(bg="#f3f6f8")

        self.file_path_var = tk.StringVar(value="No Python file selected yet.")
        self.status_var = tk.StringVar(value="Select a Python file to begin.")
        self.summary_var = tk.StringVar(value="0 findings  |  0 categories")

        self._configure_styles()
        self._build_layout()
        self._set_state("EMPTY", "Select a Python file to begin.")

    def current_result(self) -> ScanResult | None:
        return self._result

    def set_selected_file(self, path: str) -> None:
        self._selected_file = path
        self.file_path_var.set(path)
        self._result = None
        self._update_summary(None)
        self.result_view.show_empty("Press scan to analyze the selected Python file.")
        self._set_state("READY", f"Ready to scan {Path(path).name}.")

    def run_scan(self) -> None:
        if not self._selected_file:
            self._set_state("EMPTY", "Select a Python file before scanning.")
            return

        self._set_state("SCANNING", "Scanning with AST-based static analysis.")
        self.update_idletasks()

        result = self._scan_service(self._selected_file)
        self._result = result
        self._update_summary(result)

        if result.status == GOOD_PATTERNS_FOUND:
            self.result_view.set_findings(result.findings)
            categories = len({finding.category for finding in result.findings})
            self._set_state(
                "SUCCESS_WITH_FINDINGS",
                f"Found {len(result.findings)} good patterns across {categories} categories.",
            )
        elif result.status == NO_GOOD_PATTERNS_FOUND:
            self.result_view.show_empty(
                "No good security patterns were found for the current rules."
            )
            self._set_state(
                "SUCCESS_EMPTY",
                "Scan finished successfully, but no good patterns were found.",
            )
        elif result.status == PARSE_ERROR:
            warning = result.warnings[0] if result.warnings else "Python syntax error."
            self.result_view.show_error(warning)
            self._set_state(
                "ERROR",
                f"Could not analyze the file because of a syntax error. {warning}",
            )
        elif result.status == READ_ERROR:
            warning = result.warnings[0] if result.warnings else "Could not read file."
            self.result_view.show_error(warning)
            self._set_state(
                "ERROR",
                f"Could not read the selected file. {warning}",
            )
        else:
            self.result_view.show_error("Unknown scan result status.")
            self._set_state("ERROR", "Unknown scan result status.")

    def save_current_result(self) -> None:
        if self._result is None:
            return

        file_path = filedialog.asksaveasfilename(
            title="Save scan result as JSON",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialfile=f"{Path(self._result.target).stem or 'scan-result'}.json",
        )
        if not file_path:
            return

        Path(file_path).write_text(
            json.dumps(self._result.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Root.TFrame", background="#f3f6f8")
        style.configure(
            "Card.TFrame",
            background="#ffffff",
            relief="flat",
        )
        style.configure(
            "Title.TLabel",
            background="#f3f6f8",
            foreground="#12202f",
            font=("Segoe UI", 22, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background="#f3f6f8",
            foreground="#52606d",
            font=("Segoe UI", 11),
        )
        style.configure(
            "SectionTitle.TLabel",
            background="#ffffff",
            foreground="#12202f",
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "SectionLabel.TLabel",
            background="#ffffff",
            foreground="#52606d",
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "DetailTitle.TLabel",
            background="#ffffff",
            foreground="#12202f",
            font=("Segoe UI", 14, "bold"),
        )
        style.configure(
            "Muted.TLabel",
            background="#ffffff",
            foreground="#5f6f7f",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Summary.TLabel",
            background="#ffffff",
            foreground="#213243",
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(18, 10),
        )

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=20, style="Root.TFrame")
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(3, weight=1)

        header = ttk.Frame(root, style="Root.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        ttk.Label(header, text="착한코드검거단", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Find positive security evidence in one Python file without executing it.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(6, 0))

        top_card = ttk.Frame(root, padding=18, style="Card.TFrame")
        top_card.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        top_card.columnconfigure(0, weight=1)
        top_card.columnconfigure(1, weight=0)

        ttk.Label(top_card, text="Selected File", style="SectionTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Button(top_card, text="파일 선택", command=self._choose_file).grid(
            row=0, column=1, sticky="e"
        )

        ttk.Label(
            top_card,
            textvariable=self.file_path_var,
            style="Muted.TLabel",
            wraplength=900,
            justify="left",
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 14))

        action_row = ttk.Frame(top_card, style="Card.TFrame")
        action_row.grid(row=2, column=0, columnspan=2, sticky="ew")
        action_row.columnconfigure(1, weight=1)

        self.scan_button = ttk.Button(
            action_row,
            text="착한코드 검거 시작",
            command=self.run_scan,
            style="Primary.TButton",
        )
        self.scan_button.grid(row=0, column=0, sticky="w")

        ttk.Label(
            action_row,
            textvariable=self.status_var,
            style="Muted.TLabel",
            wraplength=760,
            justify="left",
        ).grid(row=0, column=1, sticky="ew", padx=(14, 0))

        summary_card = ttk.Frame(root, padding=18, style="Card.TFrame")
        summary_card.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        summary_card.columnconfigure(0, weight=1)
        ttk.Label(summary_card, text="Scan Summary", style="SectionTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            summary_card,
            textvariable=self.summary_var,
            style="Summary.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(10, 0))

        self.result_view = ResultView(root)
        self.result_view.grid(row=3, column=0, sticky="nsew", pady=(0, 16))

        bottom_card = ttk.Frame(root, padding=18, style="Card.TFrame")
        bottom_card.grid(row=4, column=0, sticky="ew")
        bottom_card.columnconfigure(1, weight=1)

        self.export_button = ttk.Button(
            bottom_card,
            text="JSON 결과 저장",
            command=self.save_current_result,
        )
        self.export_button.grid(row=0, column=0, sticky="w")

        ttk.Label(
            bottom_card,
            text=(
                "This tool shows positive security patterns only. "
                "It does not guarantee the file is free of vulnerabilities."
            ),
            style="Muted.TLabel",
            wraplength=780,
            justify="left",
        ).grid(row=0, column=1, sticky="e", padx=(16, 0))

    def _choose_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select a Python file",
            filetypes=[("Python Files", "*.py")],
        )
        if file_path:
            self.set_selected_file(file_path)

    def _set_state(self, state: str, message: str) -> None:
        self.status_var.set(message)

        if state in {"EMPTY"} or state in {"SCANNING"}:
            self.scan_button.configure(state="disabled")
        else:
            self.scan_button.configure(
                state="normal" if self._selected_file is not None else "disabled"
            )

        self._update_export_state()

    def _update_export_state(self) -> None:
        enabled = (
            self._result is not None
            and self._result.status
            in {GOOD_PATTERNS_FOUND, NO_GOOD_PATTERNS_FOUND}
        )
        self.export_button.configure(state="normal" if enabled else "disabled")

    def _update_summary(self, result: ScanResult | None) -> None:
        if result is None:
            self.summary_var.set("0 findings  |  0 categories")
            return

        finding_count = len(result.findings)
        category_count = len({finding.category for finding in result.findings})
        self.summary_var.set(
            f"{finding_count} findings  |  {category_count} categories"
        )

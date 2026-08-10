from __future__ import annotations

import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from goodcode.core.models import (
    GOOD_PATTERNS_FOUND,
    NO_GOOD_PATTERNS_FOUND,
    PARSE_ERROR,
    READ_ERROR,
    ScanResult,
)
from goodcode.gui.result_view import ResultView


def _ensure_tk_library_paths() -> None:
    base_path = Path(sys.base_prefix)
    candidates = (
        (base_path / "tcl" / "tcl8.6", base_path / "tcl" / "tk8.6"),
        (
            base_path / "Library" / "lib" / "tcl8.6",
            base_path / "Library" / "lib" / "tk8.6",
        ),
    )

    for tcl_path, tk_path in candidates:
        if (tcl_path / "init.tcl").exists() and (tk_path / "tk.tcl").exists():
            os.environ["TCL_LIBRARY"] = str(tcl_path)
            os.environ["TK_LIBRARY"] = str(tk_path)
            return


class MainWindow(tk.Tk):
    def __init__(self, scan_service) -> None:
        _ensure_tk_library_paths()
        super().__init__()
        self._scan_service = scan_service
        self._selected_file: str | None = None
        self._result: ScanResult | None = None

        self.title("착한코드검거단")
        self.geometry("1380x860")
        self.minsize(1220, 760)
        self.configure(bg="#f4f7f6")

        self.page_title_var = tk.StringVar(value="검거소")
        self.file_path_var = tk.StringVar(value="아직 선택된 파일이 없습니다.")
        self.file_hint_var = tk.StringVar(
            value="코드는 이 앱 안에서만 읽히며 실행되지 않습니다."
        )
        self.status_var = tk.StringVar(value="Python 파일을 선택해주세요.")
        self.summary_var = tk.StringVar(value="0 findings · 0 categories · 0 lines")
        self._status_badge_var = tk.StringVar(value="EMPTY")

        self.nav_buttons: dict[str, ttk.Button] = {}
        self.logo_image: tk.PhotoImage | None = None
        self.logo_label: tk.Label | None = None

        self._configure_styles()
        self._build_layout()
        self._set_state("EMPTY", "Python 파일을 선택해주세요.")

    def current_result(self) -> ScanResult | None:
        return self._result

    def set_selected_file(self, path: str) -> None:
        self._selected_file = path
        self.file_path_var.set(path)
        self.file_hint_var.set(f"{Path(path).name} 분석 준비가 완료되었습니다.")
        self._result = None
        self._update_summary(None)
        self.result_view.show_empty("파일이 준비되었습니다. 검거 시작 버튼을 눌러주세요.")
        self._set_state("READY", f"{Path(path).name} 분석 준비 완료")

    def run_scan(self) -> None:
        if not self._selected_file:
            self._set_state("EMPTY", "Python 파일을 먼저 선택해주세요.")
            return

        self._set_state("SCANNING", "AST 기반 정적 분석으로 규칙을 적용하는 중입니다.")
        self.update_idletasks()

        result = self._scan_service(self._selected_file)
        self._result = result
        self._update_summary(result)

        if result.status == GOOD_PATTERNS_FOUND:
            self.result_view.set_findings(result.findings)
            categories = len({finding.category for finding in result.findings})
            self._set_state(
                "SUCCESS_WITH_FINDINGS",
                f"{len(result.findings)}개의 착한코드를 검거했습니다 · 카테고리 {categories}개",
            )
            return

        if result.status == NO_GOOD_PATTERNS_FOUND:
            self.result_view.show_empty(
                "현재 규칙 기준으로 확인 가능한 착한코드를 찾지 못했습니다."
            )
            self._set_state(
                "SUCCESS_EMPTY",
                "분석은 정상 종료되었지만 표시할 착한코드는 없습니다.",
            )
            return

        if result.status == PARSE_ERROR:
            warning = result.warnings[0] if result.warnings else "Python 문법 오류입니다."
            self.result_view.show_error(warning)
            self._set_state("ERROR", f"문법 오류 때문에 분석할 수 없습니다. {warning}")
            return

        if result.status == READ_ERROR:
            warning = result.warnings[0] if result.warnings else "파일을 읽을 수 없습니다."
            self.result_view.show_error(warning)
            self._set_state("ERROR", f"파일을 읽을 수 없습니다. {warning}")
            return

        self.result_view.show_error("알 수 없는 분석 상태입니다.")
        self._set_state("ERROR", "알 수 없는 분석 상태입니다.")

    def save_current_result(self) -> None:
        if self._result is None:
            return

        file_path = filedialog.asksaveasfilename(
            title="JSON 결과 저장",
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

        style.configure("Page.TFrame", background="#f4f7f6")
        style.configure("Topbar.TFrame", background="#ffffff")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("SoftCard.TFrame", background="#f7faf9")
        style.configure("InfoBar.TFrame", background="#eef3f2")
        title_font = ("Pretendard", 24, "bold")
        body_font = ("Pretendard", 10)
        body_bold_font = ("Pretendard", 10, "bold")
        small_font = ("Pretendard", 9)
        style.configure("Brand.TLabel", background="#ffffff", foreground="#112431", font=("Pretendard", 14, "bold"))
        style.configure("BrandSmall.TLabel", background="#ffffff", foreground="#7b8a97", font=("Pretendard", 8, "bold"))
        style.configure("PageKicker.TLabel", background="#f4f7f6", foreground="#738391", font=small_font)
        style.configure("Title.TLabel", background="#f4f7f6", foreground="#132632", font=title_font)
        style.configure("Subtitle.TLabel", background="#f4f7f6", foreground="#5e6f7b", font=body_font)
        style.configure("PanelTitle.TLabel", background="#ffffff", foreground="#112431", font=("Pretendard", 11, "bold"))
        style.configure("PanelCount.TLabel", background="#ffffff", foreground="#7b8a97", font=small_font)
        style.configure("FileBadge.TLabel", background="#ffffff", foreground="#5f7180", font=("Consolas", 9, "bold"))
        style.configure("Body.TLabel", background="#ffffff", foreground="#4f6170", font=body_font)
        style.configure("StrongBody.TLabel", background="#ffffff", foreground="#1d3141", font=body_bold_font)
        style.configure("DetailTitle.TLabel", background="#ffffff", foreground="#172935", font=("Pretendard", 14, "bold"))
        style.configure("SummaryStrip.TLabel", background="#f7faf9", foreground="#485d6c", font=small_font)
        style.configure("StatusBadge.TLabel", background="#eef4f2", foreground="#5f756f", padding=(8, 4), font=small_font)
        style.configure("Disclaimer.TLabel", background="#eef3f2", foreground="#667887", font=small_font)
        style.configure("Footer.TLabel", background="#f4f7f6", foreground="#7b8a97", font=small_font)

        style.configure(
            "Topnav.TButton",
            background="#ffffff",
            foreground="#5c6d79",
            borderwidth=0,
            padding=(10, 6),
            font=body_bold_font,
        )
        style.map(
            "Topnav.TButton",
            background=[("active", "#ffffff")],
            foreground=[("active", "#0f7568")],
        )

        style.configure(
            "TopnavActive.TButton",
            background="#ffffff",
            foreground="#0f7568",
            borderwidth=0,
            padding=(10, 6),
            font=body_bold_font,
        )
        style.map(
            "TopnavActive.TButton",
            background=[("disabled", "#ffffff")],
            foreground=[("disabled", "#0f7568")],
        )

        style.configure(
            "Primary.TButton",
            background="#0f7568",
            foreground="#ffffff",
            borderwidth=0,
            focusthickness=0,
            padding=(18, 11),
            font=body_bold_font,
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#0a5e54"), ("disabled", "#c5d2cf")],
            foreground=[("disabled", "#f6f8f8")],
        )

        style.configure(
            "Ghost.TButton",
            background="#ffffff",
            foreground="#163443",
            bordercolor="#d9e3e1",
            lightcolor="#d9e3e1",
            darkcolor="#d9e3e1",
            padding=(14, 9),
            font=small_font,
        )
        style.map(
            "Ghost.TButton",
            background=[("active", "#f0f6f4"), ("disabled", "#f6f8f8")],
            foreground=[("disabled", "#94a3af")],
        )

        style.configure(
            "Treeview",
            background="#ffffff",
            foreground="#1c3141",
            fieldbackground="#ffffff",
            borderwidth=0,
            rowheight=42,
            font=body_font,
        )
        style.map("Treeview", background=[("selected", "#dff3ee")], foreground=[("selected", "#0f7568")])
        style.configure(
            "Treeview.Heading",
            background="#f7faf9",
            foreground="#677887",
            borderwidth=0,
            font=small_font,
        )

    def _build_layout(self) -> None:
        shell = ttk.Frame(self, padding=20, style="Page.TFrame")
        shell.pack(fill="both", expand=True)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)

        outer = ttk.Frame(shell, style="Page.TFrame")
        outer.grid(row=0, column=0, sticky="nsew")
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        center = ttk.Frame(outer, style="Page.TFrame")
        center.grid(row=0, column=0, sticky="n")
        center.columnconfigure(0, weight=1)
        center.rowconfigure(2, weight=1)

        self._build_topbar(center)
        self._build_page_header(center)
        self._build_content(center)
        self._build_footer(center)

    def _build_topbar(self, parent: ttk.Frame) -> None:
        topbar = ttk.Frame(parent, padding=(18, 10), style="Topbar.TFrame")
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.columnconfigure(1, weight=1)

        brand = ttk.Frame(topbar, style="Topbar.TFrame")
        brand.grid(row=0, column=0, sticky="w")
        self.logo_label = self._create_logo_label(brand)
        self.logo_label.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 12))
        ttk.Label(brand, text="착한코드검거단", style="Brand.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(brand, text="v0.1", style="BrandSmall.TLabel").grid(row=0, column=2, sticky="w", padx=(8, 0))

        nav = ttk.Frame(topbar, style="Topbar.TFrame")
        nav.grid(row=0, column=1, sticky="w", padx=(28, 0))
        for name in ("홈", "검거소", "랭킹", "규칙집"):
            button = ttk.Button(
                nav,
                text=name,
                style="TopnavActive.TButton" if name == "검거소" else "Topnav.TButton",
                command=lambda item=name: self._show_placeholder(item),
            )
            if name == "검거소":
                button.configure(state="disabled")
            button.pack(side="left", padx=(0, 6))
            self.nav_buttons[name] = button

        ttk.Label(
            topbar,
            text="STATIC · 대상 코드는 실행하지 않음",
            style="StatusBadge.TLabel",
        ).grid(row=0, column=2, sticky="e")

        self.nav_underline = tk.Frame(topbar, bg="#0f7568", height=2)
        topbar.update_idletasks()
        self._place_nav_underline()

    def _place_nav_underline(self) -> None:
        active_button = self.nav_buttons.get("검거소")
        if not active_button:
            return
        active_button.update_idletasks()
        self.nav_underline.place(
            in_=active_button,
            x=10,
            rely=1.0,
            y=-1,
            width=max(24, active_button.winfo_width() - 20),
            height=2,
        )

    def _create_logo_label(self, parent: ttk.Frame) -> tk.Label:
        logo_path = Path("assets/branding/good-code-hunters-logo.png")
        if logo_path.exists():
            try:
                original = tk.PhotoImage(file=str(logo_path))
                scale = max(1, original.width() // 138)
                self.logo_image = original.subsample(scale, scale)
                return tk.Label(parent, image=self.logo_image, bg="#ffffff", bd=0)
            except tk.TclError:
                self.logo_image = None

        return tk.Label(
            parent,
            text="GCH",
            bg="#ffffff",
            fg="#5f7180",
            font=("Consolas", 10, "bold"),
            bd=0,
        )

    def _build_page_header(self, parent: ttk.Frame) -> None:
        header = ttk.Frame(parent, padding=(6, 18, 6, 16), style="Page.TFrame")
        header.grid(row=1, column=0, sticky="ew")
        ttk.Label(header, text="홈 / 검거소", style="PageKicker.TLabel").pack(anchor="w")
        ttk.Label(header, textvariable=self.page_title_var, style="Title.TLabel").pack(anchor="w", pady=(6, 4))
        ttk.Label(
            header,
            text="Python 파일 하나를 실행하지 않고 정적으로 분석해 확인 가능한 보안 패턴을 찾습니다.",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

    def _build_content(self, parent: ttk.Frame) -> None:
        content = ttk.Frame(parent, style="Page.TFrame")
        content.grid(row=2, column=0, sticky="nsew")
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(1, weight=1)

        self._build_upload_panel(content)
        self._build_results_panel(content)
        self._build_disclaimer(content)

    def _build_upload_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.Frame(parent, padding=22, style="Card.TFrame")
        panel.grid(row=0, column=0, sticky="ew", padx=(0, 16), pady=(0, 16))
        panel.columnconfigure(0, weight=1)

        header = ttk.Frame(panel, style="Card.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="분석 대상", style="PanelTitle.TLabel").pack(side="left")
        ttk.Label(header, text=".py · 단일 파일", style="PanelCount.TLabel").pack(side="right")

        drop = ttk.Frame(panel, padding=16, style="SoftCard.TFrame")
        drop.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        drop.columnconfigure(1, weight=1)
        ttk.Label(drop, text=".py", style="FileBadge.TLabel").grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 12))
        ttk.Label(drop, text="Python 파일을 선택해주세요.", style="StrongBody.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(
            drop,
            textvariable=self.file_hint_var,
            style="Body.TLabel",
            wraplength=680,
            justify="left",
        ).grid(row=1, column=1, sticky="ew", pady=(4, 0))
        ttk.Button(drop, text="파일 선택", style="Ghost.TButton", command=self._choose_file).grid(
            row=0, column=2, rowspan=2, sticky="e", padx=(14, 0)
        )

        path_bar = ttk.Frame(panel, padding=(12, 10), style="SoftCard.TFrame")
        path_bar.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        path_bar.columnconfigure(0, weight=1)
        ttk.Label(
            path_bar,
            textvariable=self.file_path_var,
            style="Body.TLabel",
            wraplength=780,
            justify="left",
        ).grid(row=0, column=0, sticky="ew")

        action_row = ttk.Frame(panel, style="Card.TFrame")
        action_row.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        action_row.columnconfigure(2, weight=1)
        self.scan_button = ttk.Button(
            action_row,
            text="착한코드 검거 시작",
            command=self.run_scan,
            style="Primary.TButton",
        )
        self.scan_button.grid(row=0, column=0, sticky="w")
        ttk.Label(action_row, text="ast.parse() · AST 순회만 수행", style="PanelCount.TLabel").grid(
            row=0, column=1, sticky="w", padx=(12, 0)
        )

        status_row = ttk.Frame(panel, style="Card.TFrame")
        status_row.grid(row=4, column=0, sticky="ew", pady=(12, 0))
        status_row.columnconfigure(1, weight=1)
        self.status_badge = ttk.Label(
            status_row,
            textvariable=self._status_badge_var,
            style="StatusBadge.TLabel",
        )
        self.status_badge.grid(row=0, column=0, sticky="w")
        ttk.Label(
            status_row,
            textvariable=self.status_var,
            style="Body.TLabel",
            wraplength=760,
            justify="left",
        ).grid(row=0, column=1, sticky="ew", padx=(10, 0))

    def _build_results_panel(self, parent: ttk.Frame) -> None:
        left_stack = ttk.Frame(parent, style="Page.TFrame")
        left_stack.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
        left_stack.columnconfigure(0, weight=1)
        left_stack.rowconfigure(1, weight=1)

        summary_card = ttk.Frame(left_stack, style="Card.TFrame")
        summary_card.grid(row=0, column=0, sticky="ew")
        summary_card.columnconfigure(0, weight=1)

        summary_head = ttk.Frame(summary_card, padding=(18, 14), style="Card.TFrame")
        summary_head.grid(row=0, column=0, sticky="ew")
        ttk.Label(summary_head, text="검거 결과", style="PanelTitle.TLabel").pack(side="left")
        self.findings_count_label = ttk.Label(summary_head, text="—", style="PanelCount.TLabel")
        self.findings_count_label.pack(side="right")

        self.summary_strip = ttk.Label(
            summary_card,
            textvariable=self.summary_var,
            style="SummaryStrip.TLabel",
            anchor="w",
            padding=(18, 11),
        )
        self.summary_strip.grid(row=1, column=0, sticky="ew")

        self.result_view = ResultView(left_stack)
        self.result_view.grid(row=1, column=0, sticky="nsew")

        self.export_button = ttk.Button(
            self.result_view.detail_footer,
            text="JSON 결과 저장",
            command=self.save_current_result,
            style="Ghost.TButton",
        )
        self.export_button.grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.result_view.detail_footer,
            text="ScanResult v1.0 · line ASC · column ASC · rule ASC",
            style="PanelCount.TLabel",
        ).grid(row=0, column=1, sticky="e")

    def _build_disclaimer(self, parent: ttk.Frame) -> None:
        disclaimer = ttk.Frame(parent, padding=(14, 10), style="InfoBar.TFrame")
        disclaimer.grid(row=2, column=0, sticky="ew", padx=(0, 16), pady=(16, 0))
        disclaimer.columnconfigure(1, weight=1)
        ttk.Label(disclaimer, text="안내", style="PanelCount.TLabel").grid(row=0, column=0, sticky="nw", padx=(0, 12))
        ttk.Label(
            disclaimer,
            text=(
                "이 결과는 현재 규칙으로 확인된 긍정적 보안 패턴만 보여줍니다. "
                "코드 전체에 취약점이 없음을 보증하지 않습니다."
            ),
            style="Disclaimer.TLabel",
            wraplength=830,
            justify="left",
        ).grid(row=0, column=1, sticky="ew")

    def _build_footer(self, parent: ttk.Frame) -> None:
        footer = ttk.Frame(parent, padding=(6, 14, 6, 0), style="Page.TFrame")
        footer.grid(row=3, column=0, sticky="ew")
        ttk.Label(
            footer,
            text="착한코드검거단 MVP v0.1 · 홈 · 검거소 · 랭킹 · 규칙집",
            style="Footer.TLabel",
        ).pack(anchor="w")

    def _choose_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Python 파일 선택",
            filetypes=[("Python Files", "*.py")],
        )
        if file_path:
            self.set_selected_file(file_path)

    def _show_placeholder(self, item: str) -> None:
        messagebox.showinfo(
            "준비 중",
            f"{item} 화면 감성은 반영하지만, 현재 MVP 동작 화면은 검거소 중심입니다.",
        )

    def _set_state(self, state: str, message: str) -> None:
        badge_map = {
            "EMPTY": "EMPTY",
            "READY": "READY",
            "SCANNING": "SCANNING",
            "SUCCESS_WITH_FINDINGS": "SUCCESS",
            "SUCCESS_EMPTY": "SUCCESS_EMPTY",
            "ERROR": "ERROR",
        }
        self._status_badge_var.set(badge_map.get(state, state))
        self.status_var.set(message)

        if state in {"EMPTY", "SCANNING"}:
            self.scan_button.configure(state="disabled")
        else:
            self.scan_button.configure(
                state="normal" if self._selected_file is not None else "disabled"
            )

        self._update_export_state()

    def _update_export_state(self) -> None:
        enabled = (
            self._result is not None
            and self._result.status in {GOOD_PATTERNS_FOUND, NO_GOOD_PATTERNS_FOUND}
        )
        self.export_button.configure(state="normal" if enabled else "disabled")

    def _update_summary(self, result: ScanResult | None) -> None:
        if result is None:
            self.summary_var.set("0 findings · 0 categories · 0 lines")
            self.findings_count_label.configure(text="—")
            return

        finding_count = len(result.findings)
        category_count = len({finding.category for finding in result.findings})
        line_count = len({finding.line for finding in result.findings})
        self.summary_var.set(
            f"{finding_count} findings · {category_count} categories · {line_count} lines"
        )
        self.findings_count_label.configure(text=f"{finding_count} / total")

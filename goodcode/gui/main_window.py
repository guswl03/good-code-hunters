from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tempfile import gettempdir
from tkinter import filedialog, ttk

from goodcode.core.models import (
    GOOD_PATTERNS_FOUND,
    NO_GOOD_PATTERNS_FOUND,
    PARSE_ERROR,
    READ_ERROR,
    ScanResult,
)
from goodcode.exporters import export_scan_result
from goodcode.gui.result_view import ResultView


# ===
# 만든 이유: 소스 실행 위치와 PyInstaller 임시 실행 위치 모두에서 로고를 찾기 위해 필요하다.
# 코드 설명: frozen 실행이면 _MEIPASS, 개발 실행이면 저장소 루트를 기준으로 리소스 경로를 만든다.
# ===
def _resource_path(relative_path: str) -> Path:
    frozen_root = getattr(sys, "_MEIPASS", None)
    base_path = Path(frozen_root) if frozen_root else Path(__file__).resolve().parents[2]
    return base_path / relative_path


class MainWindow(tk.Tk):
    SAMPLE_FILE_NAME = "good_code_hunters_sample.py"
    SAMPLE_SOURCE = """import sqlite3
import secrets
import hashlib
import hmac
import subprocess
import yaml

conn = sqlite3.connect("app.db")
cursor = conn.cursor()
user_id = 7
cursor.execute(
    "SELECT * FROM users WHERE id = ?",
    (user_id,),
)

token = secrets.token_urlsafe(32)
password_hash = hashlib.pbkdf2_hmac("sha256", b"hunter-password", b"fixed-salt", 200_000)

expected = b"good-code-hunters"
provided = b"good-code-hunters"
is_match = hmac.compare_digest(provided, expected)

result = subprocess.run(["git", "status"], shell=False, check=False)
config = yaml.safe_load("safe: true")
"""

    def __init__(self, scan_service) -> None:
        super().__init__()
        self._scan_service = scan_service
        self._selected_file: str | None = None
        self._result: ScanResult | None = None

        self.title("착한코드검거단")
        self.geometry("1380x860")
        self.minsize(1220, 760)
        self.configure(bg="#f4f7f6")

        self.page_title_var = tk.StringVar(value="Python 보안 패턴 분석")
        self.product_description_var = tk.StringVar(
            value="Python 코드를 실행하지 않고 좋은 보안 패턴을 찾는 정적 분석기입니다."
        )
        self.file_path_var = tk.StringVar(value="아직 선택된 파일이 없습니다.")
        self.file_hint_var = tk.StringVar(
            value="Python 파일 하나를 선택하세요. 코드는 읽기만 하며 실행하지 않습니다."
        )
        self.status_var = tk.StringVar(value="Python 파일을 선택해주세요.")
        self.summary_var = tk.StringVar(value="0 findings · 0 categories · 0 lines")
        self._status_badge_var = tk.StringVar(value="EMPTY")
        self.disclaimer_var = tk.StringVar(
            value=(
                "이 결과는 확인 가능한 좋은 보안 패턴만 보여줍니다. "
                "파일 전체에 취약점이 없음을 보증하지 않습니다."
            )
        )

        self.pages: dict[str, ttk.Frame] = {}
        self.current_page = "검거소"
        self.logo_image: tk.PhotoImage | None = None
        self.logo_label: tk.Label | None = None
        self.sample_button: ttk.Button | None = None

        self._configure_styles()
        self._build_layout()
        self._init_pages()
        self._show_page("검거소")
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

        self._set_state("SCANNING", "AST 기반 정적 분석으로 규칙 6종을 적용하는 중입니다.")
        self.update_idletasks()

        result = self._scan_service(self._selected_file)
        self._result = result
        self._update_summary(result)

        if result.status == GOOD_PATTERNS_FOUND:
            self.result_view.set_findings(result.findings)
            categories = len({finding.category for finding in result.findings})
            self._set_state(
                "SUCCESS_WITH_FINDINGS",
                f"{len(result.findings)}개의 착한코드를 확인했습니다 · 카테고리 {categories}개",
            )
            return

        if result.status == NO_GOOD_PATTERNS_FOUND:
            self.result_view.show_empty("현재 규칙 기준으로 확인 가능한 착한코드가 없습니다.")
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

        # ===
        # 만든 이유: GUI와 Golden Test가 동일한 PRD JSON 계약을 사용해야 한다.
        # 코드 설명: GUI는 저장 위치만 선택하고 UTF-8 직렬화는 D의 Exporter에 맡긴다.
        # ===
        try:
            export_scan_result(self._result, file_path)
        except OSError:
            self._set_state(
                "ERROR",
                "JSON 결과를 저장할 수 없습니다. 저장 위치와 권한을 확인해주세요.",
            )

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        title_font = ("Pretendard", 24, "bold")
        body_font = ("Pretendard", 10)
        body_bold_font = ("Pretendard", 10, "bold")
        small_font = ("Pretendard", 9)

        style.configure("Page.TFrame", background="#f4f7f6")
        style.configure("Topbar.TFrame", background="#ffffff")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("SoftCard.TFrame", background="#f7faf9")
        style.configure("InfoBar.TFrame", background="#eef3f2")

        style.configure(
            "Brand.TLabel",
            background="#ffffff",
            foreground="#112431",
            font=("Pretendard", 14, "bold"),
        )
        style.configure(
            "BrandSmall.TLabel",
            background="#ffffff",
            foreground="#7b8a97",
            font=("Pretendard", 8, "bold"),
        )
        style.configure(
            "PageKicker.TLabel",
            background="#f4f7f6",
            foreground="#738391",
            font=small_font,
        )
        style.configure(
            "Title.TLabel",
            background="#f4f7f6",
            foreground="#132632",
            font=title_font,
        )
        style.configure(
            "Subtitle.TLabel",
            background="#f4f7f6",
            foreground="#5e6f7b",
            font=body_font,
        )
        style.configure(
            "PanelTitle.TLabel",
            background="#ffffff",
            foreground="#112431",
            font=("Pretendard", 11, "bold"),
        )
        style.configure(
            "PanelCount.TLabel",
            background="#ffffff",
            foreground="#7b8a97",
            font=small_font,
        )
        style.configure(
            "FileBadge.TLabel",
            background="#ffffff",
            foreground="#5f7180",
            font=("Consolas", 9, "bold"),
        )
        style.configure(
            "Body.TLabel",
            background="#ffffff",
            foreground="#4f6170",
            font=body_font,
        )
        style.configure(
            "StrongBody.TLabel",
            background="#ffffff",
            foreground="#1d3141",
            font=body_bold_font,
        )
        style.configure(
            "DetailTitle.TLabel",
            background="#ffffff",
            foreground="#172935",
            font=("Pretendard", 14, "bold"),
        )
        style.configure(
            "SummaryStrip.TLabel",
            background="#f7faf9",
            foreground="#485d6c",
            font=small_font,
        )
        style.configure(
            "StatusBadge.TLabel",
            background="#eef4f2",
            foreground="#5f756f",
            padding=(8, 4),
            font=small_font,
        )
        style.configure(
            "Disclaimer.TLabel",
            background="#eef3f2",
            foreground="#667887",
            font=small_font,
        )
        style.configure(
            "Footer.TLabel",
            background="#f4f7f6",
            foreground="#7b8a97",
            font=small_font,
        )

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
        style.map(
            "Treeview",
            background=[("selected", "#dff3ee")],
            foreground=[("selected", "#0f7568")],
        )
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
        center.grid(row=0, column=0, sticky="nsew")
        center.columnconfigure(0, weight=1)
        center.rowconfigure(2, weight=1)

        self._build_topbar(center)
        self._build_page_header(center)
        self.page_container = ttk.Frame(center, style="Page.TFrame")
        self.page_container.grid(row=2, column=0, sticky="nsew")
        self.page_container.columnconfigure(0, weight=1)
        self.page_container.rowconfigure(0, weight=1)
        self._build_content(self.page_container)
        self._build_footer(center)

    def _build_topbar(self, parent: ttk.Frame) -> None:
        topbar = ttk.Frame(parent, padding=(18, 10), style="Topbar.TFrame")
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.columnconfigure(1, weight=1)

        brand = ttk.Frame(topbar, style="Topbar.TFrame")
        brand.grid(row=0, column=0, sticky="w")
        self.logo_label = self._create_logo_label(brand)
        self.logo_label.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 12))
        ttk.Label(brand, text="착한코드검거단", style="Brand.TLabel").grid(
            row=0, column=1, sticky="w"
        )
        ttk.Label(brand, text="v0.1", style="BrandSmall.TLabel").grid(
            row=0, column=2, sticky="w", padx=(8, 0)
        )

        ttk.Label(
            topbar,
            text="STATIC · 대상 코드는 실행하지 않음",
            style="StatusBadge.TLabel",
        ).grid(row=0, column=2, sticky="e")

    def _create_logo_label(self, parent: ttk.Frame) -> tk.Label:
        logo_path = _resource_path("assets/branding/good-code-hunters-logo.png")
        if logo_path.exists():
            try:
                original = tk.PhotoImage(file=str(logo_path))
                scale = max(1, max(original.width(), original.height()) // 42)
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
        ttk.Label(
            header,
            text="코드를 실행하지 않는 AST 정적 분석",
            style="PageKicker.TLabel",
        ).pack(anchor="w")
        ttk.Label(header, textvariable=self.page_title_var, style="Title.TLabel").pack(
            anchor="w", pady=(6, 4)
        )
        ttk.Label(
            header,
            textvariable=self.product_description_var,
            style="Subtitle.TLabel",
        ).pack(anchor="w")

    def _build_content(self, parent: ttk.Frame) -> None:
        content = ttk.Frame(parent, style="Page.TFrame")
        content.grid(row=0, column=0, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)

        self._build_upload_panel(content)
        self._build_results_panel(content)
        self._build_disclaimer(content)
        self.scan_page = content

    def _init_pages(self) -> None:
        # ===
        # 만든 이유: PRD는 핵심 흐름을 하나의 메인 화면에서 처리하도록 요구한다.
        # 코드 설명: 분석 화면만 등록해 랭킹·티어 등 MVP 밖 기능이 production에 노출되지 않게 한다.
        # ===
        self.pages = {"검거소": self.scan_page}

    def _show_page(self, name: str) -> None:
        page = self.pages.get(name)
        if page is None:
            return

        for candidate in self.pages.values():
            candidate.grid_remove()
        page.grid(row=0, column=0, sticky="nsew")
        page.tkraise()
        self.current_page = name

        title, description = (
            "Python 보안 패턴 분석",
            "Python 코드를 실행하지 않고 좋은 보안 패턴을 찾는 정적 분석기입니다.",
        )
        self.page_title_var.set(title)
        self.product_description_var.set(description)

    def _build_upload_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.Frame(parent, padding=16, style="Card.TFrame")
        panel.grid(row=0, column=0, sticky="ew", padx=(0, 16), pady=(0, 16))
        panel.columnconfigure(0, weight=1)

        header = ttk.Frame(panel, style="Card.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="분석 대상", style="PanelTitle.TLabel").pack(side="left")

        header_actions = ttk.Frame(header, style="Card.TFrame")
        header_actions.pack(side="right")
        self.sample_button = ttk.Button(
            header_actions,
            text="예시로 확인",
            style="Ghost.TButton",
            command=self._load_sample_file,
        )
        self.sample_button.pack(side="left", padx=(0, 8))
        ttk.Label(
            header_actions,
            text=".py · 단일 파일",
            style="PanelCount.TLabel",
        ).pack(side="left")

        file_row = ttk.Frame(panel, padding=(14, 11), style="SoftCard.TFrame")
        file_row.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        file_row.columnconfigure(1, weight=1)
        ttk.Label(file_row, text=".py", style="FileBadge.TLabel").grid(
            row=0, column=0, rowspan=2, sticky="nw", padx=(0, 12)
        )
        ttk.Label(
            file_row,
            textvariable=self.file_path_var,
            style="StrongBody.TLabel",
            wraplength=760,
            justify="left",
        ).grid(row=0, column=1, sticky="w")
        ttk.Label(
            file_row,
            textvariable=self.file_hint_var,
            style="Body.TLabel",
            wraplength=760,
            justify="left",
        ).grid(row=1, column=1, sticky="ew", pady=(4, 0))
        ttk.Button(
            file_row,
            text="파일 선택",
            style="Ghost.TButton",
            command=self._choose_file,
        ).grid(row=0, column=2, rowspan=2, sticky="e", padx=(14, 0))

        action_row = ttk.Frame(panel, style="Card.TFrame")
        action_row.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        action_row.columnconfigure(3, weight=1)
        self.scan_button = ttk.Button(
            action_row,
            text="착한코드 검거 시작",
            command=self.run_scan,
            style="Primary.TButton",
        )
        self.scan_button.grid(row=0, column=0, sticky="w")
        ttk.Label(
            action_row,
            text="ast.parse() · AST 순회만 수행",
            style="PanelCount.TLabel",
        ).grid(row=0, column=1, sticky="w", padx=(12, 0))
        self.status_badge = ttk.Label(
            action_row,
            textvariable=self._status_badge_var,
            style="StatusBadge.TLabel",
        )
        self.status_badge.grid(row=0, column=2, sticky="e", padx=(18, 0))
        ttk.Label(
            action_row,
            textvariable=self.status_var,
            style="Body.TLabel",
            wraplength=440,
            justify="left",
        ).grid(row=0, column=3, sticky="ew", padx=(10, 0))

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
        ttk.Label(summary_head, text="검거 결과", style="PanelTitle.TLabel").pack(
            side="left"
        )
        self.findings_count_label = ttk.Label(
            summary_head,
            text="—",
            style="PanelCount.TLabel",
        )
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
        ttk.Label(disclaimer, text="안내", style="PanelCount.TLabel").grid(
            row=0, column=0, sticky="nw", padx=(0, 12)
        )
        ttk.Label(
            disclaimer,
            textvariable=self.disclaimer_var,
            style="Disclaimer.TLabel",
            wraplength=830,
            justify="left",
        ).grid(row=0, column=1, sticky="ew")

    def _build_footer(self, parent: ttk.Frame) -> None:
        footer = ttk.Frame(parent, padding=(6, 14, 6, 0), style="Page.TFrame")
        footer.grid(row=3, column=0, sticky="ew")
        ttk.Label(
            footer,
            text="착한코드검거단 MVP v0.1 · AST 정적 분석 · No Execution",
            style="Footer.TLabel",
        ).pack(anchor="w")

    def _choose_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Python 파일 선택",
            filetypes=[("Python Files", "*.py")],
        )
        if file_path:
            self.set_selected_file(file_path)

    def _load_sample_file(self) -> None:
        sample_path = Path(gettempdir()) / self.SAMPLE_FILE_NAME
        sample_path.write_text(self.SAMPLE_SOURCE, encoding="utf-8")
        self.set_selected_file(str(sample_path))

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

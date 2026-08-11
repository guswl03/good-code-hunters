from __future__ import annotations

import gc
import tkinter as tk
from pathlib import Path

from goodcode.core.models import (
    GOOD_PATTERNS_FOUND,
    NO_GOOD_PATTERNS_FOUND,
    PARSE_ERROR,
    READ_ERROR,
    Finding,
    ScanResult,
)


def make_finding() -> Finding:
    return Finding(
        rule_id="GOOD002",
        name="Cryptographically Secure Randomness",
        category="cryptography",
        confidence="HIGH",
        file="sample.py",
        line=10,
        column=4,
        evidence="token = secrets.token_urlsafe(32)",
        message="Uses secrets for secure token generation.",
    )


def make_result(status: str, findings: list[Finding] | None = None) -> ScanResult:
    return ScanResult(
        findings=[] if findings is None else findings,
        target="sample.py",
        status=status,
        warnings=[],
    )


def destroy_widget(widget: tk.Misc) -> None:
    try:
        widget.update_idletasks()
    except tk.TclError:
        pass
    try:
        widget.destroy()
    except tk.TclError:
        pass
    tk._default_root = None
    gc.collect()


def test_result_view_shows_selected_finding_details() -> None:
    from goodcode.gui.result_view import ResultView

    root = tk.Tk()
    root.withdraw()

    finding = make_finding()
    view = ResultView(root)
    view.set_findings([finding])

    assert view.selected_finding() == finding

    destroy_widget(root)


def test_main_window_moves_to_ready_after_file_selection() -> None:
    from goodcode.gui.main_window import MainWindow

    window = MainWindow(scan_service=lambda path: make_result(NO_GOOD_PATTERNS_FOUND))
    window.withdraw()

    window.set_selected_file("sample.py")

    assert str(window.scan_button["state"]) == "normal"
    assert "sample.py" in window.file_path_var.get()

    destroy_widget(window)


def test_main_window_starts_on_single_analysis_screen() -> None:
    from goodcode.gui.main_window import MainWindow

    window = MainWindow(scan_service=lambda path: make_result(NO_GOOD_PATTERNS_FOUND))
    window.withdraw()
    window.update_idletasks()

    assert "실행하지 않고" in window.product_description_var.get()
    assert window.scan_page.winfo_manager() == "grid"
    assert window.current_page == "검거소"
    assert set(window.pages) == {"홈", "검거소", "랭킹", "규칙집"}
    assert str(window.scan_button["state"]) == "disabled"

    destroy_widget(window)


def test_main_window_loads_brand_logo_image() -> None:
    from goodcode.gui.main_window import MainWindow

    window = MainWindow(scan_service=lambda path: make_result(NO_GOOD_PATTERNS_FOUND))
    window.withdraw()

    assert window.logo_label is not None
    assert window.logo_image is not None

    destroy_widget(window)


def test_single_screen_exposes_primary_workflow() -> None:
    from goodcode.gui.main_window import MainWindow

    window = MainWindow(scan_service=lambda path: make_result(NO_GOOD_PATTERNS_FOUND))
    window.withdraw()
    window.update_idletasks()

    assert "Python 파일" in window.file_hint_var.get()
    assert window.sample_button is not None
    assert window.result_view.winfo_manager() == "grid"
    assert "보증" in window.disclaimer_var.get()

    destroy_widget(window)


def test_navigation_switches_between_all_pages() -> None:
    from goodcode.gui.main_window import MainWindow

    window = MainWindow(scan_service=lambda path: make_result(NO_GOOD_PATTERNS_FOUND))
    window.withdraw()

    assert window.current_page == "검거소"
    assert list(window.nav_buttons) == ["홈", "검거소", "랭킹", "규칙집"]

    for page_name in ("홈", "랭킹", "규칙집", "검거소"):
        window.nav_buttons[page_name].invoke()
        assert window.current_page == page_name
        assert window.pages[page_name].winfo_manager() == "grid"

    destroy_widget(window)


def test_main_window_loads_sample_file_for_preview() -> None:
    from goodcode.gui.main_window import MainWindow

    window = MainWindow(scan_service=lambda path: make_result(NO_GOOD_PATTERNS_FOUND))
    window.withdraw()

    window._load_sample_file()

    assert window.sample_button is not None
    assert window._selected_file is not None
    assert Path(window._selected_file).exists()
    assert MainWindow.SAMPLE_FILE_NAME in window._selected_file
    assert "good_code_hunters_sample.py" in window.file_path_var.get()

    destroy_widget(window)


def test_main_window_renders_good_patterns_found() -> None:
    from goodcode.gui.main_window import MainWindow

    finding = make_finding()
    window = MainWindow(
        scan_service=lambda path: make_result(GOOD_PATTERNS_FOUND, [finding])
    )
    window.withdraw()
    window.set_selected_file("sample.py")

    window.run_scan()

    assert window.current_result() is not None
    assert window.current_result().status == GOOD_PATTERNS_FOUND
    assert window.result_view.selected_finding() == finding
    assert "1" in window.summary_var.get()
    assert str(window.export_button["state"]) == "normal"

    destroy_widget(window)


def test_main_window_renders_empty_scan_result() -> None:
    from goodcode.gui.main_window import MainWindow

    window = MainWindow(scan_service=lambda path: make_result(NO_GOOD_PATTERNS_FOUND))
    window.withdraw()
    window.set_selected_file("sample.py")

    window.run_scan()

    assert window.current_result() is not None
    assert window.current_result().status == NO_GOOD_PATTERNS_FOUND
    assert str(window.export_button["state"]) == "normal"

    destroy_widget(window)


def test_main_window_renders_parse_error() -> None:
    from goodcode.gui.main_window import MainWindow

    result = ScanResult(
        findings=[],
        target="broken.py",
        status=PARSE_ERROR,
        warnings=["Line 3: invalid syntax"],
    )
    window = MainWindow(scan_service=lambda path: result)
    window.withdraw()
    window.set_selected_file("broken.py")

    window.run_scan()

    assert window.current_result() is not None
    assert window.current_result().status == PARSE_ERROR
    assert str(window.export_button["state"]) == "disabled"

    destroy_widget(window)


def test_main_window_renders_read_error() -> None:
    from goodcode.gui.main_window import MainWindow

    result = ScanResult(
        findings=[],
        target="missing.py",
        status=READ_ERROR,
        warnings=["missing file"],
    )
    window = MainWindow(scan_service=lambda path: result)
    window.withdraw()
    window.set_selected_file("missing.py")

    window.run_scan()

    assert window.current_result() is not None
    assert window.current_result().status == READ_ERROR
    assert str(window.export_button["state"]) == "disabled"

    destroy_widget(window)


def test_app_uses_real_scan_file() -> None:
    import app

    assert app.scan_file is not None

from __future__ import annotations

import json
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


def make_result(
    status: str,
    findings: list[Finding] | None = None,
    warnings: list[str] | None = None,
) -> ScanResult:
    return ScanResult(
        findings=[] if findings is None else findings,
        target="sample.py",
        status=status,
        warnings=[] if warnings is None else warnings,
    )


# ===
# 만든 이유: Windows Tcl이 한 프로세스에서 여러 Tk 루트를 반복 생성할 때 생기는 간헐 오류를 피한다.
# 코드 설명: 하나의 실제 MainWindow에서 MVP의 모든 상태와 JSON 저장 흐름을 순서대로 검증한다.
# ===
def test_main_window_complete_mvp_workflow(tmp_path: Path, monkeypatch) -> None:
    from goodcode.gui import main_window
    from goodcode.gui.main_window import MainWindow

    current = {"result": make_result(NO_GOOD_PATTERNS_FOUND)}
    window = MainWindow(scan_service=lambda _path: current["result"])
    window.withdraw()

    try:
        window.update_idletasks()
        assert "실행하지 않고" in window.product_description_var.get()
        assert window.current_page == "검거소"
        assert set(window.pages) == {"검거소"}
        assert str(window.scan_button["state"]) == "disabled"
        assert window.logo_label is not None
        assert window.logo_image is not None
        assert window.sample_button is not None
        assert window.result_view.winfo_manager() == "grid"
        assert "보증" in window.disclaimer_var.get()

        window._load_sample_file()
        assert window._selected_file is not None
        assert Path(window._selected_file).exists()
        assert MainWindow.SAMPLE_FILE_NAME in window._selected_file

        finding = make_finding()
        current["result"] = make_result(GOOD_PATTERNS_FOUND, [finding])
        window.set_selected_file("sample.py")
        assert str(window.scan_button["state"]) == "normal"
        window.run_scan()
        assert window.current_result() is not None
        assert window.current_result().status == GOOD_PATTERNS_FOUND
        assert window.result_view.selected_finding() == finding
        assert "1" in window.summary_var.get()
        assert str(window.export_button["state"]) == "normal"

        output = tmp_path / "scan-result.json"
        monkeypatch.setattr(
            main_window.filedialog,
            "asksaveasfilename",
            lambda **_kwargs: str(output),
        )
        window.save_current_result()
        payload = json.loads(output.read_text(encoding="utf-8"))
        assert payload["summary"] == {"findings": 1, "categories": 1}
        assert payload["findings"][0]["rule_id"] == "GOOD002"
        assert "file" not in payload["findings"][0]

        def fail_export(_result, _path) -> None:
            raise OSError("permission denied")

        monkeypatch.setattr(main_window, "export_scan_result", fail_export)
        window.save_current_result()
        assert "저장할 수 없습니다" in window.status_var.get()

        current["result"] = make_result(NO_GOOD_PATTERNS_FOUND)
        window.set_selected_file("empty.py")
        window.run_scan()
        assert window.current_result().status == NO_GOOD_PATTERNS_FOUND
        assert str(window.export_button["state"]) == "normal"

        current["result"] = make_result(
            PARSE_ERROR,
            warnings=["Line 3: invalid syntax"],
        )
        window.set_selected_file("broken.py")
        window.run_scan()
        assert window.current_result().status == PARSE_ERROR
        assert str(window.export_button["state"]) == "disabled"

        current["result"] = make_result(
            READ_ERROR,
            warnings=["missing file"],
        )
        window.set_selected_file("missing.py")
        window.run_scan()
        assert window.current_result().status == READ_ERROR
        assert str(window.export_button["state"]) == "disabled"
    finally:
        window.destroy()


def test_app_uses_real_scan_file() -> None:
    import app

    assert app.scan_file is not None

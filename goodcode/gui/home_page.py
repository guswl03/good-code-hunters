from __future__ import annotations

from tkinter import ttk


class HomePage(ttk.Frame):
    """Simple home page widget matching the MVP UI style."""

    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, style="Page.TFrame")
        # Centered welcome message
        ttk.Label(
            self,
            text="착한코드검거단에 오신 것을 환영합니다!",
            style="Title.TLabel",
        ).pack(pady=40)
        ttk.Label(
            self,
            text="파일을 선택하고 ‘착한코드 검거 시작’ 버튼을 눌러 보세요.",
            style="Subtitle.TLabel",
        ).pack()

from __future__ import annotations

from tkinter import ttk

from goodcode.gui.rulebook_data import CATEGORY_LABELS, RULES


class RulebookPage(ttk.Frame):
    """Display the list of good security pattern rules."""

    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, style="Page.TFrame")
        self._build_ui()

    def _build_ui(self) -> None:
        header = ttk.Label(self, text="규칙집", style="Title.TLabel")
        header.pack(pady=20)
        columns = ("rule_id", "name", "category", "confidence")
        tree = ttk.Treeview(self, columns=columns, show="headings", height=20)
        for col, txt in zip(columns, ["Rule ID", "Name", "Category", "Confidence"]):
            tree.heading(col, text=txt)
            tree.column(col, width=120, anchor="center")
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        # Populate data
        for rule in RULES:
            tree.insert(
                "",
                "end",
                values=(
                    rule.get("id"),
                    rule.get("name"),
                    CATEGORY_LABELS.get(rule.get("category"), rule.get("category")),
                    rule.get("confidence"),
                ),
            )

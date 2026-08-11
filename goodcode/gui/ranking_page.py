from __future__ import annotations

from tkinter import ttk

from goodcode.gui.rankings import leaderboard
from goodcode.gui.session_stats import SessionStats


class RankingPage(ttk.Frame):
    """Display ranking leaderboard based on session stats and sample data."""

    def __init__(self, parent: ttk.Frame) -> None:
        super().__init__(parent, style="Page.TFrame")
        self.session = SessionStats()
        self._build_ui()

    def _build_ui(self) -> None:
        header = ttk.Label(self, text="랭킹", style="Title.TLabel")
        header.pack(pady=20)
        columns = ("rank", "name", "team", "finds", "cats", "tier")
        tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col, txt in zip(columns, ["Rank", "Name", "Team", "Finds", "Cats", "Tier"]):
            tree.heading(col, text=txt)
            tree.column(col, width=100, anchor="center")
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        # Populate data
        rows = leaderboard(self.session)
        for row in rows:
            tree.insert(
                "",
                "end",
                values=(
                    row.get("rank"),
                    row.get("name"),
                    row.get("team"),
                    row.get("finds"),
                    row.get("cats"),
                    row.get("tier"),
                ),
            )

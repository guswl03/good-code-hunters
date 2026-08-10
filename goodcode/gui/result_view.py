from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from goodcode.core.models import Finding


class ResultView(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_select: callable | None = None,
    ) -> None:
        super().__init__(master, padding=0)
        self._on_select = on_select
        self._findings: list[Finding] = []
        self._selected: Finding | None = None
        self._message_var = tk.StringVar(value="Select a Python file to see results.")
        self._detail_title_var = tk.StringVar(value="No finding selected")
        self._detail_meta_var = tk.StringVar(value="")
        self._detail_message_var = tk.StringVar(value="")

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self._build_findings_panel()
        self._build_detail_panel()

    def _build_findings_panel(self) -> None:
        findings_frame = ttk.Frame(self, padding=12, style="Card.TFrame")
        findings_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        findings_frame.columnconfigure(0, weight=1)
        findings_frame.rowconfigure(1, weight=1)

        ttk.Label(
            findings_frame,
            text="Findings",
            style="SectionTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")

        self._message_label = ttk.Label(
            findings_frame,
            textvariable=self._message_var,
            style="Muted.TLabel",
            wraplength=420,
            justify="left",
        )
        self._message_label.grid(row=1, column=0, sticky="nsew", pady=(12, 0))

        columns = ("rule_id", "name", "category", "line")
        self._tree = ttk.Treeview(
            findings_frame,
            columns=columns,
            show="headings",
            height=12,
            selectmode="browse",
        )
        self._tree.heading("rule_id", text="Rule ID")
        self._tree.heading("name", text="Rule Name")
        self._tree.heading("category", text="Category")
        self._tree.heading("line", text="Line")
        self._tree.column("rule_id", width=90, anchor="w")
        self._tree.column("name", width=240, anchor="w")
        self._tree.column("category", width=150, anchor="w")
        self._tree.column("line", width=60, anchor="center")
        self._tree.bind("<<TreeviewSelect>>", self._handle_select)

    def _build_detail_panel(self) -> None:
        detail_frame = ttk.Frame(self, padding=12, style="Card.TFrame")
        detail_frame.grid(row=0, column=1, sticky="nsew")
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(3, weight=1)

        ttk.Label(
            detail_frame,
            text="Finding Detail",
            style="SectionTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            detail_frame,
            textvariable=self._detail_title_var,
            style="DetailTitle.TLabel",
            wraplength=320,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(12, 4))

        ttk.Label(
            detail_frame,
            textvariable=self._detail_meta_var,
            style="Muted.TLabel",
            wraplength=320,
            justify="left",
        ).grid(row=2, column=0, sticky="w")

        evidence_frame = ttk.Frame(detail_frame, padding=(0, 12, 0, 0))
        evidence_frame.grid(row=3, column=0, sticky="nsew")
        evidence_frame.columnconfigure(0, weight=1)
        evidence_frame.rowconfigure(1, weight=1)

        ttk.Label(
            evidence_frame,
            text="Evidence",
            style="SectionLabel.TLabel",
        ).grid(row=0, column=0, sticky="w")

        self._evidence_text = tk.Text(
            evidence_frame,
            height=8,
            wrap="word",
            state="disabled",
            relief="flat",
            borderwidth=1,
        )
        self._evidence_text.grid(row=1, column=0, sticky="nsew", pady=(6, 12))

        ttk.Label(
            evidence_frame,
            text="Why it matters",
            style="SectionLabel.TLabel",
        ).grid(row=2, column=0, sticky="w")

        ttk.Label(
            evidence_frame,
            textvariable=self._detail_message_var,
            wraplength=320,
            justify="left",
        ).grid(row=3, column=0, sticky="nsew", pady=(6, 0))

    def set_findings(self, findings: list[Finding]) -> None:
        self._findings = list(findings)
        self._selected = None
        self._tree.delete(*self._tree.get_children())

        if not self._findings:
            self.show_empty("No good security patterns were found for the current rules.")
            return

        self._message_label.grid_remove()
        self._tree.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        for index, finding in enumerate(self._findings):
            item_id = str(index)
            self._tree.insert(
                "",
                "end",
                iid=item_id,
                values=(
                    finding.rule_id,
                    finding.name,
                    finding.category,
                    finding.line,
                ),
            )

        first_item = self._tree.get_children()[0]
        self._tree.selection_set(first_item)
        self._tree.focus(first_item)
        self._select_index(0)

    def show_empty(self, message: str) -> None:
        self._findings = []
        self._selected = None
        self._tree.delete(*self._tree.get_children())
        self._tree.grid_remove()
        self._message_var.set(message)
        self._message_label.grid()
        self.clear_detail()

    def show_error(self, message: str) -> None:
        self.show_empty(message)

    def clear_detail(self) -> None:
        self._detail_title_var.set("No finding selected")
        self._detail_meta_var.set("")
        self._detail_message_var.set("")
        self._set_evidence("")

    def selected_finding(self) -> Finding | None:
        return self._selected

    def _handle_select(self, _event: tk.Event[tk.Misc]) -> None:
        selection = self._tree.selection()
        if not selection:
            return

        self._select_index(int(selection[0]))

    def _select_index(self, index: int) -> None:
        self._selected = self._findings[index]
        finding = self._selected
        self._detail_title_var.set(finding.name)
        self._detail_meta_var.set(
            f"{finding.file}  |  line {finding.line}, column {finding.column}"
        )
        self._detail_message_var.set(finding.message)
        self._set_evidence(finding.evidence)
        if self._on_select is not None:
            self._on_select(finding)

    def _set_evidence(self, evidence: str) -> None:
        self._evidence_text.configure(state="normal")
        self._evidence_text.delete("1.0", "end")
        if evidence:
            self._evidence_text.insert("1.0", evidence)
        self._evidence_text.configure(state="disabled")

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from goodcode.core.models import Finding


class ResultView(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        on_select=None,
    ) -> None:
        super().__init__(master, style="Page.TFrame")
        self._on_select = on_select
        self._findings: list[Finding] = []
        self._selected: Finding | None = None
        self._message_var = tk.StringVar(value="아직 분석 결과가 없습니다.")
        self._detail_id_var = tk.StringVar(value="")
        self._detail_title_var = tk.StringVar(value="선택된 Finding이 없습니다")
        self._detail_meta_var = tk.StringVar(value="")
        self._detail_message_var = tk.StringVar(value="")

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self._build_findings_panel()
        self._build_detail_panel()

    def _build_findings_panel(self) -> None:
        self.findings_container = ttk.Frame(self, style="Card.TFrame")
        self.findings_container.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self.findings_container.columnconfigure(0, weight=1)
        self.findings_container.rowconfigure(2, weight=1)

        filters = ttk.Frame(self.findings_container, padding=(18, 12), style="Card.TFrame")
        filters.grid(row=0, column=0, sticky="ew")
        ttk.Label(filters, text="결과 목록", style="PanelTitle.TLabel").pack(side="left")
        ttk.Label(filters, text="Rule / Pattern / Category / Line", style="PanelCount.TLabel").pack(
            side="right"
        )

        self._message_label = ttk.Label(
            self.findings_container,
            textvariable=self._message_var,
            style="Body.TLabel",
            padding=(18, 12),
            wraplength=640,
            justify="left",
        )
        self._message_label.grid(row=1, column=0, sticky="ew")

        columns = ("rule_id", "name", "category", "line")
        self._tree = ttk.Treeview(
            self.findings_container,
            columns=columns,
            show="headings",
            height=14,
            selectmode="browse",
        )
        self._tree.heading("rule_id", text="Rule")
        self._tree.heading("name", text="Pattern")
        self._tree.heading("category", text="Category")
        self._tree.heading("line", text="Line")
        self._tree.column("rule_id", width=100, anchor="w")
        self._tree.column("name", width=340, anchor="w")
        self._tree.column("category", width=170, anchor="w")
        self._tree.column("line", width=70, anchor="center")
        self._tree.bind("<<TreeviewSelect>>", self._handle_select)

        tree_frame = ttk.Frame(self.findings_container, padding=(12, 0, 12, 12), style="Card.TFrame")
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        self._tree.grid(in_=tree_frame, row=0, column=0, sticky="nsew")

    def _build_detail_panel(self) -> None:
        self.detail_container = ttk.Frame(self, style="Card.TFrame")
        self.detail_container.grid(row=0, column=1, sticky="nsew")
        self.detail_container.columnconfigure(0, weight=1)
        self.detail_container.rowconfigure(1, weight=1)

        detail_head = ttk.Frame(self.detail_container, padding=(18, 14), style="Card.TFrame")
        detail_head.grid(row=0, column=0, sticky="ew")
        detail_head.columnconfigure(1, weight=1)
        ttk.Label(detail_head, text="Finding 상세", style="PanelTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self._detail_index_label = ttk.Label(
            detail_head,
            text="—",
            style="PanelCount.TLabel",
        )
        self._detail_index_label.grid(row=0, column=1, sticky="e")

        detail_body = ttk.Frame(self.detail_container, padding=(18, 8, 18, 18), style="Card.TFrame")
        detail_body.grid(row=1, column=0, sticky="nsew")
        detail_body.columnconfigure(0, weight=1)
        detail_body.rowconfigure(3, weight=1)

        ttk.Label(
            detail_body,
            textvariable=self._detail_id_var,
            style="PanelCount.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            detail_body,
            textvariable=self._detail_title_var,
            style="DetailTitle.TLabel",
            wraplength=380,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(4, 6))

        ttk.Label(
            detail_body,
            textvariable=self._detail_meta_var,
            style="Body.TLabel",
            wraplength=380,
            justify="left",
        ).grid(row=2, column=0, sticky="w", pady=(0, 14))

        ttk.Label(detail_body, text="Evidence", style="PanelCount.TLabel").grid(
            row=3, column=0, sticky="nw"
        )
        self._evidence_text = tk.Text(
            detail_body,
            height=10,
            wrap="word",
            relief="flat",
            borderwidth=0,
            background="#f7faf9",
            foreground="#243746",
            font=("Consolas", 10),
            padx=12,
            pady=10,
        )
        self._evidence_text.grid(row=4, column=0, sticky="nsew", pady=(6, 14))

        ttk.Label(detail_body, text="왜 좋은 코드인가", style="PanelCount.TLabel").grid(
            row=5, column=0, sticky="w"
        )
        ttk.Label(
            detail_body,
            textvariable=self._detail_message_var,
            style="Body.TLabel",
            wraplength=380,
            justify="left",
        ).grid(row=6, column=0, sticky="ew", pady=(6, 0))

        self.detail_footer = ttk.Frame(self.detail_container, padding=(18, 14), style="Card.TFrame")
        self.detail_footer.grid(row=2, column=0, sticky="ew")
        self.detail_footer.columnconfigure(1, weight=1)

        self.clear_detail()

    def set_findings(self, findings: list[Finding]) -> None:
        self._findings = list(findings)
        self._selected = None
        self._tree.delete(*self._tree.get_children())

        if not self._findings:
            self.show_empty("현재 규칙 기준으로 확인 가능한 착한코드가 없습니다.")
            return

        self._message_label.grid_remove()
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
        self._message_var.set(message)
        self._message_label.grid()
        self._detail_index_label.configure(text="—")
        self.clear_detail()

    def show_error(self, message: str) -> None:
        self.show_empty(message)

    def clear_detail(self) -> None:
        self._detail_id_var.set("")
        self._detail_title_var.set("선택된 Finding이 없습니다")
        self._detail_meta_var.set("결과 목록에서 항목을 선택하면 상세 정보가 여기에 표시됩니다.")
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
        self._detail_index_label.configure(text=f"{index + 1} / {len(self._findings)}")
        self._detail_id_var.set(finding.rule_id)
        self._detail_title_var.set(finding.name)
        self._detail_meta_var.set(
            f"{finding.file} · line {finding.line} · column {finding.column}"
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

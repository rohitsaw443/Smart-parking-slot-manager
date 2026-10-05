"""
parking_history_view.py - Interface for viewing and searching historical parking records.
Tracks every vehicle's entry and exit, slot assigned, duration, and status with persistence.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config import (
    COLOR_BG,
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_LIGHT,
    COLOR_PRIMARY_HOVER,
    COLOR_SUCCESS,
    COLOR_SUCCESS_LIGHT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    FONT_SECTION_TITLE,
    FONT_BODY,
    FONT_BODY_BOLD,
)


class ParkingHistoryView(tk.Frame):
    """View displaying historical logs of all vehicle entries and exits with search."""

    def __init__(self, parent, parking_manager):
        super().__init__(parent, bg=COLOR_BG)
        self.pm = parking_manager

        container = tk.Frame(self, bg=COLOR_BG, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        self._build_history_summary(container)
        self._build_search_filter_bar(container)
        self._build_history_table(container)

        self.refresh_data()

    def _build_history_summary(self, parent):
        """Build top summary cards with live counters."""
        top_card = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        top_card.pack(fill="x", pady=(0, 14))

        tk.Label(
            top_card,
            text="📜 Parking History & Audit Trail",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w")

        tk.Label(
            top_card,
            text="Persistent audit log recording every vehicle entry, slot assignment, departure time, and duration",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 12))

        # Metrics row (3 badges)
        metrics_row = tk.Frame(top_card, bg=COLOR_CARD_BG)
        metrics_row.pack(fill="x")

        self.total_records_lbl = tk.Label(
            metrics_row,
            text="0 Total Sessions",
            font=FONT_BODY_BOLD,
            fg=COLOR_PRIMARY,
            bg=COLOR_PRIMARY_LIGHT,
            padx=12,
            pady=6,
        )
        self.total_records_lbl.pack(side="left", padx=(0, 10))

        self.active_sessions_lbl = tk.Label(
            metrics_row,
            text="0 Currently Parked",
            font=FONT_BODY_BOLD,
            fg=COLOR_SUCCESS,
            bg=COLOR_SUCCESS_LIGHT,
            padx=12,
            pady=6,
        )
        self.active_sessions_lbl.pack(side="left", padx=(0, 10))

        self.completed_sessions_lbl = tk.Label(
            metrics_row,
            text="0 Completed Exits",
            font=FONT_BODY_BOLD,
            fg=COLOR_TEXT_SECONDARY,
            bg="#F1F5F9",
            padx=12,
            pady=6,
        )
        self.completed_sessions_lbl.pack(side="left")

    def _build_search_filter_bar(self, parent):
        """Build search input and filter bar for finding vehicles in history."""
        search_card = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=12,
        )
        search_card.pack(fill="x", pady=(0, 14))

        search_row = tk.Frame(search_card, bg=COLOR_CARD_BG)
        search_row.pack(fill="x")

        tk.Label(
            search_row,
            text="Search History:",
            font=FONT_BODY_BOLD,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(side="left", padx=(0, 8))

        self.search_entry = tk.Entry(
            search_row,
            font=("Segoe UI", 10),
            bg="#F8FAFC",
            fg=COLOR_TEXT_PRIMARY,
            relief="solid",
            bd=1,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))
        self.search_entry.insert(0, "")
        self.search_entry.bind("<Return>", lambda e: self._handle_search())

        # Status filter
        self.status_filter = ttk.Combobox(
            search_row,
            values=["All Statuses", "Active (Parked)", "Completed (Exited)"],
            state="readonly",
            font=FONT_BODY,
            width=18,
        )
        self.status_filter.current(0)
        self.status_filter.pack(side="left", padx=(0, 10), ipady=3)
        self.status_filter.bind("<<ComboboxSelected>>", lambda e: self._handle_search())

        # Search button
        search_btn = tk.Button(
            search_row,
            text="🔍 Find",
            font=FONT_BODY_BOLD,
            bg=COLOR_PRIMARY,
            fg="#FFFFFF",
            activebackground=COLOR_PRIMARY_HOVER,
            activeforeground="#FFFFFF",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._handle_search,
        )
        search_btn.pack(side="left", padx=(0, 6))

        # Reset button
        reset_btn = tk.Button(
            search_row,
            text="Reset / All",
            font=FONT_BODY,
            bg="#F1F5F9",
            fg=COLOR_TEXT_PRIMARY,
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._handle_reset,
        )
        reset_btn.pack(side="left")

    def _build_history_table(self, parent):
        """Build historical records table."""
        table_card = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        table_card.pack(fill="both", expand=True)

        hdr_row = tk.Frame(table_card, bg=COLOR_CARD_BG)
        hdr_row.pack(fill="x", pady=(0, 8))

        tk.Label(
            hdr_row,
            text="All Recorded Parking Sessions",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(side="left")

        self.table_count_lbl = tk.Label(
            hdr_row,
            text="Showing 0 records",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD_BG,
        )
        self.table_count_lbl.pack(side="right")

        # Treeview table
        columns = ("id", "plate", "type", "slot", "entry", "exit", "status", "duration")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", height=9)

        headings = [
            ("id", "Record ID", 100),
            ("plate", "Vehicle Number", 150),
            ("type", "Vehicle Type", 110),
            ("slot", "Slot", 90),
            ("entry", "Entry Time", 130),
            ("exit", "Exit Time", 130),
            ("status", "Status", 120),
            ("duration", "Duration", 110),
        ]

        for col_id, heading, width in headings:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor="w")

        self.tree.pack(fill="both", expand=True, pady=(0, 10))

        # Bottom info note
        self.status_note = tk.Label(
            table_card,
            text="💾 Persistent Storage Active: All records are automatically saved to disk and preserved across application restarts.",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD_BG,
            anchor="w",
        )
        self.status_note.pack(fill="x")

    def _handle_search(self):
        """Filter table based on query and status dropdown."""
        query = self.search_entry.get().strip().upper()
        status_choice = self.status_filter.get()

        matching = self.pm.search_history(query)

        # Apply status filter if selected
        if status_choice == "Active (Parked)":
            matching = [r for r in matching if r.get("status") == "Active"]
        elif status_choice == "Completed (Exited)":
            matching = [r for r in matching if r.get("status") == "Completed"]

        self._populate_table(matching)

    def _handle_reset(self):
        """Reset search and reload all records."""
        self.search_entry.delete(0, tk.END)
        self.status_filter.current(0)
        self.refresh_data()

    def _populate_table(self, records):
        """Populate treeview rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for rec in records:
            status = rec.get("status", "--")
            status_display = "🟢 Parked (Active)" if status == "Active" else "⚪ Completed"

            self.tree.insert(
                "",
                "end",
                values=(
                    rec.get("record_id", "--"),
                    rec.get("vehicle_number", "--"),
                    rec.get("vehicle_type", "--"),
                    rec.get("slot_number", "--"),
                    rec.get("entry_time", "--"),
                    rec.get("exit_time", "--"),
                    status_display,
                    rec.get("duration", "--"),
                ),
            )

        self.table_count_lbl.configure(text=f"Showing {len(records)} record(s)")

    def refresh_data(self):
        """Reload historical records and update summary counters."""
        all_records = self.pm.history
        total_count = len(all_records)
        active_count = sum(1 for r in all_records if r.get("status") == "Active")
        completed_count = sum(1 for r in all_records if r.get("status") == "Completed")

        self.total_records_lbl.configure(text=f"{total_count} Total Session{'s' if total_count != 1 else ''}")
        self.active_sessions_lbl.configure(text=f"{active_count} Currently Parked")
        self.completed_sessions_lbl.configure(text=f"{completed_count} Completed Exit{'s' if completed_count != 1 else ''}")

        # Check if an active search query is in the box
        query = self.search_entry.get().strip()
        if query:
            self._handle_search()
        else:
            self._populate_table(all_records)

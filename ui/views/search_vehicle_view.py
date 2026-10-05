"""
search_vehicle_view.py - Interface for searching vehicles by registration number.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config import (
    COLOR_BG,
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_HOVER,
    COLOR_SUCCESS,
    COLOR_SUCCESS_LIGHT,
    COLOR_DANGER,
    COLOR_DANGER_LIGHT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    FONT_SECTION_TITLE,
    FONT_BODY,
    FONT_BODY_BOLD,
)


class SearchVehicleView(tk.Frame):
    """View for searching vehicles and inspecting their slot, type, entry time, and status."""

    def __init__(self, parent, parking_manager):
        super().__init__(parent, bg=COLOR_BG)
        self.pm = parking_manager

        container = tk.Frame(self, bg=COLOR_BG, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        self._build_search_card(container)
        self._build_result_card(container)
        self._build_active_vehicles_table(container)

        # Initial data load
        self.refresh_data()

    def _build_search_card(self, parent):
        """Build search query bar."""
        card = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        card.pack(fill="x", pady=(0, 14))

        tk.Label(
            card,
            text="🔍 Search Vehicle",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w")

        tk.Label(
            card,
            text="Search by vehicle registration plate number to locate assigned slot and status",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 10))

        controls_row = tk.Frame(card, bg=COLOR_CARD_BG)
        controls_row.pack(fill="x")

        self.query_entry = tk.Entry(
            controls_row,
            font=("Segoe UI", 11),
            bg="#F8FAFC",
            fg=COLOR_TEXT_PRIMARY,
            relief="solid",
            bd=1,
        )
        self.query_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))
        self.query_entry.focus_set()
        self.query_entry.bind("<Return>", lambda e: self._handle_search())

        search_btn = tk.Button(
            controls_row,
            text="🔍 Search Vehicle",
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

        reset_btn = tk.Button(
            controls_row,
            text="Reset",
            font=FONT_BODY,
            bg="#F1F5F9",
            fg=COLOR_TEXT_PRIMARY,
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
            command=self._reset_search,
        )
        reset_btn.pack(side="left")

    def _build_result_card(self, parent):
        """Build card displaying detailed search match results."""
        self.result_card = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=14,
        )
        self.result_card.pack(fill="x", pady=(0, 14))

        # Title row
        self.result_title_lbl = tk.Label(
            self.result_card,
            text="Search Result Details",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        )
        self.result_title_lbl.pack(anchor="w")

        # Result Details Box
        self.details_box = tk.Frame(self.result_card, bg="#F8FAFC", padx=16, pady=12)
        self.details_box.pack(fill="x", pady=(8, 0))

        # 4 Key display labels: Slot Number, Vehicle Type, Entry Time, Status
        self.info_labels = {}
        info_keys = [
            ("Vehicle Number:", "vehicle_number"),
            ("Status:", "status"),
            ("Slot Number:", "slot_number"),
            ("Vehicle Type:", "vehicle_type"),
            ("Entry Time:", "entry_time"),
            ("Duration So Far:", "duration_so_far"),
        ]

        # Use 3 columns in grid
        for i, (label_text, key) in enumerate(info_keys):
            r = i // 3
            c = (i % 3) * 2

            lbl_title = tk.Label(
                self.details_box,
                text=label_text,
                font=FONT_BODY_BOLD,
                fg=COLOR_TEXT_SECONDARY,
                bg="#F8FAFC",
            )
            lbl_title.grid(row=r, column=c, sticky="w", padx=(10, 4), pady=4)

            lbl_val = tk.Label(
                self.details_box,
                text="--",
                font=("Segoe UI", 10, "bold"),
                fg=COLOR_TEXT_PRIMARY,
                bg="#F8FAFC",
            )
            lbl_val.grid(row=r, column=c + 1, sticky="w", padx=(0, 20), pady=4)
            self.info_labels[key] = lbl_val

    def _build_active_vehicles_table(self, parent):
        """Build table displaying currently parked vehicles."""
        table_card = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=14,
        )
        table_card.pack(fill="both", expand=True)

        hdr_row = tk.Frame(table_card, bg=COLOR_CARD_BG)
        hdr_row.pack(fill="x", pady=(0, 8))

        self.table_title = tk.Label(
            hdr_row,
            text="Currently Parked Vehicles (Live Records)",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        )
        self.table_title.pack(side="left")

        self.table_count_lbl = tk.Label(
            hdr_row,
            text="0 Active Vehicles",
            font=FONT_BODY_BOLD,
            fg=COLOR_PRIMARY,
            bg=COLOR_CARD_BG,
        )
        self.table_count_lbl.pack(side="right")

        # Treeview table
        columns = ("slot", "plate", "type", "entry_time", "status")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", height=8)

        headings = [
            ("slot", "Slot Number", 130),
            ("plate", "Vehicle Number", 180),
            ("type", "Vehicle Type", 150),
            ("entry_time", "Entry Time", 180),
            ("status", "Status", 150),
        ]

        for col_id, heading, width in headings:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor="w")

        self.tree.pack(fill="both", expand=True, pady=(0, 6))

        # Double click row to view in search result box
        self.tree.bind("<Double-1>", self._on_row_select)

    def _handle_search(self):
        """Search vehicle in the parking manager."""
        query = self.query_entry.get().strip().upper()

        found, msg, details = self.pm.search_vehicle(query)

        if found and details is not None:
            self._display_result(details)
        else:
            # Clear result display
            for key, lbl in self.info_labels.items():
                lbl.configure(text="--", fg=COLOR_TEXT_PRIMARY)
            self.info_labels["status"].configure(text="Not Found", fg=COLOR_DANGER)

            messagebox.showinfo(
                title="Search Vehicle",
                message=msg,
                parent=self,
            )

    def _display_result(self, details: dict):
        """Populate the result card with vehicle information."""
        self.info_labels["vehicle_number"].configure(
            text=details.get("vehicle_number", "--"), fg=COLOR_PRIMARY
        )
        status_text = details.get("status", "--")
        is_parked = details.get("is_currently_parked", False)
        status_col = COLOR_SUCCESS if is_parked else COLOR_TEXT_SECONDARY
        self.info_labels["status"].configure(text=status_text, fg=status_col)

        self.info_labels["slot_number"].configure(
            text=details.get("slot_number", "--"), fg="#065F46" if is_parked else COLOR_TEXT_PRIMARY
        )
        self.info_labels["vehicle_type"].configure(
            text=details.get("vehicle_type", "--")
        )
        self.info_labels["entry_time"].configure(
            text=details.get("entry_time", "--")
        )
        self.info_labels["duration_so_far"].configure(
            text=details.get("duration_so_far", "--")
        )

    def _on_row_select(self, event):
        """Handle row click in table to load into search view."""
        selected_items = self.tree.selection()
        if selected_items:
            item = self.tree.item(selected_items[0])
            values = item["values"]
            if values and len(values) >= 2:
                plate = str(values[1])
                self.query_entry.delete(0, tk.END)
                self.query_entry.insert(0, plate)
                self._handle_search()

    def _reset_search(self):
        """Reset search and repopulate table."""
        self.query_entry.delete(0, tk.END)
        for key, lbl in self.info_labels.items():
            lbl.configure(text="--", fg=COLOR_TEXT_PRIMARY)
        self.refresh_data()
        self.query_entry.focus_set()

    def refresh_data(self):
        """Reload active parked vehicles into the table."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        occupied_slots = [s for s in self.pm.slots if s.is_occupied]
        for slot in occupied_slots:
            self.tree.insert(
                "",
                "end",
                values=(
                    slot.slot_number,
                    slot.vehicle_number,
                    slot.vehicle_type,
                    slot.entry_time,
                    "Parked (Occupied)",
                ),
            )

        self.table_count_lbl.configure(
            text=f"{len(occupied_slots)} Active Parked Vehicles"
        )

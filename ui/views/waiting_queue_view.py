"""
waiting_queue_view.py - Interface for managing the FIFO vehicle waiting queue.
Displays queue position, token, vehicle number, type, and live auto-assignment status.
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
    COLOR_WARNING,
    COLOR_WARNING_LIGHT,
    COLOR_SUCCESS,
    COLOR_SUCCESS_LIGHT,
    COLOR_DANGER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    FONT_SECTION_TITLE,
    FONT_BODY,
    FONT_BODY_BOLD,
)


class WaitingQueueView(tk.Frame):
    """View for FIFO waiting queue management when parking capacity is constrained."""

    def __init__(self, parent, parking_manager, on_data_updated=None):
        super().__init__(parent, bg=COLOR_BG)
        self.pm = parking_manager
        self.on_data_updated = on_data_updated

        container = tk.Frame(self, bg=COLOR_BG, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        self._build_queue_summary(container)
        self._build_queue_table(container)

        self.refresh_data()

    def _build_queue_summary(self, parent):
        """Build top queue metrics row."""
        summary_card = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        summary_card.pack(fill="x", pady=(0, 16))

        tk.Label(
            summary_card,
            text="⏳ Live FIFO Waiting Queue",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w")

        tk.Label(
            summary_card,
            text="First-In-First-Out line: vehicles wait here when all 20 slots are full and are auto-assigned when any slot frees up",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 12))

        # Stats Row (3 KPI cards)
        stats_row = tk.Frame(summary_card, bg=COLOR_CARD_BG)
        stats_row.pack(fill="x")

        # 1. Total in Queue
        box_q = tk.Frame(
            stats_row, bg=COLOR_WARNING_LIGHT, highlightbackground="#FDE68A", highlightthickness=1, padx=14, pady=10
        )
        box_q.pack(side="left", padx=(0, 12), fill="x", expand=True)
        tk.Label(box_q, text="VEHICLES IN QUEUE", font=(FONT_BODY[0], 8), fg=COLOR_TEXT_SECONDARY, bg=COLOR_WARNING_LIGHT).pack(anchor="w")
        self.queue_count_lbl = tk.Label(box_q, text="0 Vehicles", font=FONT_BODY_BOLD, fg=COLOR_WARNING, bg=COLOR_WARNING_LIGHT)
        self.queue_count_lbl.pack(anchor="w", pady=(2, 0))

        # 2. Next Vehicle in Line
        box_next = tk.Frame(
            stats_row, bg=COLOR_PRIMARY_LIGHT, highlightbackground="#BFDBFE", highlightthickness=1, padx=14, pady=10
        )
        box_next.pack(side="left", padx=(0, 12), fill="x", expand=True)
        tk.Label(box_next, text="NEXT IN LINE (PRIORITY #1)", font=(FONT_BODY[0], 8), fg=COLOR_TEXT_SECONDARY, bg=COLOR_PRIMARY_LIGHT).pack(anchor="w")
        self.next_vehicle_lbl = tk.Label(box_next, text="None (Queue Empty)", font=FONT_BODY_BOLD, fg=COLOR_PRIMARY, bg=COLOR_PRIMARY_LIGHT)
        self.next_vehicle_lbl.pack(anchor="w", pady=(2, 0))

        # 3. Facility Slot Status
        box_stat = tk.Frame(
            stats_row, bg=COLOR_SUCCESS_LIGHT, highlightbackground="#A7F3D0", highlightthickness=1, padx=14, pady=10
        )
        box_stat.pack(side="left", fill="x", expand=True)
        tk.Label(box_stat, text="LOT OCCUPANCY STATUS", font=(FONT_BODY[0], 8), fg=COLOR_TEXT_SECONDARY, bg=COLOR_SUCCESS_LIGHT).pack(anchor="w")
        self.lot_status_lbl = tk.Label(box_stat, text="20 Slots Available", font=FONT_BODY_BOLD, fg=COLOR_SUCCESS, bg=COLOR_SUCCESS_LIGHT)
        self.lot_status_lbl.pack(anchor="w", pady=(2, 0))

    def _build_queue_table(self, parent):
        """Build waiting queue list table and queue actions."""
        table_card = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        table_card.pack(fill="both", expand=True)

        # Header and action buttons row
        top_bar = tk.Frame(table_card, bg=COLOR_CARD_BG)
        top_bar.pack(fill="x", pady=(0, 10))

        tk.Label(
            top_bar,
            text="Queue Order & Driver Information",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(side="left")

        btn_box = tk.Frame(top_bar, bg=COLOR_CARD_BG)
        btn_box.pack(side="right")

        remove_btn = tk.Button(
            btn_box,
            text="❌ Cancel / Remove Selected",
            font=FONT_BODY,
            bg="#FEF2F2",
            fg=COLOR_DANGER,
            relief="solid",
            bd=1,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._handle_remove_selected,
        )
        remove_btn.pack(side="left", padx=(0, 8))

        refresh_btn = tk.Button(
            btn_box,
            text="🔄 Refresh",
            font=FONT_BODY,
            bg="#F1F5F9",
            fg=COLOR_TEXT_PRIMARY,
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.refresh_data,
        )
        refresh_btn.pack(side="left")

        # Treeview table
        columns = ("pos", "token", "plate", "type", "queued_at", "status")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", height=8)

        headings = [
            ("pos", "Queue Position", 140),
            ("token", "Token ID", 110),
            ("plate", "Vehicle Number", 180),
            ("type", "Vehicle Type", 140),
            ("queued_at", "Queued Time", 160),
            ("status", "Queue Status", 180),
        ]

        for col_id, heading, width in headings:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor="w")

        self.tree.pack(fill="both", expand=True, pady=(0, 10))

        # Bottom explanatory banner
        banner_box = tk.Frame(
            table_card,
            bg=COLOR_PRIMARY_LIGHT,
            highlightbackground="#BFDBFE",
            highlightthickness=1,
            padx=12,
            pady=8,
        )
        banner_box.pack(fill="x")

        tk.Label(
            banner_box,
            text="ℹ️ Automatic FIFO Allocation:",
            font=FONT_BODY_BOLD,
            fg=COLOR_PRIMARY,
            bg=COLOR_PRIMARY_LIGHT,
        ).pack(side="left", padx=(0, 6))

        tk.Label(
            banner_box,
            text="When any vehicle exits via 'Vehicle Exit', the first vehicle (#1) above is immediately assigned the freed slot.",
            font=FONT_BODY,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_PRIMARY_LIGHT,
        ).pack(side="left")

    def _handle_remove_selected(self):
        """Remove selected vehicle from the waiting queue."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                title="No Vehicle Selected",
                message="Please select a vehicle from the queue table to remove.",
                parent=self,
            )
            return

        item = self.tree.item(selected[0])
        values = item.get("values", [])
        if not values or len(values) < 3:
            return

        plate = str(values[2])
        confirm = messagebox.askyesno(
            title="Confirm Removal",
            message=f"Are you sure you want to remove vehicle '{plate}' from the Waiting Queue?",
            parent=self,
        )
        if confirm:
            success, msg = self.pm.remove_from_queue(plate)
            if success:
                messagebox.showinfo(title="Vehicle Removed", message=msg, parent=self)
                self.refresh_data()
                if self.on_data_updated:
                    self.on_data_updated()
            else:
                messagebox.showerror(title="Removal Error", message=msg, parent=self)

    def refresh_data(self):
        """Reload live waiting queue into summary and table."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        q_list = list(self.pm.waiting_queue)
        q_len = len(q_list)

        # Update summary cards
        self.queue_count_lbl.configure(text=f"{q_len} Vehicle{'s' if q_len != 1 else ''}")

        if q_len > 0:
            first_veh = q_list[0]
            self.next_vehicle_lbl.configure(
                text=f"{first_veh['vehicle_number']} ({first_veh['vehicle_type']}) [{first_veh.get('token', 'WQ-01')}]"
            )
        else:
            self.next_vehicle_lbl.configure(text="None (Queue Empty)")

        avail = self.pm.get_available_count()
        occ = self.pm.get_occupied_count()
        if avail == 0:
            self.lot_status_lbl.configure(
                text="All 20 Slots Full (Queuing Active)", fg=COLOR_DANGER
            )
        else:
            self.lot_status_lbl.configure(
                text=f"{avail} Slots Available ({occ} Occupied)", fg=COLOR_SUCCESS
            )

        # Populate table
        for idx, item in enumerate(q_list):
            pos_label = f"#1 (Next in line)" if idx == 0 else f"#{idx + 1}"
            status_text = "Waiting for next slot" if idx == 0 else f"{idx} vehicle(s) ahead"

            self.tree.insert(
                "",
                "end",
                values=(
                    pos_label,
                    item.get("token", f"WQ-{idx+1:02d}"),
                    item.get("vehicle_number", "--"),
                    item.get("vehicle_type", "--"),
                    item.get("queued_at", "--"),
                    status_text,
                ),
            )

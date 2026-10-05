"""
parking_slots_view.py - Visual display of all 20 parking slots with live status.
Each slot displays slot number, status, vehicle number, vehicle type, and entry time.
"""

import tkinter as tk
from tkinter import ttk
from config import (
    COLOR_BG,
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_LIGHT,
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


class ParkingSlotsView(tk.Frame):
    """View showing the real-time visual grid of all 20 parking slots."""

    def __init__(self, parent, parking_manager, on_quick_action=None):
        super().__init__(parent, bg=COLOR_BG)
        self.pm = parking_manager
        self.on_quick_action = on_quick_action

        self.slot_widgets = []  # Will store widget references for dynamic updating

        container = tk.Frame(self, bg=COLOR_BG, padx=24, pady=16)
        container.pack(fill="both", expand=True)

        self._build_header_stats(container)
        self._build_slots_grid(container)

        # Initial refresh
        self.refresh_data()

    def _build_header_stats(self, parent):
        """Build top status bar with counts and legend."""
        ctrl_card = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=12,
        )
        ctrl_card.pack(fill="x", pady=(0, 12))

        # Title & Subtitle
        top_box = tk.Frame(ctrl_card, bg=COLOR_CARD_BG)
        top_box.pack(fill="x")

        tk.Label(
            top_box,
            text="🅿️ Parking Slots Overview (20 Slots)",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(side="left")

        # Live counters on right
        counts_box = tk.Frame(top_box, bg=COLOR_CARD_BG)
        counts_box.pack(side="right")

        self.avail_badge = tk.Label(
            counts_box,
            text="20 Available",
            font=FONT_BODY_BOLD,
            fg=COLOR_SUCCESS,
            bg=COLOR_SUCCESS_LIGHT,
            padx=10,
            pady=3,
        )
        self.avail_badge.pack(side="left", padx=4)

        self.occ_badge = tk.Label(
            counts_box,
            text="0 Occupied",
            font=FONT_BODY_BOLD,
            fg=COLOR_DANGER,
            bg=COLOR_DANGER_LIGHT,
            padx=10,
            pady=3,
        )
        self.occ_badge.pack(side="left", padx=4)

        # Legend row
        legend_row = tk.Frame(ctrl_card, bg=COLOR_CARD_BG)
        legend_row.pack(fill="x", pady=(8, 0))

        tk.Label(
            legend_row,
            text="Status Legend:",
            font=(FONT_BODY[0], 8, "bold"),
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD_BG,
        ).pack(side="left", padx=(0, 8))

        # Green available pill
        leg_avail = tk.Frame(
            legend_row, bg=COLOR_SUCCESS_LIGHT, highlightbackground="#A7F3D0", highlightthickness=1, padx=8, pady=2
        )
        leg_avail.pack(side="left", padx=4)
        tk.Label(leg_avail, text="● Available (Free)", font=FONT_BODY, fg=COLOR_SUCCESS, bg=COLOR_SUCCESS_LIGHT).pack()

        # Red occupied pill
        leg_occ = tk.Frame(
            legend_row, bg=COLOR_DANGER_LIGHT, highlightbackground="#FECACA", highlightthickness=1, padx=8, pady=2
        )
        leg_occ.pack(side="left", padx=4)
        tk.Label(leg_occ, text="● Occupied (Vehicle Parked)", font=FONT_BODY, fg=COLOR_DANGER, bg=COLOR_DANGER_LIGHT).pack()

    def _build_slots_grid(self, parent):
        """Build 4 rows x 5 columns grid container for all 20 slots."""
        self.grid_container = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        self.grid_container.pack(fill="both", expand=True)

        # 5 equal-width columns
        for c in range(5):
            self.grid_container.columnconfigure(c, weight=1, uniform="slot_col")

        # 4 equal-height rows
        for r in range(4):
            self.grid_container.rowconfigure(r, weight=1, uniform="slot_row")

        # Create 20 slot card widgets
        self.slot_widgets = []
        for i in range(20):
            r = i // 5
            c = i % 5

            card = tk.Frame(
                self.grid_container,
                bg=COLOR_SUCCESS_LIGHT,
                highlightbackground="#A7F3D0",
                highlightthickness=1,
                padx=8,
                pady=6,
            )
            card.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

            # Slot header: Number + Status Badge
            top_row = tk.Frame(card, bg=COLOR_SUCCESS_LIGHT)
            top_row.pack(fill="x")

            slot_num_lbl = tk.Label(
                top_row,
                text=f"Slot {i + 1:02d}",
                font=("Segoe UI", 10, "bold"),
                fg=COLOR_TEXT_PRIMARY,
                bg=COLOR_SUCCESS_LIGHT,
            )
            slot_num_lbl.pack(side="left")

            status_lbl = tk.Label(
                top_row,
                text="Available",
                font=("Segoe UI", 8, "bold"),
                fg=COLOR_SUCCESS,
                bg=COLOR_SUCCESS_LIGHT,
            )
            status_lbl.pack(side="right")

            # Vehicle Number Display
            v_num_lbl = tk.Label(
                card,
                text="--",
                font=("Segoe UI", 10, "bold"),
                fg=COLOR_TEXT_MUTED,
                bg=COLOR_SUCCESS_LIGHT,
            )
            v_num_lbl.pack(anchor="w", pady=(2, 0))

            # Vehicle Type & Entry Time row
            details_box = tk.Frame(card, bg=COLOR_SUCCESS_LIGHT)
            details_box.pack(fill="x", pady=(2, 0))

            type_lbl = tk.Label(
                details_box,
                text="Type: --",
                font=("Segoe UI", 8),
                fg=COLOR_TEXT_SECONDARY,
                bg=COLOR_SUCCESS_LIGHT,
            )
            type_lbl.pack(side="left")

            time_lbl = tk.Label(
                details_box,
                text="Time: --",
                font=("Segoe UI", 8),
                fg=COLOR_TEXT_SECONDARY,
                bg=COLOR_SUCCESS_LIGHT,
            )
            time_lbl.pack(side="right")

            # Save references to update dynamically
            self.slot_widgets.append({
                "card": card,
                "top_row": top_row,
                "slot_num": slot_num_lbl,
                "status": status_lbl,
                "v_num": v_num_lbl,
                "details_box": details_box,
                "type": type_lbl,
                "time": time_lbl,
            })

    def refresh_data(self):
        """Update all 20 slot cards with live data from parking manager."""
        avail_cnt = self.pm.get_available_count()
        occ_cnt = self.pm.get_occupied_count()

        # Update top badges
        self.avail_badge.configure(text=f"{avail_cnt} Available")
        self.occ_badge.configure(text=f"{occ_cnt} Occupied")

        # Update each slot card
        for i, slot in enumerate(self.pm.slots):
            if i >= len(self.slot_widgets):
                break

            w = self.slot_widgets[i]

            if slot.is_occupied:
                bg = COLOR_DANGER_LIGHT
                border = "#FECACA"
                status_text = "Occupied"
                status_color = COLOR_DANGER
                v_num_text = slot.vehicle_number or "--"
                v_num_color = "#991B1B"
                v_type_text = f"Type: {slot.vehicle_type}"
                v_time_text = f"In: {slot.entry_time}"
            else:
                bg = COLOR_SUCCESS_LIGHT
                border = "#A7F3D0"
                status_text = "Available"
                status_color = COLOR_SUCCESS
                v_num_text = "Available"
                v_num_color = "#047857"
                v_type_text = "Type: --"
                v_time_text = "Time: --"

            # Apply styling
            w["card"].configure(bg=bg, highlightbackground=border)
            w["top_row"].configure(bg=bg)
            w["slot_num"].configure(bg=bg)
            w["status"].configure(text=status_text, fg=status_color, bg=bg)
            w["v_num"].configure(text=v_num_text, fg=v_num_color, bg=bg)
            w["details_box"].configure(bg=bg)
            w["type"].configure(text=v_type_text, bg=bg)
            w["time"].configure(text=v_time_text, bg=bg)

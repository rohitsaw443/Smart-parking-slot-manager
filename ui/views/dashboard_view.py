"""
dashboard_view.py - Main dashboard showing live statistics for the 20-slot parking facility.
"""

import tkinter as tk
from config import (
    COLOR_BG,
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_LIGHT,
    COLOR_SUCCESS,
    COLOR_SUCCESS_LIGHT,
    COLOR_WARNING,
    COLOR_WARNING_LIGHT,
    COLOR_PURPLE,
    COLOR_PURPLE_LIGHT,
    COLOR_DANGER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    FONT_CARD_TITLE,
    FONT_CARD_VALUE,
    FONT_CARD_NOTE,
    FONT_SECTION_TITLE,
    FONT_BODY,
    FONT_BODY_BOLD,
)


class DashboardView(tk.Frame):
    """Dashboard view displaying live metrics, slot distribution, and recent activity."""

    def __init__(self, parent, parking_manager):
        super().__init__(parent, bg=COLOR_BG)
        self.pm = parking_manager

        # Padding container
        self.container = tk.Frame(self, bg=COLOR_BG, padx=24, pady=20)
        self.container.pack(fill="both", expand=True)

        self._build_metric_cards()
        self._build_details_section()

        # Initial refresh
        self.refresh_data()

    def _build_metric_cards(self):
        """Build top 4 KPI summary cards."""
        cards_row = tk.Frame(self.container, bg=COLOR_BG)
        cards_row.pack(fill="x", pady=(0, 20))

        # Metrics definition: (key, title, note, icon, accent_col, light_bg)
        self.metric_defs = [
            ("total", "TOTAL SLOTS", "Full facility capacity", "🅿️", COLOR_PRIMARY, COLOR_PRIMARY_LIGHT),
            ("occupied", "OCCUPIED SLOTS", "Currently parked vehicles", "🚗", COLOR_WARNING, COLOR_WARNING_LIGHT),
            ("available", "AVAILABLE SLOTS", "Ready for incoming vehicles", "✅", COLOR_SUCCESS, COLOR_SUCCESS_LIGHT),
            ("queue", "WAITING QUEUE", "Vehicles waiting in FIFO line", "⏳", COLOR_PURPLE, COLOR_PURPLE_LIGHT),
        ]

        self.kpi_labels = {}

        for i, (key, title, note, icon, accent_col, light_bg) in enumerate(self.metric_defs):
            card = tk.Frame(
                cards_row,
                bg=COLOR_CARD_BG,
                highlightbackground=COLOR_CARD_BORDER,
                highlightthickness=1,
                padx=16,
                pady=16,
            )
            cards_row.columnconfigure(i, weight=1, uniform="metric_cards")
            card.grid(row=0, column=i, sticky="nsew", padx=6)

            top_box = tk.Frame(card, bg=COLOR_CARD_BG)
            top_box.pack(fill="x", pady=(0, 8))

            tk.Label(
                top_box,
                text=title,
                font=FONT_CARD_TITLE,
                fg=COLOR_TEXT_SECONDARY,
                bg=COLOR_CARD_BG,
            ).pack(side="left")

            tk.Label(
                top_box,
                text=icon,
                font=("Segoe UI", 12),
                bg=light_bg,
                fg=accent_col,
                padx=6,
                pady=2,
            ).pack(side="right")

            val_lbl = tk.Label(
                card,
                text="0",
                font=FONT_CARD_VALUE,
                fg=COLOR_TEXT_PRIMARY,
                bg=COLOR_CARD_BG,
            )
            val_lbl.pack(anchor="w", pady=(0, 4))
            self.kpi_labels[key] = val_lbl

            note_lbl = tk.Label(
                card,
                text=note,
                font=FONT_CARD_NOTE,
                fg=COLOR_TEXT_MUTED,
                bg=COLOR_CARD_BG,
            )
            note_lbl.pack(anchor="w")

    def _build_details_section(self):
        """Build the lower 2-column detailed breakdown panels."""
        lower_row = tk.Frame(self.container, bg=COLOR_BG)
        lower_row.pack(fill="both", expand=True)

        lower_row.columnconfigure(0, weight=6, uniform="lower_cols")
        lower_row.columnconfigure(1, weight=5, uniform="lower_cols")

        self._build_category_breakdown(lower_row)
        self._build_recent_activity(lower_row)

    def _build_category_breakdown(self, parent):
        """Build left panel: Slot distribution by vehicle type."""
        self.cat_panel = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=18,
        )
        self.cat_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(
            self.cat_panel,
            text="Slot Occupancy by Vehicle Type",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            self.cat_panel,
            text="Real-time distribution of parked vehicle categories across 20 slots",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 16))

        # Dynamic category progress rows
        self.cat_widgets = {}
        cat_configs = [
            ("cars", "Cars (Sedan / SUV / Hatchback)", COLOR_PRIMARY),
            ("bikes", "Bikes (Two-Wheelers)", "#3B82F6"),
            ("others", "Other Vehicles (Vans / Trucks / EV)", COLOR_PURPLE),
            ("available", "Available Free Slots", COLOR_SUCCESS),
        ]

        for key, display_name, col in cat_configs:
            row_box = tk.Frame(self.cat_panel, bg=COLOR_CARD_BG)
            row_box.pack(fill="x", pady=6)

            txt_box = tk.Frame(row_box, bg=COLOR_CARD_BG)
            txt_box.pack(fill="x")

            name_lbl = tk.Label(
                txt_box,
                text=display_name,
                font=FONT_BODY_BOLD,
                fg=COLOR_TEXT_PRIMARY,
                bg=COLOR_CARD_BG,
            )
            name_lbl.pack(side="left")

            count_lbl = tk.Label(
                txt_box,
                text="0 / 20",
                font=FONT_BODY,
                fg=COLOR_TEXT_SECONDARY,
                bg=COLOR_CARD_BG,
            )
            count_lbl.pack(side="right")

            bar_bg = tk.Frame(row_box, bg="#E2E8F0", height=8)
            bar_bg.pack(fill="x", pady=(4, 0))
            bar_bg.pack_propagate(False)

            fill_bar = tk.Frame(bar_bg, bg=col)
            fill_bar.place(relx=0, rely=0, relwidth=0, relheight=1.0)

            self.cat_widgets[key] = {
                "count_lbl": count_lbl,
                "fill_bar": fill_bar,
            }

    def _build_recent_activity(self, parent):
        """Build right panel: Live system operations & recent exit records."""
        self.status_panel = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=18,
        )
        self.status_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(
            self.status_panel,
            text="Recent Activity & Operations",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 4))

        tk.Label(
            self.status_panel,
            text="Latest events recorded in the parking facility",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 12))

        # Activity list container
        self.activity_box = tk.Frame(self.status_panel, bg=COLOR_CARD_BG)
        self.activity_box.pack(fill="both", expand=True)

        self.activity_labels = []
        for _ in range(5):
            lbl = tk.Label(
                self.activity_box,
                text="",
                font=FONT_BODY,
                fg=COLOR_TEXT_SECONDARY,
                bg=COLOR_CARD_BG,
                anchor="w",
            )
            lbl.pack(fill="x", pady=3)
            self.activity_labels.append(lbl)

        # Bottom Tip
        tip_box = tk.Frame(
            self.status_panel,
            bg=COLOR_PRIMARY_LIGHT,
            highlightbackground="#BFDBFE",
            highlightthickness=1,
            padx=12,
            pady=10,
        )
        tip_box.pack(fill="x", side="bottom", pady=(12, 0))

        tk.Label(
            tip_box,
            text="💡 Quick Actions",
            font=FONT_BODY_BOLD,
            fg=COLOR_PRIMARY,
            bg=COLOR_PRIMARY_LIGHT,
        ).pack(anchor="w")

        tk.Label(
            tip_box,
            text="Use 'Park Vehicle' to assign a slot, 'Vehicle Exit' to free a slot, or 'Parking Slots' to inspect the full 20-slot grid.",
            font=FONT_BODY,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_PRIMARY_LIGHT,
            wraplength=380,
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

    def refresh_data(self):
        """Update all KPI cards, category bars, and recent activity list."""
        summary = self.pm.get_summary()

        # Update KPI labels
        self.kpi_labels["total"].configure(text=str(summary["total_slots"]))
        self.kpi_labels["occupied"].configure(text=str(summary["occupied_slots"]))
        self.kpi_labels["available"].configure(text=str(summary["available_slots"]))
        self.kpi_labels["queue"].configure(text=str(summary["queue_count"]))

        # Update Category breakdown
        tot = summary["total_slots"]
        cats = [
            ("cars", summary["car_count"]),
            ("bikes", summary["bike_count"]),
            ("others", summary["other_count"]),
            ("available", summary["available_slots"]),
        ]

        for key, count in cats:
            pct = count / tot if tot > 0 else 0
            w = self.cat_widgets.get(key)
            if w:
                w["count_lbl"].configure(text=f"{count} / {tot} ({int(pct * 100)}%)")
                w["fill_bar"].place(relx=0, rely=0, relwidth=pct, relheight=1.0)

        # Update Recent Activity
        activities = []
        # Add waiting queue alerts if any
        if summary["queue_count"] > 0:
            activities.append(
                f"⏳ [Queue Alert] {summary['queue_count']} vehicle(s) waiting for available slots in FIFO line"
            )

        # Add recent exits
        for rec in self.pm.history:
            if rec.get("status") == "Completed":
                activities.append(
                    f"🚪 [Exit] {rec['vehicle_number']} ({rec['vehicle_type']}) exited {rec['slot_number']} at {rec.get('exit_time', '--')}"
                )
            if len(activities) >= 3:
                break

        # Add recent active parkings
        active_slots = [s for s in self.pm.slots if s.is_occupied]
        for s in active_slots[:2]:
            activities.append(
                f"🚗 [Parked] {s.vehicle_number} ({s.vehicle_type}) assigned to {s.slot_number} at {s.entry_time}"
            )
            if len(activities) >= 5:
                break

        if not activities:
            activities = ["● Facility ready. No vehicle activities recorded yet."]

        for i, lbl in enumerate(self.activity_labels):
            if i < len(activities):
                lbl.configure(text=activities[i])
            else:
                lbl.configure(text="")

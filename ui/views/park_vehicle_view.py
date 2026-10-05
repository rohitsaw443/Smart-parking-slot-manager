"""
park_vehicle_view.py - Interface for parking a vehicle and assigning available slots.
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
    COLOR_WARNING,
    COLOR_WARNING_LIGHT,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    FONT_SECTION_TITLE,
    FONT_BODY,
    FONT_BODY_BOLD,
)


class ParkVehicleView(tk.Frame):
    """View for vehicle entry registration and automatic slot assignment."""

    def __init__(self, parent, parking_manager, on_data_updated=None):
        super().__init__(parent, bg=COLOR_BG)
        self.pm = parking_manager
        self.on_data_updated = on_data_updated

        container = tk.Frame(self, bg=COLOR_BG, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        container.columnconfigure(0, weight=6, uniform="park_cols")
        container.columnconfigure(1, weight=4, uniform="park_cols")

        self._build_form(container)
        self._build_side_preview(container)

        # Initial refresh
        self.refresh_data()

    def _build_form(self, parent):
        """Build registration form."""
        form_card = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=24,
            pady=20,
        )
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(
            form_card,
            text="🚗 Park Vehicle",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w")

        tk.Label(
            form_card,
            text="Enter vehicle registration plate and select vehicle type to auto-assign a slot",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 16))

        # Vehicle Number Field
        tk.Label(
            form_card,
            text="Vehicle Number (e.g. DL 01 AB 1234) *",
            font=FONT_BODY_BOLD,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 4))

        self.plate_entry = tk.Entry(
            form_card,
            font=("Segoe UI", 12),
            bg="#F8FAFC",
            fg=COLOR_TEXT_PRIMARY,
            relief="solid",
            bd=1,
        )
        self.plate_entry.pack(fill="x", ipady=8, pady=(0, 14))
        self.plate_entry.focus_set()
        # Bind Enter key to submit
        self.plate_entry.bind("<Return>", lambda e: self._handle_park())

        # Vehicle Type Selection
        tk.Label(
            form_card,
            text="Vehicle Type *",
            font=FONT_BODY_BOLD,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 4))

        self.type_combo = ttk.Combobox(
            form_card,
            values=["Car", "Bike", "Other"],
            state="readonly",
            font=("Segoe UI", 11),
        )
        self.type_combo.current(0)  # Default: Car
        self.type_combo.pack(fill="x", ipady=6, pady=(0, 20))

        # Action Buttons
        btn_box = tk.Frame(form_card, bg=COLOR_CARD_BG)
        btn_box.pack(fill="x", pady=(0, 14))

        park_btn = tk.Button(
            btn_box,
            text="🅿️ Assign Slot & Park",
            font=FONT_BODY_BOLD,
            bg=COLOR_PRIMARY,
            fg="#FFFFFF",
            activebackground=COLOR_PRIMARY_HOVER,
            activeforeground="#FFFFFF",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._handle_park,
        )
        park_btn.pack(side="left", padx=(0, 8))

        clear_btn = tk.Button(
            btn_box,
            text="Clear",
            font=FONT_BODY,
            bg="#F1F5F9",
            fg=COLOR_TEXT_PRIMARY,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._clear_form,
        )
        clear_btn.pack(side="left")

        # Feedback Message Label (inline status)
        self.feedback_box = tk.Frame(form_card, bg=COLOR_CARD_BG, pady=4)
        self.feedback_box.pack(fill="x")

        self.feedback_lbl = tk.Label(
            self.feedback_box,
            text="",
            font=FONT_BODY_BOLD,
            bg=COLOR_CARD_BG,
            wraplength=480,
            justify="left",
        )
        self.feedback_lbl.pack(anchor="w")

    def _build_side_preview(self, parent):
        """Build right panel with slot allocation preview and parking lot status."""
        self.preview_card = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=20,
        )
        self.preview_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(
            self.preview_card,
            text="Slot Allocation Status",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 12))

        # Dynamic Next Slot Container
        self.slot_banner = tk.Frame(
            self.preview_card,
            bg=COLOR_SUCCESS_LIGHT,
            highlightbackground="#A7F3D0",
            highlightthickness=1,
            padx=16,
            pady=16,
        )
        self.slot_banner.pack(fill="x", pady=(0, 16))

        self.slot_banner_title = tk.Label(
            self.slot_banner,
            text="NEXT AVAILABLE SLOT",
            font=("Segoe UI", 8, "bold"),
            fg=COLOR_SUCCESS,
            bg=COLOR_SUCCESS_LIGHT,
        )
        self.slot_banner_title.pack(anchor="w")

        self.slot_name_lbl = tk.Label(
            self.slot_banner,
            text="Slot 01",
            font=("Segoe UI", 24, "bold"),
            fg="#065F46",
            bg=COLOR_SUCCESS_LIGHT,
        )
        self.slot_name_lbl.pack(anchor="w", pady=(4, 2))

        self.slot_sub_lbl = tk.Label(
            self.slot_banner,
            text="First in sequential order (1 - 20)",
            font=FONT_BODY,
            fg="#047857",
            bg=COLOR_SUCCESS_LIGHT,
        )
        self.slot_sub_lbl.pack(anchor="w")

        # Live Facility Availability Stats
        tk.Label(
            self.preview_card,
            text="Facility Capacity Breakdown",
            font=FONT_BODY_BOLD,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(8, 6))

        self.stats_rows_box = tk.Frame(self.preview_card, bg=COLOR_CARD_BG)
        self.stats_rows_box.pack(fill="x")

        self.avail_stat_lbl = tk.Label(
            self.stats_rows_box,
            text="Available Slots: 20 / 20",
            font=FONT_BODY,
            fg=COLOR_SUCCESS,
            bg=COLOR_CARD_BG,
        )
        self.avail_stat_lbl.pack(anchor="w", pady=2)

        self.occ_stat_lbl = tk.Label(
            self.stats_rows_box,
            text="Occupied Slots: 0 / 20",
            font=FONT_BODY,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_CARD_BG,
        )
        self.occ_stat_lbl.pack(anchor="w", pady=2)

        # Guidance Note
        note = tk.Label(
            self.preview_card,
            text="ℹ️ Tip: Vehicles are automatically assigned to the earliest free slot. Once parked, the slot is immediately reserved and marked occupied.",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD_BG,
            wraplength=280,
            justify="left",
        )
        note.pack(side="bottom", fill="x", pady=(16, 0))

    def _handle_park(self):
        """Process vehicle parking submission or queuing if full."""
        v_num = self.plate_entry.get().strip().upper()
        v_type = self.type_combo.get()

        success, msg, assigned_slot, action = self.pm.park_vehicle(v_num, v_type)

        if success and action == "parked" and assigned_slot is not None:
            # Inline success banner
            self.feedback_lbl.configure(
                text=f"✅ {msg}",
                fg=COLOR_SUCCESS,
            )
            messagebox.showinfo(
                title="Vehicle Parked Successfully",
                message=(
                    f"Vehicle '{v_num}' ({v_type}) has been successfully parked!\n\n"
                    f"Assigned Slot: {assigned_slot.slot_number}\n"
                    f"Entry Time: {assigned_slot.entry_time}"
                ),
                parent=self,
            )
            self.plate_entry.delete(0, tk.END)
            self.refresh_data()

            if self.on_data_updated:
                self.on_data_updated()

        elif success and action == "queued":
            # Added to FIFO Waiting Queue
            q_pos = len(self.pm.waiting_queue)
            self.feedback_lbl.configure(
                text=f"⏳ Vehicle '{v_num}' placed in Waiting Queue at Position #{q_pos}.",
                fg="#D97706",
            )
            messagebox.showinfo(
                title="Added to Waiting Queue",
                message=msg,
                parent=self,
            )
            self.plate_entry.delete(0, tk.END)
            self.refresh_data()

            if self.on_data_updated:
                self.on_data_updated()

        else:
            # Inline error
            self.feedback_lbl.configure(
                text=f"❌ {msg}",
                fg=COLOR_DANGER,
            )
            messagebox.showerror(
                title="Parking Error",
                message=msg,
                parent=self,
            )

    def _clear_form(self):
        """Clear the form fields and feedback."""
        self.plate_entry.delete(0, tk.END)
        self.type_combo.current(0)
        self.feedback_lbl.configure(text="")
        self.plate_entry.focus_set()

    def refresh_data(self):
        """Refresh dynamic slot preview and counters."""
        next_slot = self.pm.get_first_available_slot()
        avail_cnt = self.pm.get_available_count()
        occ_cnt = self.pm.get_occupied_count()
        tot_cnt = self.pm.total_slots
        queue_cnt = len(self.pm.waiting_queue)

        if next_slot is not None:
            self.slot_banner.configure(bg=COLOR_SUCCESS_LIGHT, highlightbackground="#A7F3D0")
            self.slot_banner_title.configure(
                text="NEXT AVAILABLE SLOT", fg=COLOR_SUCCESS, bg=COLOR_SUCCESS_LIGHT
            )
            self.slot_name_lbl.configure(
                text=next_slot.slot_number, fg="#065F46", bg=COLOR_SUCCESS_LIGHT
            )
            self.slot_sub_lbl.configure(
                text=f"Ready for allocation ({avail_cnt} free)", fg="#047857", bg=COLOR_SUCCESS_LIGHT
            )
        else:
            self.slot_banner.configure(bg=COLOR_WARNING_LIGHT, highlightbackground="#FDE68A")
            self.slot_banner_title.configure(
                text="ALL SLOTS FULL - WAITING QUEUE ACTIVE", fg=COLOR_WARNING, bg=COLOR_WARNING_LIGHT
            )
            self.slot_name_lbl.configure(
                text=f"Queue #{queue_cnt + 1}", fg="#B45309", bg=COLOR_WARNING_LIGHT
            )
            self.slot_sub_lbl.configure(
                text=f"Next vehicle will be queued ({queue_cnt} currently waiting)", fg="#92400E", bg=COLOR_WARNING_LIGHT
            )

        self.avail_stat_lbl.configure(
            text=f"Available Slots: {avail_cnt} / {tot_cnt}",
            fg=COLOR_SUCCESS if avail_cnt > 0 else COLOR_DANGER,
        )
        self.occ_stat_lbl.configure(
            text=f"Occupied Slots: {occ_cnt} / {tot_cnt} (Queue: {queue_cnt})",
        )

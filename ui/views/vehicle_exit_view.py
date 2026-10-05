"""
vehicle_exit_view.py - Interface for vehicle exit checkout, freeing slot, and exit logs.
"""

import tkinter as tk
from tkinter import messagebox
from config import (
    COLOR_BG,
    COLOR_CARD_BG,
    COLOR_CARD_BORDER,
    COLOR_PRIMARY,
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


class VehicleExitView(tk.Frame):
    """View for processing vehicle exit, freeing slots, and displaying exit receipts."""

    def __init__(self, parent, parking_manager, on_data_updated=None):
        super().__init__(parent, bg=COLOR_BG)
        self.pm = parking_manager
        self.on_data_updated = on_data_updated

        container = tk.Frame(self, bg=COLOR_BG, padx=24, pady=20)
        container.pack(fill="both", expand=True)

        container.columnconfigure(0, weight=6, uniform="exit_cols")
        container.columnconfigure(1, weight=5, uniform="exit_cols")

        self._build_exit_form(container)
        self._build_receipt_card(container)

    def _build_exit_form(self, parent):
        """Build vehicle exit search and checkout form."""
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
            text="🚪 Vehicle Exit & Checkout",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w")

        tk.Label(
            form_card,
            text="Enter vehicle registration number to process checkout and release the parking slot",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 16))

        # Vehicle Plate Input
        tk.Label(
            form_card,
            text="Vehicle Number (e.g. DL 01 AB 1234) *",
            font=FONT_BODY_BOLD,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 4))

        self.exit_plate_entry = tk.Entry(
            form_card,
            font=("Segoe UI", 12),
            bg="#F8FAFC",
            fg=COLOR_TEXT_PRIMARY,
            relief="solid",
            bd=1,
        )
        self.exit_plate_entry.pack(fill="x", ipady=8, pady=(0, 16))
        self.exit_plate_entry.focus_set()
        # Bind Enter key to exit action
        self.exit_plate_entry.bind("<Return>", lambda e: self._handle_exit())

        # Buttons
        btn_box = tk.Frame(form_card, bg=COLOR_CARD_BG)
        btn_box.pack(fill="x", pady=(0, 14))

        exit_btn = tk.Button(
            btn_box,
            text="🚪 Process Exit & Free Slot",
            font=FONT_BODY_BOLD,
            bg=COLOR_PRIMARY,
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._handle_exit,
        )
        exit_btn.pack(side="left", padx=(0, 8))

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

        # Feedback banner
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

    def _build_receipt_card(self, parent):
        """Build exit receipt details panel."""
        self.receipt_card = tk.Frame(
            parent,
            bg=COLOR_CARD_BG,
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=20,
            pady=20,
        )
        self.receipt_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(
            self.receipt_card,
            text="Latest Exit Summary",
            font=FONT_SECTION_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_CARD_BG,
        ).pack(anchor="w", pady=(0, 12))

        # Receipt Container
        self.rcpt_box = tk.Frame(
            self.receipt_card,
            bg="#F8FAFC",
            highlightbackground=COLOR_CARD_BORDER,
            highlightthickness=1,
            padx=16,
            pady=16,
        )
        self.rcpt_box.pack(fill="x", pady=(0, 16))

        # Dynamic fields in receipt
        self.rcpt_labels = {}
        fields = [
            ("Record ID", "record_id", "No exit processed yet"),
            ("Vehicle Number", "vehicle_number", "--"),
            ("Vehicle Type", "vehicle_type", "--"),
            ("Freed Slot", "slot_number", "--"),
            ("Entry Time", "entry_time", "--"),
            ("Exit Time", "exit_time", "--"),
            ("Parking Duration", "duration", "--"),
        ]

        for label_text, key, default_val in fields:
            row = tk.Frame(self.rcpt_box, bg="#F8FAFC")
            row.pack(fill="x", pady=3)

            tk.Label(
                row,
                text=label_text,
                font=FONT_BODY,
                fg=COLOR_TEXT_SECONDARY,
                bg="#F8FAFC",
            ).pack(side="left")

            val_lbl = tk.Label(
                row,
                text=default_val,
                font=FONT_BODY_BOLD,
                fg=COLOR_TEXT_PRIMARY,
                bg="#F8FAFC",
            )
            val_lbl.pack(side="right")
            self.rcpt_labels[key] = val_lbl

        # Status note
        self.receipt_note = tk.Label(
            self.receipt_card,
            text="ℹ️ When you process an exit, the vehicle duration and departure timestamp will be recorded and displayed here.",
            font=FONT_BODY,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD_BG,
            wraplength=320,
            justify="left",
        )
        self.receipt_note.pack(side="bottom", fill="x", pady=(16, 0))

    def _handle_exit(self):
        """Process vehicle exit and automatic waiting queue allocation."""
        v_num = self.exit_plate_entry.get().strip().upper()

        success, msg, exit_info, auto_alloc = self.pm.exit_vehicle(v_num)

        if success and exit_info is not None:
            # Inline message
            self.feedback_lbl.configure(text=f"✅ {msg.splitlines()[0]}", fg=COLOR_SUCCESS)

            # Update receipt labels
            for key, val in exit_info.items():
                if key in self.rcpt_labels:
                    self.rcpt_labels[key].configure(text=str(val))

            # Success popup dialog with auto-allocation info if applicable
            title_text = "Vehicle Exit & Queue Allocation" if auto_alloc else "Vehicle Exit Successful"
            messagebox.showinfo(
                title=title_text,
                message=msg,
                parent=self,
            )

            # Clear entry
            self.exit_plate_entry.delete(0, tk.END)

            # Notify global views to update slots, queue, dashboard, and history
            if self.on_data_updated:
                self.on_data_updated()
        else:
            # Error feedback
            self.feedback_lbl.configure(text=f"❌ {msg}", fg=COLOR_DANGER)
            messagebox.showerror(
                title="Exit Error",
                message=msg,
                parent=self,
            )

    def _clear_form(self):
        """Clear the exit entry field."""
        self.exit_plate_entry.delete(0, tk.END)
        self.feedback_lbl.configure(text="")
        self.exit_plate_entry.focus_set()

    def refresh_data(self):
        """Refresh placeholder if needed."""
        pass

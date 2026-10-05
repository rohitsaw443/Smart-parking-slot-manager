"""
header.py - Top header bar for the main application area.
Displays the current screen title, description, live clock, and system status indicator.
"""

import time
import tkinter as tk
from config import (
    COLOR_HEADER_BG,
    COLOR_HEADER_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_SUCCESS_LIGHT,
    FONT_HEADER_TITLE,
    FONT_HEADER_SUBTITLE,
    FONT_BODY,
    FONT_BODY_BOLD,
)


class Header(tk.Frame):
    """Top bar displaying page header information and live status."""

    def __init__(self, parent):
        super().__init__(
            parent,
            bg=COLOR_HEADER_BG,
            height=70,
            highlightbackground=COLOR_HEADER_BORDER,
            highlightthickness=1,
        )
        self.pack_propagate(False)

        # Left: Title and subtitle
        self.title_box = tk.Frame(self, bg=COLOR_HEADER_BG, padx=24, pady=12)
        self.title_box.pack(side="left", fill="y")

        self.title_lbl = tk.Label(
            self.title_box,
            text="Dashboard",
            font=FONT_HEADER_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_HEADER_BG,
            anchor="w",
        )
        self.title_lbl.pack(anchor="w")

        self.subtitle_lbl = tk.Label(
            self.title_box,
            text="Real-time parking facility overview and quick stats",
            font=FONT_HEADER_SUBTITLE,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_HEADER_BG,
            anchor="w",
        )
        self.subtitle_lbl.pack(anchor="w")

        # Right: Live Clock & System Status
        self.status_box = tk.Frame(self, bg=COLOR_HEADER_BG, padx=24, pady=16)
        self.status_box.pack(side="right", fill="y")

        # System Status Badge
        self.badge_frame = tk.Frame(
            self.status_box,
            bg=COLOR_SUCCESS_LIGHT,
            padx=10,
            pady=4,
            highlightbackground="#A7F3D0",
            highlightthickness=1,
        )
        self.badge_frame.pack(side="right", padx=(12, 0))

        self.badge_dot = tk.Label(
            self.badge_frame,
            text="●",
            font=("Segoe UI", 8),
            fg=COLOR_SUCCESS,
            bg=COLOR_SUCCESS_LIGHT,
        )
        self.badge_dot.pack(side="left", padx=(0, 4))

        self.badge_text = tk.Label(
            self.badge_frame,
            text="System Online",
            font=FONT_BODY_BOLD,
            fg=COLOR_SUCCESS,
            bg=COLOR_SUCCESS_LIGHT,
        )
        self.badge_text.pack(side="left")

        # Live Clock Label
        self.clock_lbl = tk.Label(
            self.status_box,
            text="",
            font=FONT_BODY,
            fg=COLOR_TEXT_SECONDARY,
            bg=COLOR_HEADER_BG,
        )
        self.clock_lbl.pack(side="right")

        # Start live clock
        self._update_clock()

    def set_title(self, title, subtitle=""):
        """Update header title and subtitle dynamically."""
        self.title_lbl.configure(text=title)
        self.subtitle_lbl.configure(text=subtitle)

    def _update_clock(self):
        """Update clock display every second."""
        now_str = time.strftime("%I:%M:%S %p  |  %a, %b %d, %Y")
        self.clock_lbl.configure(text=f"🕒 {now_str}")
        self.after(1000, self._update_clock)

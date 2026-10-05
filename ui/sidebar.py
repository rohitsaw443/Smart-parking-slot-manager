"""
sidebar.py - Left navigation sidebar component.
Contains navigation buttons for switching views and exiting the application.
"""

import tkinter as tk
from config import (
    COLOR_SIDEBAR_BG,
    COLOR_SIDEBAR_BORDER,
    COLOR_PRIMARY,
    COLOR_PRIMARY_LIGHT,
    COLOR_NAV_TEXT,
    COLOR_NAV_HOVER,
    COLOR_EXIT_BG,
    COLOR_EXIT_HOVER,
    COLOR_EXIT_TEXT,
    COLOR_EXIT_BORDER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_MUTED,
    FONT_APP_TITLE,
    FONT_APP_SUBTITLE,
    FONT_NAV,
    FONT_NAV_ACTIVE,
    FONT_BODY,
    FONT_BODY_BOLD,
)


class Sidebar(tk.Frame):
    """Left sidebar containing branding, navigation menu, and exit button."""

    def __init__(self, parent, on_navigate, on_exit):
        super().__init__(parent, bg=COLOR_SIDEBAR_BG, width=240)
        self.pack_propagate(False)

        self.on_navigate = on_navigate
        self.on_exit = on_exit

        self.active_item = None
        self.nav_buttons = {}  # Store button references: {key: (frame, bar, icon_lbl, text_lbl)}

        # Build Sidebar Sections
        self._build_brand_header()
        self._build_nav_menu()
        self._build_bottom_exit()

    def _build_brand_header(self):
        """Build top logo and application title."""
        header_frame = tk.Frame(self, bg=COLOR_SIDEBAR_BG, padx=16, pady=20)
        header_frame.pack(fill="x")

        # Logo Icon Badge
        logo_badge = tk.Label(
            header_frame,
            text="🅿️",
            font=("Segoe UI", 20),
            bg=COLOR_PRIMARY_LIGHT,
            fg=COLOR_PRIMARY,
            padx=8,
            pady=4,
        )
        logo_badge.pack(side="left", padx=(0, 10))

        # Title & Subtitle container
        title_box = tk.Frame(header_frame, bg=COLOR_SIDEBAR_BG)
        title_box.pack(side="left", fill="both", expand=True)

        title_lbl = tk.Label(
            title_box,
            text="Smart Parking",
            font=FONT_APP_TITLE,
            fg=COLOR_TEXT_PRIMARY,
            bg=COLOR_SIDEBAR_BG,
            anchor="w",
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            title_box,
            text="Slot Manager v1.0",
            font=FONT_APP_SUBTITLE,
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_SIDEBAR_BG,
            anchor="w",
        )
        subtitle_lbl.pack(anchor="w")

        # Divider line
        divider = tk.Frame(self, bg=COLOR_SIDEBAR_BORDER, height=1)
        divider.pack(fill="x", padx=16, pady=(0, 10))

    def _build_nav_menu(self):
        """Build navigation buttons for each application section."""
        nav_container = tk.Frame(self, bg=COLOR_SIDEBAR_BG)
        nav_container.pack(fill="both", expand=True, padx=8, pady=4)

        # Section Label
        section_lbl = tk.Label(
            nav_container,
            text="MAIN MENU",
            font=(FONT_NAV[0], 8, "bold"),
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_SIDEBAR_BG,
            anchor="w",
            padx=8,
            pady=6,
        )
        section_lbl.pack(fill="x")

        # Navigation items: (key, display_label, icon)
        menu_items = [
            ("dashboard", "Dashboard", "📊"),
            ("park_vehicle", "Park Vehicle", "🚗"),
            ("vehicle_exit", "Vehicle Exit", "🚪"),
            ("search_vehicle", "Search Vehicle", "🔍"),
            ("parking_slots", "Parking Slots", "🅿️"),
            ("waiting_queue", "Waiting Queue", "⏳"),
            ("parking_history", "Parking History", "📜"),
        ]

        for key, label, icon in menu_items:
            self._create_nav_item(nav_container, key, label, icon)

    def _create_nav_item(self, parent, key, label, icon):
        """Creates an attractive modern button with hover and active state."""
        item_frame = tk.Frame(parent, bg=COLOR_SIDEBAR_BG, cursor="hand2")
        item_frame.pack(fill="x", pady=2)

        # Left indicator bar (appears colored when active)
        indicator = tk.Frame(item_frame, bg=COLOR_SIDEBAR_BG, width=4)
        indicator.pack(side="left", fill="y")

        # Content container
        content = tk.Frame(item_frame, bg=COLOR_SIDEBAR_BG, padx=8, pady=8)
        content.pack(side="left", fill="both", expand=True)

        icon_lbl = tk.Label(
            content,
            text=icon,
            font=("Segoe UI", 12),
            bg=COLOR_SIDEBAR_BG,
            fg=COLOR_NAV_TEXT,
            width=2,
            anchor="center",
        )
        icon_lbl.pack(side="left", padx=(0, 8))

        text_lbl = tk.Label(
            content,
            text=label,
            font=FONT_NAV,
            bg=COLOR_SIDEBAR_BG,
            fg=COLOR_NAV_TEXT,
            anchor="w",
        )
        text_lbl.pack(side="left", fill="x", expand=True)

        # Store widgets for state updates
        self.nav_buttons[key] = {
            "frame": item_frame,
            "indicator": indicator,
            "content": content,
            "icon": icon_lbl,
            "text": text_lbl,
        }

        # Bind click and hover events to all inner widgets
        widgets = (item_frame, indicator, content, icon_lbl, text_lbl)
        for w in widgets:
            w.bind("<Button-1>", lambda e, k=key: self.on_navigate(k))
            w.bind("<Enter>", lambda e, k=key: self._on_hover(k, True))
            w.bind("<Leave>", lambda e, k=key: self._on_hover(k, False))

    def _build_bottom_exit(self):
        """Build the Exit button at the bottom of the sidebar."""
        bottom_frame = tk.Frame(self, bg=COLOR_SIDEBAR_BG, padx=12, pady=16)
        bottom_frame.pack(side="bottom", fill="x")

        # Divider
        divider = tk.Frame(bottom_frame, bg=COLOR_SIDEBAR_BORDER, height=1)
        divider.pack(fill="x", pady=(0, 12))

        # Exit Button Card
        exit_btn_frame = tk.Frame(
            bottom_frame,
            bg=COLOR_EXIT_BG,
            highlightbackground=COLOR_EXIT_BORDER,
            highlightthickness=1,
            cursor="hand2",
            padx=10,
            pady=8,
        )
        exit_btn_frame.pack(fill="x")

        exit_icon = tk.Label(
            exit_btn_frame,
            text="❌",
            font=("Segoe UI", 10),
            bg=COLOR_EXIT_BG,
            fg=COLOR_EXIT_TEXT,
        )
        exit_icon.pack(side="left", padx=(0, 8))

        exit_text = tk.Label(
            exit_btn_frame,
            text="Exit Application",
            font=FONT_BODY_BOLD,
            bg=COLOR_EXIT_BG,
            fg=COLOR_EXIT_TEXT,
            anchor="w",
        )
        exit_text.pack(side="left", fill="x", expand=True)

        # Hover effects for Exit button
        def on_exit_hover(enter):
            bg = COLOR_EXIT_HOVER if enter else COLOR_EXIT_BG
            exit_btn_frame.configure(bg=bg)
            exit_icon.configure(bg=bg)
            exit_text.configure(bg=bg)

        for w in (exit_btn_frame, exit_icon, exit_text):
            w.bind("<Button-1>", lambda e: self.on_exit())
            w.bind("<Enter>", lambda e: on_exit_hover(True))
            w.bind("<Leave>", lambda e: on_exit_hover(False))

    def set_active(self, active_key):
        """Update navigation styling when an item is selected."""
        self.active_item = active_key

        for key, widgets in self.nav_buttons.items():
            is_active = (key == active_key)

            bg_color = COLOR_PRIMARY_LIGHT if is_active else COLOR_SIDEBAR_BG
            fg_color = COLOR_PRIMARY if is_active else COLOR_NAV_TEXT
            font_choice = FONT_NAV_ACTIVE if is_active else FONT_NAV
            bar_color = COLOR_PRIMARY if is_active else COLOR_SIDEBAR_BG

            widgets["frame"].configure(bg=bg_color)
            widgets["indicator"].configure(bg=bar_color)
            widgets["content"].configure(bg=bg_color)
            widgets["icon"].configure(bg=bg_color, fg=fg_color)
            widgets["text"].configure(bg=bg_color, fg=fg_color, font=font_choice)

    def _on_hover(self, key, is_entering):
        """Handle subtle hover highlight for inactive navigation items."""
        if key == self.active_item:
            return  # Keep active styling untouched

        widgets = self.nav_buttons.get(key)
        if not widgets:
            return

        bg_color = COLOR_NAV_HOVER if is_entering else COLOR_SIDEBAR_BG
        bar_color = COLOR_SIDEBAR_BORDER if is_entering else COLOR_SIDEBAR_BG

        widgets["frame"].configure(bg=bg_color)
        widgets["indicator"].configure(bg=bar_color)
        widgets["content"].configure(bg=bg_color)
        widgets["icon"].configure(bg=bg_color)
        widgets["text"].configure(bg=bg_color)

"""
main.py - Entry point for the Smart Parking Slot Manager application.
Run this file to start the desktop GUI.
"""

import sys
import tkinter as tk
from tkinter import ttk

from ui.main_window import MainWindow


def enable_high_dpi_awareness():
    """Enable high-DPI scaling on Windows so text and icons render crisp and sharp."""
    if sys.platform.startswith("win"):
        try:
            from ctypes import windll
            # Set Process DPI Awareness (1 = Process_System_DPI_Aware)
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def configure_ttk_styles():
    """Configure modern styles for standard ttk widgets (Treeview, Combobox)."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Style Combobox
    style.configure(
        "TCombobox",
        fieldbackground="#F8FAFC",
        background="#FFFFFF",
        foreground="#0F172A",
        padding=4,
    )

    # Style Treeview
    style.configure(
        "Treeview",
        background="#FFFFFF",
        foreground="#0F172A",
        fieldbackground="#FFFFFF",
        rowheight=28,
        font=("Segoe UI", 9),
    )
    style.configure(
        "Treeview.Heading",
        background="#F1F5F9",
        foreground="#334155",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        padding=6,
    )
    style.map(
        "Treeview",
        background=[("selected", "#EFF6FF")],
        foreground=[("selected", "#1D4ED8")],
    )


def main():
    """Initialize Tkinter and launch the Smart Parking Slot Manager."""
    # 1. Enable crisp font rendering on Windows
    enable_high_dpi_awareness()

    # 2. Create the root Tkinter window
    root = tk.Tk()

    # 3. Apply modern widget themes
    configure_ttk_styles()

    # 4. Initialize Main Application Window
    MainWindow(root)

    # 5. Start the event loop
    root.mainloop()


if __name__ == "__main__":
    main()

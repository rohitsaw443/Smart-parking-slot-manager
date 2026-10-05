"""
main_window.py - Main application window and layout orchestrator.
Combines Sidebar, Header, and Content Views with smooth navigation.
"""

import sys
import tkinter as tk
from tkinter import messagebox

from config import (
    APP_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MIN_WIDTH,
    MIN_HEIGHT,
    COLOR_BG,
    COLOR_SIDEBAR_BORDER,
)
from parking_manager import ParkingManager
from ui.sidebar import Sidebar
from ui.header import Header
from ui.views.dashboard_view import DashboardView
from ui.views.park_vehicle_view import ParkVehicleView
from ui.views.vehicle_exit_view import VehicleExitView
from ui.views.search_vehicle_view import SearchVehicleView
from ui.views.parking_slots_view import ParkingSlotsView
from ui.views.waiting_queue_view import WaitingQueueView
from ui.views.parking_history_view import ParkingHistoryView

# View titles and descriptions for top header bar
VIEW_INFO = {
    "dashboard": (
        "Dashboard Overview",
        "Real-time parking facility capacity, occupancy metrics, and operational status",
    ),
    "park_vehicle": (
        "Park Vehicle",
        "Register incoming vehicle and automatically assign first available slot",
    ),
    "vehicle_exit": (
        "Vehicle Exit",
        "Process vehicle checkout, record exit duration, and free parking slot",
    ),
    "search_vehicle": (
        "Search Vehicle",
        "Search vehicle by number to locate slot number, type, entry time, and status",
    ),
    "parking_slots": (
        "Parking Slots (20 Slots)",
        "Visual real-time grid of all 20 parking slots and their occupancy status",
    ),
    "waiting_queue": (
        "Waiting Queue (FIFO)",
        "Ordered waiting line for arriving vehicles when facility reaches full capacity",
    ),
    "parking_history": (
        "Parking History & Records",
        "Audit trail of completed parking sessions, timestamps, and durations",
    ),
}


class MainWindow:
    """Main application controller for the Smart Parking Slot Manager."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self._configure_root_window()

        # Initialize core parking manager with 20 slots
        self.pm = ParkingManager(total_slots=20)

        # Master layout container
        self.master_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.master_frame.pack(fill="both", expand=True)

        # Build UI layout components
        self._build_sidebar()
        self._build_main_area()
        self._initialize_views()

        # Start on the Dashboard
        self.show_view("dashboard")

        # Handle window close (X button in window title bar)
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def _configure_root_window(self):
        """Set window title, dimensions, minimum size, and center on screen."""
        self.root.title(APP_TITLE)
        self.root.configure(bg=COLOR_BG)
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)

        # Center window on screen
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        pos_x = max(0, (screen_w - WINDOW_WIDTH) // 2)
        pos_y = max(0, (screen_h - WINDOW_HEIGHT) // 2)

        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{pos_x}+{pos_y}")

    def _build_sidebar(self):
        """Build left sidebar navigation with all requested buttons."""
        self.sidebar = Sidebar(
            self.master_frame,
            on_navigate=self.show_view,
            on_exit=self.on_exit,
        )
        self.sidebar.pack(side="left", fill="y")

        # Vertical divider border
        divider = tk.Frame(self.master_frame, bg=COLOR_SIDEBAR_BORDER, width=1)
        divider.pack(side="left", fill="y")

    def _build_main_area(self):
        """Build the right-hand main content area with header and view host."""
        self.main_area = tk.Frame(self.master_frame, bg=COLOR_BG)
        self.main_area.pack(side="right", fill="both", expand=True)

        # Top Header Bar
        self.header = Header(self.main_area)
        self.header.pack(fill="x")

        # Dynamic View Content Container
        self.content_container = tk.Frame(self.main_area, bg=COLOR_BG)
        self.content_container.pack(fill="both", expand=True)

    def _initialize_views(self):
        """Instantiate views for each sidebar section with shared ParkingManager."""
        self.views = {
            "dashboard": DashboardView(self.content_container, self.pm),
            "park_vehicle": ParkVehicleView(
                self.content_container, self.pm, on_data_updated=self.refresh_all_views
            ),
            "vehicle_exit": VehicleExitView(
                self.content_container, self.pm, on_data_updated=self.refresh_all_views
            ),
            "search_vehicle": SearchVehicleView(self.content_container, self.pm),
            "parking_slots": ParkingSlotsView(self.content_container, self.pm),
            "waiting_queue": WaitingQueueView(
                self.content_container, self.pm, on_data_updated=self.refresh_all_views
            ),
            "parking_history": ParkingHistoryView(self.content_container, self.pm),
        }

    def show_view(self, view_key: str):
        """Switch active view and update sidebar selection & header title."""
        if view_key not in self.views:
            return

        # Hide all view frames
        for view in self.views.values():
            view.pack_forget()

        # Display selected view
        target_view = self.views[view_key]
        target_view.pack(fill="both", expand=True)

        # Automatically refresh view data if supported
        if hasattr(target_view, "refresh_data"):
            target_view.refresh_data()

        # Update sidebar active indicator
        self.sidebar.set_active(view_key)

        # Update header title and subtitle
        title, subtitle = VIEW_INFO.get(view_key, (APP_TITLE, ""))
        self.header.set_title(title, subtitle)

    def refresh_all_views(self):
        """Notify all views to synchronize with the latest parking data."""
        for view in self.views.values():
            if hasattr(view, "refresh_data"):
                view.refresh_data()

    def on_exit(self):
        """Confirm and cleanly exit the application."""
        answer = messagebox.askyesno(
            title="Exit Confirmation",
            message="Are you sure you want to exit Smart Parking Slot Manager?",
            icon="question",
            parent=self.root,
        )
        if answer:
            self.root.destroy()
            sys.exit(0)

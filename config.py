"""
config.py - Application configuration, theme settings, and UI constants.
Beginner-friendly configuration file for Smart Parking Slot Manager.
"""

# ==========================================
# WINDOW CONFIGURATION
# ==========================================
APP_TITLE = "Smart Parking Slot Manager"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
MIN_WIDTH = 1000
MIN_HEIGHT = 650

# ==========================================
# COLOR PALETTE (Clean Light Modern Theme)
# ==========================================
# Backgrounds
COLOR_BG = "#F8FAFC"               # Soft light slate background for main area
COLOR_SIDEBAR_BG = "#FFFFFF"       # Crisp white sidebar
COLOR_SIDEBAR_BORDER = "#E2E8F0"   # Light border between sidebar and content
COLOR_CARD_BG = "#FFFFFF"          # Card background
COLOR_CARD_BORDER = "#E2E8F0"      # Card subtle border
COLOR_HEADER_BG = "#FFFFFF"        # Top header background
COLOR_HEADER_BORDER = "#E2E8F0"    # Top header bottom border

# Brand & Accent Colors
COLOR_PRIMARY = "#2563EB"          # Vibrant blue for active items & primary buttons
COLOR_PRIMARY_HOVER = "#1D4ED8"    # Darker blue for hover
COLOR_PRIMARY_LIGHT = "#EFF6FF"    # Very light blue for active nav highlight
COLOR_ACCENT = "#3B82F6"           # Light accent blue

# Typography Colors
COLOR_TEXT_PRIMARY = "#0F172A"     # Deep slate for headings & primary text
COLOR_TEXT_SECONDARY = "#64748B"   # Neutral slate for secondary descriptions
COLOR_TEXT_MUTED = "#94A3B8"       # Light slate for hints & timestamps
COLOR_NAV_TEXT = "#334155"         # Default sidebar text color
COLOR_NAV_HOVER = "#F8FAFC"        # Light hover background for nav items

# Status & Indicator Colors
COLOR_SUCCESS = "#10B981"          # Green for Available slots / Online status
COLOR_SUCCESS_LIGHT = "#ECFDF5"    # Soft green background
COLOR_WARNING = "#F59E0B"          # Amber/Orange for Waiting Queue
COLOR_WARNING_LIGHT = "#FFFBEB"    # Soft amber background
COLOR_DANGER = "#EF4444"           # Red for Occupied slots / Alerts
COLOR_DANGER_LIGHT = "#FEF2F2"     # Soft red background
COLOR_PURPLE = "#8B5CF6"           # Purple for statistics
COLOR_PURPLE_LIGHT = "#F5F3FF"     # Soft purple background

# Exit Button Styling
COLOR_EXIT_TEXT = "#DC2626"
COLOR_EXIT_BG = "#FEF2F2"
COLOR_EXIT_HOVER = "#FEE2E2"
COLOR_EXIT_BORDER = "#FECACA"

# ==========================================
# TYPOGRAPHY (Modern Segoe UI Font Set)
# ==========================================
FONT_FAMILY = "Segoe UI"

FONT_APP_TITLE = (FONT_FAMILY, 13, "bold")
FONT_APP_SUBTITLE = (FONT_FAMILY, 9)

FONT_NAV = (FONT_FAMILY, 10, "normal")
FONT_NAV_ACTIVE = (FONT_FAMILY, 10, "bold")

FONT_HEADER_TITLE = (FONT_FAMILY, 16, "bold")
FONT_HEADER_SUBTITLE = (FONT_FAMILY, 9)

FONT_CARD_TITLE = (FONT_FAMILY, 9, "bold")
FONT_CARD_VALUE = (FONT_FAMILY, 22, "bold")
FONT_CARD_NOTE = (FONT_FAMILY, 8)

FONT_SECTION_TITLE = (FONT_FAMILY, 11, "bold")
FONT_BODY = (FONT_FAMILY, 9)
FONT_BODY_BOLD = (FONT_FAMILY, 9, "bold")

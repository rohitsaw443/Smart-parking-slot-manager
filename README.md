# Smart Parking Slot Manager 🅿️🚗

A modern, desktop-based Parking Management GUI built with **Python** and **Tkinter**.

---

## 🌟 Overview & Key Highlights

- **Window Title:** `Smart Parking Slot Manager`
- **Default Resolution:** `1200 x 750` (responsive with minimum size set to `1000 x 650`)
- **Theme:** Clean, modern, light-colored SaaS-inspired design (soft slate background, crisp white panels, vibrant blue accents)
- **High-DPI Support:** Windows DPI awareness enabled for sharp typography and crisp icons
- **Facility Capacity:** **20 Parking Slots** (`Slot 01` to `Slot 20`)
- **Real-Time Synchronization:** Parking or exiting a vehicle immediately updates the visual slot grid, dashboard statistics, search table, and audit history.

---

## 🚀 Core Features Implemented

### 1. 🅿️ 20 Parking Slots (`ui/views/parking_slots_view.py`)
- Visual grid layout of **20 parking slots** (`Slot 01` to `Slot 20`).
- Each slot displays:
  - **Slot Number** (e.g. `Slot 01`)
  - **Status** (🟢 `Available` or 🔴 `Occupied`)
  - **Vehicle Number** (e.g. `DL 01 AB 1234` or `Available`)
  - **Vehicle Type** (`Car`, `Bike`, or `Other`)
  - **Entry Time** (e.g. `02:30:15 PM`)
- Top counters showing live count of available and occupied slots.

### 2. 🚗 Park Vehicle (`ui/views/park_vehicle_view.py`)
- User enters vehicle registration number.
- User selects vehicle type: **Car**, **Bike**, or **Other**.
- Automatically assigns the **first available parking slot** sequentially.
- Displays a clear confirmation dialog with the assigned slot number and entry timestamp.
- Immediate UI updates across all tabs.
- **Validations**: Empty input check, duplicate vehicle check, lot full check.

### 3. 🚪 Vehicle Exit (`ui/views/vehicle_exit_view.py`)
- User enters vehicle registration number.
- Locates vehicle, calculates parking duration, and frees the parking slot.
- Records departure timestamp and duration into the history audit log.
- Shows a detailed exit dialog and receipt card.
- **Validations**: Empty input check, vehicle not found error dialog.

### 4. 🔍 Search Vehicle (`ui/views/search_vehicle_view.py`)
- Search by vehicle number.
- Displays **Slot Number**, **Vehicle Type**, **Entry Time**, and **Status** (`Parked (Occupied)` / `Exited`).
- Includes a live table of all currently parked vehicles with double-click quick view.

---

## 📁 Project Structure

```text
SmartParkingSlotManager1/
│
├── config.py                       # Global colors, typography, dimensions, and constants
├── parking_manager.py              # Core business logic: 20 slots, park, exit, search, history
├── main.py                         # Application entry point with DPI awareness & event loop
├── README.md                       # Project documentation & run guide
│
└── ui/
    ├── __init__.py                 # UI package marker
    ├── main_window.py              # Master window orchestrator & view synchronizer
    ├── sidebar.py                  # Left navigation bar with all 8 buttons
    ├── header.py                   # Top bar showing active view title and live clock
    │
    └── views/
        ├── __init__.py             # Views package marker
        ├── dashboard_view.py       # Live dashboard with KPI cards and distribution bars
        ├── park_vehicle_view.py    # Vehicle check-in & first-available slot assignment
        ├── vehicle_exit_view.py    # Vehicle checkout, duration calculation & receipt
        ├── search_vehicle_view.py  # Vehicle search and active parked vehicles table
        ├── parking_slots_view.py   # Visual 20-slot color-coded grid
        ├── waiting_queue_view.py   # FIFO waiting queue management interface
        └── parking_history_view.py # Historical departure records & audit trail
```

---

## 💻 How to Run

1. Make sure Python 3.8+ is installed:
   ```bash
   python --version
   ```
2. Run the application from this directory:
   ```bash
   python main.py
   ```

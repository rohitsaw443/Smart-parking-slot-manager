"""
parking_manager.py - Core business logic for Smart Parking Slot Manager.
Manages the 20 parking slots, FIFO waiting queue, vehicle entry/exit,
search, and persistent history records.
"""

from collections import deque
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Any

from storage import save_parking_data, load_parking_data


class ParkingSlot:
    """Represents an individual parking slot in the facility."""

    def __init__(self, slot_id: int):
        self.slot_id: int = slot_id
        self.slot_number: str = f"Slot {slot_id:02d}"  # e.g. "Slot 01" to "Slot 20"
        self.is_occupied: bool = False
        self.vehicle_number: Optional[str] = None
        self.vehicle_type: Optional[str] = None         # "Car", "Bike", "Other"
        self.entry_time: Optional[str] = None           # e.g. "02:30:15 PM"
        self.entry_datetime: Optional[datetime] = None  # Datetime for duration calculation

    def park(self, vehicle_number: str, vehicle_type: str, entry_dt: Optional[datetime] = None) -> None:
        """Assign this slot to a vehicle."""
        now = entry_dt or datetime.now()
        self.is_occupied = True
        self.vehicle_number = vehicle_number.strip().upper()
        self.vehicle_type = vehicle_type
        self.entry_datetime = now
        self.entry_time = now.strftime("%I:%M:%S %p")

    def free(self) -> None:
        """Release this slot when vehicle exits."""
        self.is_occupied = False
        self.vehicle_number = None
        self.vehicle_type = None
        self.entry_time = None
        self.entry_datetime = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert slot details to dictionary representation for persistence."""
        return {
            "slot_id": self.slot_id,
            "slot_number": self.slot_number,
            "is_occupied": self.is_occupied,
            "vehicle_number": self.vehicle_number,
            "vehicle_type": self.vehicle_type,
            "entry_time": self.entry_time,
            "entry_iso": self.entry_datetime.isoformat() if self.entry_datetime else None,
        }

    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """Restore slot details from stored dictionary."""
        self.is_occupied = data.get("is_occupied", False)
        self.vehicle_number = data.get("vehicle_number")
        self.vehicle_type = data.get("vehicle_type")
        self.entry_time = data.get("entry_time")
        iso_str = data.get("entry_iso")
        if iso_str:
            try:
                self.entry_datetime = datetime.fromisoformat(iso_str)
            except Exception:
                self.entry_datetime = datetime.now()
        else:
            self.entry_datetime = None


class ParkingManager:
    """Manages 20 parking slots, FIFO waiting queue, and persistent history."""

    def __init__(self, total_slots: int = 20):
        self.total_slots: int = total_slots
        self.slots: List[ParkingSlot] = [ParkingSlot(i) for i in range(1, total_slots + 1)]
        self.waiting_queue: deque = deque()  # FIFO Queue: elements are dicts
        self.history: List[Dict[str, Any]] = []
        self._history_counter: int = 1
        self._queue_token_counter: int = 1

        # Load persisted data on startup
        self.load_state()

    # ==========================================
    # DATA PERSISTENCE (SAVE / LOAD)
    # ==========================================
    def save_state(self) -> bool:
        """Serialize current state and save to persistent storage."""
        data = {
            "total_slots": self.total_slots,
            "slots": [s.to_dict() for s in self.slots],
            "waiting_queue": list(self.waiting_queue),
            "history": self.history,
            "history_counter": self._history_counter,
            "queue_token_counter": self._queue_token_counter,
            "last_updated": datetime.now().isoformat(),
        }
        return save_parking_data(data)

    def load_state(self) -> bool:
        """Load and restore state from persistent storage."""
        data = load_parking_data()
        if not data:
            return False

        try:
            # Restore slots
            saved_slots = data.get("slots", [])
            for saved_s in saved_slots:
                s_id = saved_s.get("slot_id")
                if s_id and 1 <= s_id <= len(self.slots):
                    self.slots[s_id - 1].load_from_dict(saved_s)

            # Restore waiting queue (FIFO)
            saved_queue = data.get("waiting_queue", [])
            self.waiting_queue = deque(saved_queue)

            # Restore history
            self.history = data.get("history", [])

            # Restore counters
            self._history_counter = data.get("history_counter", len(self.history) + 1)
            self._queue_token_counter = data.get("queue_token_counter", len(self.waiting_queue) + 1)
            return True
        except Exception as e:
            print(f"[ParkingManager] Error parsing stored state: {e}")
            return False

    # ==========================================
    # QUERIES & SUMMARY HELPERS
    # ==========================================
    def get_available_count(self) -> int:
        """Return the number of available slots."""
        return sum(1 for s in self.slots if not s.is_occupied)

    def get_occupied_count(self) -> int:
        """Return the number of occupied slots."""
        return sum(1 for s in self.slots if s.is_occupied)

    def get_first_available_slot(self) -> Optional[ParkingSlot]:
        """Find and return the first available slot in sequential order."""
        for slot in self.slots:
            if not slot.is_occupied:
                return slot
        return None

    def is_vehicle_parked(self, vehicle_number: str) -> bool:
        """Check if a vehicle is currently parked in any slot."""
        v_num = vehicle_number.strip().upper()
        return any(s.is_occupied and s.vehicle_number == v_num for s in self.slots)

    def is_vehicle_in_queue(self, vehicle_number: str) -> Tuple[bool, int]:
        """Check if vehicle is already waiting in queue. Returns (is_in_queue, position)."""
        v_num = vehicle_number.strip().upper()
        for i, item in enumerate(self.waiting_queue):
            if item["vehicle_number"] == v_num:
                return True, i + 1
        return False, 0

    def get_slot_by_vehicle(self, vehicle_number: str) -> Optional[ParkingSlot]:
        """Locate the slot where the given vehicle is parked."""
        v_num = vehicle_number.strip().upper()
        for slot in self.slots:
            if slot.is_occupied and slot.vehicle_number == v_num:
                return slot
        return None

    def get_summary(self) -> Dict[str, Any]:
        """Return counts and statistics for the dashboard."""
        car_count = sum(1 for s in self.slots if s.is_occupied and s.vehicle_type == "Car")
        bike_count = sum(1 for s in self.slots if s.is_occupied and s.vehicle_type == "Bike")
        other_count = sum(1 for s in self.slots if s.is_occupied and s.vehicle_type == "Other")

        return {
            "total_slots": self.total_slots,
            "occupied_slots": self.get_occupied_count(),
            "available_slots": self.get_available_count(),
            "queue_count": len(self.waiting_queue),
            "car_count": car_count,
            "bike_count": bike_count,
            "other_count": other_count,
            "total_history_count": len(self.history),
        }

    # ==========================================
    # CORE OPERATION 1: PARK VEHICLE (WITH FIFO QUEUE)
    # ==========================================
    def park_vehicle(
        self, vehicle_number: str, vehicle_type: str
    ) -> Tuple[bool, str, Optional[ParkingSlot], str]:
        """
        Parks a vehicle into first available slot, OR adds to FIFO Waiting Queue if all 20 slots full.
        Returns: (success: bool, message: str, assigned_slot: ParkingSlot | None, action: "parked"|"queued"|"error")
        """
        # 1. Validate vehicle number
        v_clean = vehicle_number.strip().upper()
        if not v_clean:
            return False, "Vehicle number cannot be empty. Please enter a valid registration plate.", None, "error"

        if len(v_clean) < 3:
            return False, "Vehicle number is too short. Please enter a valid registration plate.", None, "error"

        # 2. Validate vehicle type
        valid_types = ("Car", "Bike", "Other")
        if vehicle_type not in valid_types:
            return False, f"Invalid vehicle type. Allowed types are: {', '.join(valid_types)}.", None, "error"

        # 3. Check if vehicle is already parked
        existing_slot = self.get_slot_by_vehicle(v_clean)
        if existing_slot is not None:
            return (
                False,
                f"Vehicle '{v_clean}' is already parked in {existing_slot.slot_number}.",
                None,
                "error",
            )

        # 4. Check if vehicle is already waiting in queue
        in_queue, pos = self.is_vehicle_in_queue(v_clean)
        if in_queue:
            return (
                False,
                f"Vehicle '{v_clean}' is already waiting in the queue at position #{pos}.",
                None,
                "error",
            )

        # 5. Check if slot is available
        slot = self.get_first_available_slot()

        if slot is not None:
            # Assign slot immediately
            slot.park(v_clean, vehicle_type)

            # Record entry in history
            now = datetime.now()
            history_rec = {
                "record_id": f"#REC-{self._history_counter:04d}",
                "vehicle_number": v_clean,
                "vehicle_type": vehicle_type,
                "slot_number": slot.slot_number,
                "entry_time": slot.entry_time,
                "exit_time": "Currently Parked",
                "status": "Active",
                "duration": "Active",
                "date": now.strftime("%Y-%m-%d"),
            }
            self._history_counter += 1
            self.history.insert(0, history_rec)

            self.save_state()
            return True, f"Vehicle '{v_clean}' successfully parked in {slot.slot_number}!", slot, "parked"

        else:
            # All 20 slots occupied -> Add to FIFO Waiting Queue
            now = datetime.now()
            queue_item = {
                "token": f"WQ-{self._queue_token_counter:02d}",
                "vehicle_number": v_clean,
                "vehicle_type": vehicle_type,
                "queued_at": now.strftime("%I:%M:%S %p"),
                "queued_iso": now.isoformat(),
            }
            self._queue_token_counter += 1
            self.waiting_queue.append(queue_item)
            queue_position = len(self.waiting_queue)

            self.save_state()
            return (
                True,
                f"All 20 parking slots are occupied!\n\n"
                f"Vehicle '{v_clean}' ({vehicle_type}) has been placed in the Waiting Queue.\n"
                f"Queue Position: #{queue_position} (Token: {queue_item['token']})\n"
                f"It will be automatically assigned the next available slot when a vehicle exits.",
                None,
                "queued",
            )

    # ==========================================
    # CORE OPERATION 2: VEHICLE EXIT (WITH AUTO QUEUE ALLOCATION)
    # ==========================================
    def exit_vehicle(
        self, vehicle_number: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Frees the parking slot, logs exit in history, and automatically assigns
        the freed slot to the first vehicle in the FIFO waiting queue (if any).
        Returns: (success: bool, message: str, exit_info: dict | None, auto_allocated: dict | None)
        """
        v_clean = vehicle_number.strip().upper()
        if not v_clean:
            return False, "Vehicle number cannot be empty. Please enter a vehicle number to exit.", None, None

        # Locate slot
        slot = self.get_slot_by_vehicle(v_clean)
        if slot is None:
            # Check if user tried to exit a vehicle currently in waiting queue
            in_q, q_pos = self.is_vehicle_in_queue(v_clean)
            if in_q:
                return (
                    False,
                    f"Vehicle '{v_clean}' is currently in the Waiting Queue at position #{q_pos} and has not parked yet.",
                    None,
                    None,
                )
            return (
                False,
                f"Vehicle '{v_clean}' not found in the parking lot. Please verify the vehicle number.",
                None,
                None,
            )

        # Calculate duration
        now = datetime.now()
        duration_delta = now - slot.entry_datetime if slot.entry_datetime else None

        if duration_delta:
            total_seconds = int(duration_delta.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            if hours > 0:
                duration_str = f"{hours}h {minutes}m {seconds}s"
            elif minutes > 0:
                duration_str = f"{minutes}m {seconds}s"
            else:
                duration_str = f"{seconds}s"
        else:
            duration_str = "Under 1 min"

        exit_time_str = now.strftime("%I:%M:%S %p")
        freed_slot_number = slot.slot_number

        # Exit details for receipt
        exit_info = {
            "slot_number": freed_slot_number,
            "vehicle_number": slot.vehicle_number,
            "vehicle_type": slot.vehicle_type,
            "entry_time": slot.entry_time,
            "exit_time": exit_time_str,
            "duration": duration_str,
        }

        # Update matching Active history record
        updated_history = False
        for rec in self.history:
            if rec.get("vehicle_number") == v_clean and rec.get("status") == "Active":
                rec["exit_time"] = exit_time_str
                rec["duration"] = duration_str
                rec["status"] = "Completed"
                updated_history = True
                break

        # Fallback if no active record found (e.g. legacy data)
        if not updated_history:
            history_rec = {
                "record_id": f"#REC-{self._history_counter:04d}",
                "vehicle_number": v_clean,
                "vehicle_type": slot.vehicle_type,
                "slot_number": freed_slot_number,
                "entry_time": slot.entry_time,
                "exit_time": exit_time_str,
                "status": "Completed",
                "duration": duration_str,
                "date": now.strftime("%Y-%m-%d"),
            }
            self._history_counter += 1
            self.history.insert(0, history_rec)

        # Free the slot
        slot.free()

        # ==========================================
        # AUTOMATIC FIFO QUEUE ALLOCATION
        # ==========================================
        auto_allocated_info = None
        if len(self.waiting_queue) > 0:
            # Pop first vehicle from FIFO queue
            next_veh = self.waiting_queue.popleft()
            next_plate = next_veh["vehicle_number"]
            next_type = next_veh["vehicle_type"]

            # Automatically park in this newly freed slot
            slot.park(next_plate, next_type)

            # Record entry in history for this queued vehicle
            q_history_rec = {
                "record_id": f"#REC-{self._history_counter:04d}",
                "vehicle_number": next_plate,
                "vehicle_type": next_type,
                "slot_number": freed_slot_number,
                "entry_time": slot.entry_time,
                "exit_time": "Currently Parked",
                "status": "Active",
                "duration": "Active",
                "date": now.strftime("%Y-%m-%d"),
            }
            self._history_counter += 1
            self.history.insert(0, q_history_rec)

            auto_allocated_info = {
                "slot_number": freed_slot_number,
                "vehicle_number": next_plate,
                "vehicle_type": next_type,
                "entry_time": slot.entry_time,
                "token": next_veh.get("token", "--"),
            }

            msg = (
                f"Vehicle '{v_clean}' has successfully exited!\n\n"
                f"{freed_slot_number} was freed and AUTOMATICALLY ASSIGNED to waiting vehicle:\n"
                f"Vehicle: '{next_plate}' ({next_type})\n"
                f"Token: {next_veh.get('token', '--')}\n"
                f"Entry Time: {slot.entry_time}\n\n"
                f"Remaining in Queue: {len(self.waiting_queue)} vehicles."
            )
        else:
            msg = f"Vehicle '{v_clean}' has successfully exited. {freed_slot_number} is now Available!"

        self.save_state()
        return True, msg, exit_info, auto_allocated_info

    # ==========================================
    # QUEUE MANAGEMENT HELPERS
    # ==========================================
    def remove_from_queue(self, vehicle_number: str) -> Tuple[bool, str]:
        """Remove a vehicle from the waiting queue if cancelled by the user."""
        v_clean = vehicle_number.strip().upper()
        found_idx = -1
        for i, item in enumerate(self.waiting_queue):
            if item["vehicle_number"] == v_clean:
                found_idx = i
                break

        if found_idx != -1:
            removed = self.waiting_queue[found_idx]
            del self.waiting_queue[found_idx]
            self.save_state()
            return True, f"Vehicle '{v_clean}' (Token: {removed.get('token', '--')}) removed from Waiting Queue."
        return False, f"Vehicle '{v_clean}' not found in the Waiting Queue."

    # ==========================================
    # CORE OPERATION 3: SEARCH VEHICLE
    # ==========================================
    def search_vehicle(
        self, vehicle_number: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Searches for a vehicle across currently parked slots, waiting queue, and history.
        Returns: (found: bool, message: str, details: dict | None)
        """
        v_clean = vehicle_number.strip().upper()
        if not v_clean:
            return False, "Please enter a vehicle number to search.", None

        # 1. Check currently parked slots
        slot = self.get_slot_by_vehicle(v_clean)
        if slot is not None:
            now = datetime.now()
            duration_delta = now - slot.entry_datetime if slot.entry_datetime else None
            if duration_delta:
                mins = int(duration_delta.total_seconds() // 60)
                duration_str = f"{mins} mins" if mins > 0 else "Just entered"
            else:
                duration_str = "Active"

            details = {
                "vehicle_number": slot.vehicle_number,
                "status": "Parked (Occupied)",
                "slot_number": slot.slot_number,
                "vehicle_type": slot.vehicle_type,
                "entry_time": slot.entry_time,
                "exit_time": "Currently Parked",
                "duration_so_far": duration_str,
                "is_currently_parked": True,
            }
            return True, f"Vehicle '{v_clean}' is currently parked in {slot.slot_number}.", details

        # 2. Check waiting queue
        in_q, pos = self.is_vehicle_in_queue(v_clean)
        if in_q:
            q_item = self.waiting_queue[pos - 1]
            details = {
                "vehicle_number": q_item["vehicle_number"],
                "status": f"Waiting in Queue (Position #{pos})",
                "slot_number": "Pending Allocation",
                "vehicle_type": q_item["vehicle_type"],
                "entry_time": f"Queued at {q_item['queued_at']}",
                "exit_time": "--",
                "duration_so_far": f"In Queue #{pos}",
                "is_currently_parked": False,
            }
            return True, f"Vehicle '{v_clean}' is currently in the Waiting Queue at position #{pos}.", details

        # 3. Check historical records
        for rec in self.history:
            if rec.get("vehicle_number") == v_clean:
                details = {
                    "vehicle_number": rec["vehicle_number"],
                    "status": f"Exited ({rec.get('date', 'Past Session')})",
                    "slot_number": rec.get("slot_number", "--"),
                    "vehicle_type": rec.get("vehicle_type", "--"),
                    "entry_time": rec.get("entry_time", "--"),
                    "exit_time": rec.get("exit_time", "--"),
                    "duration_so_far": rec.get("duration", "--"),
                    "is_currently_parked": False,
                }
                return (
                    True,
                    f"Vehicle '{v_clean}' previously visited and exited at {rec.get('exit_time')}.",
                    details,
                )

        return False, f"No vehicle record found for '{v_clean}'.", None

    # ==========================================
    # HISTORY SEARCH HELPER
    # ==========================================
    def search_history(self, query: str = "") -> List[Dict[str, Any]]:
        """Filter history records by vehicle number, type, slot, or status."""
        q = query.strip().upper()
        if not q:
            return list(self.history)

        results = []
        for rec in self.history:
            v_num = rec.get("vehicle_number", "").upper()
            v_type = rec.get("vehicle_type", "").upper()
            slot = rec.get("slot_number", "").upper()
            status = rec.get("status", "").upper()
            rec_id = rec.get("record_id", "").upper()

            if q in v_num or q in v_type or q in slot or q in status or q in rec_id:
                results.append(rec)
        return results

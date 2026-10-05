"""
storage.py - Safe JSON data persistence module for Smart Parking Slot Manager.
Handles saving, loading, atomic file writes with OneDrive compatibility,
and corrupted file recovery.
"""

import json
import os
import shutil
import time
from datetime import datetime
from typing import Optional, Dict, Any

# Data storage directory and file path
STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATA_FILE_PATH = os.path.join(STORAGE_DIR, "parking_data.json")


def ensure_storage_dir() -> None:
    """Ensure the data directory exists."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR, exist_ok=True)


def save_parking_data(data: Dict[str, Any]) -> bool:
    """
    Saves parking data safely to disk.
    Tries atomic replace first; if locked by cloud syncing (e.g. OneDrive),
    falls back cleanly to direct write so no data is lost.
    """
    try:
        ensure_storage_dir()
        temp_file = os.path.join(STORAGE_DIR, "parking_data.json.tmp")

        # Write data formatted with indent
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Attempt atomic replace with short retries
        saved = False
        for _ in range(3):
            try:
                os.replace(temp_file, DATA_FILE_PATH)
                saved = True
                break
            except (PermissionError, OSError):
                time.sleep(0.05)

        # Fallback to direct write if file system lock persists (OneDrive watcher)
        if not saved:
            with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

        return True
    except Exception as e:
        print(f"[Storage Error] Failed to save data: {e}")
        return False


def load_parking_data() -> Optional[Dict[str, Any]]:
    """
    Loads parking data from disk.
    If the file is missing, returns None.
    If the file is corrupted, creates a safe backup and returns None so the app recovers cleanly.
    """
    ensure_storage_dir()

    if not os.path.exists(DATA_FILE_PATH):
        return None

    try:
        with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Basic structure validation
        if not isinstance(data, dict):
            raise ValueError("Root data is not a valid JSON object")

        return data

    except Exception as e:
        print(f"[Storage Warning] Corrupted or invalid data file detected: {e}")
        # Safely preserve the corrupted file for recovery/inspection
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(STORAGE_DIR, f"parking_data_corrupt_{timestamp}.bak")
            shutil.copy2(DATA_FILE_PATH, backup_path)
            print(f"[Storage Recovery] Corrupted file backed up to: {backup_path}")
        except Exception as backup_err:
            print(f"[Storage Recovery] Could not create backup: {backup_err}")

        return None

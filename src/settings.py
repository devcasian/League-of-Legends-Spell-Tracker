"""
Settings management for the overlay application.

This module handles saving and loading user preferences.
"""

import json
import os
from config import SETTINGS_FILE, LAYOUT


def load_settings():
    """Load user settings from JSON file."""
    if not os.path.exists(SETTINGS_FILE):
        return {"layout": LAYOUT, "position": None}

    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            if "position" not in settings:
                settings["position"] = None
            return settings
    except (json.JSONDecodeError, IOError):
        return {"layout": LAYOUT, "position": None}


def save_settings(layout, position=None):
    """Save user settings to JSON file."""
    current_settings = load_settings()
    current_settings["layout"] = layout
    if position is not None:
        current_settings["position"] = position

    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(current_settings, f, indent=2)
    except IOError as e:
        print(f"Error saving settings: {e}")

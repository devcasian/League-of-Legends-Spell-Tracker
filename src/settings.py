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
        return {"layout": LAYOUT}

    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            return settings
    except (json.JSONDecodeError, IOError):
        return {"layout": LAYOUT}


def save_settings(layout):
    """Save user settings to JSON file."""
    settings = {"layout": layout}
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
    except IOError as e:
        print(f"Error saving settings: {e}")

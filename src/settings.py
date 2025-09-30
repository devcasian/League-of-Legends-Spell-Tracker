"""
Settings management for the overlay application.

This module handles saving and loading user preferences.
"""

import json
import os
from config import SETTINGS_FILE, LAYOUT, SOUND_ENABLED, SOUND_VOLUME, SOUND_ALERT_THRESHOLD


def load_settings():
    """Load user settings from JSON file."""
    if not os.path.exists(SETTINGS_FILE):
        return {
            "layout": LAYOUT,
            "position": None,
            "locked": False,
            "sound_enabled": SOUND_ENABLED,
            "sound_volume": SOUND_VOLUME,
            "sound_alert_threshold": SOUND_ALERT_THRESHOLD
        }

    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            if "position" not in settings:
                settings["position"] = None
            if "locked" not in settings:
                settings["locked"] = False
            if "sound_enabled" not in settings:
                settings["sound_enabled"] = SOUND_ENABLED
            if "sound_volume" not in settings:
                settings["sound_volume"] = SOUND_VOLUME
            if "sound_alert_threshold" not in settings:
                settings["sound_alert_threshold"] = SOUND_ALERT_THRESHOLD
            return settings
    except (json.JSONDecodeError, IOError):
        return {
            "layout": LAYOUT,
            "position": None,
            "locked": False,
            "sound_enabled": SOUND_ENABLED,
            "sound_volume": SOUND_VOLUME,
            "sound_alert_threshold": SOUND_ALERT_THRESHOLD
        }


def save_settings(layout, position=None, locked=None, sound_enabled=None, sound_volume=None, sound_alert_threshold=None):
    """Save user settings to JSON file."""
    current_settings = load_settings()
    current_settings["layout"] = layout
    if position is not None:
        current_settings["position"] = position
    if locked is not None:
        current_settings["locked"] = locked
    if sound_enabled is not None:
        current_settings["sound_enabled"] = sound_enabled
    if sound_volume is not None:
        current_settings["sound_volume"] = sound_volume
    if sound_alert_threshold is not None:
        current_settings["sound_alert_threshold"] = sound_alert_threshold

    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(current_settings, f, indent=2)
    except IOError as e:
        print(f"Error saving settings: {e}")

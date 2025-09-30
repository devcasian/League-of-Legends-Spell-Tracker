"""
Settings management for the overlay application.

This module handles saving and loading user preferences.
"""

import json
import os
from pathlib import Path
from config import LAYOUT, SOUND_ENABLED, SOUND_VOLUME, SOUND_ALERT_THRESHOLD, UI_SCALE, DEFAULT_LOCKED, DEFAULT_POSITION, USE_CHAMPION_ICONS


def get_settings_path():
    """Get the settings file path in AppData directory."""
    if os.name == 'nt':
        app_data = os.getenv('APPDATA')
        settings_dir = Path(app_data) / 'SpellTracker'
    else:
        settings_dir = Path.home() / '.config' / 'spell-tracker'

    settings_dir.mkdir(parents=True, exist_ok=True)
    return settings_dir / 'settings.json'


def load_settings():
    """Load user settings from JSON file."""
    settings_file = get_settings_path()

    if not settings_file.exists():
        return {
            "layout": LAYOUT,
            "position": DEFAULT_POSITION,
            "locked": DEFAULT_LOCKED,
            "sound_enabled": SOUND_ENABLED,
            "sound_volume": SOUND_VOLUME,
            "sound_alert_threshold": SOUND_ALERT_THRESHOLD,
            "ui_scale": UI_SCALE,
            "use_champion_icons": USE_CHAMPION_ICONS
        }

    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            if "position" not in settings:
                settings["position"] = DEFAULT_POSITION
            if "locked" not in settings:
                settings["locked"] = DEFAULT_LOCKED
            if "sound_enabled" not in settings:
                settings["sound_enabled"] = SOUND_ENABLED
            if "sound_volume" not in settings:
                settings["sound_volume"] = SOUND_VOLUME
            if "sound_alert_threshold" not in settings:
                settings["sound_alert_threshold"] = SOUND_ALERT_THRESHOLD
            if "ui_scale" not in settings:
                settings["ui_scale"] = UI_SCALE
            if "use_champion_icons" not in settings:
                settings["use_champion_icons"] = USE_CHAMPION_ICONS
            return settings
    except (json.JSONDecodeError, IOError):
        return {
            "layout": LAYOUT,
            "position": DEFAULT_POSITION,
            "locked": DEFAULT_LOCKED,
            "sound_enabled": SOUND_ENABLED,
            "sound_volume": SOUND_VOLUME,
            "sound_alert_threshold": SOUND_ALERT_THRESHOLD,
            "ui_scale": UI_SCALE,
            "use_champion_icons": USE_CHAMPION_ICONS
        }


def save_settings(layout, position=None, locked=None, sound_enabled=None, sound_volume=None, sound_alert_threshold=None, ui_scale=None, use_champion_icons=None):
    """Save user settings to JSON file."""
    settings_file = get_settings_path()
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
    if ui_scale is not None:
        current_settings["ui_scale"] = ui_scale
    if use_champion_icons is not None:
        current_settings["use_champion_icons"] = use_champion_icons

    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(current_settings, f, indent=2)
    except IOError as e:
        print(f"Error saving settings: {e}")

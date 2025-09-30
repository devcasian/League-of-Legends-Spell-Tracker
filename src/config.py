"""
Configuration settings for the League of Legends overlay.

This module contains all configurable parameters for the overlay application,
including visual settings, UI colors, and file paths.
"""

import sys
import os
from pathlib import Path


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = Path(__file__).parent.parent

    return os.path.join(base_path, relative_path)

OVERLAY_ALPHA = 0.95
OVERLAY_BG_COLOR = "#0a0a0a"
BORDER_COLOR = "#2a2a2a"

EMPTY_SLOT_BORDER_COLOR = "#555555"
EMPTY_SLOT_BORDER_WIDTH = 1

LAYOUT_TOGGLE_SIZE = 24
LAYOUT_TOGGLE_COLOR = "#888888"

PIN_BUTTON_SIZE = 24
PIN_BUTTON_COLOR = "#888888"

LOCK_BUTTON_SIZE = 24
LOCK_BUTTON_COLOR = "#888888"

ICON_SIZE = 64
SLOT_SPACING = 5

SUMMONER_SPELL_SIZE = 30
SUMMONER_SPELL_SPACING = 2

LAYOUT = "horizontal"

TIMER_FONT = ("Arial", 18, "bold")
TIMER_COLOR = "#ffffff"
TIMER_OUTLINE_COLOR = "#000000"

NAME_FONT = ("Arial", 9)
NAME_COLOR = "#cccccc"

COOLDOWN_LEVELS = [0, 1, 2]
DEFAULT_LEVEL = 0

NUM_SLOTS = 5

READY_COLOR = "#27ae60"
COOLDOWN_COLOR = "#e67e22"

READY_BORDER_COLOR = "#27ae60"
WARNING_BORDER_COLOR = "#f39c12"
ACTIVE_BORDER_COLOR = "#e74c3c"
WARNING_THRESHOLD = 10
PULSE_SPEED = 250
PULSE_DURATION = 5

MENU_BUTTON_HOVER_COLOR = "#aaaaaa"

CHAMPIONS_DATA_PATH = get_resource_path("data/champions_ult_cooldowns.json")
ICONS_DIR = get_resource_path("data/champion_icons")

SUMMONER_SPELLS_DATA_PATH = get_resource_path("data/summoner_spells_cooldowns.json")
SUMMONER_SPELLS_DIR = get_resource_path("data/summoner spells")

SOUND_FILE_PATH = get_resource_path("data/ult_ready.wav")
SOUND_ALERT_THRESHOLD = 1
SOUND_ENABLED = True
SOUND_VOLUME = 1.0

SETTINGS_BUTTON_SIZE = 24
SETTINGS_BUTTON_COLOR = "#888888"

CLOSE_BUTTON_SIZE = 24
CLOSE_BUTTON_COLOR = "#888888"

DEBUG_MODE = False
DEBUG_COOLDOWN = 10

UI_SCALE = 1.1
UI_SCALE_MIN = 0.5
UI_SCALE_MAX = 2.0
UI_SCALE_STEP = 0.1

DEFAULT_POSITION = {'x': 848, 'y': 730}
DEFAULT_LOCKED = False

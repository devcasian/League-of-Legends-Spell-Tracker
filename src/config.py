"""
Configuration settings for the League of Legends overlay.

This module contains all configurable parameters for the overlay application,
including visual settings, UI colors, and file paths.
"""

OVERLAY_ALPHA = 0.95
OVERLAY_BG_COLOR = "#0a0a0a"
BORDER_COLOR = "#2a2a2a"

ICON_SIZE = 64
SLOT_SPACING = 5

SUMMONER_SPELL_SIZE = 30
SUMMONER_SPELL_SPACING = 2

LAYOUT = "vertical"

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

CHAMPIONS_DATA_PATH = "data/champions_ult_cooldowns.json"
ICONS_DIR = "data/champion_icons"

SUMMONER_SPELLS_DATA_PATH = "data/summoner_spells_cooldowns.json"
SUMMONER_SPELLS_DIR = "data/summoner spells"
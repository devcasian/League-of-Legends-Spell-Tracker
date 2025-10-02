"""
Ability Haste calculation module for League of Legends.

This module provides functions to calculate effective cooldowns based on
ability haste, summoner spell haste, and ultimate ability haste.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any


COSMIC_INSIGHT_ID = 8347
COSMIC_INSIGHT_SUMMONER_HASTE = 18

_ITEMS_DATA = None


def _load_items_data():
    global _ITEMS_DATA
    if _ITEMS_DATA is None:
        try:
            base_path = Path(__file__).parent.parent
            items_file = base_path / "data" / "game_data" / "items_haste.json"
            with open(items_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                _ITEMS_DATA = {int(k): v for k, v in data.items()}
        except Exception as e:
            print(f"Error loading items data: {e}")
            _ITEMS_DATA = {}
    return _ITEMS_DATA


def calculate_summoner_spell_haste(items: List[int], runes: List[int]) -> int:
    """
    Calculate total summoner spell haste from items and runes.

    Args:
        items: List of item IDs
        runes: List of rune IDs

    Returns:
        Total summoner spell haste value
    """
    items_data = _load_items_data()
    total_haste = 0

    for item_id in items:
        if item_id in items_data:
            total_haste += items_data[item_id].get("summoner_haste", 0)

    if COSMIC_INSIGHT_ID in runes:
        total_haste += COSMIC_INSIGHT_SUMMONER_HASTE

    return total_haste


def calculate_ability_haste_from_items(items: List[int]) -> int:
    """
    Calculate total ability haste from items.

    Args:
        items: List of item IDs

    Returns:
        Total ability haste value from items
    """
    items_data = _load_items_data()
    total_haste = 0

    for item_id in items:
        if item_id in items_data:
            total_haste += items_data[item_id].get("ability_haste", 0)

    return total_haste


def calculate_ultimate_haste_from_items(items: List[int]) -> int:
    """
    Calculate additional ultimate ability haste from items only.

    Args:
        items: List of item IDs

    Returns:
        Additional ultimate ability haste value from items
    """
    items_data = _load_items_data()
    total_haste = 0

    for item_id in items:
        if item_id in items_data:
            total_haste += items_data[item_id].get("ultimate_haste", 0)

    return total_haste


def apply_haste(base_cooldown: float, haste: int) -> float:
    """
    Apply haste to a base cooldown using the League of Legends formula.

    Formula: Effective CD = Base CD / (1 + Haste / 100)

    Args:
        base_cooldown: Base cooldown in seconds
        haste: Total haste value

    Returns:
        Effective cooldown in seconds after applying haste
    """
    if haste <= 0:
        return base_cooldown

    return base_cooldown / (1 + haste / 100)

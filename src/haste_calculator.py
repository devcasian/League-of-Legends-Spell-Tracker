"""
Ability Haste calculation module for League of Legends.

This module provides functions to calculate effective cooldowns based on
ability haste, summoner spell haste, and ultimate ability haste.
"""

from typing import List, Dict, Any


IONIAN_BOOTS_ID = 3158
IONIAN_BOOTS_SUMMONER_HASTE = 12

COSMIC_INSIGHT_ID = 8347
COSMIC_INSIGHT_SUMMONER_HASTE = 18

EXPERIMENTAL_HEXPLATE_ID = 3084
EXPERIMENTAL_HEXPLATE_ULTIMATE_HASTE = 30

MALIGNANCE_ID = 3118
MALIGNANCE_ULTIMATE_HASTE = 20


def calculate_summoner_spell_haste(items: List[int], runes: List[int]) -> int:
    """
    Calculate total summoner spell haste from items and runes.

    Args:
        items: List of item IDs
        runes: List of rune IDs

    Returns:
        Total summoner spell haste value
    """
    total_haste = 0

    if IONIAN_BOOTS_ID in items:
        total_haste += IONIAN_BOOTS_SUMMONER_HASTE

    if COSMIC_INSIGHT_ID in runes:
        total_haste += COSMIC_INSIGHT_SUMMONER_HASTE

    return total_haste


def calculate_ultimate_haste(ability_haste: float, items: List[int]) -> int:
    """
    Calculate additional ultimate ability haste from items only.

    Args:
        ability_haste: Base ability haste from champion stats (not used, for future)
        items: List of item IDs

    Returns:
        Additional ultimate ability haste value from items
    """
    total_haste = 0

    if EXPERIMENTAL_HEXPLATE_ID in items:
        total_haste += EXPERIMENTAL_HEXPLATE_ULTIMATE_HASTE

    if MALIGNANCE_ID in items:
        total_haste += MALIGNANCE_ULTIMATE_HASTE

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

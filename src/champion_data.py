"""
Champion data loader for League of Legends overlay.

This module handles loading champion ultimate cooldown data from JSON
and provides utilities for accessing champion icons.
"""

import json
import os
from typing import Dict, List, Optional
from config import CHAMPIONS_DATA_PATH, CHAMPION_ULT_ICONS_DIR, CHAMPION_ICONS_DIR, SUMMONER_SPELLS_DATA_PATH, SUMMONER_SPELLS_DIR, DEBUG_MODE, DEBUG_COOLDOWN


class ChampionData:
    """
    Manages champion cooldown data and icon paths.

    Loads champion ultimate cooldown data from JSON file and provides
    methods to access cooldowns and icon file paths for all champions.
    """

    def __init__(self):
        self.cooldowns: Dict[str, List[float]] = {}
        self.champions: List[str] = []
        self.use_champion_icons = False
        self._load_data()

    def _load_data(self):
        try:
            with open(CHAMPIONS_DATA_PATH, 'r', encoding='utf-8') as f:
                self.cooldowns = json.load(f)

            self.champions = sorted([
                champ for champ, cd in self.cooldowns.items()
                if cd is not None
            ])

            print(f"Loaded {len(self.champions)} champions")
        except FileNotFoundError:
            print(f"Error: {CHAMPIONS_DATA_PATH} not found")
            self.champions = []
        except json.JSONDecodeError:
            print(f"Error: Failed to parse {CHAMPIONS_DATA_PATH}")
            self.champions = []

    def get_cooldown(self, champion: str, level: int = 0) -> Optional[float]:
        cooldowns = self.cooldowns.get(champion)
        if cooldowns is None or level >= len(cooldowns):
            return None
        return cooldowns[level]

    def get_all_cooldowns(self, champion: str) -> Optional[List[float]]:
        if DEBUG_MODE:
            return [DEBUG_COOLDOWN, DEBUG_COOLDOWN, DEBUG_COOLDOWN]
        return self.cooldowns.get(champion)

    def set_icon_type(self, use_champion_icons: bool):
        self.use_champion_icons = use_champion_icons

    def get_icon_path(self, champion: str) -> Optional[str]:
        icon_name = champion.replace(" ", "").replace("'", "").replace(".", "").replace("&", "")

        champion_icon_mapping = {
            "NunuWillump": "Nunu",
            "RenataGlasc": "Renata",
            "Wukong": "MonkeyKing",
        }

        ult_icon_mapping = {
            "NunuWillump": "Nunu&Willump",
        }

        if self.use_champion_icons:
            icons_dir = CHAMPION_ICONS_DIR
            icon_filename = champion_icon_mapping.get(icon_name, icon_name)
            icon_path = os.path.join(icons_dir, f"{icon_filename}.png")

            if os.path.exists(icon_path):
                return icon_path

            icon_path_alt = os.path.join(icons_dir, f"{champion.replace(' ', '')}.png")
            if os.path.exists(icon_path_alt):
                return icon_path_alt
        else:
            icons_dir = CHAMPION_ULT_ICONS_DIR
            icon_filename = ult_icon_mapping.get(icon_name, icon_name)
            icon_path = os.path.join(icons_dir, f"{icon_filename}_r.png")

            if os.path.exists(icon_path):
                return icon_path

            icon_path_alt = os.path.join(icons_dir, f"{champion.replace(' ', '')}_r.png")
            if os.path.exists(icon_path_alt):
                return icon_path_alt

        return None

    def get_champion_list(self) -> List[str]:
        return self.champions.copy()


class SummonerSpellData:
    """
    Manages summoner spell cooldown data and icon paths.

    Loads summoner spell cooldown data from JSON file and provides
    methods to access cooldowns and icon file paths for all summoner spells.
    """

    def __init__(self):
        self.cooldowns: Dict[str, float] = {}
        self.spells: List[str] = []
        self._load_data()

    def _load_data(self):
        try:
            with open(SUMMONER_SPELLS_DATA_PATH, 'r', encoding='utf-8') as f:
                self.cooldowns = json.load(f)

            self.spells = sorted([
                spell for spell, cd in self.cooldowns.items()
                if cd is not None
            ])

            print(f"Loaded {len(self.spells)} summoner spells")
        except FileNotFoundError:
            print(f"Error: {SUMMONER_SPELLS_DATA_PATH} not found")
            self.spells = []
        except json.JSONDecodeError:
            print(f"Error: Failed to parse {SUMMONER_SPELLS_DATA_PATH}")
            self.spells = []

    def get_cooldown(self, spell: str) -> Optional[float]:
        if DEBUG_MODE:
            return DEBUG_COOLDOWN
        return self.cooldowns.get(spell)

    def get_icon_path(self, spell: str) -> Optional[str]:
        icon_path = os.path.join(SUMMONER_SPELLS_DIR, f"{spell}.png")
        if os.path.exists(icon_path):
            return icon_path
        return None

    def get_spell_list(self) -> List[str]:
        return self.spells.copy()


champion_data = ChampionData()
summoner_spell_data = SummonerSpellData()
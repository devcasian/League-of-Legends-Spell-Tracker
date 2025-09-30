"""
Champion data loader for League of Legends overlay.

This module handles loading champion ultimate cooldown data from JSON
and provides utilities for accessing champion icons.
"""

import json
import os
from typing import Dict, List, Optional
from config import CHAMPIONS_DATA_PATH, ICONS_DIR


class ChampionData:
    """
    Manages champion cooldown data and icon paths.

    Loads champion ultimate cooldown data from JSON file and provides
    methods to access cooldowns and icon file paths for all champions.
    """

    def __init__(self):
        self.cooldowns: Dict[str, List[float]] = {}
        self.champions: List[str] = []
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
        return self.cooldowns.get(champion)

    def get_icon_path(self, champion: str) -> Optional[str]:
        icon_name = champion.replace(" ", "").replace("'", "").replace(".", "")

        icon_mapping = {
            "AurelionSol": "AurelionSol",
            "BelVeth": "BelVeth",
            "ChoGath": "ChoGath",
            "DrMundo": "DrMundo",
            "JarvanIV": "JarvanIV",
            "KSante": "KSante",
            "KaiSa": "KaiSa",
            "KhaZix": "KhaZix",
            "KogMaw": "KogMaw",
            "LeeSin": "LeeSin",
            "MasterYi": "MasterYi",
            "MissFortune": "MissFortune",
            "NunuWillump": "NunuWillump",
            "RekSai": "RekSai",
            "RenataGlasc": "RenataGlasc",
            "TahmKench": "TahmKench",
            "TwistedFate": "TwistedFate",
            "VelKoz": "VelKoz",
            "XinZhao": "XinZhao",
        }

        icon_filename = icon_mapping.get(icon_name, icon_name)
        icon_path = os.path.join(ICONS_DIR, f"{icon_filename}_r.png")

        if os.path.exists(icon_path):
            return icon_path

        icon_path_alt = os.path.join(ICONS_DIR, f"{champion.replace(' ', '')}_r.png")
        if os.path.exists(icon_path_alt):
            return icon_path_alt

        return None

    def get_champion_list(self) -> List[str]:
        return self.champions.copy()


champion_data = ChampionData()
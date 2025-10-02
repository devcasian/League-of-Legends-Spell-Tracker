"""
Automatic game data loader for League of Legends overlay.

This module monitors the League of Legends client for active games and
automatically populates the overlay with enemy team information.
"""

import threading
import time
from typing import Callable, Optional, List, Dict, Any
from live_client_api import LiveClientAPI
from champion_data import champion_data


class GameAutoLoader:
    """
    Monitors League of Legends client and auto-loads enemy team data.

    Periodically checks if a game is active and provides callbacks
    with parsed enemy team information (champions and summoner spells).
    """

    def __init__(self, poll_interval: float = 3.0):
        self.api = LiveClientAPI()
        self.poll_interval = poll_interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.on_game_start: Optional[Callable[[List[Dict[str, Any]]], None]] = None
        self.on_game_end: Optional[Callable[[], None]] = None
        self.game_active = False

    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.api.close()

    def _monitor_loop(self):
        while self.running:
            try:
                is_active = self.api.is_game_active()

                if is_active and not self.game_active:
                    self._handle_game_start()
                elif not is_active and self.game_active:
                    self._handle_game_end()

                time.sleep(self.poll_interval)
            except Exception as e:
                print(f"Auto-loader error: {e}")
                time.sleep(self.poll_interval)

    def _handle_game_start(self):
        self.game_active = True
        print("Game detected - loading enemy team...")

        enemy_team = self.api.get_enemy_team()
        if enemy_team and self.on_game_start:
            parsed_data = self._parse_enemy_team(enemy_team)
            self.on_game_start(parsed_data)

    def _handle_game_end(self):
        self.game_active = False
        print("Game ended")

        if self.on_game_end:
            self.on_game_end()

    def _parse_enemy_team(self, enemy_team: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        parsed = []

        for player in enemy_team:
            champion_name_raw = player.get("championName", "")
            champion_name = self._normalize_champion_name(champion_name_raw)
            summoner_spells = player.get("summonerSpells", {})

            spell1_name = summoner_spells.get("summonerSpellOne", {}).get("displayName", "")
            spell2_name = summoner_spells.get("summonerSpellTwo", {}).get("displayName", "")

            spell1 = self._normalize_spell_name(spell1_name)
            spell2 = self._normalize_spell_name(spell2_name)

            parsed.append({
                "champion": champion_name,
                "spell1": spell1,
                "spell2": spell2
            })

        return parsed

    def _normalize_champion_name(self, api_name: str) -> str:
        all_champions = champion_data.get_champion_list()

        for champ in all_champions:
            if champ.lower().replace("'", "").replace(".", "").replace(" ", "").replace("&", "") == \
               api_name.lower().replace("'", "").replace(".", "").replace(" ", "").replace("&", ""):
                return champ

        return api_name

    def _normalize_spell_name(self, display_name: str) -> str:
        spell_mapping = {
            "Flash": "flash",
            "Ignite": "ignite",
            "Teleport": "teleport",
            "Unleashed Teleport": "teleport",
            "Heal": "heal",
            "Barrier": "barrier",
            "Exhaust": "exhaust",
            "Smite": "smite",
            "Ghost": "ghost",
            "Cleanse": "cleanse",
        }

        normalized = spell_mapping.get(display_name, display_name.lower())
        if normalized != display_name.lower():
            print(f"Spell mapping: '{display_name}' -> '{normalized}'")
        else:
            print(f"Warning: Unknown spell '{display_name}', using '{normalized}'")
        return normalized

    def set_callbacks(self,
                     on_game_start: Optional[Callable[[List[Dict[str, Any]]], None]] = None,
                     on_game_end: Optional[Callable[[], None]] = None):
        self.on_game_start = on_game_start
        self.on_game_end = on_game_end

    def force_reload(self):
        if self.api.is_game_active():
            enemy_team = self.api.get_enemy_team()
            if enemy_team and self.on_game_start:
                parsed_data = self._parse_enemy_team(enemy_team)
                self.on_game_start(parsed_data)
                return True
        return False

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
from haste_calculator import calculate_summoner_spell_haste, calculate_ability_haste_from_items, calculate_ultimate_haste_from_items


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
        self.on_level_update: Optional[Callable[[List[Dict[str, Any]]], None]] = None
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
                elif is_active and self.game_active:
                    self._handle_level_update()

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

    def _handle_level_update(self):
        enemy_team = self.api.get_enemy_team()
        if enemy_team and self.on_level_update:
            sorted_enemy_team = self._sort_by_position(enemy_team)
            levels_data = []
            for player in sorted_enemy_team:
                player_level = player.get("level", 1)
                summoner_name = player.get("summonerName", "")
                ult_level_index = self._get_ult_level_index(player_level)

                items = player.get("items", [])
                item_ids = [item.get("itemID", 0) for item in items if item.get("itemID")]

                champion_stats = self.api.get_player_stats(summoner_name)
                base_ability_haste = 0.0
                if champion_stats:
                    base_ability_haste = champion_stats.get("abilityHaste", 0.0)

                items_ability_haste = calculate_ability_haste_from_items(item_ids)
                ability_haste = int(base_ability_haste) + items_ability_haste

                rune_ids = self.api.get_player_runes(summoner_name)

                summoner_haste = calculate_summoner_spell_haste(item_ids, rune_ids)
                ultimate_haste = calculate_ultimate_haste_from_items(item_ids)

                levels_data.append({
                    "level": ult_level_index,
                    "summoner_haste": summoner_haste,
                    "ability_haste": int(ability_haste),
                    "ultimate_haste": ultimate_haste
                })
            self.on_level_update(levels_data)

    def _parse_enemy_team(self, enemy_team: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sorted_enemy_team = self._sort_by_position(enemy_team)
        parsed = []

        for player in sorted_enemy_team:
            champion_name_raw = player.get("championName", "")
            champion_name = self._normalize_champion_name(champion_name_raw)
            player_level = player.get("level", 1)
            summoner_name = player.get("summonerName", "")
            summoner_spells = player.get("summonerSpells", {})

            spell1_name = summoner_spells.get("summonerSpellOne", {}).get("displayName", "")
            spell2_name = summoner_spells.get("summonerSpellTwo", {}).get("displayName", "")

            spell1 = self._normalize_spell_name(spell1_name)
            spell2 = self._normalize_spell_name(spell2_name)

            ult_level_index = self._get_ult_level_index(player_level)

            items = player.get("items", [])
            item_ids = [item.get("itemID", 0) for item in items if item.get("itemID")]

            champion_stats = self.api.get_player_stats(summoner_name)
            base_ability_haste = 0.0
            if champion_stats:
                base_ability_haste = champion_stats.get("abilityHaste", 0.0)

            items_ability_haste = calculate_ability_haste_from_items(item_ids)
            ability_haste = int(base_ability_haste) + items_ability_haste

            rune_ids = self.api.get_player_runes(summoner_name)

            summoner_haste = calculate_summoner_spell_haste(item_ids, rune_ids)
            ultimate_haste = calculate_ultimate_haste_from_items(item_ids)

            parsed.append({
                "champion": champion_name,
                "spell1": spell1,
                "spell2": spell2,
                "level": ult_level_index,
                "summoner_haste": summoner_haste,
                "ability_haste": int(ability_haste),
                "ultimate_haste": ultimate_haste
            })

        return parsed

    def _sort_by_position(self, team: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        has_positions = any(player.get("position", "").strip() for player in team)
        if not has_positions:
            print("⚠️ No position data available, skipping sort")
            return team

        position_order = {
            "TOP": 0,
            "JUNGLE": 1,
            "MIDDLE": 2,
            "MID": 2,
            "BOTTOM": 3,
            "BOT": 3,
            "ADC": 3,
            "UTILITY": 4,
            "SUPPORT": 4
        }

        def get_position_priority(player: Dict[str, Any]) -> int:
            position = player.get("position", "").upper()
            return position_order.get(position, 999)

        return sorted(team, key=get_position_priority)

    def _normalize_champion_name(self, api_name: str) -> str:
        all_champions = champion_data.get_champion_list()

        for champ in all_champions:
            if champ.lower().replace("'", "").replace(".", "").replace(" ", "").replace("&", "") == \
               api_name.lower().replace("'", "").replace(".", "").replace(" ", "").replace("&", ""):
                return champ

        return api_name

    def _get_ult_level_index(self, player_level: int) -> int:
        if player_level >= 16:
            return 2
        elif player_level >= 11:
            return 1
        elif player_level >= 6:
            return 0
        else:
            return -1

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
            "Unleashed Smite": "smite",
            "Primal Smite": "smite",
            "Ghost": "ghost",
            "Cleanse": "cleanse",
        }

        result = spell_mapping.get(display_name, display_name.lower())
        if display_name and display_name not in spell_mapping:
            print(f"⚠️ Unknown spell from API: '{display_name}' (mapped to '{result}')")
        return result

    def set_callbacks(self,
                     on_game_start: Optional[Callable[[List[Dict[str, Any]]], None]] = None,
                     on_game_end: Optional[Callable[[], None]] = None,
                     on_level_update: Optional[Callable[[List[Dict[str, Any]]], None]] = None):
        self.on_game_start = on_game_start
        self.on_game_end = on_game_end
        self.on_level_update = on_level_update

    def force_reload(self):
        if self.api.is_game_active():
            enemy_team = self.api.get_enemy_team()
            if enemy_team and self.on_game_start:
                parsed_data = self._parse_enemy_team(enemy_team)
                self.on_game_start(parsed_data)
                return True
        return False

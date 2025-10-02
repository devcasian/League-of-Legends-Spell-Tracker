"""
Live Client Data API integration for League of Legends.

This module provides access to the League of Legends Live Client Data API
which runs locally during active games at https://127.0.0.1:2999.
"""

import requests
import urllib3
from typing import Optional, Dict, List, Any

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LiveClientAPI:
    """
    Interface to League of Legends Live Client Data API.

    Provides methods to query game state and player information during
    an active League of Legends match.
    """

    BASE_URL = "https://127.0.0.1:2999/liveclientdata"

    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False

    def is_game_active(self) -> bool:
        try:
            response = self.session.get(
                f"{self.BASE_URL}/gamestats",
                timeout=2
            )
            return response.status_code == 200
        except (requests.exceptions.RequestException, Exception):
            return False

    def get_all_game_data(self) -> Optional[Dict[str, Any]]:
        try:
            response = self.session.get(
                f"{self.BASE_URL}/allgamedata",
                timeout=3
            )
            if response.status_code == 200:
                return response.json()
            return None
        except (requests.exceptions.RequestException, Exception):
            return None

    def get_all_players(self) -> Optional[List[Dict[str, Any]]]:
        data = self.get_all_game_data()
        if data and "allPlayers" in data:
            return data["allPlayers"]
        return None

    def get_active_player(self) -> Optional[Dict[str, Any]]:
        data = self.get_all_game_data()
        if data and "activePlayer" in data:
            return data["activePlayer"]
        return None

    def get_player_team(self) -> Optional[str]:
        players = self.get_all_players()
        if not players:
            return None

        active_player_data = self.get_active_player()
        if not active_player_data:
            return None

        active_summoner = active_player_data.get("summonerName")
        if not active_summoner:
            return None

        for player in players:
            if player.get("summonerName") == active_summoner:
                return player.get("team")

        return None

    def get_enemy_team(self) -> List[Dict[str, Any]]:
        players = self.get_all_players()
        if not players:
            return []

        player_team = self.get_player_team()
        if not player_team:
            return []

        enemy_team = [
            player for player in players
            if player.get("team") != player_team
        ]

        return enemy_team

    def get_own_player(self) -> List[Dict[str, Any]]:
        players = self.get_all_players()
        if not players:
            return []

        active_player_data = self.get_active_player()
        if not active_player_data:
            return []

        active_summoner = active_player_data.get("summonerName")
        if not active_summoner:
            return []

        own_player = [
            player for player in players
            if player.get("summonerName") == active_summoner
        ]

        return own_player

    def get_player_stats(self, summoner_name: str) -> Optional[Dict[str, Any]]:
        data = self.get_all_game_data()
        if not data:
            return None

        active_player = data.get("activePlayer", {})
        active_summoner = active_player.get("summonerName")

        if active_summoner == summoner_name:
            return active_player.get("championStats", {})

        return None

    def get_player_items(self, summoner_name: str) -> List[int]:
        data = self.get_all_game_data()
        if not data or "allPlayers" not in data:
            return []

        for player in data["allPlayers"]:
            if player.get("summonerName") == summoner_name:
                items = player.get("items", [])
                return [item.get("itemID", 0) for item in items if item.get("itemID")]

        return []

    def get_player_runes(self, summoner_name: str) -> List[int]:
        data = self.get_all_game_data()
        if not data or "allPlayers" not in data:
            return []

        for player in data["allPlayers"]:
            if player.get("summonerName") == summoner_name:
                rune_ids = []

                full_runes = player.get("fullRunes", {})
                general_runes = full_runes.get("generalRunes", [])
                for rune in general_runes:
                    rune_id = rune.get("id")
                    if rune_id:
                        rune_ids.append(rune_id)

                return rune_ids

        return []

    def close(self):
        self.session.close()

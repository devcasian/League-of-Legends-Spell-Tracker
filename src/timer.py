"""
Timer logic for tracking champion ultimate cooldowns.

This module provides timer classes for managing cooldown tracking
of champion ultimate abilities at different levels.
"""

import time
from typing import Optional, Callable
from haste_calculator import apply_haste


class CooldownTimer:
    """
    Manages a single champion's ultimate cooldown timer.

    Tracks cooldown state, remaining time, and level progression
    for a champion's ultimate ability.
    """

    def __init__(self, champion: str, cooldowns: list[float], level: int = 0, on_ready_callback: Optional[Callable] = None, alert_threshold: int = 4, ability_haste: int = 0, ultimate_haste: int = 0):
        self.champion = champion
        self.cooldowns = cooldowns
        self.level = level
        self.start_time: Optional[float] = None
        self.is_active = False
        self.was_ready = True
        self.sound_played = False
        self.on_ready_callback = on_ready_callback
        self.alert_threshold = alert_threshold
        self.ability_haste = ability_haste
        self.ultimate_haste = ultimate_haste

    def start(self):
        if not self.is_active and self.cooldowns:
            self.start_time = time.time()
            self.is_active = True
            self.was_ready = False
            self.sound_played = False

    def reset(self):
        self.start_time = None
        self.is_active = False
        self.sound_played = False

    def get_current_cooldown(self) -> float:
        if not self.cooldowns or self.level >= len(self.cooldowns):
            return 0.0
        base_cd = self.cooldowns[self.level]
        total_haste = self.ability_haste + self.ultimate_haste
        return apply_haste(base_cd, total_haste)

    def get_remaining_time(self) -> float:
        if not self.is_active or self.start_time is None:
            return 0.0

        elapsed = time.time() - self.start_time
        cooldown = self.get_current_cooldown()
        remaining = cooldown - elapsed

        if remaining <= self.alert_threshold and not self.sound_played and self.on_ready_callback:
            self.on_ready_callback()
            self.sound_played = True

        if remaining <= 0:
            self.reset()
            self.was_ready = True
            return 0.0

        return remaining

    def is_ready(self) -> bool:
        return not self.is_active or self.get_remaining_time() <= 0

    def set_level(self, level: int):
        if 0 <= level < len(self.cooldowns):
            self.level = level

    def increment_level(self):
        self.level = (self.level + 1) % min(3, len(self.cooldowns))

    def update_haste(self, ability_haste: int, ultimate_haste: int):
        if not self.is_active or self.start_time is None:
            self.ability_haste = ability_haste
            self.ultimate_haste = ultimate_haste
            return

        old_cooldown = self.get_current_cooldown()
        if old_cooldown <= 0:
            self.ability_haste = ability_haste
            self.ultimate_haste = ultimate_haste
            return

        elapsed = time.time() - self.start_time
        progress = elapsed / old_cooldown

        self.ability_haste = ability_haste
        self.ultimate_haste = ultimate_haste

        new_cooldown = self.get_current_cooldown()
        new_elapsed = new_cooldown * progress
        self.start_time = time.time() - new_elapsed

    def format_time(self) -> str:
        if self.is_ready():
            return "Ready"

        remaining = self.get_remaining_time()

        if remaining >= 60:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            return f"{minutes}:{seconds:02d}"
        else:
            return f"{int(remaining)}"


class SummonerSpellTimer:
    """
    Manages a single summoner spell cooldown timer.

    Tracks cooldown state and remaining time for a summoner spell.
    """

    def __init__(self, spell: str, cooldown: float, summoner_haste: int = 0):
        self.spell = spell
        self.cooldown = cooldown
        self.summoner_haste = summoner_haste
        self.start_time: Optional[float] = None
        self.is_active = False

    def start(self):
        if not self.is_active:
            self.start_time = time.time()
            self.is_active = True

    def reset(self):
        self.start_time = None
        self.is_active = False

    def get_remaining_time(self) -> float:
        if not self.is_active or self.start_time is None:
            return 0.0

        elapsed = time.time() - self.start_time
        effective_cd = apply_haste(self.cooldown, self.summoner_haste)
        remaining = effective_cd - elapsed

        if remaining <= 0:
            self.reset()
            return 0.0

        return remaining

    def is_ready(self) -> bool:
        return not self.is_active or self.get_remaining_time() <= 0

    def update_haste(self, summoner_haste: int):
        if not self.is_active or self.start_time is None:
            self.summoner_haste = summoner_haste
            return

        old_cooldown = apply_haste(self.cooldown, self.summoner_haste)
        if old_cooldown <= 0:
            self.summoner_haste = summoner_haste
            return

        elapsed = time.time() - self.start_time
        progress = elapsed / old_cooldown

        self.summoner_haste = summoner_haste

        new_cooldown = apply_haste(self.cooldown, self.summoner_haste)
        new_elapsed = new_cooldown * progress
        self.start_time = time.time() - new_elapsed

    def format_time(self) -> str:
        if self.is_ready():
            return "Ready"

        remaining = self.get_remaining_time()

        if remaining >= 60:
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            return f"{minutes}:{seconds:02d}"
        else:
            return f"{int(remaining)}"


class TimerManager:
    """Manages multiple champion timers."""

    def __init__(self):
        self.timers: dict[int, Optional[CooldownTimer]] = {}
        self.summoner_spell_timers: dict[tuple[int, int], Optional[SummonerSpellTimer]] = {}
        self.update_callbacks: list[Callable] = []

    def create_timer(self, slot: int, champion: str, cooldowns: list[float], level: int = 0, on_ready_callback: Optional[Callable] = None, alert_threshold: int = 4, ability_haste: int = 0, ultimate_haste: int = 0):
        self.timers[slot] = CooldownTimer(champion, cooldowns, level, on_ready_callback, alert_threshold, ability_haste, ultimate_haste)

    def remove_timer(self, slot: int):
        if slot in self.timers:
            del self.timers[slot]

    def get_timer(self, slot: int) -> Optional[CooldownTimer]:
        return self.timers.get(slot)

    def start_timer(self, slot: int):
        timer = self.get_timer(slot)
        if timer:
            timer.start()
            self._notify_update()

    def reset_timer(self, slot: int):
        timer = self.get_timer(slot)
        if timer:
            timer.reset()
            self._notify_update()

    def set_level(self, slot: int, level: int):
        timer = self.get_timer(slot)
        if timer:
            timer.set_level(level)
            self._notify_update()

    def increment_level(self, slot: int):
        timer = self.get_timer(slot)
        if timer:
            timer.increment_level()
            self._notify_update()

    def register_update_callback(self, callback: Callable):
        self.update_callbacks.append(callback)

    def _notify_update(self):
        for callback in self.update_callbacks:
            callback()

    def update(self):
        self._notify_update()

    def create_summoner_spell_timer(self, slot: int, spell_slot: int, spell: str, cooldown: float, summoner_haste: int = 0):
        self.summoner_spell_timers[(slot, spell_slot)] = SummonerSpellTimer(spell, cooldown, summoner_haste)

    def remove_summoner_spell_timer(self, slot: int, spell_slot: int):
        key = (slot, spell_slot)
        if key in self.summoner_spell_timers:
            del self.summoner_spell_timers[key]

    def get_summoner_spell_timer(self, slot: int, spell_slot: int) -> Optional[SummonerSpellTimer]:
        return self.summoner_spell_timers.get((slot, spell_slot))

    def start_summoner_spell_timer(self, slot: int, spell_slot: int):
        timer = self.get_summoner_spell_timer(slot, spell_slot)
        if timer:
            timer.start()
            self._notify_update()

    def reset_summoner_spell_timer(self, slot: int, spell_slot: int):
        timer = self.get_summoner_spell_timer(slot, spell_slot)
        if timer:
            timer.reset()
            self._notify_update()
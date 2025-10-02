"""
Main overlay application for League of Legends ultimate cooldown tracking.

This module provides the GUI overlay application for tracking enemy
ultimate cooldowns in League of Legends matches.
"""

import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageEnhance
import os
import pygame
import random
import threading
import pystray
from pystray import MenuItem as item

from config import *
from config import get_resource_path
from champion_data import champion_data, summoner_spell_data
from timer import TimerManager
from settings import load_settings, save_settings
from auto_loader import GameAutoLoader


def apply_ui_scale(scale):
    """Apply UI scale to all size-related constants."""
    global ICON_SIZE, SUMMONER_SPELL_SIZE, SLOT_SPACING, SUMMONER_SPELL_SPACING
    global EMPTY_SLOT_BORDER_WIDTH, LAYOUT_TOGGLE_SIZE, PIN_BUTTON_SIZE, LOCK_BUTTON_SIZE, SETTINGS_BUTTON_SIZE, CLOSE_BUTTON_SIZE
    global NAME_FONT, TIMER_FONT

    ICON_SIZE = int(64 * scale)
    SUMMONER_SPELL_SIZE = int(30 * scale)
    SLOT_SPACING = int(5 * scale)
    SUMMONER_SPELL_SPACING = int(2 * scale)
    EMPTY_SLOT_BORDER_WIDTH = max(1, int(1 * scale))

    LAYOUT_TOGGLE_SIZE = int(24 * scale)
    PIN_BUTTON_SIZE = int(24 * scale)
    LOCK_BUTTON_SIZE = int(24 * scale)
    SETTINGS_BUTTON_SIZE = int(24 * scale)
    CLOSE_BUTTON_SIZE = int(24 * scale)

    name_font_size = max(6, int(9 * scale))
    timer_font_size = max(10, int(18 * scale))
    NAME_FONT = ("Arial", name_font_size)
    TIMER_FONT = ("Arial", timer_font_size, "bold")


class ToolTip:
    """Tooltip widget for displaying hints on hover."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.scheduled_show = None

    def show(self, event=None):
        if self.scheduled_show:
            self.widget.after_cancel(self.scheduled_show)

        self.scheduled_show = self.widget.after(500, self._show_tooltip)

    def hide(self, event=None):
        if self.scheduled_show:
            self.widget.after_cancel(self.scheduled_show)
            self.scheduled_show = None

        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def _show_tooltip(self):
        if self.tooltip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes("-topmost", True)

        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#2a2a2a",
            foreground="#ffffff",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Arial", 9),
            padx=8,
            pady=4
        )
        label.pack()


class SummonerSpellSlot(tk.Frame):
    """Widget representing a single summoner spell slot with icon and timer overlay."""

    def __init__(self, parent, slot_id: int, spell_slot: int, timer_manager: TimerManager, app):
        super().__init__(parent, bg=OVERLAY_BG_COLOR)
        self.slot_id = slot_id
        self.spell_slot = spell_slot
        self.timer_manager = timer_manager
        self.app = app
        self.spell = None
        self.base_image = None
        self.photo_image = None
        self.on_double_click_callback = None
        self.timer_was_used = False

        self.canvas = tk.Canvas(
            self,
            width=SUMMONER_SPELL_SIZE,
            height=SUMMONER_SPELL_SIZE,
            bg=OVERLAY_BG_COLOR,
            highlightthickness=EMPTY_SLOT_BORDER_WIDTH,
            highlightbackground=EMPTY_SLOT_BORDER_COLOR
        )
        self.canvas.pack()

        self.canvas_image_id = None

        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)

    def clear(self):
        self.spell = None
        self.base_image = None
        self.photo_image = None
        self.timer_was_used = False

        if self.canvas_image_id:
            self.canvas.delete(self.canvas_image_id)
            self.canvas_image_id = None

        self.canvas.config(
            highlightthickness=EMPTY_SLOT_BORDER_WIDTH,
            highlightbackground=EMPTY_SLOT_BORDER_COLOR
        )

        self.timer_manager.remove_summoner_spell_timer(self.slot_id, self.spell_slot)

    def set_spell(self, spell_name: str):
        self.spell = spell_name

        icon_path = summoner_spell_data.get_icon_path(spell_name)
        if icon_path and os.path.exists(icon_path):
            try:
                img = Image.open(icon_path).convert("RGBA")
                img = img.resize((SUMMONER_SPELL_SIZE, SUMMONER_SPELL_SIZE), Image.Resampling.LANCZOS)
                self.base_image = img
                self.photo_image = ImageTk.PhotoImage(img)

                if self.canvas_image_id:
                    self.canvas.delete(self.canvas_image_id)
                self.canvas_image_id = self.canvas.create_image(
                    SUMMONER_SPELL_SIZE // 2, SUMMONER_SPELL_SIZE // 2,
                    image=self.photo_image
                )

                self.canvas.config(highlightthickness=0)
            except Exception as e:
                print(f"Error loading icon for {spell_name}: {e}")

        cooldown = summoner_spell_data.get_cooldown(spell_name)
        if cooldown:
            self.timer_manager.create_summoner_spell_timer(self.slot_id, self.spell_slot, spell_name, cooldown)

    def update_timer_display(self):
        if not self.base_image:
            return

        timer = self.timer_manager.get_summoner_spell_timer(self.slot_id, self.spell_slot)
        if not timer:
            return

        self._update_border(timer)

        img = self.base_image.copy()

        if not timer.is_ready():
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 150))
            img = Image.alpha_composite(img, overlay)

            draw = ImageDraw.Draw(img)

            remaining = timer.get_remaining_time()
            if remaining >= 60:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                text = f"{minutes}:{seconds:02d}"
            else:
                text = f"{int(remaining)}"

            try:
                font = ImageFont.truetype("arial.ttf", 12)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
                except:
                    font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (SUMMONER_SPELL_SIZE - text_width) // 2
            y = (SUMMONER_SPELL_SIZE - text_height) // 2

            outline_color = TIMER_OUTLINE_COLOR
            for adj_x in [-1, 0, 1]:
                for adj_y in [-1, 0, 1]:
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)

            draw.text((x, y), text, font=font, fill=COOLDOWN_COLOR)

        self.photo_image = ImageTk.PhotoImage(img)
        if self.canvas_image_id:
            self.canvas.itemconfig(self.canvas_image_id, image=self.photo_image)

    def _on_click(self, event):
        timer = self.timer_manager.get_summoner_spell_timer(self.slot_id, self.spell_slot)
        if timer:
            if timer.is_ready():
                self.timer_manager.start_summoner_spell_timer(self.slot_id, self.spell_slot)
                self.timer_was_used = True
            else:
                self.timer_manager.reset_summoner_spell_timer(self.slot_id, self.spell_slot)

    def _on_double_click(self, event):
        if self.app.locked or self.app.auto_load_enabled:
            return
        if self.on_double_click_callback:
            self.on_double_click_callback(self.slot_id, self.spell_slot)

    def _update_border(self, timer):
        if timer.is_ready():
            if self.timer_was_used:
                self.canvas.config(
                    highlightthickness=2,
                    highlightbackground=READY_BORDER_COLOR
                )
            else:
                self.canvas.config(
                    highlightthickness=2,
                    highlightbackground=READY_BORDER_COLOR
                )
        else:
            if timer.is_active:
                self.canvas.config(
                    highlightthickness=2,
                    highlightbackground=ACTIVE_BORDER_COLOR
                )
            else:
                self.canvas.config(
                    highlightthickness=0
                )


class ChampionSlot(tk.Frame):
    """Widget representing a single champion slot with icon and timer overlay."""

    def __init__(self, parent, slot_id: int, timer_manager: TimerManager, app):
        super().__init__(parent, bg=OVERLAY_BG_COLOR)
        self.slot_id = slot_id
        self.timer_manager = timer_manager
        self.app = app
        self.champion = None
        self.base_image = None
        self.photo_image = None
        self.summoner_spell_slots = {}
        self.timer_was_used = False
        self.ult_available = True

        self._create_widgets()

    def _create_widgets(self):
        self.name_label = tk.Label(
            self,
            text="Empty",
            font=NAME_FONT,
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            height=1
        )
        self.name_label.pack()

        if LAYOUT == "vertical":
            main_container = tk.Frame(self, bg=OVERLAY_BG_COLOR)
            main_container.pack()

            self.canvas = tk.Canvas(
                main_container,
                width=ICON_SIZE,
                height=ICON_SIZE,
                bg=OVERLAY_BG_COLOR,
                highlightthickness=EMPTY_SLOT_BORDER_WIDTH,
                highlightbackground=EMPTY_SLOT_BORDER_COLOR
            )
            self.canvas.pack(side=tk.LEFT)

            spells_container = tk.Frame(main_container, bg=OVERLAY_BG_COLOR)
            spells_container.pack(side=tk.LEFT, padx=(3, 0))

            for i in range(2):
                spell_slot = SummonerSpellSlot(spells_container, self.slot_id, i, self.timer_manager, self.app)
                spell_slot.pack(pady=(0, SUMMONER_SPELL_SPACING) if i == 0 else 0)
                spell_slot.on_double_click_callback = self.on_summoner_spell_double_click
                self.summoner_spell_slots[i] = spell_slot

            self.canvas_image_id = None
        else:
            self.canvas = tk.Canvas(
                self,
                width=ICON_SIZE,
                height=ICON_SIZE,
                bg=OVERLAY_BG_COLOR,
                highlightthickness=EMPTY_SLOT_BORDER_WIDTH,
                highlightbackground=EMPTY_SLOT_BORDER_COLOR
            )
            self.canvas.pack()

            self.canvas_image_id = None

            spells_container = tk.Frame(self, bg=OVERLAY_BG_COLOR)
            spells_container.pack(pady=(2, 0))

            for i in range(2):
                spell_slot = SummonerSpellSlot(spells_container, self.slot_id, i, self.timer_manager, self.app)
                spell_slot.pack(side=tk.LEFT, padx=(0, SUMMONER_SPELL_SPACING) if i == 0 else 0)
                spell_slot.on_double_click_callback = self.on_summoner_spell_double_click
                self.summoner_spell_slots[i] = spell_slot

        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)

    def on_summoner_spell_double_click(self, slot_id: int, spell_slot: int):
        if hasattr(self, 'on_summoner_spell_select_callback') and self.on_summoner_spell_select_callback:
            self.on_summoner_spell_select_callback(slot_id, spell_slot)

    def clear(self):
        self.champion = None
        self.base_image = None
        self.photo_image = None
        self.timer_was_used = False
        self.ult_available = True

        if self.canvas_image_id:
            self.canvas.delete(self.canvas_image_id)
            self.canvas_image_id = None

        self.canvas.config(
            highlightthickness=EMPTY_SLOT_BORDER_WIDTH,
            highlightbackground=EMPTY_SLOT_BORDER_COLOR
        )

        self.name_label.config(text="Empty")
        if self.app.show_champion_names:
            self.name_label.pack()
        else:
            self.name_label.pack_forget()

        for spell_slot in self.summoner_spell_slots.values():
            spell_slot.clear()

        self.timer_manager.remove_timer(self.slot_id)

    def set_champion(self, champion_name: str):
        self.champion = champion_name

        icon_path = champion_data.get_icon_path(champion_name)
        if icon_path and os.path.exists(icon_path):
            try:
                img = Image.open(icon_path).convert("RGBA")
                img = img.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.LANCZOS)
                self.base_image = img
                self.photo_image = ImageTk.PhotoImage(img)

                if self.canvas_image_id:
                    self.canvas.delete(self.canvas_image_id)
                self.canvas_image_id = self.canvas.create_image(
                    ICON_SIZE // 2, ICON_SIZE // 2,
                    image=self.photo_image
                )

                self.canvas.config(highlightthickness=0)
            except Exception as e:
                print(f"Error loading icon for {champion_name}: {e}")

        cooldowns = champion_data.get_all_cooldowns(champion_name)
        if cooldowns:
            self.timer_manager.create_timer(self.slot_id, champion_name, cooldowns, on_ready_callback=self.app._play_ready_sound, alert_threshold=self.app.sound_alert_threshold)

        self._update_level_display()

    def update_timer_display(self):
        if not self.base_image:
            return

        timer = self.timer_manager.get_timer(self.slot_id)
        if not timer:
            return

        self._update_border(timer)

        img = self.base_image.copy()

        if not self.ult_available:
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(0.2)
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 180))
            img = Image.alpha_composite(img, overlay)

        if not timer.is_ready():
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 150))
            img = Image.alpha_composite(img, overlay)

            draw = ImageDraw.Draw(img)

            remaining = timer.get_remaining_time()
            if remaining >= 60:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                text = f"{minutes}:{seconds:02d}"
            else:
                text = f"{int(remaining)}"

            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                except:
                    font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (ICON_SIZE - text_width) // 2
            y = (ICON_SIZE - text_height) // 2

            outline_color = TIMER_OUTLINE_COLOR
            for adj_x in [-1, 0, 1]:
                for adj_y in [-1, 0, 1]:
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)

            draw.text((x, y), text, font=font, fill=COOLDOWN_COLOR)

        self.photo_image = ImageTk.PhotoImage(img)
        if self.canvas_image_id:
            self.canvas.itemconfig(self.canvas_image_id, image=self.photo_image)

    def _on_click(self, event):
        if not self.ult_available:
            return
        timer = self.timer_manager.get_timer(self.slot_id)
        if timer:
            if timer.is_ready():
                self.timer_manager.start_timer(self.slot_id)
                self.timer_was_used = True
            else:
                self.timer_manager.reset_timer(self.slot_id)

    def _on_right_click(self, event):
        if self.app.auto_load_enabled:
            return
        timer = self.timer_manager.get_timer(self.slot_id)
        if timer:
            self.timer_manager.increment_level(self.slot_id)
            self._update_level_display()

    def _get_display_name_with_level(self):
        if not self.champion:
            return "Empty"

        timer = self.timer_manager.get_timer(self.slot_id)
        if not timer:
            return self.champion

        level_values = [6, 11, 16]
        level = level_values[timer.level] if timer.level < len(level_values) else 6

        display_name = self.champion
        max_length = 10

        if len(display_name) > max_length:
            display_name = display_name[:max_length - 1] + "."

        return f"{display_name} ({level})"

    def _update_level_display(self):
        if self.app.show_champion_names:
            display_name = self._get_display_name_with_level()
            self.name_label.config(text=display_name)
            self.name_label.pack()
        else:
            self.name_label.pack_forget()

    def set_ult_availability(self, available: bool):
        if not self.app.gray_low_level_icons:
            self.ult_available = True
        else:
            self.ult_available = available
        self.update_timer_display()

    def _on_double_click(self, event):
        if self.app.locked or self.app.auto_load_enabled:
            return
        if hasattr(self, 'on_double_click_callback') and self.on_double_click_callback:
            self.on_double_click_callback(self.slot_id)

    def update_summoner_spell_displays(self):
        for spell_slot in self.summoner_spell_slots.values():
            spell_slot.update_timer_display()

    def _update_border(self, timer):
        if not self.ult_available:
            self.canvas.config(
                highlightthickness=2,
                highlightbackground=EMPTY_SLOT_BORDER_COLOR
            )
            return

        if timer.is_ready():
            if self.timer_was_used:
                self.canvas.config(
                    highlightthickness=2,
                    highlightbackground=READY_BORDER_COLOR
                )
            else:
                self.canvas.config(
                    highlightthickness=2,
                    highlightbackground=READY_BORDER_COLOR
                )
        else:
            if timer.is_active:
                self.canvas.config(
                    highlightthickness=2,
                    highlightbackground=ACTIVE_BORDER_COLOR
                )
            else:
                self.canvas.config(
                    highlightthickness=0
                )


class SummonerSpellSelector(tk.Toplevel):
    """Summoner spell selection dialog."""

    def __init__(self, parent, callback, cleanup_callback=None, position=None):
        super().__init__(parent)
        self.callback = callback
        self.cleanup_callback = cleanup_callback
        self.selected_spell = None

        self.title("Select Summoner Spell")
        self.geometry("300x400")
        self.attributes("-topmost", True)
        self.configure(bg=OVERLAY_BG_COLOR)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        if position:
            self.update_idletasks()
            self.geometry(f"+{position[0]}+{position[1]}")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search)

        search_frame = tk.Frame(self, bg=OVERLAY_BG_COLOR)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            search_frame,
            text="Search:",
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 5))

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg="#2a2a2a",
            fg=NAME_COLOR,
            insertbackground=NAME_COLOR,
            relief=tk.FLAT,
            font=("Arial", 10)
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.focus()

        list_frame = tk.Frame(self, bg=OVERLAY_BG_COLOR)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame, bg=OVERLAY_BG_COLOR, troughcolor="#2a2a2a")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.spell_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg="#2a2a2a",
            fg=NAME_COLOR,
            selectbackground="#888888",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            font=("Arial", 10),
            highlightthickness=0
        )
        self.spell_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.spell_listbox.yview)

        self.all_spells = summoner_spell_data.get_spell_list()
        self._update_list(self.all_spells)

        self.spell_listbox.bind("<Double-Button-1>", self._on_select)
        self.spell_listbox.bind("<Return>", self._on_select)

        btn_frame = tk.Frame(self, bg=OVERLAY_BG_COLOR)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(
            btn_frame,
            text="Select",
            command=self._on_select,
            bg="#27ae60",
            fg="#ffffff",
            activebackground="#2ecc71",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            font=("Arial", 10),
            cursor="hand2",
            width=10
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            bg="#e74c3c",
            fg="#ffffff",
            activebackground="#c0392b",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            font=("Arial", 10),
            cursor="hand2",
            width=10
        ).pack(side=tk.LEFT)

    def _update_list(self, spells):
        self.spell_listbox.delete(0, tk.END)
        for spell in spells:
            self.spell_listbox.insert(tk.END, spell)

    def _on_search(self, *args):
        search_term = self.search_var.get().lower()
        filtered = [s for s in self.all_spells if search_term in s.lower()]
        self._update_list(filtered)

    def _on_close(self):
        if self.cleanup_callback:
            self.cleanup_callback()
        self.destroy()

    def _on_select(self, event=None):
        selection = self.spell_listbox.curselection()
        if selection:
            self.selected_spell = self.spell_listbox.get(selection[0])
            self.callback(self.selected_spell)
            if self.cleanup_callback:
                self.cleanup_callback()
            self.destroy()


class ChampionSelector(tk.Toplevel):
    """Champion selection dialog."""

    def __init__(self, parent, callback, cleanup_callback=None, position=None):
        super().__init__(parent)
        self.callback = callback
        self.cleanup_callback = cleanup_callback
        self.selected_champion = None

        self.title("Select Champion")
        self.geometry("300x400")
        self.attributes("-topmost", True)
        self.configure(bg=OVERLAY_BG_COLOR)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        if position:
            self.update_idletasks()
            self.geometry(f"+{position[0]}+{position[1]}")

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search)

        search_frame = tk.Frame(self, bg=OVERLAY_BG_COLOR)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            search_frame,
            text="Search:",
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 5))

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg="#2a2a2a",
            fg=NAME_COLOR,
            insertbackground=NAME_COLOR,
            relief=tk.FLAT,
            font=("Arial", 10)
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.focus()

        list_frame = tk.Frame(self, bg=OVERLAY_BG_COLOR)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(list_frame, bg=OVERLAY_BG_COLOR, troughcolor="#2a2a2a")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.champion_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg="#2a2a2a",
            fg=NAME_COLOR,
            selectbackground="#888888",
            selectforeground="#ffffff",
            relief=tk.FLAT,
            font=("Arial", 10),
            highlightthickness=0
        )
        self.champion_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.champion_listbox.yview)

        self.all_champions = champion_data.get_champion_list()
        self._update_list(self.all_champions)

        self.champion_listbox.bind("<Double-Button-1>", self._on_select)
        self.champion_listbox.bind("<Return>", self._on_select)

        btn_frame = tk.Frame(self, bg=OVERLAY_BG_COLOR)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(
            btn_frame,
            text="Select",
            command=self._on_select,
            bg="#27ae60",
            fg="#ffffff",
            activebackground="#2ecc71",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            font=("Arial", 10),
            cursor="hand2",
            width=10
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            bg="#e74c3c",
            fg="#ffffff",
            activebackground="#c0392b",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            font=("Arial", 10),
            cursor="hand2",
            width=10
        ).pack(side=tk.LEFT)

    def _update_list(self, champions):
        self.champion_listbox.delete(0, tk.END)
        for champ in champions:
            self.champion_listbox.insert(tk.END, champ)

    def _on_search(self, *args):
        search_term = self.search_var.get().lower()
        filtered = [c for c in self.all_champions if search_term in c.lower()]
        self._update_list(filtered)

    def _on_close(self):
        if self.cleanup_callback:
            self.cleanup_callback()
        self.destroy()

    def _on_select(self, event=None):
        selection = self.champion_listbox.curselection()
        if selection:
            self.selected_champion = self.champion_listbox.get(selection[0])
            self.callback(self.selected_champion)
            if self.cleanup_callback:
                self.cleanup_callback()
            self.destroy()


class SettingsDialog(tk.Toplevel):
    """Settings dialog for sound configuration."""

    def __init__(self, parent, app, position=None):
        super().__init__(parent)
        self.app = app

        self.title("Settings")
        self.geometry("320x510")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.configure(bg=OVERLAY_BG_COLOR)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        if position:
            self.update_idletasks()
            self.geometry(f"+{position[0]}+{position[1]}")

        self.sound_enabled_var = tk.BooleanVar(value=self.app.sound_enabled)
        self.use_champion_icons_var = tk.BooleanVar(value=self.app.use_champion_icons)
        self.auto_load_enabled_var = tk.BooleanVar(value=self.app.auto_load_enabled)
        self.show_champion_names_var = tk.BooleanVar(value=self.app.show_champion_names)
        self.gray_low_level_icons_var = tk.BooleanVar(value=self.app.gray_low_level_icons)
        self.current_volume = int(self.app.sound_volume * 100)
        self.current_alert_threshold = int(self.app.sound_alert_threshold)
        self.current_ui_scale = self.app.ui_scale

        main_frame = tk.Frame(self, bg=OVERLAY_BG_COLOR, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        sound_check = tk.Checkbutton(
            main_frame,
            text="Enable sound",
            variable=self.sound_enabled_var,
            command=self._on_sound_toggle,
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            selectcolor=OVERLAY_BG_COLOR,
            activebackground=OVERLAY_BG_COLOR,
            activeforeground=NAME_COLOR,
            font=("Arial", 10)
        )
        sound_check.pack(anchor=tk.W, pady=(0, 10))

        icon_type_check = tk.Checkbutton(
            main_frame,
            text="Use champion icons (instead of ult icons)",
            variable=self.use_champion_icons_var,
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            selectcolor=OVERLAY_BG_COLOR,
            activebackground=OVERLAY_BG_COLOR,
            activeforeground=NAME_COLOR,
            font=("Arial", 10)
        )
        icon_type_check.pack(anchor=tk.W, pady=(0, 10))

        auto_load_check = tk.Checkbutton(
            main_frame,
            text="Auto-load champions from game",
            variable=self.auto_load_enabled_var,
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            selectcolor=OVERLAY_BG_COLOR,
            activebackground=OVERLAY_BG_COLOR,
            activeforeground=NAME_COLOR,
            font=("Arial", 10)
        )
        auto_load_check.pack(anchor=tk.W, pady=(0, 10))

        show_names_check = tk.Checkbutton(
            main_frame,
            text="Show champion names and levels",
            variable=self.show_champion_names_var,
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            selectcolor=OVERLAY_BG_COLOR,
            activebackground=OVERLAY_BG_COLOR,
            activeforeground=NAME_COLOR,
            font=("Arial", 10)
        )
        show_names_check.pack(anchor=tk.W, pady=(0, 10))

        gray_low_level_check = tk.Checkbutton(
            main_frame,
            text="Gray out icons below level 6",
            variable=self.gray_low_level_icons_var,
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            selectcolor=OVERLAY_BG_COLOR,
            activebackground=OVERLAY_BG_COLOR,
            activeforeground=NAME_COLOR,
            font=("Arial", 10)
        )
        gray_low_level_check.pack(anchor=tk.W, pady=(0, 15))

        volume_frame = tk.Frame(main_frame, bg=OVERLAY_BG_COLOR)
        volume_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(
            volume_frame,
            text="Volume:",
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        self.volume_label = tk.Label(
            volume_frame,
            text=f"{self.current_volume}%",
            width=5,
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            font=("Arial", 10)
        )
        self.volume_label.pack(side=tk.RIGHT)

        slider_frame = tk.Frame(main_frame, bg=OVERLAY_BG_COLOR)
        slider_frame.pack(fill=tk.X, pady=(0, 20))

        self.volume_slider = tk.Scale(
            slider_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            showvalue=0,
            command=self._on_volume_change,
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            troughcolor="#2a2a2a",
            activebackground="#888888",
            highlightthickness=0,
            length=200
        )
        self.volume_slider.set(self.current_volume)
        self.volume_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.test_btn = tk.Button(
            slider_frame,
            text="Play",
            command=self._test_sound,
            bg="#2a2a2a",
            fg=NAME_COLOR,
            activebackground="#3a3a3a",
            activeforeground=NAME_COLOR,
            relief=tk.FLAT,
            font=("Arial", 9),
            cursor="hand2",
            width=6
        )
        self.test_btn.pack(side=tk.LEFT, padx=(5, 0))

        alert_frame = tk.Frame(main_frame, bg=OVERLAY_BG_COLOR)
        alert_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(
            alert_frame,
            text="Alert before ready:",
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        self.alert_label = tk.Label(
            alert_frame,
            text=f"{self.current_alert_threshold}s",
            width=5,
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            font=("Arial", 10)
        )
        self.alert_label.pack(side=tk.RIGHT)

        self.alert_slider = tk.Scale(
            main_frame,
            from_=0,
            to=5,
            orient=tk.HORIZONTAL,
            showvalue=0,
            command=self._on_alert_change,
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            troughcolor="#2a2a2a",
            activebackground="#888888",
            highlightthickness=0,
            length=200
        )
        self.alert_slider.set(self.current_alert_threshold)
        self.alert_slider.pack(fill=tk.X, pady=(0, 20))

        ui_scale_frame = tk.Frame(main_frame, bg=OVERLAY_BG_COLOR)
        ui_scale_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(
            ui_scale_frame,
            text="UI Scale:",
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            font=("Arial", 10)
        ).pack(side=tk.LEFT)

        self.scale_label = tk.Label(
            ui_scale_frame,
            text=f"{int(self.current_ui_scale * 100)}%",
            width=5,
            bg=OVERLAY_BG_COLOR,
            fg=NAME_COLOR,
            font=("Arial", 10)
        )
        self.scale_label.pack(side=tk.RIGHT)

        scale_buttons_frame = tk.Frame(main_frame, bg=OVERLAY_BG_COLOR)
        scale_buttons_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Button(
            scale_buttons_frame,
            text="−",
            command=self._decrease_scale,
            bg="#2a2a2a",
            fg=NAME_COLOR,
            activebackground="#3a3a3a",
            activeforeground=NAME_COLOR,
            relief=tk.FLAT,
            font=("Arial", 12),
            cursor="hand2",
            width=3
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            scale_buttons_frame,
            text="Reset",
            command=self._reset_scale,
            bg="#2a2a2a",
            fg=NAME_COLOR,
            activebackground="#3a3a3a",
            activeforeground=NAME_COLOR,
            relief=tk.FLAT,
            font=("Arial", 10),
            cursor="hand2",
            width=10
        ).pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(
            scale_buttons_frame,
            text="+",
            command=self._increase_scale,
            bg="#2a2a2a",
            fg=NAME_COLOR,
            activebackground="#3a3a3a",
            activeforeground=NAME_COLOR,
            relief=tk.FLAT,
            font=("Arial", 12),
            cursor="hand2",
            width=3
        ).pack(side=tk.LEFT)

        self._update_slider_state()

        btn_frame = tk.Frame(main_frame, bg=OVERLAY_BG_COLOR)
        btn_frame.pack(fill=tk.X)

        save_btn = tk.Button(
            btn_frame,
            text="Save",
            command=self._on_save,
            width=10,
            bg="#27ae60",
            fg="#ffffff",
            activebackground="#2ecc71",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            font=("Arial", 10),
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 5))

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            width=10,
            bg="#e74c3c",
            fg="#ffffff",
            activebackground="#c0392b",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            font=("Arial", 10),
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT)

    def _on_sound_toggle(self):
        self._update_slider_state()

    def _update_slider_state(self):
        if self.sound_enabled_var.get():
            self.volume_slider.config(state=tk.NORMAL)
            self.test_btn.config(state=tk.NORMAL)
        else:
            self.volume_slider.config(state=tk.DISABLED)
            self.test_btn.config(state=tk.DISABLED)

    def _on_volume_change(self, value):
        self.current_volume = int(float(value))
        self.volume_label.config(text=f"{self.current_volume}%")

    def _on_alert_change(self, value):
        self.current_alert_threshold = int(float(value))
        self.alert_label.config(text=f"{self.current_alert_threshold}s")

    def _test_sound(self):
        if self.app.ready_sound:
            volume = self.current_volume / 100.0
            self.app.ready_sound.set_volume(volume)
            self.app.ready_sound.play()

    def _decrease_scale(self):
        new_scale = round(self.current_ui_scale - UI_SCALE_STEP, 1)
        if new_scale >= UI_SCALE_MIN:
            self.current_ui_scale = new_scale
            self.scale_label.config(text=f"{int(self.current_ui_scale * 100)}%")
            self.app.ui_scale = self.current_ui_scale

            x = self.winfo_x()
            y = self.winfo_y()
            self.destroy()
            self.app._apply_scale_change()
            self.app.root.after(50, lambda: self.app._open_settings((x, y)))

    def _increase_scale(self):
        new_scale = round(self.current_ui_scale + UI_SCALE_STEP, 1)
        if new_scale <= UI_SCALE_MAX:
            self.current_ui_scale = new_scale
            self.scale_label.config(text=f"{int(self.current_ui_scale * 100)}%")
            self.app.ui_scale = self.current_ui_scale

            x = self.winfo_x()
            y = self.winfo_y()
            self.destroy()
            self.app._apply_scale_change()
            self.app.root.after(50, lambda: self.app._open_settings((x, y)))

    def _reset_scale(self):
        self.current_ui_scale = 1.0
        self.scale_label.config(text="100%")
        self.app.ui_scale = self.current_ui_scale

        x = self.winfo_x()
        y = self.winfo_y()
        self.destroy()
        self.app._apply_scale_change()
        self.app.root.after(50, lambda: self.app._open_settings((x, y)))

    def _on_close(self):
        self.app.settings_dialog = None
        self.destroy()

    def _on_save(self):
        self.app.sound_enabled = self.sound_enabled_var.get()
        self.app.sound_volume = self.current_volume / 100.0
        self.app.sound_alert_threshold = self.current_alert_threshold
        self.app.ui_scale = self.current_ui_scale

        icon_type_changed = self.app.use_champion_icons != self.use_champion_icons_var.get()
        self.app.use_champion_icons = self.use_champion_icons_var.get()

        auto_load_changed = self.app.auto_load_enabled != self.auto_load_enabled_var.get()
        self.app.auto_load_enabled = self.auto_load_enabled_var.get()

        show_names_changed = self.app.show_champion_names != self.show_champion_names_var.get()
        self.app.show_champion_names = self.show_champion_names_var.get()

        self.app.gray_low_level_icons = self.gray_low_level_icons_var.get()

        if self.app.ready_sound:
            self.app.ready_sound.set_volume(self.app.sound_volume)

        for timer in self.app.timer_manager.timers.values():
            if timer:
                timer.alert_threshold = self.app.sound_alert_threshold
                timer.sound_played = False

        if icon_type_changed:
            champion_data.set_icon_type(self.app.use_champion_icons)
            for slot in self.app.slots.values():
                if slot.champion:
                    slot.set_champion(slot.champion)

        if auto_load_changed:
            if self.app.auto_load_enabled:
                self.app._setup_auto_loader()
            else:
                if self.app.auto_loader:
                    self.app.auto_loader.stop()
                    self.app.auto_loader = None
                self.app.game_connected = False

        if show_names_changed:
            for slot in self.app.slots.values():
                slot._update_level_display()

        save_settings(LAYOUT, sound_enabled=self.app.sound_enabled, sound_volume=self.app.sound_volume, sound_alert_threshold=self.app.sound_alert_threshold, ui_scale=self.app.ui_scale, use_champion_icons=self.app.use_champion_icons, auto_load_enabled=self.app.auto_load_enabled, show_champion_names=self.app.show_champion_names, gray_low_level_icons=self.app.gray_low_level_icons)
        self.app.settings_dialog = None
        self.destroy()


class OverlayApp:
    """Main overlay application."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Spell Tracker")

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", OVERLAY_ALPHA)
        self.root.configure(bg=OVERLAY_BG_COLOR)
        self.root.resizable(False, False)

        settings = load_settings()
        global LAYOUT
        LAYOUT = settings.get("layout", LAYOUT)

        self.locked = settings.get("locked", False)
        self.sound_enabled = settings.get("sound_enabled", SOUND_ENABLED)
        self.sound_volume = settings.get("sound_volume", SOUND_VOLUME)
        self.sound_alert_threshold = settings.get("sound_alert_threshold", SOUND_ALERT_THRESHOLD)
        self.ui_scale = settings.get("ui_scale", UI_SCALE)
        self.use_champion_icons = settings.get("use_champion_icons", False)
        self.auto_load_enabled = settings.get("auto_load_enabled", AUTO_LOAD_ENABLED)
        self.show_champion_names = settings.get("show_champion_names", SHOW_CHAMPION_NAMES)
        self.gray_low_level_icons = settings.get("gray_low_level_icons", GRAY_LOW_LEVEL_ICONS)

        apply_ui_scale(self.ui_scale)
        champion_data.set_icon_type(self.use_champion_icons)

        pygame.mixer.init()
        self.ready_sound = None
        if os.path.exists(SOUND_FILE_PATH):
            self.ready_sound = pygame.mixer.Sound(SOUND_FILE_PATH)
            self.ready_sound.set_volume(self.sound_volume)

        self.timer_manager = TimerManager()
        self.timer_manager.register_update_callback(self._update_all_timers)

        self.slots = {}

        self.drag_start_x = 0
        self.drag_start_y = 0

        self.settings_dialog = None
        self.champion_selector = None
        self.summoner_spell_selector = None

        self.tray_icon = None
        self._setup_tray_icon()

        self.auto_loader = None
        self.game_connected = False
        if self.auto_load_enabled:
            self._setup_auto_loader()

        self._create_ui()
        self._debug_populate_slots()
        self._setup_drag_and_drop()
        self._start_update_loop()

        position = settings.get("position")
        if position and isinstance(position, dict):
            x = position.get("x", 100)
            y = position.get("y", 100)
            self.root.geometry(f"+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_ui(self):
        menu_frame = tk.Frame(self.root, bg=OVERLAY_BG_COLOR, bd=0)
        menu_frame.pack(pady=(0, 2))

        self.toggle_canvas = tk.Canvas(
            menu_frame,
            width=LAYOUT_TOGGLE_SIZE,
            height=LAYOUT_TOGGLE_SIZE,
            bg=OVERLAY_BG_COLOR,
            highlightthickness=0
        )
        self.toggle_canvas.pack(side=tk.LEFT, padx=2, pady=2)

        self._draw_layout_icon(self.toggle_canvas)
        self.toggle_canvas.bind("<Button-1>", lambda e: self._toggle_layout())

        self.toggle_tooltip = ToolTip(self.toggle_canvas, "Toggle layout (horizontal/vertical)")

        def on_enter_toggle(e):
            self._draw_layout_icon(self.toggle_canvas, MENU_BUTTON_HOVER_COLOR)
            self.toggle_tooltip.show()

        def on_leave_toggle(e):
            self._draw_layout_icon(self.toggle_canvas)
            self.toggle_tooltip.hide()

        self.toggle_canvas.bind("<Enter>", on_enter_toggle)
        self.toggle_canvas.bind("<Leave>", on_leave_toggle)

        self.pin_canvas = tk.Canvas(
            menu_frame,
            width=PIN_BUTTON_SIZE,
            height=PIN_BUTTON_SIZE,
            bg=OVERLAY_BG_COLOR,
            highlightthickness=0
        )
        self.pin_canvas.pack(side=tk.LEFT, padx=2, pady=2)

        self._draw_pin_icon(self.pin_canvas)
        self.pin_canvas.bind("<Button-1>", lambda e: self._save_position())

        self.pin_tooltip = ToolTip(self.pin_canvas, "Save current position")

        def on_enter_pin(e):
            self._draw_pin_icon(self.pin_canvas, MENU_BUTTON_HOVER_COLOR)
            self.pin_tooltip.show()

        def on_leave_pin(e):
            self._draw_pin_icon(self.pin_canvas)
            self.pin_tooltip.hide()

        self.pin_canvas.bind("<Enter>", on_enter_pin)
        self.pin_canvas.bind("<Leave>", on_leave_pin)

        self.lock_canvas = tk.Canvas(
            menu_frame,
            width=LOCK_BUTTON_SIZE,
            height=LOCK_BUTTON_SIZE,
            bg=OVERLAY_BG_COLOR,
            highlightthickness=0
        )
        self.lock_canvas.pack(side=tk.LEFT, padx=2, pady=2)

        self._draw_lock_icon(self.lock_canvas)
        self.lock_canvas.bind("<Button-1>", lambda e: self._toggle_lock())

        self.lock_tooltip = ToolTip(self.lock_canvas, "Lock overlay (prevent changes)")

        def on_enter_lock(e):
            self._draw_lock_icon(self.lock_canvas, MENU_BUTTON_HOVER_COLOR)
            self.lock_tooltip.show()

        def on_leave_lock(e):
            self._draw_lock_icon(self.lock_canvas)
            self.lock_tooltip.hide()

        self.lock_canvas.bind("<Enter>", on_enter_lock)
        self.lock_canvas.bind("<Leave>", on_leave_lock)

        self.settings_canvas = tk.Canvas(
            menu_frame,
            width=SETTINGS_BUTTON_SIZE,
            height=SETTINGS_BUTTON_SIZE,
            bg=OVERLAY_BG_COLOR,
            highlightthickness=0
        )
        self.settings_canvas.pack(side=tk.LEFT, padx=2, pady=2)

        self._draw_settings_icon(self.settings_canvas)
        self.settings_canvas.bind("<Button-1>", lambda e: self._open_settings())

        self.settings_tooltip = ToolTip(self.settings_canvas, "Settings")

        def on_enter_settings(e):
            self._draw_settings_icon(self.settings_canvas, MENU_BUTTON_HOVER_COLOR)
            self.settings_tooltip.show()

        def on_leave_settings(e):
            self._draw_settings_icon(self.settings_canvas)
            self.settings_tooltip.hide()

        self.settings_canvas.bind("<Enter>", on_enter_settings)
        self.settings_canvas.bind("<Leave>", on_leave_settings)

        self.close_canvas = tk.Canvas(
            menu_frame,
            width=CLOSE_BUTTON_SIZE,
            height=CLOSE_BUTTON_SIZE,
            bg=OVERLAY_BG_COLOR,
            highlightthickness=0
        )
        self.close_canvas.pack(side=tk.LEFT, padx=2, pady=2)

        self._draw_close_icon(self.close_canvas)
        self.close_canvas.bind("<Button-1>", lambda e: self._quit_app())

        self.close_tooltip = ToolTip(self.close_canvas, "Close application")

        def on_enter_close(e):
            self._draw_close_icon(self.close_canvas, "#e74c3c")
            self.close_tooltip.show()

        def on_leave_close(e):
            self._draw_close_icon(self.close_canvas)
            self.close_tooltip.hide()

        self.close_canvas.bind("<Enter>", on_enter_close)
        self.close_canvas.bind("<Leave>", on_leave_close)

        self.border_frame = tk.Frame(self.root, bg=BORDER_COLOR, bd=0, relief="solid")
        self.border_frame.pack(fill=tk.BOTH, expand=True)

        inner_frame = tk.Frame(self.border_frame, bg=OVERLAY_BG_COLOR, bd=0, relief="flat")
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.main_frame = tk.Frame(inner_frame, bg=OVERLAY_BG_COLOR)
        self.main_frame.pack(padx=3, pady=3)

        self._create_slots()

    def _draw_layout_icon(self, canvas, color=None):
        canvas.delete("all")
        if color is None:
            color = LAYOUT_TOGGLE_COLOR

        if LAYOUT == "horizontal":
            for i in range(3):
                y = 6 + i * 6
                canvas.create_line(6, y, 18, y, fill=color, width=2)
        else:
            for i in range(3):
                x = 6 + i * 6
                canvas.create_line(x, 6, x, 18, fill=color, width=2)

    def _draw_pin_icon(self, canvas, color=None):
        canvas.delete("all")
        if color is None:
            color = PIN_BUTTON_COLOR

        canvas.create_oval(10, 6, 14, 10, fill=color, outline=color)
        canvas.create_line(12, 10, 12, 18, fill=color, width=2)
        canvas.create_line(9, 15, 15, 15, fill=color, width=2)

    def _draw_lock_icon(self, canvas, color=None):
        canvas.delete("all")
        if color is None:
            color = LOCK_BUTTON_COLOR

        if self.locked:
            canvas.create_rectangle(8, 11, 16, 18, outline=color, width=2)
            canvas.create_arc(9, 6, 15, 13, start=0, extent=180, outline=color, width=2, style="arc")
            canvas.create_oval(11, 13, 13, 15, fill=color, outline=color)
        else:
            canvas.create_rectangle(8, 11, 16, 18, outline=color, width=2)
            canvas.create_arc(9, 6, 15, 13, start=0, extent=180, outline=color, width=2, style="arc")
            canvas.create_line(14, 8, 17, 8, fill=color, width=2)
            canvas.create_oval(11, 13, 13, 15, fill=color, outline=color)

    def _draw_settings_icon(self, canvas, color=None):
        canvas.delete("all")
        if color is None:
            color = SETTINGS_BUTTON_COLOR

        canvas.create_oval(10, 10, 14, 14, outline=color, width=2)
        for angle in range(0, 360, 90):
            import math
            rad = math.radians(angle)
            x1 = 12 + math.cos(rad) * 4
            y1 = 12 + math.sin(rad) * 4
            x2 = 12 + math.cos(rad) * 6
            y2 = 12 + math.sin(rad) * 6
            canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

    def _draw_close_icon(self, canvas, color=None):
        canvas.delete("all")
        if color is None:
            color = CLOSE_BUTTON_COLOR

        canvas.create_line(7, 7, 17, 17, fill=color, width=2)
        canvas.create_line(17, 7, 7, 17, fill=color, width=2)

    def _get_dialog_position(self, dialog_width=300, dialog_height=400):
        """Calculate position for dialog to appear left of overlay."""
        overlay_x = self.root.winfo_x()
        overlay_y = self.root.winfo_y()
        overlay_height = self.root.winfo_height()

        dialog_x = overlay_x - dialog_width - 10
        dialog_y = overlay_y + (overlay_height - dialog_height) // 2

        if dialog_x < 0:
            dialog_x = overlay_x + self.root.winfo_width() + 10

        return (dialog_x, dialog_y)

    def _open_settings(self, position=None):
        if self.settings_dialog and self.settings_dialog.winfo_exists():
            self.settings_dialog.lift()
            self.settings_dialog.focus_force()
            return

        if position is None:
            position = self._get_dialog_position(320, 410)

        self.settings_dialog = SettingsDialog(self.root, self, position)

    def _quit_app(self):
        self._exit_app()

    def _create_slots(self):
        for i in range(NUM_SLOTS):
            slot = ChampionSlot(self.main_frame, i, self.timer_manager, self)
            if LAYOUT == "horizontal":
                slot.pack(side=tk.LEFT, padx=SLOT_SPACING)
            else:
                slot.pack(pady=SLOT_SPACING)
            self.slots[i] = slot

            slot.on_double_click_callback = self._select_champion
            slot.on_summoner_spell_select_callback = self._select_summoner_spell

    def _debug_populate_slots(self):
        if not DEBUG_MODE:
            return

        all_champions = champion_data.get_champion_list()
        all_spells = summoner_spell_data.get_spell_list()

        if len(all_champions) < NUM_SLOTS:
            return

        selected_champions = random.sample(all_champions, NUM_SLOTS)

        for slot_id, champion_name in enumerate(selected_champions):
            if slot_id in self.slots:
                self.slots[slot_id].set_champion(champion_name)

                spell1 = random.choice(all_spells)
                spell2 = random.choice(all_spells)

                self.slots[slot_id].summoner_spell_slots[0].set_spell(spell1)
                self.slots[slot_id].summoner_spell_slots[1].set_spell(spell2)

    def _toggle_layout(self):
        global LAYOUT
        LAYOUT = "horizontal" if LAYOUT == "vertical" else "vertical"
        save_settings(LAYOUT, sound_enabled=self.sound_enabled, sound_volume=self.sound_volume, sound_alert_threshold=self.sound_alert_threshold, ui_scale=self.ui_scale, use_champion_icons=self.use_champion_icons, auto_load_enabled=self.auto_load_enabled, show_champion_names=self.show_champion_names, gray_low_level_icons=self.gray_low_level_icons)

        slot_states = {}
        for slot_id, slot in self.slots.items():
            slot_state = {
                'champion': slot.champion,
                'summoner_spells': {},
                'timer_state': None,
                'spell_timer_states': {}
            }

            timer = self.timer_manager.get_timer(slot_id)
            if timer:
                slot_state['timer_state'] = {
                    'level': timer.level,
                    'is_active': timer.is_active,
                    'start_time': timer.start_time
                }

            for spell_slot_id, spell_slot in slot.summoner_spell_slots.items():
                slot_state['summoner_spells'][spell_slot_id] = spell_slot.spell

                spell_timer = self.timer_manager.get_summoner_spell_timer(slot_id, spell_slot_id)
                if spell_timer:
                    slot_state['spell_timer_states'][spell_slot_id] = {
                        'is_active': spell_timer.is_active,
                        'start_time': spell_timer.start_time
                    }

            slot_states[slot_id] = slot_state

        for slot in self.slots.values():
            slot.destroy()
        self.slots.clear()

        self._create_slots()

        for slot_id, slot_state in slot_states.items():
            if slot_state['champion'] and slot_id in self.slots:
                self.slots[slot_id].set_champion(slot_state['champion'])

                if slot_state['timer_state']:
                    timer = self.timer_manager.get_timer(slot_id)
                    if timer:
                        timer.level = slot_state['timer_state']['level']
                        timer.is_active = slot_state['timer_state']['is_active']
                        timer.start_time = slot_state['timer_state']['start_time']

            for spell_slot_id, spell_name in slot_state['summoner_spells'].items():
                if spell_name and slot_id in self.slots:
                    spell_slot_widget = self.slots[slot_id].summoner_spell_slots.get(spell_slot_id)
                    if spell_slot_widget:
                        spell_slot_widget.set_spell(spell_name)

                        if spell_slot_id in slot_state['spell_timer_states']:
                            spell_timer = self.timer_manager.get_summoner_spell_timer(slot_id, spell_slot_id)
                            if spell_timer:
                                timer_state = slot_state['spell_timer_states'][spell_slot_id]
                                spell_timer.is_active = timer_state['is_active']
                                spell_timer.start_time = timer_state['start_time']

        self._draw_layout_icon(self.toggle_canvas)

    def _apply_scale_change(self):
        slot_states = {}
        for slot_id, slot in self.slots.items():
            slot_state = {
                'champion': slot.champion,
                'summoner_spells': {},
                'timer_state': None,
                'spell_timer_states': {}
            }

            timer = self.timer_manager.get_timer(slot_id)
            if timer:
                slot_state['timer_state'] = {
                    'level': timer.level,
                    'is_active': timer.is_active,
                    'start_time': timer.start_time
                }

            for spell_slot_id, spell_slot in slot.summoner_spell_slots.items():
                slot_state['summoner_spells'][spell_slot_id] = spell_slot.spell

                spell_timer = self.timer_manager.get_summoner_spell_timer(slot_id, spell_slot_id)
                if spell_timer:
                    slot_state['spell_timer_states'][spell_slot_id] = {
                        'is_active': spell_timer.is_active,
                        'start_time': spell_timer.start_time
                    }

            slot_states[slot_id] = slot_state

        apply_ui_scale(self.ui_scale)

        for widget in self.root.winfo_children():
            widget.destroy()
        self.slots.clear()

        self._create_ui()

        for slot_id, slot_state in slot_states.items():
            if slot_state['champion'] and slot_id in self.slots:
                self.slots[slot_id].set_champion(slot_state['champion'])

                if slot_state['timer_state']:
                    timer = self.timer_manager.get_timer(slot_id)
                    if timer:
                        timer.level = slot_state['timer_state']['level']
                        timer.is_active = slot_state['timer_state']['is_active']
                        timer.start_time = slot_state['timer_state']['start_time']

            for spell_slot_id, spell_name in slot_state['summoner_spells'].items():
                if spell_name and slot_id in self.slots:
                    spell_slot_widget = self.slots[slot_id].summoner_spell_slots.get(spell_slot_id)
                    if spell_slot_widget:
                        spell_slot_widget.set_spell(spell_name)

                        if spell_slot_id in slot_state['spell_timer_states']:
                            spell_timer = self.timer_manager.get_summoner_spell_timer(slot_id, spell_slot_id)
                            if spell_timer:
                                timer_state = slot_state['spell_timer_states'][spell_slot_id]
                                spell_timer.is_active = timer_state['is_active']
                                spell_timer.start_time = timer_state['start_time']

    def _toggle_lock(self):
        self.locked = not self.locked
        save_settings(LAYOUT, locked=self.locked, sound_enabled=self.sound_enabled, sound_volume=self.sound_volume, sound_alert_threshold=self.sound_alert_threshold, ui_scale=self.ui_scale, use_champion_icons=self.use_champion_icons, auto_load_enabled=self.auto_load_enabled, show_champion_names=self.show_champion_names, gray_low_level_icons=self.gray_low_level_icons)
        self._draw_lock_icon(self.lock_canvas)

    def _setup_auto_loader(self):
        if self.auto_loader:
            self.auto_loader.stop()

        self.auto_loader = GameAutoLoader(poll_interval=AUTO_LOAD_POLL_INTERVAL)
        self.auto_loader.set_callbacks(
            on_game_start=self._on_game_start,
            on_game_end=self._on_game_end,
            on_level_update=self._on_level_update
        )
        self.auto_loader.start()

    def _on_game_start(self, enemy_team_data):
        self.game_connected = True
        self.root.after(0, lambda: self._update_game_status_and_load(enemy_team_data))

    def _on_game_end(self):
        self.game_connected = False
        self.root.after(0, self._clear_all_slots)

    def _on_level_update(self, levels_data):
        self.root.after(0, lambda: self._update_levels(levels_data))

    def _clear_all_slots(self):
        print("Game ended - clearing all slots...")
        for slot in self.slots.values():
            slot.clear()

    def _update_game_status_and_load(self, enemy_team_data):
        self._populate_from_game_data(enemy_team_data)

    def _update_levels(self, levels_data):
        for i, level_data in enumerate(levels_data[:NUM_SLOTS]):
            ult_level = level_data.get("level", 0)
            if i in self.slots:
                slot = self.slots[i]
                timer = self.timer_manager.get_timer(i)
                if timer:
                    if ult_level == -1:
                        slot.set_ult_availability(False)
                    else:
                        slot.set_ult_availability(True)
                        if timer.level != ult_level:
                            self.timer_manager.set_level(i, ult_level)
                            slot._update_level_display()

    def _populate_from_game_data(self, enemy_team_data):
        print(f"Auto-loading {len(enemy_team_data)} champions from game...")

        for i, player_data in enumerate(enemy_team_data[:NUM_SLOTS]):
            champion = player_data.get("champion")
            spell1 = player_data.get("spell1")
            spell2 = player_data.get("spell2")
            ult_level = player_data.get("level", 0)

            if champion and i in self.slots:
                slot = self.slots[i]
                slot.set_champion(champion)

                if ult_level == -1:
                    slot.set_ult_availability(False)
                else:
                    slot.set_ult_availability(True)
                    self.timer_manager.set_level(i, ult_level)
                    slot._update_level_display()

                if spell1 and 0 in slot.summoner_spell_slots:
                    slot.summoner_spell_slots[0].set_spell(spell1)

                if spell2 and 1 in slot.summoner_spell_slots:
                    slot.summoner_spell_slots[1].set_spell(spell2)

                print(f"Loaded slot {i}: {champion} lvl{ult_level} ({spell1}/{spell2})")

    def _setup_drag_and_drop(self):
        self.dragging = False

        def start_drag(event):
            if self.locked:
                return
            if event.widget.__class__.__name__ != 'Canvas':
                self.dragging = True
                self.drag_start_x = event.x_root - self.root.winfo_x()
                self.drag_start_y = event.y_root - self.root.winfo_y()

        def do_drag(event):
            if self.dragging:
                x = event.x_root - self.drag_start_x
                y = event.y_root - self.drag_start_y
                self.root.geometry(f"+{x}+{y}")

        def stop_drag(event):
            self.dragging = False

        self.root.bind("<Button-1>", start_drag, add="+")
        self.root.bind("<B1-Motion>", do_drag, add="+")
        self.root.bind("<ButtonRelease-1>", stop_drag, add="+")

    def _play_ready_sound(self):
        if self.ready_sound and self.sound_enabled:
            self.ready_sound.play()

    def _select_champion(self, slot_id: int):
        if self.champion_selector and self.champion_selector.winfo_exists():
            self.champion_selector.lift()
            self.champion_selector.focus_force()
            return

        def on_selected(champion_name):
            self.slots[slot_id].set_champion(champion_name)

        def on_cleanup():
            self.champion_selector = None

        position = self._get_dialog_position(300, 400)
        self.champion_selector = ChampionSelector(self.root, on_selected, on_cleanup, position)

    def _select_summoner_spell(self, slot_id: int, spell_slot: int):
        if self.summoner_spell_selector and self.summoner_spell_selector.winfo_exists():
            self.summoner_spell_selector.lift()
            self.summoner_spell_selector.focus_force()
            return

        def on_selected(spell_name):
            if slot_id in self.slots:
                spell_slot_widget = self.slots[slot_id].summoner_spell_slots.get(spell_slot)
                if spell_slot_widget:
                    spell_slot_widget.set_spell(spell_name)

        def on_cleanup():
            self.summoner_spell_selector = None

        position = self._get_dialog_position(300, 400)
        self.summoner_spell_selector = SummonerSpellSelector(self.root, on_selected, on_cleanup, position)

    def _update_all_timers(self):
        for slot in self.slots.values():
            slot.update_timer_display()
            slot._update_level_display()
            slot.update_summoner_spell_displays()

    def _start_update_loop(self):
        self._update_all_timers()
        self.root.after(100, self._start_update_loop)

    def _save_position(self):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        position = {"x": x, "y": y}
        save_settings(LAYOUT, position, sound_enabled=self.sound_enabled, sound_volume=self.sound_volume, sound_alert_threshold=self.sound_alert_threshold, ui_scale=self.ui_scale, use_champion_icons=self.use_champion_icons, auto_load_enabled=self.auto_load_enabled, show_champion_names=self.show_champion_names, gray_low_level_icons=self.gray_low_level_icons)

    def _setup_tray_icon(self):
        logo_path = get_resource_path("data/assets/logo.ico")
        if os.path.exists(logo_path):
            tray_image = Image.open(logo_path)
        else:
            tray_image = Image.new('RGB', (64, 64), color='#0a0a0a')
            draw = ImageDraw.Draw(tray_image)
            draw.rectangle([16, 16, 48, 48], fill='#27ae60')

        menu = pystray.Menu(
            item('Show/Hide', self._toggle_window_visibility),
            item('Exit', self._exit_app)
        )

        self.tray_icon = pystray.Icon("spell_tracker", tray_image, "Spell Tracker", menu)

        tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        tray_thread.start()

    def _toggle_window_visibility(self):
        if self.root.winfo_viewable():
            self.root.withdraw()
        else:
            self.root.deiconify()

    def _exit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self._on_closing()

    def _on_closing(self):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        position = {"x": x, "y": y}
        save_settings(LAYOUT, position, sound_enabled=self.sound_enabled, sound_volume=self.sound_volume, sound_alert_threshold=self.sound_alert_threshold, ui_scale=self.ui_scale, use_champion_icons=self.use_champion_icons, auto_load_enabled=self.auto_load_enabled, show_champion_names=self.show_champion_names, gray_low_level_icons=self.gray_low_level_icons)
        if self.auto_loader:
            self.auto_loader.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    app = OverlayApp()
    app.run()


if __name__ == "__main__":
    main()
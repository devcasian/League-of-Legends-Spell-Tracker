"""
Main overlay application for League of Legends ultimate cooldown tracking.

This module provides the GUI overlay application for tracking enemy
ultimate cooldowns in League of Legends matches.
"""

import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os

from config import *
from champion_data import champion_data
from timer import TimerManager


class ChampionSlot(tk.Frame):
    """Widget representing a single champion slot with icon and timer overlay."""

    def __init__(self, parent, slot_id: int, timer_manager: TimerManager):
        super().__init__(parent, bg=OVERLAY_BG_COLOR)
        self.slot_id = slot_id
        self.timer_manager = timer_manager
        self.champion = None
        self.base_image = None
        self.photo_image = None

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

        self.canvas = tk.Canvas(
            self,
            width=ICON_SIZE,
            height=ICON_SIZE,
            bg=OVERLAY_BG_COLOR,
            highlightthickness=0
        )
        self.canvas.pack()

        self.canvas_image_id = None

        self.level_label = tk.Label(
            self,
            text="Lvl 6",
            font=("Arial", 8),
            bg=OVERLAY_BG_COLOR,
            fg="#888888",
            height=1
        )
        self.level_label.pack()

        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)

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
            except Exception as e:
                print(f"Error loading icon for {champion_name}: {e}")

        display_name = champion_name
        if len(display_name) > 10:
            display_name = champion_name[:9] + "."
        self.name_label.config(text=display_name)

        cooldowns = champion_data.get_all_cooldowns(champion_name)
        if cooldowns:
            self.timer_manager.create_timer(self.slot_id, champion_name, cooldowns)

    def update_timer_display(self):
        if not self.base_image:
            return

        timer = self.timer_manager.get_timer(self.slot_id)
        if not timer:
            return

        img = self.base_image.copy()

        if not timer.is_ready():
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 150))
            img = Image.alpha_composite(img, overlay)

            draw = ImageDraw.Draw(img)

            remaining = timer.get_remaining_time()
            if remaining >= 60:
                minutes = int(remaining // 60)
                seconds = remaining % 60
                text = f"{minutes}:{seconds:04.1f}"
            else:
                text = f"{remaining:.1f}"

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
        timer = self.timer_manager.get_timer(self.slot_id)
        if timer:
            if timer.is_ready():
                self.timer_manager.start_timer(self.slot_id)
            else:
                self.timer_manager.reset_timer(self.slot_id)

    def _on_right_click(self, event):
        timer = self.timer_manager.get_timer(self.slot_id)
        if timer:
            self.timer_manager.increment_level(self.slot_id)
            self._update_level_display()

    def _update_level_display(self):
        timer = self.timer_manager.get_timer(self.slot_id)
        if timer:
            level_names = ["Lvl 6", "Lvl 11", "Lvl 16"]
            if timer.level < len(level_names):
                self.level_label.config(text=level_names[timer.level])

    def _on_double_click(self, event):
        if hasattr(self, 'on_double_click_callback') and self.on_double_click_callback:
            self.on_double_click_callback(self.slot_id)


class ChampionSelector(tk.Toplevel):
    """Champion selection dialog."""

    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.selected_champion = None

        self.title("Select Champion")
        self.geometry("300x400")
        self.attributes("-topmost", True)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search)

        search_frame = tk.Frame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.focus()

        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.champion_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.champion_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.champion_listbox.yview)

        self.all_champions = champion_data.get_champion_list()
        self._update_list(self.all_champions)

        self.champion_listbox.bind("<Double-Button-1>", self._on_select)
        self.champion_listbox.bind("<Return>", self._on_select)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(btn_frame, text="Select", command=self._on_select).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=2)

    def _update_list(self, champions):
        self.champion_listbox.delete(0, tk.END)
        for champ in champions:
            self.champion_listbox.insert(tk.END, champ)

    def _on_search(self, *args):
        search_term = self.search_var.get().lower()
        filtered = [c for c in self.all_champions if search_term in c.lower()]
        self._update_list(filtered)

    def _on_select(self, event=None):
        selection = self.champion_listbox.curselection()
        if selection:
            self.selected_champion = self.champion_listbox.get(selection[0])
            self.callback(self.selected_champion)
            self.destroy()


class OverlayApp:
    """Main overlay application."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LoL Ult Tracker")

        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", OVERLAY_ALPHA)
        self.root.configure(bg=OVERLAY_BG_COLOR)
        self.root.resizable(False, False)

        self.timer_manager = TimerManager()
        self.timer_manager.register_update_callback(self._update_all_timers)

        self.slots = {}

        self.drag_start_x = 0
        self.drag_start_y = 0

        self._create_ui()
        self._setup_drag_and_drop()
        self._start_update_loop()

    def _create_ui(self):
        border_frame = tk.Frame(self.root, bg=BORDER_COLOR, bd=0, relief="solid")
        border_frame.pack(fill=tk.BOTH, expand=True)

        inner_frame = tk.Frame(border_frame, bg=OVERLAY_BG_COLOR, bd=0, relief="flat")
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        main_frame = tk.Frame(inner_frame, bg=OVERLAY_BG_COLOR)
        main_frame.pack(padx=3, pady=3)

        for i in range(NUM_SLOTS):
            slot = ChampionSlot(main_frame, i, self.timer_manager)
            if LAYOUT == "horizontal":
                slot.pack(side=tk.LEFT, padx=SLOT_SPACING)
            else:
                slot.pack(pady=SLOT_SPACING)
            self.slots[i] = slot

            slot.on_double_click_callback = self._select_champion

    def _setup_drag_and_drop(self):
        self.dragging = False

        def start_drag(event):
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

    def _select_champion(self, slot_id: int):
        def on_selected(champion_name):
            self.slots[slot_id].set_champion(champion_name)

        ChampionSelector(self.root, on_selected)

    def _update_all_timers(self):
        for slot in self.slots.values():
            slot.update_timer_display()
            slot._update_level_display()

    def _start_update_loop(self):
        self._update_all_timers()
        self.root.after(100, self._start_update_loop)

    def run(self):
        self.root.mainloop()


def main():
    app = OverlayApp()
    app.run()


if __name__ == "__main__":
    main()
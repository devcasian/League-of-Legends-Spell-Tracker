# League of Legends Spell Tracker

<div align="center">

**Compact overlay for tracking enemy ultimate and summoner spell cooldowns in League of Legends**

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)

</div>

---

## 📋 Description

Lightweight overlay application for tracking enemy ultimate and summoner spell cooldowns in League of Legends. Helps monitor important enemy abilities and make better decisions during matches.

## ✨ Features

- 🎯 **5 enemy slots** - track opposing team's ultimates and summoner spells
- ⏱️ **Accurate timers** - automatic cooldown selection based on level (6/11/16)
- 🖼️ **Visual icons** - all 171 champions with ultimate ability icons + summoner spells
- 🔊 **Sound alerts** - customizable notifications when ultimates are ready
- 🎨 **Compact design** - minimalist interface with scalable UI (0.5x-2.0x)
- 🎨 **Visual effects** - color-coded borders (red=active, green=ready)
- 🔍 **Semi-transparent** - doesn't block game view
- 🔝 **Always on top** - window stays visible over the game
- 🖱️ **Drag & Drop** - move the window anywhere on screen
- 🔒 **Lock mode** - prevent accidental changes during gameplay
- 📍 **System tray** - minimize to tray and quick exit
- ⚙️ **Settings dialog** - configure sound, volume, alerts, and UI scale
- 🔄 **Layout toggle** - switch between horizontal and vertical layouts

## 🚀 Quick Start

### For Users (Recommended)

1. **Download** the latest release from [Releases](https://github.com/devcasian/League-of-Legends-Spell-Tracker/releases)
2. **Run** `Spell-Tracker.exe`
3. **No installation required** - the executable contains everything needed

### For Developers

If you want to modify the code or contribute:

#### Requirements

- Python 3.13 or newer
- Pillow (PIL) for image processing

#### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/devcasian/League-of-Legends-Spell-Tracker.git
cd League-of-Legends-Spell-Tracker
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python run.py
```

4. **Build executable (optional):**
```bash
python build.py
```

**Note:** If you have a `settings.json` in the project directory, the build script will use those values as defaults for the compiled executable. This lets you customize default settings for distribution.

## 🎮 Usage

### Champion Slots

- **Double-click (LMB)** on champion icon → Open champion selection window
- **Left-click (LMB)** → Start/reset ultimate timer
- **Right-click (RMB)** → Cycle ultimate level (6 → 11 → 16)

### Summoner Spell Slots

- **Double-click (LMB)** on summoner spell icon → Open spell selection window
- **Left-click (LMB)** → Start/reset spell timer

### Menu Bar Controls

- **Layout toggle** - Switch between horizontal/vertical layouts
- **Pin button** - Save current window position
- **Lock button** - Lock overlay (prevents window movement and champion changes)
- **Settings** - Open settings dialog (sound, volume, alert threshold, UI scale)
- **Close (X)** - Exit application

### System Tray

- **Right-click tray icon** → Open menu
  - **Show/Hide** - Toggle overlay visibility
  - **Exit** - Close application

### Window Movement

- **Drag empty area** → Move window (when not locked)

### Visual Indicators

- **Red border** - Timer is active (ability on cooldown)
- **Green border** - Ability is ready (after first use)
- **Gray border** - Empty slot

## 🗂️ Project Structure

```
League-of-Legends-Spell-Tracker/
├── run.py                              # Application entry point
├── build.py                            # Build script for creating .exe
├── spell-tracker.spec                  # PyInstaller configuration
├── requirements.txt                    # Python dependencies
├── README.md                           # Documentation
├── LICENSE                             # MIT license
├── .gitignore                          # Git ignore rules
├── .gitattributes                      # Git attributes
├── .github/workflows/
│   └── build-release.yml               # GitHub Actions auto-build
├── src/                                # Source code
│   ├── overlay.py                      # Main GUI application
│   ├── champion_data.py                # Champion data loader
│   ├── timer.py                        # Cooldown timer logic
│   ├── config.py                       # Application settings
│   └── settings.py                     # Settings persistence
└── data/                               # Game data
    ├── champions_ult_cooldowns.json    # Ultimate cooldowns
    ├── summoner_spells_cooldowns.json  # Summoner spell cooldowns
    ├── champion_icons/                 # Champion icons (171 files)
    ├── summoner spells/                # Summoner spell icons (10 files)
    ├── ult_ready.wav                   # Sound effect
    └── logo.ico                        # Application icon
```

## ⚙️ Configuration

### In-App Settings

Click the **Settings button** in the menu bar to configure:

- **Sound Enabled** - Toggle sound notifications on/off
- **Sound Volume** - Adjust volume (0.0 - 1.0)
- **Alert Threshold** - Set when to play sound (seconds before ready)
- **UI Scale** - Scale interface size (0.5x - 2.0x)

Settings are automatically saved to:
- **Windows**: `%APPDATA%\SpellTracker\settings.json`
- **Linux**: `~/.config/spell-tracker/settings.json`

This means you can move the .exe anywhere and your settings will persist!

### Advanced Configuration

Edit `src/config.py` to customize:

```python
OVERLAY_ALPHA = 0.95                # Window transparency
ICON_SIZE = 64                      # Base icon size (before scaling)
OVERLAY_BG_COLOR = "#0a0a0a"        # Background color
TIMER_COLOR = "#ffffff"             # Timer text color
READY_BORDER_COLOR = "#27ae60"      # Ready state color (green)
ACTIVE_BORDER_COLOR = "#e74c3c"     # Active timer color (red)
TIMER_FONT = ("Arial", 18, "bold")  # Timer font
DEBUG_MODE = False                  # Debug mode (shorter cooldowns)
```

## 🤝 Contributing

Contributions are welcome! If you have suggestions or found a bug:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 TODO

- [x] Sound notifications when ultimate is ready
- [x] Support for summoner spells
- [ ] Compact mode (minimize UI for more screen space)
- [ ] Theme customization (custom colors/fonts)
- [ ] Export/import settings (share configurations)

## 📄 License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ for the League of Legends community**

[Report Bug](https://github.com/devcasian/League-of-Legends-Spell-Tracker/issues) · [Request Feature](https://github.com/devcasian/League-of-Legends-Spell-Tracker/issues)

</div>
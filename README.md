# LoL Ultimate Cooldown Tracker

<div align="center">

**Compact overlay for tracking enemy ultimate cooldowns in League of Legends**

![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)

</div>

---

## 📋 Description

Lightweight overlay application for tracking enemy ultimate cooldowns in League of Legends. Helps monitor important enemy abilities and make better decisions during matches.

## ✨ Features

- 🎯 **5 enemy slots** - track opposing team's ultimates
- ⏱️ **Accurate timers** - automatic cooldown selection based on level (6/11/16)
- 🖼️ **Visual icons** - all 171 champions with ultimate ability icons
- 🎨 **Compact design** - minimalist interface with 64x64 pixel icons
- 🔍 **Semi-transparent** - doesn't block game view
- 🔝 **Always on top** - window stays visible over the game
- 🖱️ **Drag & Drop** - move the window anywhere on screen

## 📦 Installation

### Requirements

- Python 3.13 or newer
- Pillow (PIL) for image processing

### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/devcasian/League-of-Legends-Spell-Tracker.git
```

```bash
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

## 🎮 Usage

### Managing Champions

- **Double-click (LMB)** on an empty icon → Open champion selection window
- Use search to quickly find the champion you need

### Managing Timers

- **Left-click (LMB)** on an icon → Toggle timer (start/reset)
  - If timer is not active → start cooldown
  - If timer is active → reset cooldown

- **Right-click (RMB)** on an icon → Change ultimate level
  - Cycles through: 6 → 11 → 16 → 6
  - Level is displayed below the icon

### Moving the Window

- **Click on empty area** + drag mouse → Move the overlay window

## 🗂️ Project Structure

```
lol-ult-tracker/
├── run.py                          # Application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # Documentation
├── LICENSE                         # MIT license
├── .gitignore                      # Git ignore rules
├── .gitattributes                  # Git attributes
├── src/                            # Source code
│   ├── overlay.py                  # Main GUI application
│   ├── champion_data.py            # Champion data loader
│   ├── timer.py                    # Cooldown timer logic
│   └── config.py                   # Application settings
└── data/                           # Game data
    ├── champions_ult_cooldowns.json   # Ultimate cooldowns
    └── champion_icons/                # Ultimate icons (171 files)
```

## ⚙️ Configuration

Edit `src/config.py` to change:

```python
OVERLAY_ALPHA = 0.95

ICON_SIZE = 64

TIMER_COLOR = "#ffffff"
COOLDOWN_COLOR = "#e67e22"

TIMER_FONT = ("Arial", 18, "bold")
```

## 🤝 Contributing

Contributions are welcome! If you have suggestions or found a bug:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 TODO

- [ ] Sound notifications when ultimate is ready
- [ ] Support for other abilities (not just ultimates)
- [ ] Theme customization
- [ ] Export/import settings

## 📄 License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ for the League of Legends community**

[Report Bug](https://github.com/devcasian/League-of-Legends-Spell-Tracker/issues) · [Request Feature](https://github.com/devcasian/League-of-Legends-Spell-Tracker/issues)

</div>
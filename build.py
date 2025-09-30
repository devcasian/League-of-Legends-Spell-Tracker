#!/usr/bin/env python3
"""
Build script for creating standalone executable using PyInstaller.
"""

import subprocess
import sys
import shutil
import json
from pathlib import Path

def check_pyinstaller():
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def apply_current_settings():
    """Apply current settings.json values as defaults in config.py before build."""
    settings_file = Path(__file__).parent / "settings.json"
    config_file = Path(__file__).parent / "src" / "config.py"

    if not settings_file.exists():
        print("No settings.json found, using config.py defaults")
        return

    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        with open(config_file, 'r', encoding='utf-8') as f:
            config_lines = f.readlines()

        replacements = {
            'LAYOUT = ': f'LAYOUT = "{settings.get("layout", "horizontal")}"',
            'SOUND_ENABLED = ': f'SOUND_ENABLED = {settings.get("sound_enabled", True)}',
            'SOUND_VOLUME = ': f'SOUND_VOLUME = {settings.get("sound_volume", 1.0)}',
            'SOUND_ALERT_THRESHOLD = ': f'SOUND_ALERT_THRESHOLD = {settings.get("sound_alert_threshold", 1)}',
            'UI_SCALE = ': f'UI_SCALE = {settings.get("ui_scale", 1.0)}',
            'DEFAULT_POSITION = ': f'DEFAULT_POSITION = {settings.get("position")}',
            'DEFAULT_LOCKED = ': f'DEFAULT_LOCKED = {settings.get("locked", False)}',
        }

        new_lines = []
        for line in config_lines:
            modified = False
            for key, value in replacements.items():
                if line.startswith(key):
                    new_lines.append(value + '\n')
                    modified = True
                    break
            if not modified:
                new_lines.append(line)

        with open(config_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        print("✓ Applied current settings as defaults")
    except Exception as e:
        print(f"Warning: Could not apply settings: {e}")
        print("Continuing with existing config.py defaults")

def build():
    spec_file = Path(__file__).parent / "spell-tracker.spec"

    if not spec_file.exists():
        print(f"Error: {spec_file} not found")
        return False

    apply_current_settings()

    print("Building executable...")
    subprocess.check_call([sys.executable, "-m", "PyInstaller", "--clean", str(spec_file)])

    dist_dir = Path(__file__).parent / "dist"
    exe_file = dist_dir / "Spell-Tracker.exe"

    if exe_file.exists():
        print(f"\n✓ Build successful!")
        print(f"Executable: {exe_file}")
        print(f"Size: {exe_file.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print("Error: Build failed")
        return False

    return True

def clean():
    print("Cleaning build directories...")
    for dir_name in ["build", "dist"]:
        dir_path = Path(__file__).parent / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Removed {dir_name}/")

if __name__ == "__main__":
    if "--clean" in sys.argv:
        clean()
        sys.exit(0)

    if not check_pyinstaller():
        print("PyInstaller not found")
        response = input("Install PyInstaller? (y/n): ")
        if response.lower() == 'y':
            install_pyinstaller()
        else:
            print("Aborted")
            sys.exit(1)

    success = build()
    sys.exit(0 if success else 1)

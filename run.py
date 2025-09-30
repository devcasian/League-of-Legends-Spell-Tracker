#!/usr/bin/env python3
"""
League of Legends Spell Tracker
Entry point for the application.
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from overlay import main

if __name__ == "__main__":
    main()
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('data/game_data/champions_ult_cooldowns.json', 'data/game_data'),
        ('data/game_data/summoner_spells_cooldowns.json', 'data/game_data'),
        ('data/game_data/items_haste.json', 'data/game_data'),
        ('data/icons/champions', 'data/icons/champions'),
        ('data/icons/champion_ults', 'data/icons/champion_ults'),
        ('data/icons/summoner_spells', 'data/icons/summoner_spells'),
        ('data/sounds/ult_ready.wav', 'data/sounds'),
        ('data/assets/logo.ico', 'data/assets'),
    ],
    hiddenimports=['overlay', 'champion_data', 'timer', 'config', 'settings', 'auto_loader', 'live_client_api', 'haste_calculator', 'requests', 'urllib3', 'pystray', 'pystray._win32'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Spell-Tracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='data/assets/logo.ico',
)

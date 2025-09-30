# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('data/champions_ult_cooldowns.json', 'data'),
        ('data/summoner_spells_cooldowns.json', 'data'),
        ('data/champion_icons', 'data/champion_icons'),
        ('data/summoner spells', 'data/summoner spells'),
        ('data/ult_ready.wav', 'data'),
        ('data/logo.ico', 'data'),
    ],
    hiddenimports=['overlay', 'champion_data', 'timer', 'config', 'settings', 'pystray', 'pystray._win32'],
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
    icon='data/logo.ico',
)

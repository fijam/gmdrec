# -*- mode: python ; coding: utf-8 -*-
import gooey
gooey_root = os.path.dirname(gooey.__file__)

from PyInstaller.utils.hooks import collect_data_files

datas = []
datas += collect_data_files('unihandecode')
datas += [('settings.conf', '.')]

a = Analysis(
    ['mdrec.py', 'hardware.py', 'logic.py', 'webapi.py', 'settings.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mdrec',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    hide_console='hide-early',
    icon=os.path.join(gooey_root, 'images', 'program_icon.ico')
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='gmdrec',
)

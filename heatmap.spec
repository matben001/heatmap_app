# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['heatmap.py'],
    pathex=[],
    binaries=[],
    datas=[('data_temp', 'data_temp')],
    hiddenimports=['tkinter','pandas','matplotlib.widgets','matplotlib.pyplot','numpy','scipy.interpolate', 'submodules.ldparser.ldparser'],
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
    a.binaries,
    a.datas,
    [],
    name='heatmap',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

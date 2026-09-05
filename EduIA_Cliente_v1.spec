# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


datos = collect_data_files("customtkinter")
datos += [
    ("assets/logo_eduia.png", "assets"),
    ("assets/icono_eduia.ico", "assets"),
]

modulos_ocultos = collect_submodules("pyttsx3.drivers")


a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datos,
    hiddenimports=modulos_ocultos,
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
    name="EduIA",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icono_eduia.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="EduIA",
)

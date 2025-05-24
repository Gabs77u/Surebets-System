# build.spec para PyInstaller
# Garante inclusão de arquivos estáticos, templates e tratamento especial para src/data

block_cipher = None

from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('backend', includes=['**/*.sql', '**/*.json', '**/*.csv'])
datas += collect_data_files('config')
datas += collect_data_files('frontend', includes=['**/*'])
datas += collect_data_files('src/data', includes=['**/*'])

hiddenimports = [
    'psycopg2',
    'dash',
    'dash_bootstrap_components',
    'flask',
    'requests',
    'fastapi',
    'pandas',
    'numpy',
    'APScheduler',
    'python_socketio',
]

import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SurebetsSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['./Code/main.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('./UI/MacOS/start-fa.ui', './UI/MacOS'),
    ('./UI/Windows/start-fa.ui', './UI/Windows'),
	('./UI/MacOS/home-fa.ui', './UI/MacOS'),
	('./UI/Windows/home-fa.ui', './UI/Windows'),
	('./UI/MacOS/book-fa.ui', './UI/MacOS'),
	('./UI/Windows/book-fa.ui', './UI/Windows'),
	('./UI/MacOS/user-fa.ui', './UI/MacOS'),
	('./UI/Windows/user-fa.ui', './UI/Windows'),
	('./UI/MacOS/transaction-fa.ui', './UI/MacOS'),
	('./UI/Windows/transaction-fa.ui', './UI/Windows'),
	('./UI/MacOS/LibSettingsDialog-fa.ui', './UI/MacOS'),
	('./UI/Windows/LibSettingsDialog-fa.ui', './UI/Windows'),
    ],
    hiddenimports=[
	'dogpile.cache',
	'dogpile.cache.backends.file'
    ],
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
    name='EasyLib',
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
    icon='icon-256.ico',
)
app = BUNDLE(
    exe,
    name='EasyLib.app',
    icon='./icon-256.ico',
    bundle_identifier=None,
)

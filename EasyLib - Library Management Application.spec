# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['./Code/main.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('./UI/start-fa.ui', './UI'),
	('./UI/home-fa.ui', './UI'),
	('./UI/book-fa.ui', './UI'),
	('./UI/user-fa.ui', './UI'),
	('./UI/transaction-fa.ui', './UI'),
	('./UI/LibSettingsDialog-fa.ui', './UI'),
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

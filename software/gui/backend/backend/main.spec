import sys
from pathlib import Path

# SPECPATH is provided by PyInstaller - it's the directory containing the spec file
# Navigate from backend/backend/ up to software/client
client_path = Path(SPECPATH).parent.parent.parent / 'client'
sys.path.insert(0, str(client_path))

a = Analysis(
    ['main.py'],
    pathex=[str(client_path)],  # Tell PyInstaller where to find dbay
    binaries=[],
    datas=[
        ('config/vsource_params.json', 'config'),
        ('dbay_control/', 'dbay_control'),
        ('modules/', 'modules'),  # Include module spec files for dynamic loading
    ],
    hiddenimports=['dbay', 'dbay.client', 'dbay.direct', 'dbay.http', 'dbay.state', 
                   'dbay.modules', 'dbay.modules.dac4d', 'dbay.modules.dac16d',
                   'dbay.modules.adc4d', 'dbay.modules.fafd', 'dbay.modules.hic4',
                   'dbay.modules.dac4eth', 'dbay.modules.empty', 'dbay.addons',
                   'dbay.addons.vsource'],
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
    name='dbaybackend',
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
    contents_directory="device-bay_internal"
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='dbaybackend',
)

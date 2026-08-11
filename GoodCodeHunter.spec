# -*- mode: python ; coding: utf-8 -*-

# ===
# 만든 이유: Windows onedir 배포본에 GUI 코드와 로고 리소스를 같은 방식으로 포함해야 한다.
# 코드 설명: app.py를 분석해 GoodCodeHunter.exe와 실행 의존 파일을 dist 폴더에 수집한다.
# ===

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[
        (
            "assets/branding/good-code-hunters-logo.png",
            "assets/branding",
        )
    ],
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
    name="GoodCodeHunter",
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="GoodCodeHunter",
)

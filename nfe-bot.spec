# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from typing import Iterable, List, Tuple

from PyInstaller.building.build_main import Analysis, PYZ, EXE
from PyInstaller.config import CONF as PYI_CONF
from PyInstaller.utils.hooks import (
    collect_all,
    collect_data_files,
    collect_submodules,
    copy_metadata,
)

block_cipher = None

try:
    SPEC_PATH = Path(__file__).resolve()
except NameError:
    SPEC_PATH = Path(PYI_CONF.get("spec", Path.cwd())).resolve()
PROJECT_ROOT = SPEC_PATH.parent
APP_DIR = PROJECT_ROOT / "app"
MAIN_SCRIPT = str(APP_DIR / "interface.py")

PYI_CONF.setdefault("workpath", str(PROJECT_ROOT / "build"))
PYI_CONF.setdefault("distpath", str(PROJECT_ROOT / "dist"))
PYI_CONF.setdefault("specpath", str(PROJECT_ROOT))
# When executing this spec directly (e.g. `python nfe-bot.spec`)
# PyInstaller's global CONF dictionary may not have the `spec` key yet.
# Providing a default path avoids KeyError inside Analysis.
PYI_CONF.setdefault("spec", str(SPEC_PATH))
# PyInstaller expects `code_cache` to be a mapping; provide an empty dict when running
# directly so the Analysis step can register compiled modules without errors.
PYI_CONF.setdefault("code_cache", {})


def _extend_hiddenimports(base: Iterable[str], packages: Iterable[str]) -> List[str]:
    hidden: List[str] = list(base)
    for package in packages:
        try:
            hidden.extend(collect_submodules(package))
        except Exception:
            if package not in hidden:
                hidden.append(package)
    return sorted(set(hidden))


def _extend_datas(base: Iterable[Tuple[str, str]], packages: Iterable[str]) -> List[Tuple[str, str]]:
    data_entries: List[Tuple[str, str]] = list(base)
    for package in packages:
        try:
            data_entries.extend(collect_data_files(package))
        except Exception:
            continue
    return data_entries


def _extend_metadata(base: Iterable[Tuple[str, str]], packages: Iterable[str]) -> List[Tuple[str, str]]:
    metadata_entries: List[Tuple[str, str]] = list(base)
    for package in packages:
        try:
            metadata_entries.extend(copy_metadata(package))
        except Exception:
            continue
    return metadata_entries


_pyside_datas, _pyside_binaries, _pyside_hiddenimports = collect_all("PySide6")
_shiboken_datas, _shiboken_binaries, _shiboken_hiddenimports = collect_all("shiboken6")

datas = [
    (str(APP_DIR / "assets"), "assets"),
    (str(APP_DIR / "view"), "view"),
]
datas.extend(_pyside_datas)
datas.extend(_shiboken_datas)
datas = _extend_datas(
    datas,
    (
        "certifi",
        "pandas",
        "tzdata",
    ),
)
datas = _extend_metadata(
    datas,
    (
        "requests",
        "urllib3",
        "chardet",
        "charset-normalizer",
        "idna",
        "python-dotenv",
        "beautifulsoup4",
        "xmltodict",
        "openpyxl",
        "pandas",
        "numpy",
        "python-dateutil",
        "pytz",
        "tzdata",
        "soupsieve",
        "typing_extensions",
    ),
)

marca_dagua = PROJECT_ROOT / "marca_dagua.png"
if marca_dagua.exists():
    datas.append((str(marca_dagua), "."))

binaries = list(_pyside_binaries) + list(_shiboken_binaries)

hiddenimports = _extend_hiddenimports(
    list(_pyside_hiddenimports) + list(_shiboken_hiddenimports),
    (
        "bs4",
        "certifi",
        "charset_normalizer",
        "chardet",
        "dotenv",
        "idna",
        "numpy",
        "openpyxl",
        "pandas",
        "python_dateutil",
        "pytz",
        "requests",
        "soupsieve",
        "tkinter",
        "typing_extensions",
        "tzdata",
        "urllib3",
        "win32com",
        "xmltodict",
    ),
)

a = Analysis(
    [MAIN_SCRIPT],
    pathex=[str(PROJECT_ROOT), str(APP_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
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
    name="Bot de NF-e",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=str(APP_DIR / "assets" / "nfe-bot-fundo.ico"),
)

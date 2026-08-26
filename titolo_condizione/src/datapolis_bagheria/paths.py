from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
TABLES = OUTPUTS / "tables"
NOTEBOOKS = ROOT / "notebooks"


def ensure_directories() -> None:
    for directory in (RAW, INTERIM, PROCESSED, FIGURES, TABLES, NOTEBOOKS):
        directory.mkdir(parents=True, exist_ok=True)


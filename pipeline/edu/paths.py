from __future__ import annotations

from pathlib import Path

# Il package vive in pipeline/edu/ dentro il repo condiviso: i raw stanno in
# data/raw/edu/ (append-only come il resto di data/raw), le tavole analitiche
# vanno dritte in data/processed/ col prefisso edu_ (sono l'interfaccia che gli
# altri thread già leggono), i report in docs/edu/ e le figure in figures/edu/.
ROOT = Path(__file__).resolve().parents[2]
CONFIG = Path(__file__).resolve().parent / "config"
DATA = ROOT / "data"
RAW = DATA / "raw" / "edu"
PROCESSED = DATA / "processed"
TABLES = PROCESSED
OUTPUTS = ROOT / "docs" / "edu"
FIGURES = ROOT / "figures" / "edu"
NOTEBOOKS = ROOT / "notebooks"


def ensure_directories() -> None:
    for directory in (RAW, PROCESSED, FIGURES, OUTPUTS):
        directory.mkdir(parents=True, exist_ok=True)

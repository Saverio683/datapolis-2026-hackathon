"""Interfaccia col thread educazione (titolo_condizione/).

Copia in data/processed/ — col prefisso edu_ — le tavole del thread educazione
che gli altri thread possono citare: la regola del repo è che i dati condivisi
passino SOLO da data/processed/ (Python scrive, R legge), quindi nessun notebook
o script R legge direttamente dentro titolo_condizione/.

    uv run python -m pipeline.edu

Le sorgenti sono file committati e rigenerabili dalla pipeline di quel thread
(`make process` dentro titolo_condizione/); provenance in
titolo_condizione/data/raw/manifest.csv e docs/sources.md sezione 10.
"""
from pathlib import Path
import shutil

RADICE = Path(__file__).resolve().parents[1]
EDU = RADICE / "titolo_condizione"
PROCESSED = RADICE / "data" / "processed"

TABELLE = {
    "outputs/tables/youth_states_2018_2024.csv": "edu_youth_states_2018_2024.csv",
    "outputs/tables/change_decomposition_2018_2024.csv": "edu_change_decomposition_2018_2024.csv",
    "outputs/tables/gaps_vs_sicily.csv": "edu_gaps_vs_sicily.csv",
    "outputs/tables/matched_peers_2011.csv": "edu_matched_peers_2011.csv",
    "outputs/tables/model_robustness_2011.csv": "edu_model_robustness_2011.csv",
    "outputs/tables/historical_bagheria.csv": "edu_historical_bagheria.csv",
    "outputs/tables/historical_benchmarks_2011.csv": "edu_historical_benchmarks_2011.csv",
    "data/processed/technical_schools.csv": "edu_technical_schools.csv",
}


def copia() -> list[str]:
    copiati = []
    for sorgente, destinazione in TABELLE.items():
        shutil.copyfile(EDU / sorgente, PROCESSED / destinazione)
        copiati.append(destinazione)
    return copiati


if __name__ == "__main__":
    for nome in copia():
        print("ok", nome)

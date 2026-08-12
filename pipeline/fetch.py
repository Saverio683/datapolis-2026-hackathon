"""Scarica i dataset grezzi ISTAT in data/raw/.

Append-only: un file per download, datato, mai sovrascritto. Se il file di oggi
esiste già il download viene saltato, quindi rilanciare lo script è innocuo.

Ogni download aggiunge una riga a data/raw/manifest.csv (url esatto, data, sha256).
Gli endpoint e le trappole di parsing sono documentati in docs/sources.md.

    uv run python -m pipeline.fetch
    uv run python -m pipeline.fetch --dry-run    # stampa cosa scaricherebbe, non tocca la rete
"""

from __future__ import annotations

import csv
import hashlib
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
MANIFEST = RAW / "manifest.csv"

# Bagheria, Comune di Palermo, Sicilia, Italia (codici CL_ITTER107, vedi docs/sources.md)
TERRITORI = "082006+082053+ITG1+IT"

OTTOMILA = "https://ottomilacensus.istat.it/fileadmin/download"
# Confini amministrativi generalizzati. Le annate 1991-2023 non sono più su questo storage
# (verificato 2026-08-12: 404): l'unico vintage disponibile è quello corrente, quindi la
# mappa dei dati 2011 usa confini 2026. Lo scarto va verificato sul join, non assunto.
CARTOGRAFIA = "https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati"
SDMX = "https://esploradati.istat.it/SDMXWS/rest"
SDMX_CSV = "application/vnd.sdmx.data+csv;version=1.0.0"
SDMX_STRUCT = "application/vnd.sdmx.structure+json;version=1.0"


def sdmx_key(n_dimensioni: int) -> str:
    """Chiave SDMX: FREQ e REF_AREA fissati, una posizione vuota per ogni altra dimensione.

    L'ordine è quello della DSD e il numero di posizioni deve combaciare, altrimenti
    il server risponde 422.
    """
    return ".".join(["A", TERRITORI] + [""] * (n_dimensioni - 2))


def _sdmx_url(dataflow: str, n_dimensioni: int) -> str:
    return f"{SDMX}/data/IT1,{dataflow},1.0/{sdmx_key(n_dimensioni)}/ALL/?detail=full"


# Le etichette dei codici (1 = occupato, LSE = licenza media, ...) si prendono da qui
# invece di ricopiarle a mano: la fonte è la stessa dei dati e non va fuori sincrono.
CODELIST = {
    "CL_SEXISTAT1": "genere",
    "CL_FORZE_LAV": "condizione",
    "CL_TITOLO_STUDIO": "titolo_studio",
    "CL_CITTADINANZA": "cittadinanza",
    "CL_STATCIV2": "stato_civile",
    "CL_ETA1": "eta",
}


# (nome, url, header Accept, marcatore atteso nella prima riga)
FONTI: list[tuple[str, str, str | None, bytes]] = [
    # --- 8milaCensus: censimenti 1991-2011, 99 indicatori, formato wide ---
    ("8milacensus_indicatori_sicilia", f"{OTTOMILA}/19/confini/confini_19.csv", None, b"AnnoCP"),
    ("8milacensus_indicatori_prov_reg_italia", f"{OTTOMILA}/Province_Regioni_Italia_confini_2011.csv", None, b"AnnoCP"),
    ("8milacensus_codebook", f"{OTTOMILA}/Descrizione_degli_indicatori_serie_confini_2011.csv", None, b"Descrizione tema"),
    ("8milacensus_legenda_simboli", f"{OTTOMILA}/Legenda_codici_e_simboli_indicatori_ai_confini_2011.csv", None, b";"),
    # --- Censimento permanente via SDMX: serie annuale 2018-2024 ---
    ("censpop_lavoro_eta_genere", _sdmx_url("DF_DCSS_ISTR_LAV_PEN_2_TV_3", 10), SDMX_CSV, b"DATAFLOW"),
    ("censpop_istruzione_eta_genere", _sdmx_url("DF_DCSS_ISTR_LAV_PEN_2_TV_1", 10), SDMX_CSV, b"DATAFLOW"),
    ("censpop_popolazione_eta_singola", _sdmx_url("DF_DCSS_POP_DEMCITMIG_SETA_1", 9), SDMX_CSV, b"DATAFLOW"),
    # --- Cartografia: confini comunali generalizzati, per le mappe ---
    ("istat_confini_comuni", f"{CARTOGRAFIA}/2026/Limiti01012026_g.zip", None, b"PK"),
] + [
    (f"codelist_{nome}", f"{SDMX}/codelist/IT1/{cl}/1.0", SDMX_STRUCT, b"codelists")
    for cl, nome in CODELIST.items()
]


def _estensione(url: str, accept: str | None) -> str:
    if url.endswith(".zip"):
        return ".zip"
    return ".json" if accept and "json" in accept else ".csv"


def scarica(url: str, accept: str | None) -> bytes:
    """GET con timeout e tre tentativi. ISTAT ogni tanto tronca la connessione."""
    # Senza Accept-Language le codelist tornano in inglese ("employed person"): le
    # etichette finiscono nelle figure, e le figure sono in italiano.
    headers = {"Accept-Language": "it"}
    if accept:
        headers["Accept"] = accept
    for tentativo in range(1, 4):
        try:
            risposta = requests.get(url, headers=headers, timeout=180)
            risposta.raise_for_status()
            return risposta.content
        except requests.RequestException as errore:
            if tentativo == 3:
                raise
            print(f"    tentativo {tentativo} fallito ({errore}), riprovo")
            time.sleep(2 * tentativo)
    raise AssertionError("irraggiungibile")


def annota(destinazione: Path, url: str, blob: bytes) -> None:
    intestazione = not MANIFEST.exists()
    with MANIFEST.open("a", newline="", encoding="utf-8") as f:
        scrittore = csv.writer(f)
        if intestazione:
            scrittore.writerow(["scaricato_il", "file", "url", "bytes", "sha256"])
        scrittore.writerow([
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            destinazione.name,
            url,
            len(blob),
            hashlib.sha256(blob).hexdigest(),
        ])


def main(dry_run: bool = False) -> int:
    if dry_run:
        _autocontrollo()
        for nome, url, accept, _ in FONTI:
            print(f"{nome}_{date.today().isoformat()}{_estensione(url, accept)}\n    {url}")
        return 0

    RAW.mkdir(parents=True, exist_ok=True)
    oggi = date.today().isoformat()
    scaricati = saltati = 0

    for nome, url, accept, atteso in FONTI:
        destinazione = RAW / f"{nome}_{oggi}{_estensione(url, accept)}"
        if destinazione.exists():
            print(f"=  {destinazione.name} (già presente)")
            saltati += 1
            continue

        print(f"↓  {nome}")
        blob = scarica(url, accept)
        prima_riga = blob.split(b"\n", 1)[0]
        # La risposta di errore di entrambi i portali è HTML con status 200: senza
        # questo controllo finirebbe in data/raw/ una pagina di errore travestita da CSV.
        if atteso not in prima_riga:
            print(f"   ERRORE {nome}: manca {atteso!r} nella prima riga -> {prima_riga[:200]!r}", file=sys.stderr)
            return 1

        destinazione.write_bytes(blob)
        annota(destinazione, url, blob)
        print(f"   {destinazione.name}  ({len(blob):,} byte)")
        scaricati += 1

    print(f"\n{scaricati} scaricati, {saltati} già presenti -> {RAW}")
    return 0


def _autocontrollo() -> None:
    """Le chiavi SDMX sono l'unico pezzo di logica che può rompersi in silenzio."""
    assert sdmx_key(10) == f"A.{TERRITORI}........", sdmx_key(10)
    assert sdmx_key(9) == f"A.{TERRITORI}.......", sdmx_key(9)
    assert len({nome for nome, *_ in FONTI}) == len(FONTI), "nomi duplicati in FONTI"
    print("autocontrollo ok\n")


if __name__ == "__main__":
    sys.exit(main(dry_run="--dry-run" in sys.argv))

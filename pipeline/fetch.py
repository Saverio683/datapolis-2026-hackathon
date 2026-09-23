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

# I cinque comuni geograficamente più vicini a Bagheria: Santa Flavia, Ficarazzi,
# Villabate, Casteldaccia, Misilmeri. La selezione la calcola notebooks/genere.ipynb sulla
# distanza fra i centroidi ISTAT; qui i codici sono fissi perché fetch non può dipendere
# da data/processed/ (sarebbe un ciclo nella pipeline). Vanno in file raw separati: i raw
# a quattro territori restano quelli che sono e gli altri thread non cambiano numeri.
VICINI = "082067+082035+082079+082023+082048"

# Le dieci "gemelle strutturali" di Bagheria: i comuni più simili per dimensione, densità,
# età, stranieri, abitazioni e distanza da Palermo (matching Mahalanobis su variabili
# non-esito, in notebooks/genere.ipynb -> data/processed/genere_gemelle.csv). Codici fissi
# qui per lo stesso motivo dei vicini: fetch non può leggere data/processed/ senza chiudere
# un ciclo nella pipeline. Santa Flavia e Misilmeri sono anche fra i vicini: i due raw
# restano separati, chi li unisse dovrebbe deduplicare per territorio.
GEMELLE = "082070+082067+082020+082073+082048+082005+082071+081008+084028+084041"

# I 390 comuni siciliani **ai confini 2011**, cioè lo stesso universo su cui il notebook
# calcola i percentili di 8milaCensus. Volutamente 390 e non i 391 di oggi: Misiliscemi
# (081025) è nato nel 2021 staccandosi da Trapani, includerlo cambierebbe il denominatore
# fra le due epoche e renderebbe i percentili non confrontabili.
COMUNI_SICILIA = (
    # Trapani (24)
    "081001", "081002", "081003", "081004", "081005", "081006", "081007", "081008", "081009",
    "081010", "081011", "081012", "081013", "081014", "081015", "081016", "081017", "081018",
    "081019", "081020", "081021", "081022", "081023", "081024",
    # Palermo (82)
    "082001", "082002", "082003", "082004", "082005", "082006", "082007", "082008", "082009",
    "082010", "082011", "082012", "082013", "082014", "082015", "082016", "082017", "082018",
    "082019", "082020", "082021", "082022", "082023", "082024", "082025", "082026", "082027",
    "082028", "082029", "082030", "082031", "082032", "082033", "082034", "082035", "082036",
    "082037", "082038", "082039", "082040", "082041", "082042", "082043", "082044", "082045",
    "082046", "082047", "082048", "082049", "082050", "082051", "082052", "082053", "082054",
    "082055", "082056", "082057", "082058", "082059", "082060", "082061", "082062", "082063",
    "082064", "082065", "082066", "082067", "082068", "082069", "082070", "082071", "082072",
    "082073", "082074", "082075", "082076", "082077", "082078", "082079", "082080", "082081",
    "082082",
    # Messina (108)
    "083001", "083002", "083003", "083004", "083005", "083006", "083007", "083008", "083009",
    "083010", "083011", "083012", "083013", "083014", "083015", "083016", "083017", "083018",
    "083019", "083020", "083021", "083022", "083023", "083024", "083025", "083026", "083027",
    "083028", "083029", "083030", "083031", "083032", "083033", "083034", "083035", "083036",
    "083037", "083038", "083039", "083040", "083041", "083042", "083043", "083044", "083045",
    "083046", "083047", "083048", "083049", "083050", "083051", "083052", "083053", "083054",
    "083055", "083056", "083057", "083058", "083059", "083060", "083061", "083062", "083063",
    "083064", "083065", "083066", "083067", "083068", "083069", "083070", "083071", "083072",
    "083073", "083074", "083075", "083076", "083077", "083078", "083079", "083080", "083081",
    "083082", "083083", "083084", "083085", "083086", "083087", "083088", "083089", "083090",
    "083091", "083092", "083093", "083094", "083095", "083096", "083097", "083098", "083099",
    "083100", "083101", "083102", "083103", "083104", "083105", "083106", "083107", "083108",
    # Agrigento (43)
    "084001", "084002", "084003", "084004", "084005", "084006", "084007", "084008", "084009",
    "084010", "084011", "084012", "084013", "084014", "084015", "084016", "084017", "084018",
    "084019", "084020", "084021", "084022", "084023", "084024", "084025", "084026", "084027",
    "084028", "084029", "084030", "084031", "084032", "084033", "084034", "084035", "084036",
    "084037", "084038", "084039", "084040", "084041", "084042", "084043",
    # Caltanissetta (22)
    "085001", "085002", "085003", "085004", "085005", "085006", "085007", "085008", "085009",
    "085010", "085011", "085012", "085013", "085014", "085015", "085016", "085017", "085018",
    "085019", "085020", "085021", "085022",
    # Enna (20)
    "086001", "086002", "086003", "086004", "086005", "086006", "086007", "086008", "086009",
    "086010", "086011", "086012", "086013", "086014", "086015", "086016", "086017", "086018",
    "086019", "086020",
    # Catania (58)
    "087001", "087002", "087003", "087004", "087005", "087006", "087007", "087008", "087009",
    "087010", "087011", "087012", "087013", "087014", "087015", "087016", "087017", "087018",
    "087019", "087020", "087021", "087022", "087023", "087024", "087025", "087026", "087027",
    "087028", "087029", "087030", "087031", "087032", "087033", "087034", "087035", "087036",
    "087037", "087038", "087039", "087040", "087041", "087042", "087043", "087044", "087045",
    "087046", "087047", "087048", "087049", "087050", "087051", "087052", "087053", "087054",
    "087055", "087056", "087057", "087058",
    # Ragusa (12)
    "088001", "088002", "088003", "088004", "088005", "088006", "088007", "088008", "088009",
    "088010", "088011", "088012",
    # Siracusa (21)
    "089001", "089002", "089003", "089004", "089005", "089006", "089007", "089008", "089009",
    "089010", "089011", "089012", "089013", "089014", "089015", "089016", "089017", "089018",
    "089019", "089020", "089021"
)

# Il server SDMX sta dietro IIS, che taglia il **segmento di path** a ~260 caratteri: oltre
# i 33 codici in una chiave la risposta è 400 "Invalid URL", non 414 (verificato 2026-08-25:
# 33 -> 200, 35 -> 400). Quindi i 390 comuni si scaricano in 12 blocchi.
CODICI_PER_QUERY = 33

OTTOMILA = "https://ottomilacensus.istat.it/fileadmin/download"
# Confini amministrativi generalizzati. Le annate 1991-2023 non sono più su questo storage
# (verificato 2026-08-12: 404): l'unico vintage disponibile è quello corrente, quindi la
# mappa dei dati 2011 usa confini 2026. Lo scarto va verificato sul join, non assunto.
CARTOGRAFIA = "https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati"
# Matrici del pendolarismo: l'unica fonte pubblica con la matrice **origine-destinazione**
# comune per comune (chi parte da Bagheria e dove arriva), incrociata con sesso, motivo,
# mezzo, fascia oraria e durata del tragitto. Il censimento permanente il comune di
# destinazione non lo pubblica (verificato 2026-08-28: LOC_DEST servita solo come
# ALL/SMPUR/OMPUR), quindi senza questa fonte il thread mobilità non ha destinazioni.
# Tre censimenti, stesso passo di 8milaCensus: 1991, 2001, 2011.
PENDOLARISMO = "https://www.istat.it/storage/cartografia/matrici_pendolarismo"
MATPEN_2021 = "https://esploradati.istat.it/databrowser/DWL/PERMPOP/MATPEN"
SDMX = "https://esploradati.istat.it/SDMXWS/rest"
SDMX_CSV = "application/vnd.sdmx.data+csv;version=1.0.0"
SDMX_STRUCT = "application/vnd.sdmx.structure+json;version=1.0"


def sdmx_key(n_dimensioni: int, territori: str = TERRITORI) -> str:
    """Chiave SDMX: FREQ e REF_AREA fissati, una posizione vuota per ogni altra dimensione.

    L'ordine è quello della DSD e il numero di posizioni deve combaciare, altrimenti
    il server risponde 422.
    """
    return ".".join(["A", territori] + [""] * (n_dimensioni - 2))


def _sdmx_url(dataflow: str, n_dimensioni: int, territori: str = TERRITORI) -> str:
    return f"{SDMX}/data/IT1,{dataflow},1.0/{sdmx_key(n_dimensioni, territori)}/ALL/?detail=full"


def _blocchi(codici: tuple[str, ...], quanti: int) -> list[str]:
    """I codici a gruppi di `quanti`, già uniti con il '+' che SDMX vuole nella chiave."""
    return ["+".join(codici[i:i + quanti]) for i in range(0, len(codici), quanti)]


def _sdmx_url_15piu(territori: str) -> str:
    """La tavola lavoro ristretta alla sola classe 15+, cittadinanza e titolo totali.

    Senza il vincolo i 390 comuni sarebbero ~320.000 righe per usarne un quinto: le altre
    classi d'età non servono al confronto con 8milaCensus, che è tutto su 15 anni e più.
    L'ordine delle posizioni è quello della DSD: FREQ, REF_AREA, INDICATOR, GENDER,
    AGE_NOCLASS, CITIZENSHIP, EDU_ATTAIN, CUR_ACT_STAT, LOC_DEST, REAS_COMMUTING.
    """
    chiave = f"A.{territori}...Y_GE15.TOTAL.ALL..."
    return f"{SDMX}/data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_3,1.0/{chiave}/ALL/?detail=full"


def _sdmx_url_15_24(territori: str) -> str:
    """La stessa tavola lavoro ristretta alla classe 15-24: fascia di lavoro del progetto.

    Porta nei 390 comuni il tasso di occupazione e la quota di casalinghe delle 15-24enni,
    finora disponibili solo per i quattro territori, i vicini e le gemelle. Stesse
    posizioni della DSD di _sdmx_url_15piu; "Y15-24" ha la lunghezza di "Y_GE15", quindi
    il vincolo di IIS sul segmento di path resta quello già verificato.
    """
    chiave = f"A.{territori}...Y15-24.TOTAL.ALL..."
    return f"{SDMX}/data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_3,1.0/{chiave}/ALL/?detail=full"


def _sdmx_url_popres_statciv() -> str:
    """Popolazione al 1° gennaio per età singola, sesso e stato civile (DCIS_POPRES1).

    Il censimento permanente NON incrocia lo stato civile a livello comunale: su tutta la
    famiglia DEMCITMIG la dimensione MARITAL_STATUS è servita solo come ALL e una chiave
    esplicita risponde 404 NoRecordsFound (verificato 2026-08-26). La tavola che lo espone
    è DCIS_POPRES1 — popolazione residente al 1° gennaio, base censuaria dal 2019 — che è
    una FONTE DIVERSA dal censimento permanente: stock al 1° gennaio contro media annua,
    mai da mettere in serie con SETA_1. DSD a 6 dimensioni:
    FREQ, REF_AREA, DATA_TYPE (=JAN), SEX (codici legacy 1/2/9), AGE, MARITAL_STATUS.
    """
    return f"{SDMX}/data/IT1,22_289_DF_DCIS_POPRES1_26,1.0/A.{TERRITORI}..../ALL/?detail=full"


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
    # --- Gli stessi due dataflow per i cinque comuni vicini, in file a parte ---
    ("censpop_lavoro_vicini", _sdmx_url("DF_DCSS_ISTR_LAV_PEN_2_TV_3", 10, VICINI), SDMX_CSV, b"DATAFLOW"),
    ("censpop_istruzione_vicini", _sdmx_url("DF_DCSS_ISTR_LAV_PEN_2_TV_1", 10, VICINI), SDMX_CSV, b"DATAFLOW"),
    ("censpop_popolazione_vicini", _sdmx_url("DF_DCSS_POP_DEMCITMIG_SETA_1", 9, VICINI), SDMX_CSV, b"DATAFLOW"),
    # --- La stessa tavola lavoro per le dieci gemelle strutturali: porta il confronto di
    #     fig10 (oggi fermo ai tre censimenti 1991-2011) dentro il censimento permanente ---
    ("censpop_lavoro_gemelle", _sdmx_url("DF_DCSS_ISTR_LAV_PEN_2_TV_3", 10, GEMELLE), SDMX_CSV, b"DATAFLOW"),
    # --- Popolazione per classi quinquennali: unica tavola comunale che copre 2001 e 2011
    #     oltre al 2018-2024, quindi l'unico ponte demografico attraverso il buco 2012-2017 ---
    ("censpop_demografia_classi", _sdmx_url("DF_DCSS_POP_DEMCITMIG_TV_1", 9), SDMX_CSV, b"DATAFLOW"),
    # --- Stato civile per età singola e sesso (DCIS_POPRES1, anni 2019-2026): la copertura
    #     per anno NON è uniforme fra i territori e va verificata in analisi, non assunta ---
    ("popres_stato_civile_eta", _sdmx_url_popres_statciv(), SDMX_CSV, b"DATAFLOW"),
    # --- Matrici origine-destinazione del pendolarismo (censimenti 1991/2001/2011) ---
    ("istat_matrice_pendolarismo_1991", f"{PENDOLARISMO}/matrici_pendolarismo_1991.zip", None, b"PK"),
    ("istat_matrice_pendolarismo_2001", f"{PENDOLARISMO}/matrici_pendolarismo_2001.zip", None, b"PK"),
    ("istat_matrice_pendolarismo_2011", f"{PENDOLARISMO}/matrici_pendolarismo_2011.zip", None, b"PK"),
    # La stessa matrice rifatta sul censimento permanente 2021 — l'anno base del progetto.
    # Non sta nel catalogo del pendolarismo ma dentro IstatData, come dataflow "bulk"
    # (DF_BULK_PEND_LAV_2021_1): l'API dati risponde 404, il file vero è nell'annotazione
    # ATTACHED_DATA_FILES del dataflow. Copre il solo motivo lavoro.
    ("istat_matrice_pendolarismo_lavoro_2021", f"{MATPEN_2021}/matrix_pendoLAVORO_2021.zip", None, b"PK"),
    ("istat_matrice_pendolarismo_lavoro_2021_leggimi", f"{MATPEN_2021}/leggimi_file_matrix_pendoLAVORO_2021.doc", None, b"\xd0\xcf"),
    # --- Cartografia: confini comunali generalizzati, per le mappe ---
    ("istat_confini_comuni", f"{CARTOGRAFIA}/2026/Limiti01012026_g.zip", None, b"PK"),
] + [
    (f"codelist_{nome}", f"{SDMX}/codelist/IT1/{cl}/1.0", SDMX_STRUCT, b"codelists")
    for cl, nome in CODELIST.items()
] + [
    # --- I 390 comuni siciliani sulla sola classe 15+, in 12 blocchi (vedi CODICI_PER_QUERY):
    #     è il denominatore dei percentili regionali, finora disponibile solo al 2011 ---
    (f"censpop_lavoro_15piu_sicilia_{i:02d}", _sdmx_url_15piu(blocco), SDMX_CSV, b"DATAFLOW")
    for i, blocco in enumerate(_blocchi(COMUNI_SICILIA, CODICI_PER_QUERY), start=1)
] + [
    # --- I 390 comuni sulla classe 15-24: variabilità delle variazioni fra comuni simili
    #     (sostituisce la potenza binomiale dei KPI) e posizione di Bagheria in Sicilia ---
    (f"censpop_lavoro_15_24_sicilia_{i:02d}", _sdmx_url_15_24(blocco), SDMX_CSV, b"DATAFLOW")
    for i, blocco in enumerate(_blocchi(COMUNI_SICILIA, CODICI_PER_QUERY), start=1)
] + [
    # --- Rilevazione sulle forze di lavoro (RCFL): incidenza NEET per sesso ed età,
    #     Sicilia e Italia. FONTE DIVERSA dal censimento (campionaria, regionale): è il
    #     NEET 15-34 del bando a scala regionale, mai in serie con il proxy comunale 15-24.
    #     DSD a 10 posizioni: FREQ, REF_AREA, DATA_TYPE, SEX, AGE, LABPROF_STATUS_A,
    #     EURO_LABOUR_STATUS, EDU_LEV_HIGHEST, CITIZENSHIP, ROLE_IN_HOUSEHOLD ---
    ("rcfl_neet_regionale", _sdmx_url("172_931_DF_DCCV_NEET1_11", 10, "ITG1+IT"), SDMX_CSV, b"DATAFLOW"),
]


def _estensione(url: str, accept: str | None) -> str:
    if url.endswith((".zip", ".doc")):
        return url[-4:]
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
            # 600s e non 180: sulle query per età singola il server SDMX accetta la
            # connessione e poi impiega minuti a produrre il corpo (verificato 2026-08-25).
            risposta = requests.get(url, headers=headers, timeout=600)
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


def main(dry_run: bool = False, solo: str | None = None) -> int:
    """--solo <pezzo di nome> scarica una fonte sola: serve per aggiungerne una senza
    riscaricare (e ridatare) tutte le altre."""
    fonti = [f for f in FONTI if solo is None or solo in f[0]]
    if solo is not None and not fonti:
        print(f"nessuna fonte contiene {solo!r}", file=sys.stderr)
        return 1

    if dry_run:
        _autocontrollo()
        for nome, url, accept, _ in fonti:
            print(f"{nome}_{date.today().isoformat()}{_estensione(url, accept)}\n    {url}")
        return 0

    RAW.mkdir(parents=True, exist_ok=True)
    oggi = date.today().isoformat()
    scaricati = saltati = 0

    for nome, url, accept, atteso in fonti:
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
    assert sdmx_key(9, VICINI) == f"A.{VICINI}.......", sdmx_key(9, VICINI)
    assert len({nome for nome, *_ in FONTI}) == len(FONTI), "nomi duplicati in FONTI"
    assert len(COMUNI_SICILIA) == len(set(COMUNI_SICILIA)) == 390, len(COMUNI_SICILIA)
    assert "081025" not in COMUNI_SICILIA, "Misiliscemi non esisteva nel 2011"
    blocchi = _blocchi(COMUNI_SICILIA, CODICI_PER_QUERY)
    assert sum(b.count("+") + 1 for b in blocchi) == 390, blocchi
    # Il vincolo vero non è la lunghezza della URL ma quella del singolo segmento di path:
    # se questa assert salta, il server risponde 400 e il CSV finisce vuoto.
    piu_lungo = max(len(f"A.{b}...Y_GE15.TOTAL.ALL...") for b in blocchi)
    assert piu_lungo <= 254, f"chiave di {piu_lungo} caratteri: IIS taglia a ~260"
    assert all(_sdmx_url_15_24(b).count("Y15-24") == 1 for b in blocchi)
    assert len(_sdmx_url_15_24(blocchi[0])) == len(_sdmx_url_15piu(blocchi[0]))
    print("autocontrollo ok\n")


if __name__ == "__main__":
    argomenti = [a for a in sys.argv[1:] if a.startswith("--solo=")]
    sys.exit(main(dry_run="--dry-run" in sys.argv,
                  solo=argomenti[0].split("=", 1)[1] if argomenti else None))

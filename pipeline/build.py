"""data/raw/ -> data/processed/: quattro tabelle long, nessuna scelta di analisi dentro.

Ogni thread filtra quello che gli serve; qui si normalizza e basta. Le figure non si
costruiscono in R a partire da questi file: si filtrano.

Output:
    territori.csv                  lookup codice -> nome, livello, fonte
    indicatori.csv                 lookup codice 8milaCensus -> nome, tema, descrizione
    codici.csv                     lookup codice SDMX -> etichetta (genere, condizione, ...)
    ottomilacensus_long.csv        99 indicatori x 1991/2001/2011
    censpop_istr_lav_long.csv      lavoro + istruzione per genere ed età, 2018-2024
    tasso_occupazione_eta.csv      occupati / popolazione per classe d'età e genere,
                                   2018-2024 senza il 2020 (manca il numeratore)
    censpop_popolazione_long.csv   popolazione per età singola e genere, 2018-2024
    censpop_lavoro_gemelle_long.csv        lavoro per le 10 gemelle strutturali, 2018-2024
    censpop_lavoro_15piu_sicilia_long.csv  lavoro 15+ per i 390 comuni siciliani, 2018-2024
    censpop_lavoro_15_24_sicilia_long.csv  lavoro 15-24 per i 390 comuni siciliani, 2018-2024
    rcfl_neet_regionale_long.csv   incidenza NEET della rilevazione forze di lavoro per sesso
                                   ed età, Sicilia e Italia (fonte campionaria regionale)
    censpop_demografia_classi_long.csv     popolazione per classi quinquennali, 2001-2024
    popres_stato_civile_long.csv           popolazione al 1° gennaio per età, sesso e
                                           stato civile (DCIS_POPRES1, 2019-2026)
    pendolarismo_od_long.csv       matrice origine-destinazione degli spostamenti per studio
                                   o lavoro (censimenti 2001, 2011 e 2021), origini siciliane
    pendolarismo_mezzo_long.csv    gli stessi spostamenti per mezzo, orario di uscita e
                                   durata del tragitto (solo 2011, stima campionaria)
    pendolarismo_benchmark_long.csv  gli stessi spostamenti aggregati a Italia e Sicilia,
                                   il confronto territoriale che chiede il bando
    pendolarismo_mezzi.csv         lookup codice mezzo -> etichetta

Le descrizioni stanno nei lookup e non nelle tabelle lunghe: ripetute su ogni riga
gonfiavano ottomilacensus_long da 4 a 40 MB. In R è una join in più.

    uv run python -m pipeline.build
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

RADICE = Path(__file__).resolve().parents[1]
RAW = RADICE / "data" / "raw"
PROCESSED = RADICE / "data" / "processed"

# Colonne descrittive dei file 8milaCensus: tutto il resto sono i 99 indicatori.
CHIAVI_8MILA = [
    "AnnoCP",
    "Livello territoriale",
    "Codice Regione 2011",
    "Codice Provincia 2011",
    "Codice comune 2011",
    "Denominazione del territorio",
]


def ultimo(prefisso: str, estensione: str = ".csv") -> Path:
    """Il raw più recente per quel prefisso. I nomi finiscono in _AAAA-MM-GG, l'ordine alfabetico basta."""
    candidati = sorted(RAW.glob(f"{prefisso}_*{estensione}"))
    if not candidati:
        raise SystemExit(f"manca {prefisso}_*{estensione} in data/raw/ — lancia prima: uv run python -m pipeline.fetch")
    return candidati[-1]


def numero_italiano(colonna: pd.Series) -> pd.Series:
    """'5.002.904' -> 5002904.0, '1,6' -> 1.6, '-' -> NaN (dato non disponibile)."""
    return pd.to_numeric(
        colonna.str.strip().str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce",
    )


def codice_territorio(riga: pd.Series) -> str:
    """Codice canonico condiviso fra le due fonti.

    I comuni usano il codice ISTAT a 6 cifre, che combacia con CL_ITTER107 di SDMX.
    Sicilia e Italia usano i codici SDMX, così le due tabelle si uniscono senza mappature.
    Province e altre regioni non esistono in SDMX: prefisso esplicito per non confonderle.
    """
    livello = riga["Livello territoriale"]
    if livello == "1":
        return riga["Codice comune 2011"].zfill(6)
    if livello == "2":
        return "PROV" + riga["Codice Provincia 2011"].zfill(3)
    if livello == "3":
        return "ITG1" if riga["Codice Regione 2011"] == "19" else "REG" + riga["Codice Regione 2011"].zfill(2)
    return "IT"


def costruisci_ottomilacensus() -> tuple[pd.DataFrame, pd.DataFrame]:
    pezzi = []
    for prefisso in ("8milacensus_indicatori_sicilia", "8milacensus_indicatori_prov_reg_italia"):
        grezzo = pd.read_csv(ultimo(prefisso), sep=";", dtype=str, encoding="cp1252", keep_default_na=False)
        # Coda di righe vuote lasciata dall'export Excel: senza questo filtro diventano territori fantasma.
        grezzo = grezzo[grezzo["AnnoCP"].str.strip() != ""]
        pezzi.append(grezzo)
    grezzo = pd.concat(pezzi, ignore_index=True)

    grezzo["territorio"] = grezzo.apply(codice_territorio, axis=1)
    indicatori = [c for c in grezzo.columns if c not in CHIAVI_8MILA and c != "territorio"]

    lungo = grezzo.melt(
        id_vars=["territorio", "Denominazione del territorio", "Livello territoriale", "AnnoCP"],
        value_vars=indicatori,
        var_name="indicatore",
        value_name="valore",
    ).rename(columns={
        "Denominazione del territorio": "nome_territorio",
        "Livello territoriale": "livello",
        "AnnoCP": "anno",
    })

    lungo["valore"] = numero_italiano(lungo["valore"])
    lungo["anno"] = lungo["anno"].astype(int)

    codebook = pd.read_csv(ultimo("8milacensus_codebook"), sep=";", dtype=str, encoding="cp1252")
    codebook.columns = ["tema", "indicatore", "nome_indicatore", "descrizione"]
    codebook["indicatore"] = codebook["indicatore"].str.strip()
    for colonna in ("tema", "nome_indicatore", "descrizione"):
        codebook[colonna] = codebook[colonna].str.replace(r"\s+", " ", regex=True).str.strip()

    orfani = sorted(set(lungo["indicatore"]) - set(codebook["indicatore"]))
    if orfani:
        print(f"   ATTENZIONE: {len(orfani)} indicatori assenti dal codebook: {orfani[:10]}")

    lungo = lungo[["territorio", "nome_territorio", "livello", "anno", "indicatore", "valore"]]
    return lungo, codebook[["indicatore", "nome_indicatore", "tema", "descrizione"]]


def eta_in_anni(colonna: pd.Series) -> pd.Series:
    """'Y15' -> 15. Le classi ('Y15-24') e i totali restano NaN: servono i codici, non un numero."""
    return pd.to_numeric(colonna.str.extract(r"^Y(\d+)$", expand=False), errors="coerce")


def leggi_sdmx(prefisso: str, colonne: dict[str, str]) -> pd.DataFrame:
    grezzo = pd.read_csv(ultimo(prefisso), dtype=str)
    tabella = grezzo[list(colonne)].rename(columns=colonne)
    tabella["valore"] = pd.to_numeric(grezzo["OBS_VALUE"], errors="coerce")
    tabella["anno"] = tabella["anno"].astype(int)
    return tabella


COLONNE_ISTR_LAV = {
    "REF_AREA": "territorio",
    "TIME_PERIOD": "anno",
    "GENDER": "genere",
    "AGE_NOCLASS": "eta",
    "CITIZENSHIP": "cittadinanza",
    "EDU_ATTAIN": "titolo_studio",
    "CUR_ACT_STAT": "condizione",
}

COLONNE_POPOLAZIONE = {
    "REF_AREA": "territorio",
    "TIME_PERIOD": "anno",
    "GENDER": "genere",
    "AGE_NOCLASS": "eta",
    "MARITAL_STATUS": "stato_civile",
    "CITIZENSHIP": "cittadinanza",
}

# Stessa tavola di popolazione ma per classi quinquennali: la dimensione età si chiama
# AGE_CLASS e non AGE_NOCLASS, ed è l'unica differenza rispetto a COLONNE_POPOLAZIONE.
COLONNE_DEMOGRAFIA_CLASSI = {**COLONNE_POPOLAZIONE, "AGE_CLASS": "eta"}
del COLONNE_DEMOGRAFIA_CLASSI["AGE_NOCLASS"]


def costruisci_censpop_istr_lav() -> pd.DataFrame:
    colonne = COLONNE_ISTR_LAV
    pezzi = []
    for prefisso, tavola in (("censpop_lavoro_eta_genere", "lavoro"),
                             ("censpop_istruzione_eta_genere", "istruzione")):
        tabella = leggi_sdmx(prefisso, colonne)
        tabella["tavola"] = tavola
        pezzi.append(tabella)
    lungo = pd.concat(pezzi, ignore_index=True)
    lungo["eta_anni"] = eta_in_anni(lungo["eta"])
    return lungo[["territorio", "anno", "tavola", "genere", "eta", "eta_anni",
                  "cittadinanza", "titolo_studio", "condizione", "valore"]]


# Le uniche classi d'età su cui il censimento permanente pubblica la condizione
# professionale a livello comunale. Y_GE15 è il totale, non una quinta fascia: le altre
# quattro lo compongono, e sommarle a lui conta due volte le stesse persone.
CLASSI_LAVORO = {"Y15-24": "15-24", "Y25-49": "25-49", "Y50-64": "50-64",
                 "Y_GE65": "65+", "Y_GE15": "15+ (totale)"}


def costruisci_tasso_occupazione_eta(istr_lav: pd.DataFrame) -> pd.DataFrame:
    """Occupati (condizione 1) sulla popolazione della classe (condizione 99), per classe d'età.

    Il 2020 sparisce da solo, ed è giusto così: sulla 15-24 la fonte non pubblica nessuna
    riga, sulle altre classi pubblica solo il denominatore. Il rapporto non esiste in
    nessuna classe, e `dropna()` lo lascia fuori invece di scrivere uno zero o un buco
    ambiguo. Chi disegna la serie rimette la riga vuota (`complete()` in R).
    """
    quadro = istr_lav[
        istr_lav["tavola"].eq("lavoro") & istr_lav["eta"].isin(list(CLASSI_LAVORO))
        & istr_lav["cittadinanza"].eq("TOTAL") & istr_lav["titolo_studio"].eq("ALL")
        & istr_lav["condizione"].isin(["1", "99"])
    ].pivot_table(index=["territorio", "anno", "eta", "genere"], columns="condizione",
                  values="valore", aggfunc="first").dropna().reset_index()
    quadro["classe"] = quadro["eta"].map(CLASSI_LAVORO)
    quadro["tasso_occupazione"] = 100 * quadro["1"] / quadro["99"]
    return (quadro.rename(columns={"1": "occupati", "99": "popolazione"})
            [["territorio", "anno", "eta", "classe", "genere", "occupati", "popolazione",
              "tasso_occupazione"]]
            .sort_values(["territorio", "genere", "eta", "anno"], ignore_index=True))


def costruisci_censpop_popolazione() -> pd.DataFrame:
    lungo = leggi_sdmx("censpop_popolazione_eta_singola", COLONNE_POPOLAZIONE)
    lungo["eta_anni"] = eta_in_anni(lungo["eta"])
    return lungo[["territorio", "anno", "genere", "eta", "eta_anni",
                  "stato_civile", "cittadinanza", "valore"]]


def costruisci_censpop_vicini() -> dict[str, pd.DataFrame]:
    """Le stesse due tavole per i cinque comuni vicini a Bagheria, in file a parte.

    Restano separate di proposito: i _long condivisi continuano a contenere quattro
    territori, così nessun altro thread si ritrova numeri diversi senza averlo chiesto.
    Se i raw non ci sono (fetch vecchio), si salta invece di rompere la pipeline di tutti.
    """
    if _mancano("vicini", "censpop_lavoro_vicini", "censpop_istruzione_vicini",
                "censpop_popolazione_vicini"):
        return {}

    uscite: dict[str, pd.DataFrame] = {}
    pezzi = []
    for prefisso, tavola in (("censpop_lavoro_vicini", "lavoro"),
                             ("censpop_istruzione_vicini", "istruzione")):
        tabella = leggi_sdmx(prefisso, COLONNE_ISTR_LAV)
        tabella["tavola"] = tavola
        pezzi.append(tabella)
    istr_lav = pd.concat(pezzi, ignore_index=True)
    istr_lav["eta_anni"] = eta_in_anni(istr_lav["eta"])
    uscite["censpop_istr_lav_vicini_long.csv"] = istr_lav[
        ["territorio", "anno", "tavola", "genere", "eta", "eta_anni",
         "cittadinanza", "titolo_studio", "condizione", "valore"]]

    popolazione = leggi_sdmx("censpop_popolazione_vicini", COLONNE_POPOLAZIONE)
    popolazione["eta_anni"] = eta_in_anni(popolazione["eta"])
    uscite["censpop_popolazione_vicini_long.csv"] = popolazione[
        ["territorio", "anno", "genere", "eta", "eta_anni",
         "stato_civile", "cittadinanza", "valore"]]
    return uscite


def _mancano(solo: str, *prefissi: str) -> bool:
    """True se manca almeno uno dei raw, con l'istruzione per scaricarlo.

    I raw aggiunti dopo il primo giro non ci sono in tutte le copie del repo: si salta
    l'uscita che li usa invece di rompere la pipeline di chi non li ha ancora.
    """
    assenti = [p for p in prefissi if not list(RAW.glob(f"{p}_*.csv"))]
    if assenti:
        print(f"   {', '.join(assenti[:3])}{'...' if len(assenti) > 3 else ''}"
              f" assenti in data/raw/: salto (uv run python -m pipeline.fetch --solo={solo})")
    return bool(assenti)


def costruisci_censpop_gemelle() -> dict[str, pd.DataFrame]:
    """Tavola lavoro per le dieci gemelle strutturali di Bagheria, 2018-2024.

    File a parte per la stessa ragione dei vicini. Attenzione a chi unisse i due:
    Santa Flavia e Misilmeri stanno in entrambi, sommarli conta quei comuni due volte.
    """
    if _mancano("gemelle", "censpop_lavoro_gemelle"):
        return {}
    tabella = leggi_sdmx("censpop_lavoro_gemelle", COLONNE_ISTR_LAV)
    tabella["tavola"] = "lavoro"
    tabella["eta_anni"] = eta_in_anni(tabella["eta"])
    return {"censpop_lavoro_gemelle_long.csv": tabella[
        ["territorio", "anno", "tavola", "genere", "eta", "eta_anni",
         "cittadinanza", "titolo_studio", "condizione", "valore"]]}


def costruisci_censpop_sicilia_15piu() -> dict[str, pd.DataFrame]:
    """I 390 comuni siciliani sulla sola classe 15+, ricomposti dai 12 blocchi del fetch.

    È il denominatore dei percentili regionali, che finora esistevano solo al 2011.
    Il conteggio dei comuni è un assert e non un commento: un blocco tornato vuoto non si
    vede a occhio, i percentili verrebbero fuori lo stesso e sarebbero sbagliati.
    """
    prefissi = [f"censpop_lavoro_15piu_sicilia_{i:02d}" for i in range(1, 13)]
    if _mancano("15piu", *prefissi):
        return {}
    lungo = pd.concat([leggi_sdmx(p, COLONNE_ISTR_LAV) for p in prefissi], ignore_index=True)
    comuni = lungo["territorio"].nunique()
    assert comuni == 390, f"{comuni} comuni invece di 390: un blocco è tornato vuoto"
    assert set(lungo["eta"]) == {"Y_GE15"}, sorted(set(lungo["eta"]))
    return {"censpop_lavoro_15piu_sicilia_long.csv": lungo[
        ["territorio", "anno", "genere", "eta",
         "cittadinanza", "titolo_studio", "condizione", "valore"]]}


def costruisci_censpop_sicilia_15_24() -> dict[str, pd.DataFrame]:
    """I 390 comuni sulla classe 15-24, ricomposti dai 12 blocchi del fetch.

    Stessa costruzione della 15+. Serve a due cose del thread genere: la posizione di
    Bagheria fra i comuni siciliani sulla fascia di lavoro del progetto, e quanto si muove
    senza interventi il tasso di un comune della sua taglia (il metro dei KPI).
    """
    prefissi = [f"censpop_lavoro_15_24_sicilia_{i:02d}" for i in range(1, 13)]
    if _mancano("15_24_sicilia", *prefissi):
        return {}
    lungo = pd.concat([leggi_sdmx(p, COLONNE_ISTR_LAV) for p in prefissi], ignore_index=True)
    comuni = lungo["territorio"].nunique()
    assert comuni == 390, f"{comuni} comuni invece di 390: un blocco è tornato vuoto"
    assert set(lungo["eta"]) == {"Y15-24"}, sorted(set(lungo["eta"]))
    assert not lungo.duplicated(["territorio", "anno", "genere", "condizione"]).any()
    return {"censpop_lavoro_15_24_sicilia_long.csv": lungo[
        ["territorio", "anno", "genere", "eta",
         "cittadinanza", "titolo_studio", "condizione", "valore"]]}


def costruisci_rcfl_neet() -> dict[str, pd.DataFrame]:
    """Incidenza NEET (%) della rilevazione sulle forze di lavoro, Sicilia e Italia.

    FONTE DIVERSA dal censimento: stima campionaria, solo regionale, definizione europea
    (non occupati e non in istruzione né formazione, anche non formale). È il NEET 15-34 del
    bando a scala regionale; il proxy comunale 15-24 «fuori da lavoro e studio» non ci va
    mai in serie. SEX usa i codici legacy ISTAT: 1 maschi, 2 femmine, 9 totale.
    """
    if _mancano("rcfl_neet", "rcfl_neet_regionale"):
        return {}
    grezzo = pd.read_csv(ultimo("rcfl_neet_regionale"), dtype=str)
    totali = {"DATA_TYPE": "NEET_I", "LABPROF_STATUS_A": "99", "EURO_LABOUR_STATUS": "TOT",
              "EDU_LEV_HIGHEST": "99", "CITIZENSHIP": "TOTAL", "ROLE_IN_HOUSEHOLD": "TOT"}
    for colonna, codice in totali.items():
        assert set(grezzo[colonna]) == {codice}, (colonna, sorted(set(grezzo[colonna])))
    tabella = pd.DataFrame({
        "territorio": grezzo["REF_AREA"],
        "anno": grezzo["TIME_PERIOD"].astype(int),
        "genere": grezzo["SEX"].map({"1": "M", "2": "F", "9": "T"}),
        "eta": grezzo["AGE"],
        "neet_pct": pd.to_numeric(grezzo["OBS_VALUE"], errors="coerce"),
    })
    assert tabella["genere"].notna().all() and tabella["neet_pct"].notna().all()
    assert not tabella.duplicated(["territorio", "anno", "genere", "eta"]).any()
    return {"rcfl_neet_regionale_long.csv":
            tabella.sort_values(["territorio", "eta", "genere", "anno"], ignore_index=True)}


def _verifica_15_24(istr_lav: pd.DataFrame, sicilia: pd.DataFrame) -> None:
    """Bagheria e Palermo nella tavola dei 390 = le stesse righe della tavola a 4 territori."""
    chiavi = ["territorio", "anno", "genere", "condizione"]
    quattro = istr_lav[istr_lav["tavola"].eq("lavoro") & istr_lav["eta"].eq("Y15-24")
                       & istr_lav["cittadinanza"].eq("TOTAL") & istr_lav["titolo_studio"].eq("ALL")
                       & istr_lav["territorio"].isin(["082006", "082053"])]
    confronto = quattro.merge(sicilia, on=chiavi, suffixes=("_4", "_390"))
    assert len(confronto) == len(quattro) > 0, (len(confronto), len(quattro))
    scarto = (confronto["valore_4"] - confronto["valore_390"]).abs().max()
    assert scarto == 0, f"le due tavole 15-24 divergono (scarto massimo {scarto})"
    print(f"   verifica 15-24 ok: {len(confronto)} celle di Bagheria e Palermo identiche nelle due tavole")


def costruisci_censpop_demografia_classi() -> dict[str, pd.DataFrame]:
    """Popolazione per classi quinquennali e genere: 2001, 2011 e 2018-2024.

    L'unica tavola comunale che attraversa i due censimenti: SETA_1 parte dal 2018 e le
    età singole solo dal 2021. Le classi Y15-19...Y30-34 ricompongono il 15-34 esatto,
    quindi la serie demografica del target si allunga di vent'anni.
    """
    if _mancano("demografia_classi", "censpop_demografia_classi"):
        return {}
    lungo = leggi_sdmx("censpop_demografia_classi", COLONNE_DEMOGRAFIA_CLASSI)
    return {"censpop_demografia_classi_long.csv": lungo[
        ["territorio", "anno", "genere", "eta", "stato_civile", "cittadinanza", "valore"]]}


COLONNE_POPRES_STATCIV = {
    "REF_AREA": "territorio",
    "TIME_PERIOD": "anno",
    "SEX": "genere",
    "AGE": "eta",
    "MARITAL_STATUS": "stato_civile",
}

# DCIS_POPRES1 usa i codici legacy di CL_SEXISTAT1 (1/2/9): qui si normalizzano ai M/F/T
# del resto della pipeline, così i filtri di notebook e figure non dipendono dalla fonte.
SESSO_LEGACY = {"1": "M", "2": "F", "9": "T"}


def costruisci_popres_stato_civile() -> dict[str, pd.DataFrame]:
    """Popolazione al 1° gennaio per età singola, sesso e stato civile (DCIS_POPRES1).

    Fonte diversa dal censimento permanente (stock al 1° gennaio su base censuaria, dal
    2019, contro la media annua di SETA_1): file a parte, mai in serie con
    censpop_popolazione_long. La copertura per anno non è uniforme fra i territori
    (il 2026 esiste solo per alcuni): si lascia com'è e si verifica in analisi.
    """
    if _mancano("stato_civile", "popres_stato_civile_eta"):
        return {}
    lungo = leggi_sdmx("popres_stato_civile_eta", COLONNE_POPRES_STATCIV)
    lungo["genere"] = lungo["genere"].map(SESSO_LEGACY)
    assert lungo["genere"].notna().all(), "codice sesso fuori dai legacy 1/2/9"
    lungo["eta_anni"] = eta_in_anni(lungo["eta"])
    return {"popres_stato_civile_long.csv": lungo[
        ["territorio", "anno", "genere", "eta", "eta_anni", "stato_civile", "valore"]]}


DIMENSIONI_CODIFICATE = {
    "genere": ["genere"],
    "condizione": ["condizione"],
    "titolo_studio": ["titolo_studio"],
    "cittadinanza": ["cittadinanza"],
    "stato_civile": ["stato_civile"],
    "eta": ["eta"],
}


# I confini escono come tabella di vertici, non come GeoJSON: in R le mappe si disegnano
# con geom_polygon e nessun pacchetto geografico, perché sf non è installabile senza le
# librerie di sistema GDAL/GEOS (vedi CLAUDE.md). La geometria resta lavoro di Python.
COD_REG_SICILIA = 19
CRS_MAPPA = 32633        # WGS 84 / UTM zona 33N: la zona che contiene la Sicilia
SEMPLIFICA_METRI = 100   # i confini "generalizzati" ISTAT sono già lisci, questo toglie i vertici ridondanti


def costruisci_confini_sicilia() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Poligoni dei comuni siciliani come vertici (x, y) più un punto-etichetta per comune."""
    import geopandas as gpd

    archivio = ultimo("istat_confini_comuni", ".zip")
    # encoding esplicito: il DBF della shapefile ISTAT contiene byte UTF-8 ma non dichiara
    # la codepage, e fiona ripiega su latin-1 — «Basicò» usciva «BasicÃ²», e con lui Cefalù,
    # Canicattì, Paternò e altri undici comuni accentati.
    comuni = gpd.read_file(f"zip://{archivio}!Com01012026_g/Com01012026_g_WGS84.shp",
                           encoding="utf-8")
    sicilia = comuni[comuni["COD_REG"].eq(COD_REG_SICILIA)].to_crs(epsg=CRS_MAPPA)
    sicilia = sicilia.assign(geometry=sicilia.geometry.simplify(SEMPLIFICA_METRI, preserve_topology=True))

    righe = []
    for _, comune in sicilia.iterrows():
        # explode: le isole (Eolie, Egadi, Pelagie) sono parti separate dello stesso comune
        # e vanno disegnate come poligoni distinti, non collegate da una linea.
        parti = getattr(comune.geometry, "geoms", [comune.geometry])
        for i_parte, parte in enumerate(parti):
            # anello 0 = contorno esterno, 1+ = buchi (enclave): in ggplot sono subgroup.
            for i_anello, anello in enumerate([parte.exterior, *parte.interiors]):
                x, y = anello.coords.xy
                righe.append(pd.DataFrame({
                    "territorio": comune["PRO_COM_T"].zfill(6),
                    "nome_comune": comune["COMUNE"],
                    "parte": i_parte,
                    "anello": i_anello,
                    "ordine": range(len(x)),
                    "x": pd.Series(x).round(0).astype(int),
                    "y": pd.Series(y).round(0).astype(int),
                }))
    poligoni = pd.concat(righe, ignore_index=True)

    # representative_point() sta dentro il poligono anche per le forme concave, il centroide no.
    punti = sicilia.geometry.representative_point()
    centroidi = pd.DataFrame({
        "territorio": sicilia["PRO_COM_T"].str.zfill(6).values,
        "nome_comune": sicilia["COMUNE"].values,
        "x": punti.x.round(0).astype(int).values,
        "y": punti.y.round(0).astype(int).values,
    })
    return poligoni, centroidi


# --- Matrici del pendolarismo (censimenti 2001 e 2011) ---------------------------------
#
# Tracciato fisso, ma i campi sono separati da spazi e nessuna etichetta contiene spazi:
# `str.split()` basta e non dipende dalle posizioni esatte, che i due anni hanno diverse.
#
# 2011 - due tipi di record sulla stessa popolazione (4,9 M di righe, 28,9 M di individui):
#   S  strati origine x destinazione x sesso x motivo, conteggio ESAUSTIVO (campo `esatto`)
#   L  gli stessi strati aperti anche per mezzo/orario/durata, STIMA CAMPIONARIA (`stima`)
# Nei comuni sopra i 20.000 abitanti - Bagheria è uno - le tre variabili del tipo L sono
# rilevate su un campione: il leggimi ISTAT prescrive `esatto` per tutto ciò che sta nel
# tipo S e `stima` solo quando servono mezzo, orario o durata. Le due tabelle in uscita
# rispettano quella divisione, così nessuno mescola per sbaglio le due variabili.
#
# 2001 - un record per strato, conteggio esaustivo, e il dettaglio di mezzo/orario/durata
# esiste solo per chi si è effettivamente spostato il mercoledì di riferimento. I codici
# mezzo del 2001 non coincidono con quelli del 2011 (il 10 accorpa piedi, bici e altro):
# per questo qui si tiene solo la parte origine-destinazione, comparabile fra i due anni.
MEZZI = {
    "01": "treno", "02": "tram", "03": "metropolitana", "04": "autobus urbano, filobus",
    "05": "corriera, autobus extra-urbano", "06": "autobus aziendale o scolastico",
    "07": "auto privata (conducente)", "08": "auto privata (passeggero)",
    "09": "motocicletta, ciclomotore, scooter", "10": "bicicletta", "11": "altro mezzo",
    "12": "a piedi",
}
# Le classi di 8milaCensus M5/M6/M7, ricostruite dai codici: M6 esclude il 06 (autobus
# aziendale o scolastico), che non è servizio di linea. Verificato in _verifica_pendolarismo.
MEZZO_CLASSE = ({c: "collettivo" for c in ("01", "02", "03", "04", "05")}
                | {"06": "aziendale o scolastico"}
                | {c: "privato a motore" for c in ("07", "08", "09")}
                | {c: "piedi o bici" for c in ("10", "12")} | {"11": "altro"})
DURATE = {"1": "fino a 15 min", "2": "16-30 min", "3": "31-60 min", "4": "oltre 60 min"}
ORARI = {"1": "prima delle 7:15", "2": "7:15-8:14", "3": "8:15-9:14", "4": "dopo le 9:14"}
SESSI = {"1": "M", "2": "F"}
MOTIVI = {"1": "studio", "2": "lavoro"}
LUOGHI = {"1": "dentro", "2": "fuori", "3": "estero"}
PROVINCE_SICILIA = tuple(f"08{c}" for c in range(1, 10))
BAGHERIA = "082006"
PALERMO = "082053"


def _righe_pendolarismo(anno: int, dentro_archivio: str):
    """Righe della matrice con origine in Sicilia o destinazione a Bagheria.

    Il file 2011 è di 307 MB: si legge in streaming dallo zip, senza mai espanderlo su disco
    (data/raw/ resta append-only e l'archivio scaricato è l'unica copia). `split()` senza
    argomenti va bene anche sul 2021, che è tab-separato: nessun campo contiene spazi.
    """
    import zipfile

    nome = ("istat_matrice_pendolarismo_lavoro_2021" if anno == 2021
            else f"istat_matrice_pendolarismo_{anno}")
    with zipfile.ZipFile(ultimo(nome, ".zip")) as archivio:
        with archivio.open(dentro_archivio) as flusso:
            for riga in flusso:
                campi = riga.decode("latin-1").split()
                yield campi


def costruisci_pendolarismo() -> dict[str, pd.DataFrame]:
    def normalizza(origine, destinazione, sesso, motivo, luogo, estero):
        # luogo 3 = all'estero: il comune di destinazione non esiste e i due campi
        # provincia/comune portano il codice dello Stato. Non si inventa un codice ISTAT.
        return (origine, "ESTERO" if luogo == "3" else destinazione,
                SESSI[sesso], MOTIVI[motivo], LUOGHI[luogo])

    od, mezzo, italia = [], [], []

    # --- 2011 ---
    for c in _righe_pendolarismo(2011, "MATRICE PENDOLARISMO 2011/matrix_pendo2011_10112014.txt"):
        tipo, _res, pres, cres, sesso, motivo, luogo, pdest, cdest, estero = c[:10]
        origine, destinazione = pres + cres, pdest + cdest
        siciliano = pres in PROVINCE_SICILIA
        chiave = normalizza(origine, destinazione, sesso, motivo, luogo, estero)
        # Il benchmark nazionale e regionale che chiede il bando si accumula PRIMA del
        # filtro: il ciclo passa comunque sui 4,9 milioni di record, e rileggere 307 MB
        # una seconda volta per l'Italia sarebbe lavoro sprecato.
        if tipo == "S":
            italia.append((2011, "IT", *chiave[2:], int(c[14])))
            if siciliano:
                italia.append((2011, "ITG1", *chiave[2:], int(c[14])))
        if not siciliano and destinazione != BAGHERIA:
            continue
        if tipo == "S":
            # `esatto` c'è sempre; `stima` è ND per chi vive in convivenza (18.726 in Italia),
            # che infatti non ha record di tipo L. Si tiene il conteggio esaustivo.
            od.append((2011, *chiave, int(c[14])))
        elif siciliano:
            mezzo.append((origine, *chiave[2:], destinazione == PALERMO,
                          MEZZI[c[10]], ORARI[c[11]], DURATE[c[12]], float(c[13])))

    # --- 2001: un solo tipo di record, il flag "spostamento del mercoledì" è c[7] ---
    for c in _righe_pendolarismo(2001, "matrix_pendo2001.txt"):
        pres, cres, sesso, motivo, luogo, pdest, cdest = c[:7]
        origine, destinazione = pres + cres, pdest + cdest
        if pres not in PROVINCE_SICILIA and destinazione != BAGHERIA:
            continue
        od.append((2001, *normalizza(origine, destinazione, sesso, motivo, luogo, None), int(c[-1])))

    # --- 2021: censimento permanente, solo lavoro, nessuna disaggregazione per sesso.
    #     Tab-separato con intestazione, il comune è già a sei cifre. La definizione cambia —
    #     "almeno tre giorni a settimana" invece di "giornalmente" — quindi i livelli 2011 e
    #     2021 non stanno in serie: confrontabile è la composizione (dove vanno, su cento che
    #     escono). La colonna `definizione` obbliga a dichiararlo in qualunque figura. ---
    for c in _righe_pendolarismo(2021, "matrix_pendoLAVORO_2021.txt"):
        if c[0] == "Prov_res":
            continue
        _, origine, _, destinazione, persone = c
        luogo = "dentro" if origine == destinazione else "fuori"
        italia.append((2021, "IT", "T", "lavoro", luogo, int(persone)))
        if origine[:3] in PROVINCE_SICILIA:
            italia.append((2021, "ITG1", "T", "lavoro", luogo, int(persone)))
        if origine[:3] in PROVINCE_SICILIA or destinazione == BAGHERIA:
            od.append((2021, origine, destinazione, "T", "lavoro", luogo, int(persone)))

    colonne_od = ["anno", "origine", "destinazione", "genere", "motivo", "luogo", "persone"]
    definizioni = {2001: "giornaliero (censimento 2001)",
                   2011: "giornaliero (censimento 2011)",
                   2021: "almeno 3 giorni a settimana (censimento permanente 2021)"}
    od = (pd.DataFrame(od, columns=colonne_od)
          .groupby(colonne_od[:-1], as_index=False)["persone"].sum()
          .assign(definizione=lambda d: d["anno"].map(definizioni)))
    mezzo = (pd.DataFrame(mezzo, columns=["origine", "genere", "motivo", "luogo",
                                          "verso_palermo", "mezzo", "orario", "durata", "stima"])
             .groupby(["origine", "genere", "motivo", "luogo", "verso_palermo",
                       "mezzo", "orario", "durata"], as_index=False)["stima"].sum())
    colonne_bm = ["anno", "territorio", "genere", "motivo", "luogo", "persone"]
    benchmark = (pd.DataFrame(italia, columns=colonne_bm)
                 .groupby(colonne_bm[:-1], as_index=False)["persone"].sum()
                 .assign(definizione=lambda d: d["anno"].map(definizioni)))
    mezzi = pd.DataFrame({"mezzo": list(MEZZI.values()),
                          "classe": [MEZZO_CLASSE[c] for c in MEZZI]})
    return {"pendolarismo_od_long.csv": od,
            "pendolarismo_benchmark_long.csv": benchmark,
            "pendolarismo_mezzo_long.csv": mezzo,
            "pendolarismo_mezzi.csv": mezzi}


def costruisci_codici(*tabelle: pd.DataFrame) -> pd.DataFrame:
    """Codice -> etichetta, per le sole dimensioni codificate del censimento permanente.

    Tenuto fuori dalle tabelle lunghe (stessa logica di indicatori.csv) e filtrato ai
    codici davvero presenti nei dati: una codelist come CL_ETA1 ha 343 voci, qui ne
    servono venti.
    """
    righe = []
    for dimensione, colonne in DIMENSIONI_CODIFICATE.items():
        usati = set()
        for tabella in tabelle:
            for colonna in colonne:
                if colonna in tabella.columns:
                    usati |= set(tabella[colonna].dropna().astype(str))
        if not usati:
            continue
        contenuto = json.loads(ultimo(f"codelist_{dimensione}", ".json").read_text(encoding="utf-8"))
        for codice in contenuto["data"]["codelists"][0]["codes"]:
            if codice["id"] in usati:
                nomi = codice.get("names") or {}
                righe.append({
                    "dimensione": dimensione,
                    "codice": codice["id"],
                    "etichetta": nomi.get("it") or nomi.get("en") or codice.get("name", ""),
                })
    return pd.DataFrame(righe)


def costruisci_territori(ottomila: pd.DataFrame, *censpop: pd.DataFrame) -> pd.DataFrame:
    livelli = {"1": "comune", "2": "provincia", "3": "regione", "4": "nazione"}
    da_8mila = (ottomila[["territorio", "nome_territorio", "livello"]]
                .drop_duplicates("territorio")
                .assign(livello=lambda d: d["livello"].map(livelli), fonti="8milacensus"))

    codici_sdmx = sorted({c for tabella in censpop for c in tabella["territorio"].unique()})
    noti = set(da_8mila["territorio"])
    extra = pd.DataFrame([{"territorio": c, "nome_territorio": "", "livello": "", "fonti": "censpop"}
                          for c in codici_sdmx if c not in noti])

    territori = pd.concat([da_8mila, extra], ignore_index=True)
    entrambe = territori["territorio"].isin(codici_sdmx) & territori["fonti"].eq("8milacensus")
    territori.loc[entrambe, "fonti"] = "8milacensus+censpop"
    return territori.sort_values("territorio").reset_index(drop=True)


def _verifica(ottomila: pd.DataFrame, istr_lav: pd.DataFrame, popolazione: pd.DataFrame) -> None:
    """I valori spot di docs/sources.md. Se saltano, la trasformazione ha rotto qualcosa."""
    def uno(tabella, **filtri):
        selezione = tabella
        for colonna, valore in filtri.items():
            selezione = selezione[selezione[colonna] == valore]
        assert len(selezione) == 1, f"attesa 1 riga, trovate {len(selezione)} per {filtri}"
        return selezione["valore"].iloc[0]

    neet = uno(ottomila, territorio="082006", anno=2011, indicatore="L4")
    assert neet == 40.1, f"L4 Bagheria 2011 = {neet}, atteso 40.1"
    popolazione_2011 = uno(ottomila, territorio="082006", anno=2011, indicatore="P1")
    assert popolazione_2011 == 54257, f"P1 Bagheria 2011 = {popolazione_2011}, atteso 54257"

    occupati = uno(istr_lav, territorio="082006", anno=2021, tavola="lavoro", genere="M",
                   eta="Y15-24", condizione="1", cittadinanza="TOTAL", titolo_studio="ALL")
    assert occupati == 419, f"occupati M 15-24 Bagheria 2021 = {occupati}, atteso 419"

    tasso = costruisci_tasso_occupazione_eta(istr_lav)
    assert not tasso["anno"].eq(2020).any(), "il 2020 non ha numeratore: non deve avere un tasso"
    bagheria_2024 = tasso[tasso["territorio"].eq("082006") & tasso["anno"].eq(2024)
                          & tasso["genere"].eq("T") & tasso["eta"].eq("Y15-24")]
    assert round(bagheria_2024["tasso_occupazione"].iloc[0], 1) == 12.4, (
        f"tasso 15-24 Bagheria 2024 = {bagheria_2024['tasso_occupazione'].iloc[0]}, atteso 12.4")

    giovani = popolazione[
        popolazione["territorio"].eq("082006") & popolazione["anno"].eq(2021)
        & popolazione["genere"].eq("T") & popolazione["cittadinanza"].eq("TOTAL")
        & popolazione["eta_anni"].between(15, 34)
    ]["valore"].sum()
    assert giovani == 12174, f"popolazione 15-34 Bagheria 2021 = {giovani}, attesa 12174"
    print("   verifica ok: L4=40.1  P1=54257  occupati M 15-24=419  pop 15-34=12174"
          "  tasso 15-24 2024=12,4%")


def _verifica_pendolarismo(od: pd.DataFrame, mezzo: pd.DataFrame, benchmark: pd.DataFrame,
                           ottomila: pd.DataFrame) -> None:
    """La matrice ricostruisce gli indicatori M di 8milaCensus: sei su sei, alla prima cifra.

    Vale come prova di correttezza dell'intero tracciato — se una colonna fosse sfalsata di
    un campo, nessuno dei sei tornerebbe. M1 e M2 non sono qui perché hanno al denominatore
    la popolazione fino a 64 anni, che nella matrice non c'è.
    """
    def pubblicato(codice):
        riga = ottomila[ottomila["territorio"].eq(BAGHERIA) & ottomila["anno"].eq(2011)
                        & ottomila["indicatore"].eq(codice)]
        return riga["valore"].iloc[0]

    b = od[od["anno"].eq(2011) & od["origine"].eq(BAGHERIA)]
    per_motivo = b.pivot_table(index="motivo", columns="luogo", values="persone", aggfunc="sum")
    attesi = {"M3": ("lavoro", pubblicato("M3")), "M4": ("studio", pubblicato("M4"))}
    for codice, (motivo, atteso) in attesi.items():
        nostro = round(100 * per_motivo.loc[motivo, "fuori"] / per_motivo.loc[motivo, "dentro"], 1)
        assert nostro == atteso, f"{codice} Bagheria 2011 = {nostro}, pubblicato {atteso}"

    m = mezzo[mezzo["origine"].eq(BAGHERIA)]
    classe = m["mezzo"].map(dict(zip(MEZZI.values(), (MEZZO_CLASSE[c] for c in MEZZI))))
    quota = lambda selezione: round(100 * m.loc[selezione, "stima"].sum() / m["stima"].sum(), 1)
    controlli = {
        "M5": (quota(classe.eq("privato a motore")), pubblicato("M5")),
        "M6": (quota(classe.eq("collettivo")), pubblicato("M6")),
        "M7": (quota(classe.eq("piedi o bici")), pubblicato("M7")),
        "M8": (quota(m["durata"].isin(["fino a 15 min", "16-30 min"])), pubblicato("M8")),
        "M9": (quota(m["durata"].eq("oltre 60 min")), pubblicato("M9")),
    }
    for codice, (nostro, atteso) in controlli.items():
        assert nostro == atteso, f"{codice} Bagheria 2011 = {nostro}, pubblicato {atteso}"
    # Il 2021 ha un solo controllo possibile — il totale nazionale dichiarato nel leggimi —
    # perché nessun indicatore pubblicato lo riassume. Vale comunque: il file è tab-separato
    # e un campo fuori posto lo farebbe saltare.
    italia_2021 = benchmark.query("anno == 2021 and territorio == 'IT'")["persone"].sum()
    assert italia_2021 == 19_565_808, f"pendolari Italia 2021 = {italia_2021:,}, attesi 19.565.808"
    italia_2011 = benchmark.query("anno == 2011 and territorio == 'IT'")["persone"].sum()
    assert italia_2011 == 28_871_447, f"pendolari Italia 2011 = {italia_2011:,}, attesi 28.871.447"
    print("   verifica pendolarismo ok: M3=76.1 M4=19.6 e "
          + ", ".join(f"{c}={n}" for c, (n, _) in controlli.items())
          + f" dalla matrice 2011; totali Italia 2011 ({italia_2011:,}) e 2021 ({italia_2021:,})"
            " uguali a quelli dichiarati nei leggimi ISTAT")


def main() -> int:
    PROCESSED.mkdir(parents=True, exist_ok=True)

    print("- ottomilacensus")
    ottomila, indicatori = costruisci_ottomilacensus()
    print("- censpop istruzione e lavoro")
    istr_lav = costruisci_censpop_istr_lav()
    print("- censpop popolazione")
    popolazione = costruisci_censpop_popolazione()
    print("- censpop comuni vicini a Bagheria")
    vicini = costruisci_censpop_vicini()
    print("- censpop gemelle strutturali, 390 comuni 15+, classi quinquennali")
    recenti = {**costruisci_censpop_gemelle(),
               **costruisci_censpop_sicilia_15piu(),
               **costruisci_censpop_sicilia_15_24(),
               **costruisci_censpop_demografia_classi(),
               **costruisci_popres_stato_civile()}
    if "censpop_lavoro_15_24_sicilia_long.csv" in recenti:
        _verifica_15_24(istr_lav, recenti["censpop_lavoro_15_24_sicilia_long.csv"])
    print("- rilevazione forze di lavoro: NEET regionale")
    rcfl = costruisci_rcfl_neet()
    print("- territori e codici")
    territori = costruisci_territori(ottomila, istr_lav, popolazione,
                                     *vicini.values(), *recenti.values())
    codici = costruisci_codici(istr_lav, popolazione, *recenti.values())
    print("- confini comunali Sicilia")
    poligoni, centroidi = costruisci_confini_sicilia()
    print("- matrici del pendolarismo 2001 e 2011")
    pendolarismo = costruisci_pendolarismo()

    print("- verifica")
    _verifica(ottomila, istr_lav, popolazione)
    _verifica_pendolarismo(pendolarismo["pendolarismo_od_long.csv"],
                           pendolarismo["pendolarismo_mezzo_long.csv"],
                           pendolarismo["pendolarismo_benchmark_long.csv"], ottomila)

    uscite = {
        "territori.csv": territori,
        "indicatori.csv": indicatori,
        "codici.csv": codici,
        "ottomilacensus_long.csv": ottomila,
        "censpop_istr_lav_long.csv": istr_lav,
        "tasso_occupazione_eta.csv": costruisci_tasso_occupazione_eta(istr_lav),
        "censpop_popolazione_long.csv": popolazione,
        "comuni_sicilia_poligoni.csv": poligoni,
        "comuni_sicilia_centroidi.csv": centroidi,
        **vicini,
        **recenti,
        **rcfl,
        **pendolarismo,
    }
    print()
    for nome, tabella in uscite.items():
        percorso = PROCESSED / nome
        tabella.to_csv(percorso, index=False, encoding="utf-8")
        print(f"  {nome:32} {len(tabella):>8,} righe  {percorso.stat().st_size / 1e6:>6.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())

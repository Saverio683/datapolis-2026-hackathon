"""data/raw/ -> data/processed/: quattro tabelle long, nessuna scelta di analisi dentro.

Ogni thread filtra quello che gli serve; qui si normalizza e basta. Le figure non si
costruiscono in R a partire da questi file: si filtrano.

Output:
    territori.csv                  lookup codice -> nome, livello, fonte
    indicatori.csv                 lookup codice 8milaCensus -> nome, tema, descrizione
    codici.csv                     lookup codice SDMX -> etichetta (genere, condizione, ...)
    ottomilacensus_long.csv        99 indicatori x 1991/2001/2011
    censpop_istr_lav_long.csv      lavoro + istruzione per genere ed età, 2018-2024
    censpop_popolazione_long.csv   popolazione per età singola e genere, 2018-2024
    censpop_lavoro_gemelle_long.csv        lavoro per le 10 gemelle strutturali, 2018-2024
    censpop_lavoro_15piu_sicilia_long.csv  lavoro 15+ per i 390 comuni siciliani, 2018-2024
    censpop_demografia_classi_long.csv     popolazione per classi quinquennali, 2001-2024
    popres_stato_civile_long.csv           popolazione al 1° gennaio per età, sesso e
                                           stato civile (DCIS_POPRES1, 2019-2026)

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
    comuni = gpd.read_file(f"zip://{archivio}!Com01012026_g/Com01012026_g_WGS84.shp")
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

    giovani = popolazione[
        popolazione["territorio"].eq("082006") & popolazione["anno"].eq(2021)
        & popolazione["genere"].eq("T") & popolazione["cittadinanza"].eq("TOTAL")
        & popolazione["eta_anni"].between(15, 34)
    ]["valore"].sum()
    assert giovani == 12174, f"popolazione 15-34 Bagheria 2021 = {giovani}, attesa 12174"
    print("   verifica ok: L4=40.1  P1=54257  occupati M 15-24=419  pop 15-34=12174")


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
               **costruisci_censpop_demografia_classi(),
               **costruisci_popres_stato_civile()}
    print("- territori e codici")
    territori = costruisci_territori(ottomila, istr_lav, popolazione,
                                     *vicini.values(), *recenti.values())
    codici = costruisci_codici(istr_lav, popolazione, *recenti.values())
    print("- confini comunali Sicilia")
    poligoni, centroidi = costruisci_confini_sicilia()

    print("- verifica")
    _verifica(ottomila, istr_lav, popolazione)

    uscite = {
        "territori.csv": territori,
        "indicatori.csv": indicatori,
        "codici.csv": codici,
        "ottomilacensus_long.csv": ottomila,
        "censpop_istr_lav_long.csv": istr_lav,
        "censpop_popolazione_long.csv": popolazione,
        "comuni_sicilia_poligoni.csv": poligoni,
        "comuni_sicilia_centroidi.csv": centroidi,
        **vicini,
        **recenti,
    }
    print()
    for nome, tabella in uscite.items():
        percorso = PROCESSED / nome
        tabella.to_csv(percorso, index=False, encoding="utf-8")
        print(f"  {nome:32} {len(tabella):>8,} righe  {percorso.stat().st_size / 1e6:>6.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())

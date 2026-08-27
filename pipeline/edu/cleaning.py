from __future__ import annotations

import io
import json
import re
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .download import latest_raw
from .paths import PROCESSED, RAW, ensure_directories


BAGHERIA = "082006"
PALERMO = "082053"
KEYS_8MILA = [
    "AnnoCP",
    "Livello territoriale",
    "Codice Regione 2011",
    "Codice Provincia 2011",
    "Codice comune 2011",
    "Denominazione del territorio",
]


def _italian_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.strip().str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce",
    )


def _canonical_territory(row: pd.Series) -> str:
    level = str(row["Livello territoriale"]).strip()
    if level == "1":
        return str(row["Codice comune 2011"]).strip().zfill(6)
    if level == "2":
        return "PROV" + str(row["Codice Provincia 2011"]).strip().zfill(3)
    if level == "3":
        region = str(row["Codice Regione 2011"]).strip().zfill(2)
        return "ITG1" if region == "19" else "REG" + region
    return "IT"


def clean_ottomila() -> tuple[pd.DataFrame, pd.DataFrame]:
    chunks = []
    for source_id in ("ottomila_sicilia", "ottomila_benchmarks"):
        raw = pd.read_csv(
            latest_raw(source_id, "csv"), sep=";", encoding="cp1252", dtype=str,
            keep_default_na=False,
        )
        raw = raw[raw["AnnoCP"].str.strip().ne("")].copy()
        chunks.append(raw)
    wide = pd.concat(chunks, ignore_index=True)
    wide["territorio"] = wide.apply(_canonical_territory, axis=1)
    indicator_columns = [column for column in wide.columns if column not in KEYS_8MILA + ["territorio"]]
    long = wide.melt(
        id_vars=["territorio", "Denominazione del territorio", "Livello territoriale", "AnnoCP"],
        value_vars=indicator_columns,
        var_name="indicatore",
        value_name="valore",
    ).rename(columns={
        "Denominazione del territorio": "nome_territorio",
        "Livello territoriale": "livello",
        "AnnoCP": "anno",
    })
    long["anno"] = pd.to_numeric(long["anno"], errors="raise").astype(int)
    long["livello"] = pd.to_numeric(long["livello"], errors="raise").astype(int)
    long["valore"] = _italian_number(long["valore"])
    long = long.drop_duplicates(["territorio", "livello", "anno", "indicatore"], keep="first")

    codebook = pd.read_csv(latest_raw("ottomila_codebook", "csv"), sep=";", encoding="cp1252", dtype=str)
    codebook.columns = ["tema", "indicatore", "nome_indicatore", "descrizione"]
    codebook["indicatore"] = codebook["indicatore"].str.strip()
    for column in ("tema", "nome_indicatore", "descrizione"):
        codebook[column] = codebook[column].str.replace(r"\s+", " ", regex=True).str.strip()
    return (
        long[["territorio", "nome_territorio", "livello", "anno", "indicatore", "valore"]],
        codebook[["indicatore", "nome_indicatore", "tema", "descrizione"]],
    )


def _read_sdmx(source_id: str) -> pd.DataFrame:
    data = pd.read_csv(latest_raw(source_id, "csv"), dtype=str)
    data["OBS_VALUE"] = pd.to_numeric(data["OBS_VALUE"], errors="coerce")
    data["TIME_PERIOD"] = pd.to_numeric(data["TIME_PERIOD"], errors="raise").astype(int)
    return data


def clean_current_census() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    fields = {
        "REF_AREA": "territorio",
        "TIME_PERIOD": "anno",
        "GENDER": "genere",
        "AGE_NOCLASS": "eta",
        "CITIZENSHIP": "cittadinanza",
        "EDU_ATTAIN": "titolo_studio",
        "CUR_ACT_STAT": "condizione",
        "OBS_VALUE": "valore",
    }
    chunks = []
    for source_id, table in (("census_work", "lavoro"), ("census_education", "istruzione")):
        data = _read_sdmx(source_id)[list(fields)].rename(columns=fields)
        data["tavola"] = table
        chunks.append(data)
    current = pd.concat(chunks, ignore_index=True)
    current["eta_anni"] = pd.to_numeric(current["eta"].str.extract(r"^Y(\d+)$", expand=False), errors="coerce")
    current = current[[
        "territorio", "anno", "tavola", "genere", "eta", "eta_anni",
        "cittadinanza", "titolo_studio", "condizione", "valore",
    ]].drop_duplicates()

    pop_fields = {
        "REF_AREA": "territorio",
        "TIME_PERIOD": "anno",
        "GENDER": "genere",
        "AGE_NOCLASS": "eta",
        "MARITAL_STATUS": "stato_civile",
        "CITIZENSHIP": "cittadinanza",
        "OBS_VALUE": "valore",
    }
    population = _read_sdmx("census_population")[list(pop_fields)].rename(columns=pop_fields)
    population["eta_anni"] = pd.to_numeric(
        population["eta"].str.extract(r"^Y(\d+)$", expand=False), errors="coerce"
    )
    population = population[[
        "territorio", "anno", "genere", "eta", "eta_anni", "stato_civile", "cittadinanza", "valore",
    ]].drop_duplicates()

    commute_fields = {
        "REF_AREA": "territorio",
        "TIME_PERIOD": "anno",
        "GENDER": "genere",
        "LOC_DEST": "destinazione",
        "REAS_COMMUTING": "motivo",
        "OBS_VALUE": "valore",
    }
    commuting = _read_sdmx("census_commuting")[list(commute_fields)].rename(columns=commute_fields)
    commuting = commuting.drop_duplicates()
    return current, population, commuting


def _normalize_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text).strip().upper()


def clean_technical_schools() -> pd.DataFrame:
    schools = pd.read_csv(latest_raw("technical_schools", "csv"), dtype=str)
    schools.columns = [column.strip() for column in schools.columns]
    schools["comune_norm"] = schools["DescrizioneComune"].map(_normalize_text)
    schools["territorio"] = np.select(
        [schools["comune_norm"].eq("BAGHERIA"), schools["comune_norm"].eq("PALERMO")],
        [BAGHERIA, PALERMO],
        default="",
    )
    keep = [
        "AnnoScolastico", "territorio", "DescrizioneComune", "CodiceScuola",
        "DenominazioneScuola", "IndirizzoScuola", "CAPScuola",
        "DescrizioneTipologiaGradoIstruzioneScuola",
    ]
    return schools[keep].drop_duplicates("CodiceScuola").sort_values(["DescrizioneComune", "CodiceScuola"])


def clean_gtfs() -> tuple[pd.DataFrame, pd.DataFrame]:
    archive = latest_raw("palermo_gtfs", "zip")
    with zipfile.ZipFile(archive) as feed:
        required = {"feed_info.txt", "routes.txt", "stops.txt", "trips.txt", "stop_times.txt"}
        missing = required - set(feed.namelist())
        if missing:
            raise ValueError(f"GTFS incompleto: {sorted(missing)}")
        info = pd.read_csv(feed.open("feed_info.txt"), dtype=str)
        routes = pd.read_csv(feed.open("routes.txt"), dtype=str)
        stops = pd.read_csv(feed.open("stops.txt"), dtype=str)
        trips = pd.read_csv(feed.open("trips.txt"), dtype=str)
        stop_times = pd.read_csv(feed.open("stop_times.txt"), dtype=str)

    central_pattern = r"STAZIONE CENTRALE|GIULIO CESARE"
    central_stops = stops[stops["stop_name"].str.contains(central_pattern, case=False, na=False)].copy()
    central_stop_ids = set(central_stops["stop_id"])
    central_trip_ids = set(stop_times[stop_times["stop_id"].isin(central_stop_ids)]["trip_id"])
    central_routes = set(trips[trips["trip_id"].isin(central_trip_ids)]["route_id"])
    summary = pd.DataFrame([{
        "feed_publisher": info.loc[0, "feed_publisher_name"],
        "feed_start_date": info.loc[0, "feed_start_date"],
        "feed_end_date": info.loc[0, "feed_end_date"],
        "feed_version": info.loc[0, "feed_version"],
        "routes": routes["route_id"].nunique(),
        "stops": stops["stop_id"].nunique(),
        "trips": trips["trip_id"].nunique(),
        "central_station_stops": len(central_stop_ids),
        "routes_serving_central_station": len(central_routes),
        "scope_note": "Solo rete urbana AMAT; non include il tratto Bagheria-Palermo.",
    }])
    central = central_stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]].copy()
    return summary, central


def _optional_source_inventory(source_id: str) -> dict[str, object]:
    candidates = sorted(RAW.glob(f"{source_id}_*.csv"))
    if not candidates:
        return {"source_id": source_id, "available": False, "rows": 0, "note": "Download non disponibile al run."}
    path = candidates[-1]
    try:
        data = pd.read_csv(path, sep=None, engine="python", dtype=str)
        return {"source_id": source_id, "available": True, "rows": len(data), "note": path.name}
    except Exception as exc:
        return {"source_id": source_id, "available": False, "rows": 0, "note": f"Parsing fallito: {exc}"}


def _assert_one(data: pd.DataFrame, expected: float, **filters: object) -> None:
    selected = data
    for column, value in filters.items():
        selected = selected[selected[column].eq(value)]
    if len(selected) != 1:
        raise AssertionError(f"attesa una riga per {filters}, trovate {len(selected)}")
    actual = float(selected["valore"].iloc[0])
    if not np.isclose(actual, expected):
        raise AssertionError(f"{filters}: {actual}, atteso {expected}")


def build_clean_data() -> dict[str, object]:
    ensure_directories()
    ottomila, indicators = clean_ottomila()
    current, population, commuting = clean_current_census()
    schools = clean_technical_schools()
    gtfs_summary, central_stops = clean_gtfs()

    _assert_one(ottomila, 40.1, territorio=BAGHERIA, anno=2011, indicatore="L4")
    _assert_one(ottomila, 20.0, territorio=BAGHERIA, anno=2011, indicatore="L14")
    _assert_one(
        current, 734.0, territorio=BAGHERIA, anno=2024, tavola="lavoro", genere="T",
        eta="Y15-24", cittadinanza="TOTAL", titolo_studio="ALL", condizione="1",
    )
    young_2024 = population[
        population["territorio"].eq(BAGHERIA)
        & population["anno"].eq(2024)
        & population["genere"].eq("T")
        & population["cittadinanza"].eq("TOTAL")
        & population["eta_anni"].between(15, 34)
    ]["valore"].sum()
    if not np.isclose(young_2024, 11861):
        raise AssertionError(f"popolazione 15-34 Bagheria 2024={young_2024}, atteso 11861")

    outputs = {
        "edu_ottomilacensus_long.csv": ottomila,
        "edu_indicator_dictionary.csv": indicators,
        "edu_census_education_work_long.csv": current,
        "edu_census_population_long.csv": population,
        "edu_census_commuting_long.csv": commuting,
        "edu_technical_schools.csv": schools,
        "edu_palermo_gtfs_summary.csv": gtfs_summary,
        "edu_palermo_central_station_stops.csv": central_stops,
    }
    for filename, frame in outputs.items():
        frame.to_csv(PROCESSED / filename, index=False, encoding="utf-8")

    optional = [
        _optional_source_inventory("regional_job_offers"),
        _optional_source_inventory("accredited_job_services"),
    ]
    quality = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": {
            "sicilian_municipalities_2011": int(ottomila[(ottomila["livello"].eq(1)) & (ottomila["anno"].eq(2011))]["territorio"].nunique()),
            "ottomila_rows": len(ottomila),
            "current_rows": len(current),
            "commuting_years": sorted(map(int, commuting["anno"].unique())),
            "technical_schools_bagheria": int(schools["territorio"].eq(BAGHERIA).sum()),
            "young_15_34_bagheria_2024": int(young_2024),
            "gtfs_feed_version": str(gtfs_summary.loc[0, "feed_version"]),
        },
        "optional_sources": optional,
        "warnings": [
            "Il titolo di studio e la condizione lavorativa non sono incrociati nei dati comunali disponibili.",
            "Il 2011 usa NEET/occupazione 15-29; il 2018-2024 usa condizioni 15-24: non formano una serie continua.",
            "Il pendolarismo corrente disponibile nel dataflow copre 2018-2019 e non identifica Palermo come destinazione.",
            "Il GTFS AMAT copre Palermo urbano e non il collegamento interurbano da Bagheria.",
        ],
    }
    (PROCESSED / "edu_quality_report.json").write_text(json.dumps(quality, indent=2, ensure_ascii=False), encoding="utf-8")
    return quality

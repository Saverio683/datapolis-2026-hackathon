from __future__ import annotations

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yaml
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_score
from sklearn.preprocessing import StandardScaler

from .cleaning import BAGHERIA, PALERMO
from .paths import CONFIG, PROCESSED, RAW, TABLES, ensure_directories


BENCHMARK_NAMES = {
    BAGHERIA: "Bagheria",
    PALERMO: "Palermo",
    "ITG1": "Sicilia",
    "IT": "Italia",
}
HISTORICAL_INDICATORS = ["I5", "I6", "I7", "I8", "L4", "L14"]
POSITIVE_INDICATORS = {"I6", "I7", "I8", "L14"}
STATUS_LABELS = {
    "occupati": "Occupati",
    "in_cerca": "In cerca di lavoro",
    "studenti": "Studenti",
    "inattivi_non_studenti": "Inattivi non studenti",
    "fuori_lavoro_studio": "Fuori da lavoro e studio",
}


def _config() -> dict[str, object]:
    return yaml.safe_load((CONFIG / "analysis.yml").read_text(encoding="utf-8"))


def _load_clean() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ottomila = pd.read_csv(PROCESSED / "edu_ottomilacensus_long.csv", dtype={"territorio": str})
    current = pd.read_csv(
        PROCESSED / "edu_census_education_work_long.csv",
        dtype={"territorio": str, "condizione": str},
    )
    population = pd.read_csv(PROCESSED / "edu_census_population_long.csv", dtype={"territorio": str})
    commuting = pd.read_csv(PROCESSED / "edu_census_commuting_long.csv", dtype={"territorio": str})
    return ottomila, current, population, commuting


def _value(frame: pd.DataFrame, column: str, **filters: object) -> float:
    selected = frame
    for key, value in filters.items():
        selected = selected[selected[key].eq(value)]
    if len(selected) != 1:
        raise ValueError(f"attesa una riga per {filters}, trovate {len(selected)}")
    return float(selected[column].iloc[0])


def historical_tables(ottomila: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    municipal = ottomila[
        ottomila["livello"].eq(1) & ottomila["indicatore"].isin(HISTORICAL_INDICATORS)
    ].copy()
    municipal["percentile_sicilia"] = (
        municipal.groupby(["anno", "indicatore"])["valore"].rank(pct=True) * 100
    )
    municipal["direzione"] = np.where(
        municipal["indicatore"].isin(POSITIVE_INDICATORS),
        "alto = favorevole",
        "alto = sfavorevole",
    )
    bagheria = municipal[municipal["territorio"].eq(BAGHERIA)].sort_values(
        ["indicatore", "anno"]
    )

    benchmarks = ottomila[
        ottomila["territorio"].isin(BENCHMARK_NAMES)
        & ottomila["anno"].eq(2011)
        & ottomila["indicatore"].isin(HISTORICAL_INDICATORS)
    ].copy()
    benchmarks["territorio_nome"] = benchmarks["territorio"].map(BENCHMARK_NAMES)
    benchmarks = benchmarks[
        ["territorio", "territorio_nome", "anno", "indicatore", "valore"]
    ].sort_values(["indicatore", "territorio_nome"])

    change_rows: list[dict[str, object]] = []
    labels = {
        "I5": "Uscita precoce 15-24",
        "I6": "Diploma/laurea 25-64",
        "I7": "Titolo universitario 30-34",
        "L4": "NEET 15-29",
        "L14": "Occupazione 15-29",
    }
    for indicator, label in labels.items():
        start = bagheria[(bagheria["indicatore"].eq(indicator)) & (bagheria["anno"].eq(1991))].iloc[0]
        end = bagheria[(bagheria["indicatore"].eq(indicator)) & (bagheria["anno"].eq(2011))].iloc[0]
        value_change = float(end["valore"] - start["valore"])
        rank_change = float(end["percentile_sicilia"] - start["percentile_sicilia"])
        favourable_value_change = value_change if indicator in POSITIVE_INDICATORS else -value_change
        favourable_rank_change = rank_change if indicator in POSITIVE_INDICATORS else -rank_change
        change_rows.append({
            "indicatore": indicator,
            "metrica": label,
            "valore_1991": float(start["valore"]),
            "valore_2011": float(end["valore"]),
            "variazione_valore_pp": value_change,
            "percentile_1991": float(start["percentile_sicilia"]),
            "percentile_2011": float(end["percentile_sicilia"]),
            "variazione_percentile": rank_change,
            "miglioramento_assoluto": bool(favourable_value_change > 0),
            "convergenza_relativa": bool(favourable_rank_change > 0),
        })
    return bagheria, benchmarks, pd.DataFrame(change_rows)


def youth_state_table(current: pd.DataFrame) -> pd.DataFrame:
    selected = current[
        current["territorio"].isin(BENCHMARK_NAMES)
        & current["tavola"].eq("lavoro")
        & current["genere"].eq("T")
        & current["eta"].eq("Y15-24")
        & current["cittadinanza"].eq("TOTAL")
        & current["titolo_studio"].eq("ALL")
    ].copy()
    wide = selected.pivot_table(
        index=["territorio", "anno"], columns="condizione", values="valore", aggfunc="first"
    ).reset_index()
    for code in ("1", "12", "4", "5", "7", "24", "99"):
        if code not in wide:
            wide[code] = 0.0
    wide["popolazione"] = wide["99"]
    wide["occupati"] = wide["1"]
    wide["in_cerca"] = wide["12"]
    wide["studenti"] = wide["5"]
    wide["inattivi_non_studenti"] = wide[["4", "7", "24"]].sum(axis=1)
    wide["fuori_lavoro_studio"] = wide["in_cerca"] + wide["inattivi_non_studenti"]
    for column in STATUS_LABELS:
        wide[f"quota_{column}"] = 100 * wide[column] / wide["popolazione"]
    wide["inattivi_su_fuori"] = (
        100 * wide["inattivi_non_studenti"] / wide["fuori_lavoro_studio"]
    )
    wide["territorio_nome"] = wide["territorio"].map(BENCHMARK_NAMES)
    columns = [
        "territorio", "territorio_nome", "anno", "popolazione", "occupati", "in_cerca",
        "studenti", "inattivi_non_studenti", "fuori_lavoro_studio", "quota_occupati",
        "quota_in_cerca", "quota_studenti", "quota_inattivi_non_studenti",
        "quota_fuori_lavoro_studio", "inattivi_su_fuori",
    ]
    return wide[columns].sort_values(["territorio", "anno"])


def education_context_table(current: pd.DataFrame) -> pd.DataFrame:
    selected = current[
        current["territorio"].isin(BENCHMARK_NAMES)
        & current["tavola"].eq("istruzione")
        & current["genere"].eq("T")
        & current["eta"].isin(["Y9-24", "Y25-49"])
        & current["cittadinanza"].eq("TOTAL")
        & current["condizione"].eq("99")
    ].copy()
    wide = selected.pivot_table(
        index=["territorio", "anno", "eta"],
        columns="titolo_studio",
        values="valore",
        aggfunc="first",
    ).reset_index()
    diploma_codes = [code for code in ("USE_IF", "BL", "ML", "RDD", "ML_RDD") if code in wide]
    wide["almeno_diploma"] = wide[diploma_codes].sum(axis=1)
    wide["quota_almeno_diploma"] = 100 * wide["almeno_diploma"] / wide["ALL"]
    wide["territorio_nome"] = wide["territorio"].map(BENCHMARK_NAMES)
    wide["compatibilita"] = np.where(
        wide["eta"].eq("Y9-24"),
        "Proxy educativo: fascia diversa dal lavoro 15-24.",
        "Stessa fascia del lavoro 25-49, ma tavola aggregata separata.",
    )
    return wide[[
        "territorio", "territorio_nome", "anno", "eta", "ALL", "almeno_diploma",
        "quota_almeno_diploma", "compatibilita",
    ]].sort_values(["territorio", "eta", "anno"])


def adult_transition_context(education: pd.DataFrame, current: pd.DataFrame) -> pd.DataFrame:
    work = current[
        current["territorio"].isin(BENCHMARK_NAMES)
        & current["tavola"].eq("lavoro")
        & current["genere"].eq("T")
        & current["eta"].eq("Y25-49")
        & current["cittadinanza"].eq("TOTAL")
        & current["titolo_studio"].eq("ALL")
        & current["condizione"].isin(["1", "99"])
    ].pivot_table(
        index=["territorio", "anno"], columns="condizione", values="valore", aggfunc="first"
    ).reset_index()
    work["quota_occupati_25_49"] = 100 * work["1"] / work["99"]
    edu = education[education["eta"].eq("Y25-49")][
        ["territorio", "anno", "quota_almeno_diploma"]
    ]
    merged = edu.merge(
        work[["territorio", "anno", "quota_occupati_25_49"]],
        on=["territorio", "anno"],
        how="left",
    )
    merged["territorio_nome"] = merged["territorio"].map(BENCHMARK_NAMES)
    merged["nota"] = (
        "Aggregati separati sulla stessa fascia; non misura l'occupazione dei diplomati."
    )
    return merged[[
        "territorio", "territorio_nome", "anno", "quota_almeno_diploma",
        "quota_occupati_25_49", "nota",
    ]].sort_values(["territorio", "anno"])


def youth_population_table(population: pd.DataFrame) -> pd.DataFrame:
    selected = population[
        population["territorio"].isin(BENCHMARK_NAMES)
        & population["genere"].eq("T")
        & population["cittadinanza"].eq("TOTAL")
        & population["eta_anni"].between(15, 34)
    ]
    result = selected.groupby(["territorio", "anno"], as_index=False)["valore"].sum()
    result = result.rename(columns={"valore": "popolazione_15_34"}).sort_values(
        ["territorio", "anno"]
    )
    result["territorio_nome"] = result["territorio"].map(BENCHMARK_NAMES)
    first = result.groupby("territorio")["popolazione_15_34"].transform("first")
    result["indice_primo_anno_100"] = 100 * result["popolazione_15_34"] / first
    result["variazione_da_primo_anno_pct"] = result["indice_primo_anno_100"] - 100
    return result[[
        "territorio", "territorio_nome", "anno", "popolazione_15_34",
        "indice_primo_anno_100", "variazione_da_primo_anno_pct",
    ]]


def recent_panel(
    youth: pd.DataFrame, adult: pd.DataFrame, population: pd.DataFrame
) -> pd.DataFrame:
    panel = youth.merge(
        adult.drop(columns=["territorio_nome", "nota"]),
        on=["territorio", "anno"],
        how="left",
    ).merge(
        population.drop(columns=["territorio_nome"]),
        on=["territorio", "anno"],
        how="left",
    )
    panel["territorio_nome"] = panel["territorio"].map(BENCHMARK_NAMES)
    return panel.sort_values(["territorio", "anno"])


def gap_table(youth: pd.DataFrame, adult: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    youth_metrics = {
        "quota_occupati": ("Occupazione 15-24", "alto = favorevole"),
        "quota_in_cerca": ("In cerca di lavoro 15-24", "dipende dal contesto"),
        "quota_inattivi_non_studenti": ("Inattivi non studenti 15-24", "alto = sfavorevole"),
        "quota_fuori_lavoro_studio": ("Fuori da lavoro e studio 15-24", "alto = sfavorevole"),
    }
    for metric, (label, direction) in youth_metrics.items():
        wide = youth.pivot(index="anno", columns="territorio", values=metric)
        for year, row in wide.dropna(subset=[BAGHERIA, "ITG1"]).iterrows():
            rows.append({
                "dominio": "giovani",
                "metrica": metric,
                "metrica_label": label,
                "anno": int(year),
                "bagheria": float(row[BAGHERIA]),
                "sicilia": float(row["ITG1"]),
                "gap_bagheria_sicilia_pp": float(row[BAGHERIA] - row["ITG1"]),
                "direzione": direction,
            })
    adult_metrics = {
        "quota_almeno_diploma": ("Almeno diploma 25-49", "alto = favorevole"),
        "quota_occupati_25_49": ("Occupazione 25-49", "alto = favorevole"),
    }
    for metric, (label, direction) in adult_metrics.items():
        wide = adult.pivot(index="anno", columns="territorio", values=metric)
        for year, row in wide.dropna(subset=[BAGHERIA, "ITG1"]).iterrows():
            rows.append({
                "dominio": "adulti",
                "metrica": metric,
                "metrica_label": label,
                "anno": int(year),
                "bagheria": float(row[BAGHERIA]),
                "sicilia": float(row["ITG1"]),
                "gap_bagheria_sicilia_pp": float(row[BAGHERIA] - row["ITG1"]),
                "direzione": direction,
            })
    return pd.DataFrame(rows).sort_values(["dominio", "metrica", "anno"])


def change_decomposition(youth: pd.DataFrame, baseline: int = 2018, end: int = 2024) -> pd.DataFrame:
    bagheria = youth[youth["territorio"].eq(BAGHERIA)].set_index("anno")
    p0 = float(bagheria.loc[baseline, "popolazione"])
    p1 = float(bagheria.loc[end, "popolazione"])
    rows: list[dict[str, object]] = []
    for metric in STATUS_LABELS:
        count0 = float(bagheria.loc[baseline, metric])
        count1 = float(bagheria.loc[end, metric])
        share0 = float(bagheria.loc[baseline, f"quota_{metric}"])
        share1 = float(bagheria.loc[end, f"quota_{metric}"])
        population_effect = (p1 - p0) * share0 / 100
        rate_effect = p1 * (share1 - share0) / 100
        rows.append({
            "metrica": metric,
            "metrica_label": STATUS_LABELS[metric],
            "anno_iniziale": baseline,
            "anno_finale": end,
            "conteggio_iniziale": count0,
            "conteggio_finale": count1,
            "variazione_conteggio": count1 - count0,
            "quota_iniziale_pct": share0,
            "quota_finale_pct": share1,
            "variazione_quota_pp": share1 - share0,
            "effetto_popolazione": population_effect,
            "effetto_tasso": rate_effect,
            "check_decomposizione": (count1 - count0) - population_effect - rate_effect,
        })
    return pd.DataFrame(rows)


def commuting_context(commuting: pd.DataFrame, ottomila: pd.DataFrame) -> pd.DataFrame:
    current = commuting[
        commuting["territorio"].isin(BENCHMARK_NAMES)
        & commuting["genere"].eq("T")
        & commuting["motivo"].eq("WK")
        & commuting["anno"].eq(commuting["anno"].max())
    ].pivot_table(
        index=["territorio", "anno"], columns="destinazione", values="valore", aggfunc="first"
    ).reset_index()
    current["quota_lavoratori_fuori_comune_sui_pendolari"] = 100 * current["OMPUR"] / current["ALL"]
    current["territorio_nome"] = current["territorio"].map(BENCHMARK_NAMES)
    old = ottomila[
        ottomila["territorio"].isin(BENCHMARK_NAMES)
        & ottomila["anno"].eq(2011)
        & ottomila["indicatore"].isin(["M2", "M6"])
    ].pivot_table(index="territorio", columns="indicatore", values="valore", aggfunc="first").reset_index()
    merged = current.merge(old, on="territorio", how="left")
    merged["nota"] = "Appendice: il 2019 non identifica Palermo; M2 e M6 hanno denominatori diversi."
    return merged[[
        "territorio", "territorio_nome", "anno", "ALL", "SMPUR", "OMPUR",
        "quota_lavoratori_fuori_comune_sui_pendolari", "M2", "M6", "nota",
    ]]


def _municipal_wide(ottomila: pd.DataFrame) -> pd.DataFrame:
    return ottomila[
        ottomila["livello"].eq(1) & ottomila["anno"].eq(2011)
    ].pivot(index=["territorio", "nome_territorio"], columns="indicatore", values="valore")


def peer_table(ottomila: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    cfg = _config()["peer_matching"]
    n_peers = int(cfg["n_peers"])
    wide = _municipal_wide(ottomila).copy()
    wide["logP1"] = np.log(wide["P1"])
    features = list(cfg["features"])
    outcomes = ["L14", "L4"]
    complete = wide[features + outcomes].dropna().copy()
    scaled = StandardScaler().fit_transform(complete[features])
    bagheria_position = list(complete.index).index((BAGHERIA, "Bagheria"))
    complete["distanza_standardizzata"] = np.sqrt(
        ((scaled - scaled[bagheria_position]) ** 2).sum(axis=1)
    )
    bagheria_population = float(wide.loc[(BAGHERIA, "Bagheria"), "P1"])
    low = bagheria_population * float(cfg["population_ratio_min"])
    high = bagheria_population * float(cfg["population_ratio_max"])
    candidates = complete[np.exp(complete["logP1"]).between(low, high)].copy()
    peers = candidates.sort_values("distanza_standardizzata").iloc[1:n_peers + 1].copy()
    bagheria = complete.loc[[(BAGHERIA, "Bagheria")]].copy()
    result = pd.concat([bagheria, peers]).reset_index()
    result["ruolo"] = np.where(result["territorio"].eq(BAGHERIA), "Bagheria", "Peer")
    summary = {
        "n_peers": n_peers,
        "candidate_municipalities": int(len(candidates) - 1),
        "population_caliper_low": low,
        "population_caliper_high": high,
        "peer_median_youth_employment": float(peers["L14"].median()),
        "bagheria_youth_employment": float(bagheria["L14"].iloc[0]),
        "employment_gap_vs_peer_median": float(bagheria["L14"].iloc[0] - peers["L14"].median()),
        "peer_median_neet": float(peers["L4"].median()),
        "bagheria_neet": float(bagheria["L4"].iloc[0]),
        "neet_gap_vs_peer_median": float(bagheria["L4"].iloc[0] - peers["L4"].median()),
    }
    return result[[
        "territorio", "nome_territorio", "ruolo", "distanza_standardizzata",
        *features, *outcomes,
    ]], summary


def model_robustness(ottomila: pd.DataFrame) -> pd.DataFrame:
    config = _config()["analysis"]
    bootstrap_samples = int(config["bootstrap_samples"])
    seed = int(config["random_seed"])
    wide = _municipal_wide(ottomila).copy()
    wide["logP1"] = np.log(wide["P1"])
    models = {
        "A_istruzione": ["I5", "I6", "I7"],
        "B_istruzione_mobilita": ["I5", "I6", "I7", "M2"],
        "C_contesto_territoriale": [
            "I5", "I6", "I7", "M2", "logP1", "P10", "P12", "P13", "A1"
        ],
    }
    rng = np.random.default_rng(seed)
    rows: list[dict[str, object]] = []
    for outcome in ("L14", "L4"):
        for model_name, features in models.items():
            complete = wide[features + [outcome]].dropna().copy()
            target = wide.loc[(BAGHERIA, "Bagheria"), features].to_numpy(float).reshape(1, -1)
            data = complete.drop(index=(BAGHERIA, "Bagheria"))
            X = data[features].to_numpy(float)
            y = data[outcome].to_numpy(float)
            estimator = LinearRegression().fit(X, y)
            observed = float(wide.loc[(BAGHERIA, "Bagheria"), outcome])
            predicted = float(estimator.predict(target)[0])
            residual = observed - predicted
            folds = KFold(n_splits=10, shuffle=True, random_state=seed)
            boot_residuals: list[float] = []
            for _ in range(bootstrap_samples):
                sample = rng.integers(0, len(data), len(data))
                boot = LinearRegression().fit(X[sample], y[sample])
                boot_residuals.append(observed - float(boot.predict(target)[0]))
            low, high = np.percentile(boot_residuals, [2.5, 97.5])
            rows.append({
                "outcome": outcome,
                "modello": model_name,
                "n_comuni_training": len(data),
                "r2_in_sample": float(estimator.score(X, y)),
                "r2_cv_10fold": float(
                    cross_val_score(LinearRegression(), X, y, cv=folds, scoring="r2").mean()
                ),
                "osservato_bagheria": observed,
                "previsto_bagheria": predicted,
                "residuo_bagheria": residual,
                "residuo_ci95_basso": float(low),
                "residuo_ci95_alto": float(high),
                "uso": "Robustezza in appendice; nessuna interpretazione causale individuale.",
            })
    return pd.DataFrame(rows)


def source_inventory(
    ottomila: pd.DataFrame,
    current: pd.DataFrame,
    population: pd.DataFrame,
    commuting: pd.DataFrame,
) -> pd.DataFrame:
    manifest = pd.read_csv(RAW / "manifest.csv")
    latest = manifest.sort_values("checked_at_utc").groupby("source_id", as_index=False).tail(1)
    by_id = latest.set_index("source_id")

    def status(ids: list[str]) -> str:
        values = by_id.reindex(ids)["status"].fillna("missing")
        return "available" if values.isin(["downloaded", "cached"]).all() else ", ".join(values.unique())

    def raw_bytes(ids: list[str]) -> int:
        return int(pd.to_numeric(by_id.reindex(ids)["bytes"], errors="coerce").fillna(0).sum())

    schools = pd.read_csv(PROCESSED / "edu_technical_schools.csv", dtype=str)
    gtfs = pd.read_csv(PROCESSED / "edu_palermo_gtfs_summary.csv")
    rows = [
        {
            "fonte": "Istat 8milaCensus",
            "dataset": "Indicatori comunali e benchmark",
            "stato": status(["ottomila_sicilia", "ottomila_benchmarks", "ottomila_codebook"]),
            "periodo": "1991, 2001, 2011",
            "grana": "territorio × anno × indicatore",
            "righe_pulite": len(ottomila),
            "dimensione_raw_bytes": raw_bytes(["ottomila_sicilia", "ottomila_benchmarks", "ottomila_codebook"]),
            "uso": "Trend storico, benchmark, peer matching",
            "ruolo": "core",
            "limite": "Ultimo anno 2011; definizioni diverse dalle tavole recenti.",
        },
        {
            "fonte": "IstatData SDMX",
            "dataset": "Condizione professionale",
            "stato": status(["census_work"]),
            "periodo": "2018-2019, 2021-2024",
            "grana": "territorio × anno × età × condizione",
            "righe_pulite": int(current["tavola"].eq("lavoro").sum()),
            "dimensione_raw_bytes": raw_bytes(["census_work"]),
            "uso": "Stati 15-24 e occupazione 25-49",
            "ruolo": "core",
            "limite": "2020 assente; nessun incrocio comunale titolo × lavoro.",
        },
        {
            "fonte": "IstatData SDMX",
            "dataset": "Titolo di studio",
            "stato": status(["census_education"]),
            "periodo": "2018-2024",
            "grana": "territorio × anno × età × titolo",
            "righe_pulite": int(current["tavola"].eq("istruzione").sum()),
            "dimensione_raw_bytes": raw_bytes(["census_education"]),
            "uso": "Capitale umano 9-24 e 25-49",
            "ruolo": "core",
            "limite": "Tavola separata dalla condizione lavorativa.",
        },
        {
            "fonte": "IstatData SDMX",
            "dataset": "Popolazione per età",
            "stato": status(["census_population"]),
            "periodo": "2021-2024",
            "grana": "territorio × anno × età singola",
            "righe_pulite": len(population),
            "dimensione_raw_bytes": raw_bytes(["census_population"]),
            "uso": "Denominatore e popolazione 15-34",
            "ruolo": "core",
            "limite": "La variazione demografica non identifica la migrazione.",
        },
        {
            "fonte": "IstatData SDMX",
            "dataset": "Pendolarismo",
            "stato": status(["census_commuting"]),
            "periodo": "2018-2019",
            "grana": "territorio × anno × motivo × destinazione aggregata",
            "righe_pulite": len(commuting),
            "dimensione_raw_bytes": raw_bytes(["census_commuting"]),
            "uso": "Contesto in appendice",
            "ruolo": "appendice",
            "limite": "Non identifica Palermo come destinazione.",
        },
        {
            "fonte": "Ministero dell'Istruzione",
            "dataset": "Anagrafe istituti tecnici",
            "stato": status(["technical_schools"]),
            "periodo": str(schools["AnnoScolastico"].max()),
            "grana": "sede scolastica",
            "righe_pulite": len(schools),
            "dimensione_raw_bytes": raw_bytes(["technical_schools"]),
            "uso": "Canali operativi della policy",
            "ruolo": "policy",
            "limite": "Anagrafica di sedi, non esiti scolastici o lavorativi.",
        },
        {
            "fonte": "Comune di Palermo / AMAT",
            "dataset": "GTFS rete urbana",
            "stato": status(["palermo_gtfs"]),
            "periodo": str(gtfs.loc[0, "feed_version"]),
            "grana": "fermate, linee e corse",
            "righe_pulite": int(gtfs.loc[0, "trips"]),
            "dimensione_raw_bytes": raw_bytes(["palermo_gtfs"]),
            "uso": "Contesto in appendice",
            "ruolo": "appendice",
            "limite": "Rete urbana; non copre il collegamento Bagheria-Palermo.",
        },
        {
            "fonte": "Open Data Regione Siciliana",
            "dataset": "Offerte e operatori dei servizi al lavoro",
            "stato": status(["regional_job_offers", "accredited_job_services"]),
            "periodo": "metadati non correnti",
            "grana": "offerta / sede operatore",
            "righe_pulite": 0,
            "dimensione_raw_bytes": raw_bytes(["regional_job_offers", "accredited_job_services"]),
            "uso": "Nessun uso quantitativo",
            "ruolo": "non usata",
            "limite": "Endpoint HTTP 502 al run; esclusa dalle conclusioni.",
        },
    ]
    return pd.DataFrame(rows)


def kpi_dashboard(
    historical_benchmarks: pd.DataFrame,
    youth: pd.DataFrame,
    adult: pd.DataFrame,
) -> pd.DataFrame:
    hist = historical_benchmarks.pivot(index="indicatore", columns="territorio", values="valore")
    rows: list[dict[str, object]] = []
    for code, label, direction in [
        ("I8", "Almeno licenza media 15-19", "alto = favorevole"),
        ("I5", "Uscita precoce 15-24", "alto = sfavorevole"),
        ("L4", "NEET 15-29", "alto = sfavorevole"),
        ("L14", "Occupazione 15-29", "alto = favorevole"),
    ]:
        rows.append({
            "periodo": "2011",
            "metrica": label,
            "bagheria_pct": float(hist.loc[code, BAGHERIA]),
            "sicilia_pct": float(hist.loc[code, "ITG1"]),
            "gap_pp": float(hist.loc[code, BAGHERIA] - hist.loc[code, "ITG1"]),
            "direzione": direction,
            "definizione": "Indicatore 8milaCensus; fascia indicata nel nome.",
        })
    youth24 = youth[youth["anno"].eq(2024)].set_index("territorio")
    for metric, label, direction in [
        ("quota_occupati", "Occupazione 15-24", "alto = favorevole"),
        ("quota_inattivi_non_studenti", "Inattivi non studenti 15-24", "alto = sfavorevole"),
        ("quota_fuori_lavoro_studio", "Fuori da lavoro e studio 15-24", "alto = sfavorevole"),
    ]:
        rows.append({
            "periodo": "2024",
            "metrica": label,
            "bagheria_pct": float(youth24.loc[BAGHERIA, metric]),
            "sicilia_pct": float(youth24.loc["ITG1", metric]),
            "gap_pp": float(youth24.loc[BAGHERIA, metric] - youth24.loc["ITG1", metric]),
            "direzione": direction,
            "definizione": "Ricostruzione dalla tavola IstatData 15-24.",
        })
    adult24 = adult[adult["anno"].eq(2024)].set_index("territorio")
    for metric, label in [
        ("quota_almeno_diploma", "Almeno diploma 25-49"),
        ("quota_occupati_25_49", "Occupazione 25-49"),
    ]:
        rows.append({
            "periodo": "2024",
            "metrica": label,
            "bagheria_pct": float(adult24.loc[BAGHERIA, metric]),
            "sicilia_pct": float(adult24.loc["ITG1", metric]),
            "gap_pp": float(adult24.loc[BAGHERIA, metric] - adult24.loc["ITG1", metric]),
            "direzione": "alto = favorevole",
            "definizione": "Aggregati separati sulla stessa fascia 25-49.",
        })
    return pd.DataFrame(rows)


def finding_summary(
    historical_change: pd.DataFrame,
    youth: pd.DataFrame,
    gaps: pd.DataFrame,
    adult: pd.DataFrame,
    peers: dict[str, float],
) -> pd.DataFrame:
    b18 = youth[(youth["territorio"].eq(BAGHERIA)) & (youth["anno"].eq(2018))].iloc[0]
    b24 = youth[(youth["territorio"].eq(BAGHERIA)) & (youth["anno"].eq(2024))].iloc[0]
    s24 = youth[(youth["territorio"].eq("ITG1")) & (youth["anno"].eq(2024))].iloc[0]
    adult_b18 = adult[(adult["territorio"].eq(BAGHERIA)) & (adult["anno"].eq(2018))].iloc[0]
    adult_b24 = adult[(adult["territorio"].eq(BAGHERIA)) & (adult["anno"].eq(2024))].iloc[0]
    adult_s24 = adult[(adult["territorio"].eq("ITG1")) & (adult["anno"].eq(2024))].iloc[0]
    youth_employment_gap_2018 = _value(
        gaps, "gap_bagheria_sicilia_pp", metrica="quota_occupati", anno=2018
    )
    youth_employment_gap_2024 = _value(
        gaps, "gap_bagheria_sicilia_pp", metrica="quota_occupati", anno=2024
    )
    educational_progress = historical_change[historical_change["indicatore"].eq("I6")].iloc[0]
    return pd.DataFrame([
        {
            "priorita": 1,
            "risultato": "Il recupero recente non ha chiuso il divario occupazionale giovanile",
            "evidenza": (
                f"Occupazione 15-24: {b18['quota_occupati']:.1f}% nel 2018 e "
                f"{b24['quota_occupati']:.1f}% nel 2024; gap Sicilia "
                f"{youth_employment_gap_2018:.1f} e {youth_employment_gap_2024:.1f} p.p."
            ),
            "implicazione": "Misurare la convergenza, non soltanto il miglioramento assoluto.",
            "forza": "alta descrittiva",
        },
        {
            "priorita": 2,
            "risultato": "L'inattività non studentesca è il segmento più persistente",
            "evidenza": (
                f"Nel 2024 è il {b24['quota_inattivi_non_studenti']:.1f}%: circa "
                f"{b24['inattivi_non_studenti']:.0f} persone, "
                f"{b24['quota_inattivi_non_studenti'] - s24['quota_inattivi_non_studenti']:.1f} p.p. sopra la Sicilia. "
                f"Dal 2018 cala solo di {abs(b24['quota_inattivi_non_studenti'] - b18['quota_inattivi_non_studenti']):.1f} p.p."
            ),
            "implicazione": "La policy deve raggiungere chi non cerca, non solo assistere chi è già attivo.",
            "forza": "alta descrittiva",
        },
        {
            "priorita": 3,
            "risultato": "La riduzione dell'area fuori lavoro-studio deriva soprattutto dal calo della ricerca",
            "evidenza": (
                f"2018-2024: fuori lavoro-studio {b18['quota_fuori_lavoro_studio']:.1f}%→"
                f"{b24['quota_fuori_lavoro_studio']:.1f}%; in cerca {b18['quota_in_cerca']:.1f}%→"
                f"{b24['quota_in_cerca']:.1f}%; inattivi {b18['quota_inattivi_non_studenti']:.1f}%→"
                f"{b24['quota_inattivi_non_studenti']:.1f}%."
            ),
            "implicazione": "Il miglioramento complessivo non equivale a riattivazione del nucleo inattivo.",
            "forza": "alta descrittiva",
        },
        {
            "priorita": 4,
            "risultato": "Il capitale umano cresce, ma non è superiore al benchmark",
            "evidenza": (
                f"I6 storico {educational_progress['valore_1991']:.1f}%→{educational_progress['valore_2011']:.1f}%. "
                f"Tra i 25-49, almeno diploma {adult_b18['quota_almeno_diploma']:.1f}%→"
                f"{adult_b24['quota_almeno_diploma']:.1f}%; Sicilia 2024 "
                f"{adult_s24['quota_almeno_diploma']:.1f}%."
            ),
            "implicazione": "La policy deve integrare completamento formativo e transizione al lavoro.",
            "forza": "alta descrittiva",
        },
        {
            "priorita": 5,
            "risultato": "Il deficit di ingresso nel lavoro compare anche tra comuni comparabili",
            "evidenza": (
                f"L14 2011 Bagheria {peers['bagheria_youth_employment']:.1f}% contro mediana peer "
                f"{peers['peer_median_youth_employment']:.1f}% (gap {peers['employment_gap_vs_peer_median']:.1f} p.p.)."
            ),
            "implicazione": "Il confronto non va limitato a Palermo o alla media regionale.",
            "forza": "media; confronto ecologico",
        },
    ])


def run_analysis() -> dict[str, object]:
    ensure_directories()
    # Niente pulizia a glob: TABLES è la data/processed condivisa e il prefisso
    # edu_ copre anche gli output della cleaning. Le tavole si sovrascrivono per
    # nome esplicito qui sotto; un file orfano da rinomina va rimosso a mano.

    ottomila, current, population_raw, commuting_raw = _load_clean()
    historical, historical_benchmarks, historical_change = historical_tables(ottomila)
    youth = youth_state_table(current)
    education = education_context_table(current)
    adult = adult_transition_context(education, current)
    population = youth_population_table(population_raw)
    panel = recent_panel(youth, adult, population)
    gaps = gap_table(youth, adult)
    decomposition = change_decomposition(youth)
    commuting = commuting_context(commuting_raw, ottomila)
    peers, peer_summary = peer_table(ottomila)
    robustness = model_robustness(ottomila)
    inventory = source_inventory(ottomila, current, population_raw, commuting_raw)
    dashboard = kpi_dashboard(historical_benchmarks, youth, adult)
    findings = finding_summary(historical_change, youth, gaps, adult, peer_summary)

    tables = {
        "edu_source_inventory.csv": inventory,
        "edu_historical_bagheria.csv": historical,
        "edu_historical_benchmarks_2011.csv": historical_benchmarks,
        "edu_historical_change_1991_2011.csv": historical_change,
        "edu_youth_states_2018_2024.csv": youth,
        "edu_education_context_2018_2024.csv": education,
        "edu_adult_transition_2018_2024.csv": adult,
        "edu_youth_population_15_34.csv": population,
        "edu_recent_analysis_panel.csv": panel,
        "edu_gaps_vs_sicily.csv": gaps,
        "edu_change_decomposition_2018_2024.csv": decomposition,
        "edu_commuting_appendix.csv": commuting,
        "edu_matched_peers_2011.csv": peers,
        "edu_model_robustness_2011.csv": robustness,
        "edu_kpi_dashboard.csv": dashboard,
        "edu_finding_summary.csv": findings,
    }
    for filename, frame in tables.items():
        frame.to_csv(TABLES / filename, index=False, encoding="utf-8")

    b18 = youth[(youth["territorio"].eq(BAGHERIA)) & (youth["anno"].eq(2018))].iloc[0]
    b24 = youth[(youth["territorio"].eq(BAGHERIA)) & (youth["anno"].eq(2024))].iloc[0]
    s24 = youth[(youth["territorio"].eq("ITG1")) & (youth["anno"].eq(2024))].iloc[0]
    adult_b24 = adult[(adult["territorio"].eq(BAGHERIA)) & (adult["anno"].eq(2024))].iloc[0]
    adult_s24 = adult[(adult["territorio"].eq("ITG1")) & (adult["anno"].eq(2024))].iloc[0]
    pop_b24 = population[(population["territorio"].eq(BAGHERIA)) & (population["anno"].eq(2024))].iloc[0]
    summary: dict[str, object] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "title": _config()["project"]["title"],
        "research_question": _config()["project"]["research_question"],
        "scope": "Bagheria; popolazione totale; focus lavoro 15-24 e confronto 25-49",
        "headline": "Bagheria migliora, ma non converge: il nodo persistente è l'inattività non studentesca.",
        "current_2024": {
            "population_15_24": float(b24["popolazione"]),
            "employed_count": float(b24["occupati"]),
            "employed_pct": float(b24["quota_occupati"]),
            "students_pct": float(b24["quota_studenti"]),
            "searching_pct": float(b24["quota_in_cerca"]),
            "inactive_nonstudent_count": float(b24["inattivi_non_studenti"]),
            "inactive_nonstudent_pct": float(b24["quota_inattivi_non_studenti"]),
            "outside_work_study_pct": float(b24["quota_fuori_lavoro_studio"]),
            "inactive_share_of_outside_pct": float(b24["inattivi_su_fuori"]),
            "population_15_34": float(pop_b24["popolazione_15_34"]),
        },
        "change_2018_2024": {
            "employment_pp": float(b24["quota_occupati"] - b18["quota_occupati"]),
            "searching_pp": float(b24["quota_in_cerca"] - b18["quota_in_cerca"]),
            "inactive_nonstudent_pp": float(
                b24["quota_inattivi_non_studenti"] - b18["quota_inattivi_non_studenti"]
            ),
            "outside_work_study_pp": float(
                b24["quota_fuori_lavoro_studio"] - b18["quota_fuori_lavoro_studio"]
            ),
        },
        "gaps_vs_sicily_2024": {
            "employment_15_24_pp": float(b24["quota_occupati"] - s24["quota_occupati"]),
            "inactive_nonstudent_15_24_pp": float(
                b24["quota_inattivi_non_studenti"] - s24["quota_inattivi_non_studenti"]
            ),
            "outside_work_study_15_24_pp": float(
                b24["quota_fuori_lavoro_studio"] - s24["quota_fuori_lavoro_studio"]
            ),
            "at_least_diploma_25_49_pp": float(
                adult_b24["quota_almeno_diploma"] - adult_s24["quota_almeno_diploma"]
            ),
            "employment_25_49_pp": float(
                adult_b24["quota_occupati_25_49"] - adult_s24["quota_occupati_25_49"]
            ),
        },
        "peer_summary": peer_summary,
        "data_limits": [
            "Le tavole comunali non incrociano titolo di studio e condizione lavorativa.",
            "Il NEET storico è 15-29; la ricostruzione recente è 15-24 e non forma una serie continua.",
            "Il 2020 manca nella tavola lavoro e non viene interpolato.",
            "La popolazione 15-34 è disponibile dal 2021 e non misura direttamente la migrazione.",
        ],
    }
    (TABLES / "edu_analysis_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return summary

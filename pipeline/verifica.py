"""Verifica indipendente del thread genere: 475 controlli di regressione.

Ricalcola i numeri chiave DIRETTAMENTE da data/raw/ con un percorso di codice
autonomo — parsing proprio dei CSV SDMX e 8milaCensus, implementazioni proprie
di Wilson/Newcombe, del LPM saturo in forma analitica, dell'IRLS binomiale a
link identità, di MDE/potenza (arcoseno) e del matching di Mahalanobis — e li
confronta con i valori dichiarati in notebooks/genere.ipynb e con i CSV di
data/processed/ letti dalle figure R. Nessun codice condiviso con il notebook:
se i due percorsi coincidono, i numeri non dipendono dall'implementazione.

    uv run python -m pipeline.verifica

Ogni riga: PASS/FAIL, valore calcolato contro valore atteso; exit code 1 se
un controllo fallisce. Gli attesi sono i numeri pubblicati nel notebook: se
un aggiornamento dei raw li cambia, questo file DEVE fallire finché notebook
e attesi non vengono riallineati — è un pin di regressione, non un test unitario.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RADICE = Path(__file__).resolve().parents[1]
RAW = RADICE / "data" / "raw"
PROCESSED = RADICE / "data" / "processed"

B, P, S, I = "082006", "082053", "ITG1", "IT"
QUATTRO = [B, P, S, I]
NOMI = {B: "Bagheria", P: "Palermo", S: "Sicilia", I: "Italia"}

esiti = []


def check(nome, calcolato, atteso, tol=0.051):
    if isinstance(atteso, str):
        ok = str(calcolato) == atteso
    else:
        ok = abs(float(calcolato) - float(atteso)) <= tol
    esiti.append((ok, nome, calcolato, atteso))
    stato = "PASS" if ok else "FAIL"
    print(f"{stato}  {nome}: {calcolato}  (atteso {atteso})")


def info(nome, valore):
    print(f"INFO  {nome}: {valore}")


# ---------------------------------------------------------------- raw SDMX ---
lav = pd.read_csv(RAW / "censpop_lavoro_eta_genere_2026-08-12.csv", dtype=str)
lav["v"] = pd.to_numeric(lav["OBS_VALUE"])
lav["anno"] = lav["TIME_PERIOD"].astype(int)

ist = pd.read_csv(RAW / "censpop_istruzione_eta_genere_2026-08-12.csv", dtype=str)
ist["v"] = pd.to_numeric(ist["OBS_VALUE"])
ist["anno"] = ist["TIME_PERIOD"].astype(int)

pop = pd.read_csv(RAW / "censpop_popolazione_eta_singola_2026-08-12.csv", dtype=str)
pop["v"] = pd.to_numeric(pop["OBS_VALUE"])
pop["anno"] = pop["TIME_PERIOD"].astype(int)
pop["eta"] = pd.to_numeric(pop["AGE_NOCLASS"].str.extract(r"^Y(\d+)$", expand=False))


def cella_lav(terr, anno, gen, cond):
    r = lav[lav["REF_AREA"].eq(terr) & lav["anno"].eq(anno) & lav["GENDER"].eq(gen)
            & lav["AGE_NOCLASS"].eq("Y15-24") & lav["CITIZENSHIP"].eq("TOTAL")
            & lav["EDU_ATTAIN"].eq("ALL") & lav["CUR_ACT_STAT"].eq(cond)]
    assert len(r) == 1, (terr, anno, gen, cond, len(r))
    return r["v"].item()


# --- anni disponibili sulla classe 15-24 (il 2020 deve mancare) ---
anni_1524 = sorted(lav[lav["AGE_NOCLASS"].eq("Y15-24")]["anno"].unique().tolist())
check("anni classe 15-24 (senza 2020)", str(anni_1524), "[2018, 2019, 2021, 2022, 2023, 2024]")

# --- tassi 2024 per genere, quattro territori ---
attesi_2024 = {B: (8.2, 16.5), P: (9.6, 16.5), S: (10.4, 20.3), I: (17.3, 26.9)}
for t, (af, am) in attesi_2024.items():
    tf = 100 * cella_lav(t, 2024, "F", "1") / cella_lav(t, 2024, "F", "99")
    tm = 100 * cella_lav(t, 2024, "M", "1") / cella_lav(t, 2024, "M", "99")
    check(f"tasso occ 2024 F {NOMI[t]}", round(tf, 1), af)
    check(f"tasso occ 2024 M {NOMI[t]}", round(tm, 1), am)

check("Bagheria 2024 F popolazione (arrotondata)", round(cella_lav(B, 2024, "F", "99")), 2882, 0.5)
check("Bagheria 2024 F occupate (arrotondate)", round(cella_lav(B, 2024, "F", "1")), 236, 0.5)

# --- serie Bagheria F/M ---
serie_attese = {"F": [4.7, 5.2, 6.2, 7.7, 8.0, 8.2], "M": [11.5, 11.8, 13.8, 15.4, 15.2, 16.5]}
for gen, attesa in serie_attese.items():
    calc = [round(100 * cella_lav(B, a, gen, "1") / cella_lav(B, a, gen, "99"), 1) for a in anni_1524]
    check(f"serie tasso occ {gen} Bagheria", str(calc), str(attesa))

# --- gap non arrotondato e rapporto ---
gap_atteso = [6.9, 6.7, 7.6, 7.7, 7.2, 8.3]
rapporto_atteso = [2.47, 2.29, 2.23, 2.00, 1.89, 2.01]
for k, a in enumerate(anni_1524):
    pf = cella_lav(B, a, "F", "1") / cella_lav(B, a, "F", "99")
    pm = cella_lav(B, a, "M", "1") / cella_lav(B, a, "M", "99")
    check(f"gap {a} Bagheria (pp, non arrotondato)", round(100 * (pm - pf), 1), gap_atteso[k])
    check(f"rapporto M/F {a} Bagheria", round(pm / pf, 2), rapporto_atteso[k], 0.006)

rapporti_2024 = {P: 1.72, S: 1.95, I: 1.56}
for t, att in rapporti_2024.items():
    pf = cella_lav(t, 2024, "F", "1") / cella_lav(t, 2024, "F", "99")
    pm = cella_lav(t, 2024, "M", "1") / cella_lav(t, 2024, "M", "99")
    check(f"rapporto M/F 2024 {NOMI[t]}", round(pm / pf, 2), att, 0.006)

# ------------------------------------------- Wilson/Newcombe (implementazione propria) ---
Z = stats.norm.ppf(0.975)


def wilson_mio(x, n):
    p = x / n
    centro = (p + Z * Z / (2 * n)) / (1 + Z * Z / n)
    ampiezza = Z / (1 + Z * Z / n) * np.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return centro - ampiezza, centro + ampiezza


def newcombe_mio(xm, nm, xf, nf):
    pm, pf = xm / nm, xf / nf
    lm, um = wilson_mio(xm, nm)
    lf, uf = wilson_mio(xf, nf)
    g = pm - pf
    return (g - np.hypot(pm - lm, uf - pf), g + np.hypot(um - pm, pf - lf))


lo, hi = newcombe_mio(cella_lav(B, 2024, "M", "1"), cella_lav(B, 2024, "M", "99"),
                      cella_lav(B, 2024, "F", "1"), cella_lav(B, 2024, "F", "99"))
check("CI Newcombe gap 2024 Bagheria, basso", round(100 * lo, 1), 6.6)
check("CI Newcombe gap 2024 Bagheria, alto", round(100 * hi, 1), 10.0)

# CI di Wilson sul LIVELLO femminile 2024 (per il claim 'tasso più basso del panel')
lof, hif = wilson_mio(cella_lav(B, 2024, "F", "1"), cella_lav(B, 2024, "F", "99"))
info("Wilson 95% tasso F Bagheria 2024", f"[{100 * lof:.1f}, {100 * hif:.1f}]")

# ---------------------------------------- LPM saturo: formula analitica esatta ---
def eccesso_analitico(anni):
    """gap_Bagheria - gap_benchmark sui conteggi aggregati; SE binomiale analitico."""
    out = {}
    celle = {}
    for t in QUATTRO:
        for g in ("M", "F"):
            x = sum(cella_lav(t, a, g, "1") for a in anni)
            n = sum(cella_lav(t, a, g, "99") for a in anni)
            celle[(t, g)] = (x / n, n)
    gap = {t: celle[(t, "M")][0] - celle[(t, "F")][0] for t in QUATTRO}
    var = {t: sum(p * (1 - p) / n for p, n in (celle[(t, "M")], celle[(t, "F")])) for t in QUATTRO}
    for t in (P, S, I):
        diff = gap[B] - gap[t]
        se = np.sqrt(var[B] + var[t])
        z = diff / se
        out[t] = (100 * diff, 100 * (diff - Z * se), 100 * (diff + Z * se),
                  2 * stats.norm.sf(abs(z)))
    return out


att_2024 = {P: (1.3, -0.4, 3.1, 0.130), S: (-1.6, -3.2, 0.1, 0.066), I: (-1.4, -3.0, 0.3, 0.107)}
att_pool = {P: (1.1, 0.1, 2.1, 0.031), S: (-1.8, -2.7, -0.8, 0.000), I: (-1.9, -2.9, -1.0, 0.000)}
for etichetta, anni, attesi in (("2024", [2024], att_2024),
                                ("pooled 22-24", [2022, 2023, 2024], att_pool)):
    calc = eccesso_analitico(anni)
    for t, (e, l, h, pv) in attesi.items():
        ce, cl, ch, cp = calc[t]
        check(f"LPM {etichetta} eccesso vs {NOMI[t]}", round(ce, 1), e)
        check(f"LPM {etichetta} CI basso vs {NOMI[t]}", round(cl, 1), l)
        check(f"LPM {etichetta} CI alto vs {NOMI[t]}", round(ch, 1), h)
        check(f"LPM {etichetta} p vs {NOMI[t]}", round(cp, 3), pv, 0.0015)

# livello femminile: differenza tasso F Bagheria - benchmark, pooled 2022-24 (INFO)
for t in (P, S, I):
    xb = sum(cella_lav(B, a, "F", "1") for a in (2022, 2023, 2024))
    nb = sum(cella_lav(B, a, "F", "99") for a in (2022, 2023, 2024))
    xt = sum(cella_lav(t, a, "F", "1") for a in (2022, 2023, 2024))
    nt = sum(cella_lav(t, a, "F", "99") for a in (2022, 2023, 2024))
    pb, pt = xb / nb, xt / nt
    se = np.sqrt(pb * (1 - pb) / nb + pt * (1 - pt) / nt)
    z = (pb - pt) / se
    info(f"livello F pooled 22-24: Bagheria - {NOMI[t]}",
         f"{100 * (pb - pt):+.2f} pp, z={z:.2f}, p={2 * stats.norm.sf(abs(z)):.4f}")

# --------------------------------------------- trend OLS sul gap (ricalcolo esatto) ---
righe = []
for t in QUATTRO:
    for a in anni_1524:
        pf = cella_lav(t, a, "F", "1") / cella_lav(t, a, "F", "99")
        pm = cella_lav(t, a, "M", "1") / cella_lav(t, a, "M", "99")
        righe.append({"t": t, "anno": a, "gap": round(100 * (pm - pf), 1)})  # come nel notebook: gap a 1 decimale
serie_gap = pd.DataFrame(righe)
terr_alt = [P, S, I]
Xm = []
y = serie_gap["gap"].values
for _, r in serie_gap.iterrows():
    d = [1.0, r["anno"] - 2021]
    for t in terr_alt:
        d.append(1.0 if r["t"] == t else 0.0)
    for t in terr_alt:
        d.append((r["anno"] - 2021) if r["t"] == t else 0.0)
    Xm.append(d)
Xm = np.array(Xm)
beta, *_ = np.linalg.lstsq(Xm, y, rcond=None)
res = y - Xm @ beta
df = len(y) - Xm.shape[1]
sigma2 = res @ res / df
cov = sigma2 * np.linalg.inv(Xm.T @ Xm)
se = np.sqrt(np.diag(cov))
tq = stats.t.ppf(0.975, df)
# indice 1 = pendenza Bagheria; 5,6,7 = differenze di pendenza per Palermo, Sicilia, Italia
check("trend OLS pendenza Bagheria", round(beta[1], 3), 0.205, 0.0015)
check("trend OLS CI basso Bagheria", round(beta[1] - tq * se[1], 3), 0.060, 0.0015)
check("trend OLS CI alto Bagheria", round(beta[1] + tq * se[1], 3), 0.350, 0.0015)
check("trend OLS p Bagheria", round(2 * stats.t.sf(abs(beta[1] / se[1]), df), 3), 0.008, 0.0015)
for idx, t in zip((5, 6, 7), terr_alt):
    p_att = {P: 0.757, S: 0.019, I: 0.558}[t]
    b_att = {P: 0.030, S: 0.252, I: 0.058}[t]
    check(f"trend OLS diff pendenza {NOMI[t]}", round(beta[idx], 3), b_att, 0.0015)
    check(f"trend OLS diff p {NOMI[t]}", round(2 * stats.t.sf(abs(beta[idx] / se[idx]), df), 3), p_att, 0.0015)

# ------------------------------------------------- composizione per stato, 2024 ---
comp_attesa = {  # (F, M) in % della popolazione
    "occupati": {B: (8.2, 16.5), P: (9.6, 16.5), S: (10.4, 20.3), I: (17.3, 26.9)},
    "in cerca": {B: (6.9, 8.9), P: (7.2, 9.3), S: (6.6, 8.3), I: (5.9, 6.4)},
    "studenti": {B: (65.1, 56.4), P: (66.8, 59.8), S: (67.8, 57.0), I: (67.8, 57.4)},
    "altri":    {B: (19.9, 18.2), P: (16.4, 14.3), S: (15.2, 14.4), I: (9.0, 9.3)},
}
codici_stato = {"occupati": ["1"], "in cerca": ["12"], "studenti": ["5"], "altri": ["4", "24", "7"]}
for stato, per_terr in comp_attesa.items():
    for t, (af, am) in per_terr.items():
        for gen, att in (("F", af), ("M", am)):
            tot = cella_lav(t, 2024, gen, "99")
            q = 100 * sum(cella_lav(t, 2024, gen, c) for c in codici_stato[stato]) / tot
            check(f"composizione 2024 {stato} {gen} {NOMI[t]}", round(q, 1), att)

# partizione esatta: dettagli == totale, M+F == T, 1+12 == 22 (su tutte le celle 15-24)
key = ["REF_AREA", "anno", "GENDER"]
largo = (lav[lav["AGE_NOCLASS"].eq("Y15-24") & lav["CITIZENSHIP"].eq("TOTAL")
             & lav["EDU_ATTAIN"].eq("ALL") & lav["REF_AREA"].isin(QUATTRO)
             & lav["GENDER"].isin(["M", "F", "T"])]
         .pivot_table(index=key, columns="CUR_ACT_STAT", values="v"))
check("partizione: max |somma dettagli - 99|",
      float((largo[["1", "12", "5", "4", "24", "7"]].sum(axis=1) - largo["99"]).abs().max()), 0, 0.001)
check("partizione: max |1+12 - 22|",
      float((largo[["1", "12"]].sum(axis=1) - largo["22"]).abs().max()), 0, 0.001)
per_gen = largo["99"].unstack("GENDER")
check("partizione: max |M+F - T|", float((per_gen["M"] + per_gen["F"] - per_gen["T"]).abs().max()), 0, 0.001)

# forze di lavoro femminili Bagheria
forze_attese = {2018: 676, 2019: 663, 2021: 432, 2022: 479, 2023: 528, 2024: 434}
for a, att in forze_attese.items():
    check(f"forze lavoro F Bagheria {a}", round(cella_lav(B, a, "F", "22")), att, 0.5)

# ------------------------------------------------------------- casalinghe ---
cas_serie = {2018: (376, 12.4), 2019: (324, 10.9), 2021: (421, 14.8),
             2022: (364, 12.8), 2023: (421, 14.6), 2024: (387, 13.4)}
for a, (n_att, q_att) in cas_serie.items():
    n = cella_lav(B, a, "F", "4")
    q = 100 * n / cella_lav(B, a, "F", "99")
    check(f"casalinghe F Bagheria {a} conteggio", round(n), n_att, 0.5)
    check(f"casalinghe F Bagheria {a} quota", round(q, 1), q_att)
cas_2024 = {B: (13.4, 1.7), P: (11.3, 1.4), S: (10.1, 1.2), I: (4.6, 0.6)}
for t, (qf, qm) in cas_2024.items():
    for gen, att in (("F", qf), ("M", qm)):
        q = 100 * cella_lav(t, 2024, gen, "4") / cella_lav(t, 2024, gen, "99")
        check(f"quota casalinghe/i 2024 {gen} {NOMI[t]}", round(q, 1), att)
altra_2024 = {B: (6.4, 16.1), P: (5.0, 12.5), S: (5.1, 12.7), I: (4.4, 8.5)}
for t, (qf, qm) in altra_2024.items():
    for gen, att in (("F", qf), ("M", qm)):
        q = 100 * cella_lav(t, 2024, gen, "7") / cella_lav(t, 2024, gen, "99")
        check(f"quota altra condizione 2024 {gen} {NOMI[t]}", round(q, 1), att)

# fuori da lavoro, studio e ricerca (2024)
for gen, (tot_att, quota_att, cas_att, altra_att, pens_att) in {
        "F": (573, 19.9, 387, 183, 3), "M": (549, 18.2, 50, 485, 13)}.items():
    tot = sum(cella_lav(B, 2024, gen, c) for c in ("4", "24", "7"))
    check(f"fuori-da-tutto 2024 {gen} totale", round(tot), tot_att, 0.5)
    check(f"fuori-da-tutto 2024 {gen} quota", round(100 * tot / cella_lav(B, 2024, gen, "99"), 1), quota_att)
    check(f"fuori-da-tutto 2024 {gen} casalinghe", round(cella_lav(B, 2024, gen, "4")), cas_att, 0.5)
    check(f"fuori-da-tutto 2024 {gen} altra", round(cella_lav(B, 2024, gen, "7")), altra_att, 0.5)
    check(f"fuori-da-tutto 2024 {gen} pensione", round(cella_lav(B, 2024, gen, "24")), pens_att, 0.5)
tf = sum(cella_lav(B, 2024, "F", c) for c in ("4", "24", "7"))
tm = sum(cella_lav(B, 2024, "M", c) for c in ("4", "24", "7"))
check("fuori-da-tutto quota femminile", round(100 * tf / (tf + tm), 1), 51.1)

# ------------------------------------------------- registro: bounds casalinghe ---
def pop_f_bagheria(anno, e0, e1):
    r = pop[pop["REF_AREA"].eq(B) & pop["anno"].eq(anno) & pop["GENDER"].eq("F")
            & pop["CITIZENSHIP"].eq("TOTAL") & pop["MARITAL_STATUS"].eq("ALL")
            & pop["eta"].between(e0, e1)]
    return r["v"].sum()


p1524, p1824, p2024 = pop_f_bagheria(2024, 15, 24), pop_f_bagheria(2024, 18, 24), pop_f_bagheria(2024, 20, 24)
check("registro F 15-24 (2024)", p1524, 2882, 0.5)
check("registro F 18-24 (2024)", p1824, 2053, 0.5)
check("registro F 20-24 (2024)", p2024, 1498, 0.5)
check("registro vs tavola lavoro: pop F 15-24",
      float(abs(p1524 - cella_lav(B, 2024, "F", "99"))), 0, 0.5)
q_cas = 100 * cella_lav(B, 2024, "F", "4") / cella_lav(B, 2024, "F", "99")
check("bound 18-24", round(q_cas / (p1824 / p1524), 1), 18.8)
check("bound 20-24", round(q_cas / (p2024 / p1524), 1), 25.8)
q_ita = 100 * cella_lav(I, 2024, "F", "4") / cella_lav(I, 2024, "F", "99")
eccesso = (q_cas - q_ita) / 100 * cella_lav(B, 2024, "F", "99")
check("eccesso casalinghe vs incidenza italiana (non arrotondato)", round(eccesso), 254, 1.6)

# ------------------------------------------------------------- istruzione 9-24 ---
DIPLOMA = ["USE_IF", "BL", "ML_RDD"]
TUTTI = ["NED", "PSE", "LSE"] + DIPLOMA


def cella_ist(terr, anno, gen, titolo):
    r = ist[ist["REF_AREA"].eq(terr) & ist["anno"].eq(anno) & ist["GENDER"].eq(gen)
            & ist["AGE_NOCLASS"].eq("Y9-24") & ist["CITIZENSHIP"].eq("TOTAL")
            & ist["EDU_ATTAIN"].eq(titolo)]
    assert len(r) == 1, (terr, anno, gen, titolo, len(r))
    return r["v"].item()


ist_2024 = {B: (33.4, 29.2), P: (30.5, 28.7), S: (33.1, 30.4), I: (34.5, 32.3)}
for t, (af, am) in ist_2024.items():
    for gen, att in (("F", af), ("M", am)):
        q = 100 * sum(cella_ist(t, 2024, gen, x) for x in DIPLOMA) / cella_ist(t, 2024, gen, "ALL")
        check(f"almeno diploma 2024 {gen} {NOMI[t]}", round(q, 1), att)
# partizione istruzione esatta su tutte le celle
scarti = []
for t in QUATTRO:
    for a in sorted(ist["anno"].unique()):
        for gen in ("M", "F", "T"):
            tot = cella_ist(t, a, gen, "ALL")
            somma = sum(cella_ist(t, a, gen, x) for x in TUTTI)
            scarti.append(abs(somma - tot))
check("partizione titoli: max |somma - ALL|", max(scarti), 0, 1e-9)

# --------------------------------------------- composizione per età (2024) ---
def quota_alta(terr, gen, fascia, alta):
    dentro = pop[pop["REF_AREA"].eq(terr) & pop["anno"].eq(2024) & pop["GENDER"].eq(gen)
                 & pop["CITIZENSHIP"].eq("TOTAL") & pop["MARITAL_STATUS"].eq("ALL")
                 & pop["eta"].between(*fascia)]
    su = dentro[dentro["eta"].between(*alta)]["v"].sum()
    return 100 * su / dentro["v"].sum()


mix_lavoro = {B: (52.0, 50.7), P: (49.2, 49.6), S: (50.8, 50.6), I: (50.2, 50.7)}
mix_istr = {B: (40.8, 38.3), P: (38.5, 38.7), S: (39.5, 40.1), I: (38.8, 39.7)}
for t in QUATTRO:
    check(f"quota 20-24 in 15-24 F {NOMI[t]}", round(quota_alta(t, "F", (15, 24), (20, 24)), 1), mix_lavoro[t][0])
    check(f"quota 20-24 in 15-24 M {NOMI[t]}", round(quota_alta(t, "M", (15, 24), (20, 24)), 1), mix_lavoro[t][1])
    check(f"quota 19-24 in 9-24 F {NOMI[t]}", round(quota_alta(t, "F", (9, 24), (19, 24)), 1), mix_istr[t][0])
    check(f"quota 19-24 in 9-24 M {NOMI[t]}", round(quota_alta(t, "M", (9, 24), (19, 24)), 1), mix_istr[t][1])

# ------------------------------------------------------------ gap in persone ---
def occupate_in_piu(anni):
    agg = {}
    for t in QUATTRO:
        for g in ("M", "F"):
            x = sum(cella_lav(t, a, g, "1") for a in anni)
            n = sum(cella_lav(t, a, g, "99") for a in anni)
            agg[(t, g)] = (x / n, n)
    pop_f = agg[(B, "F")][1] / len(anni)
    base = agg[(B, "F")][0]
    return (round(pop_f * (agg[(B, "M")][0] - base)),
            round(pop_f * (agg[(P, "F")][0] - base)),
            round(pop_f * (agg[(I, "F")][0] - base)))


check("occupate in più 2024 (parità, Palermo, Italia)", str(occupate_in_piu([2024])), "(239, 40, 262)")
check("occupate in più media 22-24", str(occupate_in_piu([2022, 2023, 2024])), "(221, 34, 255)")

# ------------------------------------------------- MDE e potenza (formule proprie) ---
def mde_pp_mio(p0, n, potenza=0.80, alpha=0.05):
    h = (stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(potenza)) * np.sqrt(2 / n)
    phi0 = 2 * np.arcsin(np.sqrt(p0))
    return 100 * (np.sin((phi0 + h) / 2) ** 2 - p0)


def potenza_mia(p0, p1, n, alpha=0.05):
    h = abs(2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p0)))
    zc = stats.norm.ppf(1 - alpha / 2)
    z = h * np.sqrt(n / 2)
    return 100 * (stats.norm.sf(zc - z) + stats.norm.cdf(-zc - z))


n_f = cella_lav(B, 2024, "F", "99")
p_occ = cella_lav(B, 2024, "F", "1") / n_f
p_occ_pa = cella_lav(P, 2024, "F", "1") / cella_lav(P, 2024, "F", "99")
q_cas_b = cella_lav(B, 2024, "F", "4") / cella_lav(B, 2024, "F", "99")
q_cas_pa = cella_lav(P, 2024, "F", "4") / cella_lav(P, 2024, "F", "99")
# nel notebook p0/p1 delle casalinghe passano dalle quote arrotondate a 1 decimale: replico
q_cas_b_r, q_cas_pa_r = round(100 * q_cas_b, 1) / 100, round(100 * q_cas_pa, 1) / 100
mde_occ = [(2.14, 46), (1.49, 75), (1.21, 90)]
mde_cas = [(2.61, 68), (1.83, 93), (1.48, 99)]
for k in (1, 2, 3):
    m, pw = mde_occ[k - 1]
    check(f"MDE occ {k} anni", round(mde_pp_mio(p_occ, k * n_f), 2), m, 0.006)
    check(f"potenza occ {k} anni", round(potenza_mia(p_occ, p_occ_pa, k * n_f)), pw, 0.51)
    m, pw = mde_cas[k - 1]
    check(f"MDE casalinghe {k} anni", round(mde_pp_mio(q_cas_b_r, k * n_f), 2), m, 0.006)
    check(f"potenza casalinghe {k} anni", round(potenza_mia(q_cas_b_r, q_cas_pa_r, k * n_f)), pw, 0.51)

# --------------------------------------------------- ritenzione di coorte ---
def stock(terr, anno, gen, e0, e1):
    r = pop[pop["REF_AREA"].eq(terr) & pop["anno"].eq(anno) & pop["GENDER"].eq(gen)
            & pop["CITIZENSHIP"].eq("TOTAL") & pop["MARITAL_STATUS"].eq("ALL")
            & pop["eta"].between(e0, e1)]
    return r["v"].sum()


coorti_attese = {
    (15, 19): {B: (100.4, 98.5), P: (100.8, 101.1), S: (100.7, 103.0), I: (101.8, 104.8)},
    (20, 24): {B: (102.0, 99.7), P: (99.8, 97.7), S: (99.2, 98.3), I: (102.7, 104.1)},
    (25, 29): {B: (96.3, 101.2), P: (98.8, 96.9), S: (97.6, 97.6), I: (103.0, 103.8)},
}
for (a0, a1), per_terr in coorti_attese.items():
    for t, (af, am) in per_terr.items():
        for gen, att in (("F", af), ("M", am)):
            r = 100 * stock(t, 2024, gen, a0 + 3, a1 + 3) / stock(t, 2021, gen, a0, a1)
            check(f"ritenzione {a0}-{a1} {gen} {NOMI[t]}", round(r, 1), att)

rit_annue = {2021: 99.2, 2022: 98.8, 2023: 99.0}
for a, att in rit_annue.items():
    r = 100 * stock(B, a + 1, "F", 26, 30) / stock(B, a, "F", 25, 29)
    check(f"ritenzione annua F 25-29 {a}->{a + 1}", round(r, 1), att)

# spot del profilo per età (rolling 3)
def rolling3(terr, gen, eta_c):
    n0 = sum(stock(terr, 2021, gen, e, e) for e in (eta_c - 1, eta_c, eta_c + 1))
    n3 = sum(stock(terr, 2024, gen, e + 3, e + 3) for e in (eta_c - 1, eta_c, eta_c + 1))
    return 100 * n3 / n0


check("profilo rolling3 F Bagheria età 24", round(rolling3(B, "F", 24), 1), 99.6)
check("profilo rolling3 F Bagheria età 28", round(rolling3(B, "F", 28), 1), 96.7)
check("profilo rolling3 M Bagheria età 28", round(rolling3(B, "M", 28), 1), 103.7)
check("profilo rolling3 F Italia età 25", round(rolling3(I, "F", 25), 1), 102.9)

# popolazione 15-34 (assert condivisi)
check("pop 15-34 Bagheria 2021", stock(B, 2021, "T", 15, 34), 12174, 0.5)
check("pop 15-34 Bagheria 2024", stock(B, 2024, "T", 15, 34), 11861, 0.5)

# ------------------------------------------------------------- 8milaCensus ---
otto_sic = pd.read_csv(RAW / "8milacensus_indicatori_sicilia_2026-08-12.csv", sep=";",
                       dtype=str, encoding="cp1252", keep_default_na=False)
otto_sic = otto_sic[otto_sic["AnnoCP"].str.strip() != ""]
otto_nat = pd.read_csv(RAW / "8milacensus_indicatori_prov_reg_italia_2026-08-12.csv", sep=";",
                       dtype=str, encoding="cp1252", keep_default_na=False)
otto_nat = otto_nat[otto_nat["AnnoCP"].str.strip() != ""]


def numit(s):
    s = s.strip()
    if s in ("", "-"):
        return np.nan
    return float(s.replace(".", "").replace(",", "."))


def valore_8m(livello, codice, anno, indicatore):
    if livello == "1":
        d = otto_sic[(otto_sic["Livello territoriale"] == "1")
                     & (otto_sic["Codice comune 2011"] == codice)
                     & (otto_sic["AnnoCP"] == str(anno))]
    elif livello == "3":
        d = otto_nat[(otto_nat["Livello territoriale"] == "3")
                     & (otto_nat["Codice Regione 2011"] == codice)
                     & (otto_nat["AnnoCP"] == str(anno))]
    else:
        d = otto_nat[(otto_nat["Livello territoriale"] == "4") & (otto_nat["AnnoCP"] == str(anno))]
    assert len(d) == 1, (livello, codice, anno, len(d))
    return numit(d[indicatore].item())


def comuni_8m(anno, indicatore):
    d = otto_sic[(otto_sic["Livello territoriale"] == "1") & (otto_sic["AnnoCP"] == str(anno))]
    return d.set_index(d["Codice comune 2011"].str.zfill(6))[indicatore].map(numit).dropna()


storico_2011 = {"I1": (98.9, 102.5, 100.7, 101.5), "L1": (56.7, 57.8, 57.5, 60.7),
                "L10": (43.1, 45.0, 46.9, 54.8), "L11": (18.1, 25.5, 24.0, 36.1),
                "L2": (28.7, 35.9, 33.0, 41.8), "L6": (24.1, 22.1, 18.5, 9.8),
                "L7": (36.9, 29.1, 27.1, 13.6)}
lookup = [("1", "82006"), ("1", "82053"), ("3", "19"), ("4", "")]
for ind, attesi in storico_2011.items():
    for (liv, cod), att, nome in zip(lookup, attesi, ["Bagheria", "Palermo", "Sicilia", "Italia"]):
        check(f"8milaCensus 2011 {ind} {nome}", valore_8m(liv, cod, 2011, ind), att, 0.051)

# distribuzione L11 sui 390 comuni
v11 = comuni_8m(2011, "L11")
check("comuni con L11 2011", len(v11), 390, 0.5)
bagh = v11["082006"]
check("percentile L11 Bagheria (12°)", round(100 * (v11 < bagh).mean()), 12, 0.5)
check("posizione L11 Bagheria (49ª)", int((v11 < bagh).sum()) + 1, 49, 0.5)
check("mediana L11 Sicilia", round(v11.median(), 1), 23.6)
check("min L11", round(v11.min(), 1), 13.0)
check("max L11", round(v11.max(), 1), 39.4)

# gap delle madri: valori e percentili
madri_val = {("L2", 1991): 20.6, ("L2", 2001): 27.2, ("L2", 2011): 28.7,
             ("L11", 1991): 10.9, ("L11", 2001): 15.1, ("L11", 2011): 18.1,
             ("L10", 1991): 44.2, ("L10", 2001): 43.8, ("L10", 2011): 43.1,
             ("L7", 1991): 47.3, ("L7", 2001): 44.5, ("L7", 2011): 36.9,
             ("I1", 1991): 102.6, ("I1", 2001): 101.2, ("I1", 2011): 98.9}
madri_pct = {("L2", 1991): 7.9, ("L2", 2001): 40.8, ("L2", 2011): 31.5,
             ("L11", 1991): 22.1, ("L11", 2001): 23.6, ("L11", 2011): 12.3,
             ("L10", 1991): 63.6, ("L10", 2001): 54.9, ("L10", 2011): 14.6,
             ("L7", 1991): 45.9, ("L7", 2001): 84.4, ("L7", 2011): 94.6,
             ("I1", 1991): 34.1, ("I1", 2001): 47.4, ("I1", 2011): 37.4}
for (ind, anno), att in madri_val.items():
    check(f"madri {ind} {anno} valore Bagheria", valore_8m("1", "82006", anno, ind), att, 0.051)
for (ind, anno), att in madri_pct.items():
    v = comuni_8m(anno, ind)
    check(f"madri {ind} {anno} percentile", round(100 * (v < v["082006"]).mean(), 1), att)

# ------------------------------------------------------ gemelle (Mahalanobis) ---
centroidi = pd.read_csv(PROCESSED / "comuni_sicilia_centroidi.csv", dtype={"territorio": str})
xy = centroidi.set_index("territorio")
com = pd.DataFrame({ind: comuni_8m(2011, ind) for ind in
                    ["P1", "P7", "P11", "P12", "S1", "A1", "A4", "L11", "L7", "I1", "L4",
                     "F4", "F7", "M2"]})
com["dist_pa"] = np.hypot(xy["x"].reindex(com.index) - xy.loc["082053", "x"],
                          xy["y"].reindex(com.index) - xy.loc["082053", "y"]) / 1000
MATCH = ["P1", "P7", "P11", "P12", "S1", "A1", "A4", "dist_pa"]
Xg = com[MATCH].copy()
Xg["P1"], Xg["P7"], Xg["S1"] = np.log10(Xg["P1"]), np.log10(Xg["P7"]), np.log1p(Xg["S1"])
assert not Xg.isna().any().any()
inv = np.linalg.inv(np.cov(Xg.values.T))
diff = Xg.values - Xg.loc["082006"].values
d_mah = pd.Series(np.sqrt(np.einsum("ij,jk,ik->i", diff, inv, diff)), index=Xg.index)
top10 = d_mah.drop("082006").sort_values().head(10)
nomi_top = [otto_sic[(otto_sic["Livello territoriale"] == "1")
                     & (otto_sic["Codice comune 2011"].str.zfill(6) == c)]["Denominazione del territorio"].iloc[0]
            for c in top10.index]
attese_gemelle = ["Termini Imerese", "Santa Flavia", "Capaci", "Trabia", "Misilmeri",
                  "Altofonte", "Terrasini", "Erice", "Porto Empedocle", "Sciacca"]
check("gemelle: elenco ordinato", str(nomi_top), str(attese_gemelle))
check("gemelle: distanza rank 1", round(top10.iloc[0], 2), 1.74, 0.006)
check("gemelle: distanza rank 10", round(top10.iloc[9], 2), 2.93, 0.006)

posizioni = {"L11": (18.1, 19.8, 3), "L7": (36.9, 30.5, 8), "I1": (98.9, 101.2, 1),
             "L4": (40.1, 41.2, 4), "F4": (3.6, 4.4, 0), "F7": (11.7, 11.8, 5),
             "M2": (14.3, 24.0, 2)}
for ind, (v_att, med_att, sotto_att) in posizioni.items():
    grp = com.loc[top10.index, ind]
    check(f"gemelle {ind}: Bagheria", round(com.loc["082006", ind], 1), v_att)
    check(f"gemelle {ind}: mediana", round(grp.median(), 1), med_att)
    check(f"gemelle {ind}: sotto Bagheria", int((grp < com.loc["082006", ind]).sum()), sotto_att, 0.5)

# robustezza: z-score, PCA-4, LOVO
Zs = (Xg - Xg.mean()) / Xg.std(ddof=0)
d_z = np.sqrt(((Zs - Zs.loc["082006"]) ** 2).sum(axis=1)).drop("082006").sort_values()
check("robustezza z-score overlap", len(set(d_z.head(10).index) & set(top10.index)), 8, 0.5)
Zc = Zs.values - Zs.values.mean(0)
_, Sv, Vt = np.linalg.svd(Zc, full_matrices=False)
proi = pd.DataFrame((Zs.values @ Vt.T[:, :4]) / Sv[:4], index=Zs.index)
d_p = np.sqrt(((proi - proi.loc["082006"]) ** 2).sum(axis=1)).drop("082006").sort_values()
check("robustezza PCA-4 overlap", len(set(d_p.head(10).index) & set(top10.index)), 6, 0.5)
lovo_min = 99
for v_out in MATCH:
    Xl = Xg.drop(columns=v_out)
    invl = np.linalg.inv(np.cov(Xl.values.T))
    dl = Xl.values - Xl.loc["082006"].values
    ddl = pd.Series(np.sqrt(np.einsum("ij,jk,ik->i", dl, invl, dl)), index=Xl.index)
    lovo_min = min(lovo_min, len(set(ddl.drop("082006").sort_values().head(10).index) & set(top10.index)))
check("robustezza LOVO minimo", lovo_min, 7, 0.5)

# ---------------------------------------------------------------- nuvola 390 ---
nuv = com[["I1", "L11"]].dropna()
rho, p_rho = stats.spearmanr(nuv["I1"], nuv["L11"])
check("Spearman I1 x L11", round(rho, 2), -0.24, 0.006)
check("Spearman p", p_rho, 1.2e-06, 5e-7)
check("comuni I1<100", int((nuv["I1"] < 100).sum()), 170, 0.5)
# La mediana esatta è 24.85: il notebook la stampa "24.9" (f-string, half-up),
# round() darebbe 24.8 (half-even). Si confronta il valore, non la stampa.
check("mediana L11 se I1<100", float(nuv.loc[nuv["I1"] < 100, "L11"].median()), 24.85, 0.005)
check("mediana L11 se I1>=100", round(nuv.loc[nuv["I1"] >= 100, "L11"].median(), 1), 22.4)

# ------------------------------------------------------- famiglia precoce ---
fam_attese = {("F4", 1991): (1.3, 9.0, 2.0, 2.1, 2.9), ("F4", 2001): (1.7, 6.4, 2.6, 2.6, 4.6),
              ("F4", 2011): (3.6, 3.3, 4.4, 4.0, 7.0), ("F7", 1991): (25.6, 88.5, 24.6, 20.9, 16.3),
              ("F7", 2001): (18.4, 86.7, 17.8, 14.3, 11.0), ("F7", 2011): (11.7, 81.0, 11.8, 9.3, 7.4)}
for (ind, anno), (v_att, pct_att, med_att, pal_att, ita_att) in fam_attese.items():
    v = comuni_8m(anno, ind)
    check(f"famiglia {ind} {anno} Bagheria", round(v["082006"], 1), v_att)
    check(f"famiglia {ind} {anno} percentile", round(100 * (v < v["082006"]).mean(), 1), pct_att)
    check(f"famiglia {ind} {anno} mediana gemelle", round(v[top10.index].median(), 1), med_att)
    check(f"famiglia {ind} {anno} Palermo", valore_8m("1", "82053", anno, ind), pal_att, 0.051)
    check(f"famiglia {ind} {anno} Italia", valore_8m("4", "", anno, ind), ita_att, 0.051)

# ------------------------------------------- pretrend: IRLS binomiale identità ---
def irls_identita(Xd, yv, w_trials):
    b = np.linalg.lstsq(Xd, yv, rcond=None)[0]
    for _ in range(60):
        mu = np.clip(Xd @ b, 1e-9, 1 - 1e-9)
        W = np.diag(w_trials / (mu * (1 - mu)))
        b_new = np.linalg.solve(Xd.T @ W @ Xd, Xd.T @ W @ yv)
        if np.max(np.abs(b_new - b)) < 1e-12:
            b = b_new
            break
        b = b_new
    mu = np.clip(Xd @ b, 1e-9, 1 - 1e-9)
    W = np.diag(w_trials / (mu * (1 - mu)))
    cov_b = np.linalg.inv(Xd.T @ W @ Xd)
    return b, np.sqrt(np.diag(cov_b))


righe = []
for t in QUATTRO:
    for a in anni_1524:
        x, n = cella_lav(t, a, "F", "1"), cella_lav(t, a, "F", "99")
        righe.append({"t": t, "anno": a, "p": x / n, "n": n})
d = pd.DataFrame(righe)
Xd = []
for _, r in d.iterrows():
    riga = [1.0, r["anno"] - 2021]
    for t in terr_alt:
        riga.append(1.0 if r["t"] == t else 0.0)
    for t in terr_alt:
        riga.append((r["anno"] - 2021) if r["t"] == t else 0.0)
    Xd.append(riga)
Xd = np.array(Xd)
b, se_b = irls_identita(Xd, d["p"].values, d["n"].values)
check("pretrend pendenza Bagheria", round(100 * b[1], 2), 0.65, 0.006)
check("pretrend CI basso", round(100 * (b[1] - Z * se_b[1]), 2), 0.48, 0.006)
check("pretrend CI alto", round(100 * (b[1] + Z * se_b[1]), 2), 0.81, 0.006)
pre_att = {P: (-0.10, 0.291), S: (-0.17, 0.054), I: (-0.08, 0.328)}
for idx, t in zip((5, 6, 7), terr_alt):
    diff_att, p_att = pre_att[t]
    check(f"pretrend diff pendenza {NOMI[t]}", round(100 * b[idx], 2), diff_att, 0.006)
    check(f"pretrend p {NOMI[t]}", round(2 * stats.norm.sf(abs(b[idx] / se_b[idx])), 3), p_att, 0.0015)

# L11 vs gemelle nei tre censimenti
gem_att = {1991: (10.9, 10.8, 9.5, 14.5), 2001: (15.1, 15.0, 14.2, 17.9), 2011: (18.1, 19.8, 17.8, 22.7)}
for anno, (bg, med, q1, q3) in gem_att.items():
    v = comuni_8m(anno, "L11")
    check(f"pretrend gemelle {anno} Bagheria", round(v["082006"], 1), bg)
    check(f"pretrend gemelle {anno} mediana", round(v[top10.index].median(), 1), med)
    check(f"pretrend gemelle {anno} Q1", round(v[top10.index].quantile(0.25), 1), q1)
    check(f"pretrend gemelle {anno} Q3", round(v[top10.index].quantile(0.75), 1), q3)

# ------------------------------------- CSV processed: coerenza con i ricalcoli ---
forb = pd.read_csv(PROCESSED / "genere_forbice.csv").set_index("nome_territorio")
for t, nome in NOMI.items():
    pf = cella_lav(t, 2024, "F", "1") / cella_lav(t, 2024, "F", "99")
    pm = cella_lav(t, 2024, "M", "1") / cella_lav(t, 2024, "M", "99")
    di_f = 100 * sum(cella_ist(t, 2024, "F", x) for x in DIPLOMA) / cella_ist(t, 2024, "F", "ALL")
    di_m = 100 * sum(cella_ist(t, 2024, "M", x) for x in DIPLOMA) / cella_ist(t, 2024, "M", "ALL")
    check(f"forbice.csv vantaggio istruzione {nome}",
          forb.loc[nome, "vantaggio_istruzione_F_pp"], round(round(di_f, 1) - round(di_m, 1), 2), 0.051)
    check(f"forbice.csv rapporto occupazione {nome}",
          forb.loc[nome, "rapporto_M_F_occupazione"], round(pm / pf, 2), 0.006)

quad = pd.read_csv(PROCESSED / "genere_quadrante.csv")
check("quadrante.csv: 8 righe", len(quad), 8, 0.5)
r = quad[quad["nome_territorio"].eq("Bagheria") & quad["genere"].eq("F")]
check("quadrante.csv Bagheria F occ", r["tasso_occupazione"].item(), 8.2)
check("quadrante.csv Bagheria F diploma", r["almeno_diploma_%"].item(), 33.4)

mde_csv = pd.read_csv(PROCESSED / "genere_mde.csv")
check("mde.csv: 6 righe", len(mde_csv), 6, 0.5)
check("mde.csv MDE annuale occ", mde_csv.iloc[0]["MDE 80% (pp)"], 2.14, 0.006)
check("mde.csv potenza triennale occ", mde_csv.iloc[2]["potenza per il delta (%)"], 90, 0.51)

gp = pd.read_csv(PROCESSED / "genere_gap_persone.csv")
check("gap_persone.csv Palermo 2024", int(gp[gp["scenario"].str.contains("Palermo")]["occupate in più (2024)"].item()), 40, 0.5)

bounds_csv = pd.read_csv(PROCESSED / "genere_casalinghe_bounds.csv")
check("bounds.csv 18-24", bounds_csv.iloc[1]["quota nella fascia interessata (%)"], 18.8)
check("bounds.csv 20-24", bounds_csv.iloc[2]["quota nella fascia interessata (%)"], 25.8)

gem_csv = pd.read_csv(PROCESSED / "genere_gemelle.csv")
check("gemelle.csv elenco", str(gem_csv["nome_comune"].tolist()), str(attese_gemelle))

nuv_csv = pd.read_csv(PROCESSED / "genere_nuvola_390.csv")
check("nuvola.csv: 390 righe", len(nuv_csv), 390, 0.5)
check("nuvola.csv: 10 gemelle flaggate", int(nuv_csv["gemella"].sum()), 10, 0.5)

pre_csv = pd.read_csv(PROCESSED / "genere_pretrend.csv")
check("pretrend.csv pendenza Bagheria", pre_csv.iloc[0]["stima"], 0.65, 0.006)

# ------------------------- ponte fra i due censimenti: 15+ dal permanente ---
# Percorso autonomo: i raw dei 390 comuni e delle gemelle si rileggono qui, i tassi si
# ricalcolano dai codici CUR_ACT_STAT senza passare dal notebook. Gli attesi sono i numeri
# stampati dalla sezione "Il ponte fra i due censimenti" di notebooks/genere.ipynb.
def tassi_ge15(quadro):
    q = quadro[(quadro["AGE_NOCLASS"] == "Y_GE15") & (quadro["CITIZENSHIP"] == "TOTAL")
               & (quadro["EDU_ATTAIN"] == "ALL") & quadro["GENDER"].isin(["M", "F"])]
    c = q.pivot_table(index=["REF_AREA", "anno"], columns=["GENDER", "CUR_ACT_STAT"],
                      values="v", aggfunc="sum")
    return pd.DataFrame({"L2": 100 * c[("F", "22")] / c[("F", "99")],
                         "L11": 100 * c[("F", "1")] / c[("F", "99")],
                         "L10": 100 * c[("M", "1")] / c[("M", "99")],
                         "L7": 100 * c[("F", "12")] / c[("F", "22")]})


sic390 = pd.concat([pd.read_csv(RAW / f"censpop_lavoro_15piu_sicilia_{i:02d}_2026-08-25.csv",
                                dtype=str) for i in range(1, 13)], ignore_index=True)
sic390["v"] = pd.to_numeric(sic390["OBS_VALUE"])
sic390["anno"] = sic390["TIME_PERIOD"].astype(int)
check("15piu: comuni scaricati", sic390["REF_AREA"].nunique(), 390, 0.5)
check("15piu: anni serviti", str(sorted(int(a) for a in sic390["anno"].unique())),
      "[2018, 2019, 2021, 2022, 2023, 2024]")

t390 = tassi_ge15(sic390)
t4 = tassi_ge15(lav)

# (a) coerenza fra le due rilevazioni sullo stesso indicatore e la stessa fascia
for ind, att2018 in (("L2", 30.4), ("L11", 18.8), ("L10", 40.4), ("L7", 38.1)):
    check(f"ponte: {ind} Bagheria 2018 (permanente)", round(t4.loc[(B, 2018), ind], 1), att2018)
    check(f"ponte: {ind} Bagheria 2024 (permanente)",
          round(t4.loc[(B, 2024), ind], 1), {"L2": 27.9, "L11": 23.7, "L10": 46.1, "L7": 15.2}[ind])
# lo stesso tasso ricalcolato dal file dei 390: due raw diversi devono dare lo stesso numero
check("ponte: L11 Bagheria 2024 dai 390", round(t390.loc[(B, 2024), "L11"], 1), 23.7)

# (b) il salto interno al permanente fra 2019 e 2021 c'è su L7/L2 e non su L11/L10
for terr, att in ((B, -15.5), (P, -14.1), (S, -12.8), (I, -4.5)):
    check(f"ponte: salto L7 2019-2021 {NOMI[terr]}",
          round(t4.loc[(terr, 2021), "L7"] - t4.loc[(terr, 2019), "L7"], 1), att)
check("ponte: salto L11 2019-2021 Bagheria",
      round(t4.loc[(B, 2021), "L11"] - t4.loc[(B, 2019), "L11"], 1), 1.2)

# (c) percentili sui 390, stessa formula del 2011
pct_recenti = {("L2", 2018): 21.5, ("L2", 2024): 16.9, ("L11", 2018): 8.2, ("L11", 2024): 16.9,
               ("L10", 2018): 15.4, ("L10", 2024): 29.5, ("L7", 2018): 92.6, ("L7", 2024): 73.6}
for (ind, anno), att in pct_recenti.items():
    v = t390[ind].xs(anno, level="anno").dropna()
    check(f"ponte: percentile {ind} {anno}", round(100 * (v < v[B]).mean(), 1), att)

# (d) gemelle dentro il permanente: lo scarto non si chiude
gem_raw = pd.read_csv(RAW / "censpop_lavoro_gemelle_2026-08-25.csv", dtype=str)
gem_raw["v"] = pd.to_numeric(gem_raw["OBS_VALUE"])
gem_raw["anno"] = gem_raw["TIME_PERIOD"].astype(int)
tg = tassi_ge15(gem_raw)
check("ponte: gemelle scaricate", tg.index.get_level_values("REF_AREA").nunique(), 10, 0.5)
for anno, att_med, att_scarto in ((2018, 21.1, -2.3), (2024, 26.0, -2.3)):
    v = tg["L11"].xs(anno, level="anno")
    check(f"ponte: mediana gemelle {anno}", round(v.median(), 1), att_med)
    # differenza fra i valori GIÀ arrotondati: è quella che il CSV espone e che fig10
    # sottrae. Sul 2018 il non arrotondato darebbe -2.2 invece di -2.3.
    check(f"ponte: scarto Bagheria-gemelle {anno}",
          round(round(t390.loc[(B, anno), "L11"], 1) - round(v.median(), 1), 1), att_scarto)

# (e) i CSV letti dalle figure devono riportare gli stessi numeri
mr_csv = pd.read_csv(PROCESSED / "genere_madri_recente.csv")
check("madri_recente.csv percentile L11 2024",
      mr_csv[(mr_csv["indicatore"] == "L11") & (mr_csv["anno"] == 2024)]["percentile_390"].item(), 16.9)
gr_csv = pd.read_csv(PROCESSED / "genere_pretrend_gemelle_recente.csv")
check("pretrend_gemelle_recente.csv righe", len(gr_csv), 6, 0.5)
check("pretrend_gemelle_recente.csv Bagheria 2024",
      gr_csv[gr_csv["anno"] == 2024]["bagheria"].item(), 23.7)
co_csv = pd.read_csv(PROCESSED / "genere_coerenza_fonti.csv")
check("coerenza_fonti.csv scarto L11 Bagheria",
      co_csv[(co_csv["territorio"] == "Bagheria") & (co_csv["indicatore"] == "L11")]["scarto_2011_2018"].item(), 0.7)

# ---------------- i claim reggono al 2024: persistenza, decenni, forbice ---
# Quarto percorso autonomo. Il rho di Spearman si ricalcola come Pearson sui ranghi con
# numpy (il notebook usa scipy.stats.spearmanr), la ritenzione decennale si legge dalle
# classi quinquennali del raw demografico, la forbice si ricostruisce anno per anno dai
# codici SDMX. Gli attesi sono i numeri stampati dalla sezione "I claim reggono al 2024?".
def spearman_mio(a, b):
    """Pearson sui ranghi, ranghi medi sui pari: la definizione di Spearman."""
    return float(np.corrcoef(stats.rankdata(a), stats.rankdata(b))[0, 1])


def quintile_basso(serie):
    """Il quintile inferiore per rango percentuale, come `rank(pct=True) <= 0.2`."""
    r = stats.rankdata(serie) / len(serie)
    return set(serie.index[r <= 0.2])


# (a) la graduatoria del 2011 predice quella del 2024
occ11 = comuni_8m(2011, "L11")
occ24 = t390["L11"].xs(2024, level="anno")
occ18 = t390["L11"].xs(2018, level="anno")
platea = sorted(set(occ11.index) & set(occ24.index))
check("persistenza: platea comune fra le due epoche", len(platea), 390, 0.5)
x11, x18, x24 = (s.reindex(platea) for s in (occ11, occ18, occ24))
check("persistenza: rho Spearman 2011 vs 2024", round(spearman_mio(x11, x24), 3), 0.848, 0.0011)
check("persistenza: rho Spearman 2018 vs 2024", round(spearman_mio(x18, x24), 3), 0.919, 0.0011)

q11, q24 = quintile_basso(x11), quintile_basso(x24)
check("persistenza: comuni nel quintile basso 2011", len(q11), 77, 0.5)
check("persistenza: quintile basso 2011 ancora tale nel 2024",
      round(100 * len(q11 & q24) / len(q11), 1), 74.0)
check("persistenza: Bagheria nel quintile basso in entrambe",
      str(B in q11 and B in q24), "True")

for anno, serie, att in ((2011, x11, (18.1, 12.3, 23.6)), (2024, x24, (23.7, 16.9, 28.3))):
    check(f"distribuzione {anno}: Bagheria", round(serie[B], 1), att[0])
    check(f"distribuzione {anno}: percentile di Bagheria",
          round(100 * (serie < serie[B]).mean(), 1), att[1])
    check(f"distribuzione {anno}: mediana siciliana", round(serie.median(), 1), att[2])

# (b) ritenzione di coorte a passo quinquennale, dal raw delle classi
cls = pd.read_csv(RAW / "censpop_demografia_classi_2026-08-25.csv", dtype=str)
cls["v"] = pd.to_numeric(cls["OBS_VALUE"])
cls["anno"] = cls["TIME_PERIOD"].astype(int)
CLASSI = ["Y10-14", "Y15-19", "Y20-24", "Y25-29", "Y30-34", "Y35-39", "Y40-44", "Y45-49"]


def coorte(terr, gen, eta, anno):
    d = cls[(cls["REF_AREA"] == terr) & (cls["GENDER"] == gen) & (cls["AGE_CLASS"] == eta)
            & (cls["MARITAL_STATUS"] == "ALL") & (cls["CITIZENSHIP"] == "TOTAL")
            & (cls["anno"] == anno)]
    assert len(d) == 1, (terr, gen, eta, anno, len(d))
    return d["v"].item()


def ritenzione_coorte(terr, gen, anno0, anno1, eta="Y15-19"):
    passi, resto = divmod(anno1 - anno0, 5)
    assert resto == 0
    arrivo = CLASSI[CLASSI.index(eta) + passi]
    return 100 * coorte(terr, gen, arrivo, anno1) / coorte(terr, gen, eta, anno0)


for terr, att01, att11 in ((B, 102.9, 88.6), (P, 87.6, 90.2), (S, 97.8, 92.1), (I, 113.1, 104.4)):
    check(f"decenni F {NOMI[terr]} 2001-2011", round(ritenzione_coorte(terr, "F", 2001, 2011), 1), att01)
    check(f"decenni F {NOMI[terr]} 2011-2021", round(ritenzione_coorte(terr, "F", 2011, 2021), 1), att11)
check("decenni M Bagheria 2001-2011", round(ritenzione_coorte(B, "M", 2001, 2011), 1), 98.4)
check("decenni M Bagheria 2011-2021", round(ritenzione_coorte(B, "M", 2011, 2021), 1), 83.9)
check("decenni: ribaltamento F Bagheria fra i due decenni",
      round(ritenzione_coorte(B, "F", 2011, 2021) - ritenzione_coorte(B, "F", 2001, 2011), 1), -14.3)
check("decenni: ribaltamento M Bagheria fra i due decenni",
      round(ritenzione_coorte(B, "M", 2011, 2021) - ritenzione_coorte(B, "M", 2001, 2011), 1), -14.5)
# controlli interni al solo permanente: la perdita è attuale e sta sulla 20-24 -> 25-29
check("decenni: F Bagheria 20-24 2018-2023",
      round(ritenzione_coorte(B, "F", 2018, 2023, "Y20-24"), 1), 92.8)
check("decenni: F Bagheria 20-24 2019-2024",
      round(ritenzione_coorte(B, "F", 2019, 2024, "Y20-24"), 1), 93.3)
check("decenni: F Italia 20-24 2019-2024",
      round(ritenzione_coorte(I, "F", 2019, 2024, "Y20-24"), 1), 102.2)

# (c) la forbice anno per anno, con il vicinato come territorio unico
lav_vic = pd.read_csv(RAW / "censpop_lavoro_vicini_2026-08-25.csv", dtype=str)
lav_vic["v"] = pd.to_numeric(lav_vic["OBS_VALUE"])
lav_vic["anno"] = lav_vic["TIME_PERIOD"].astype(int)
ist_vic = pd.read_csv(RAW / "censpop_istruzione_vicini_2026-08-25.csv", dtype=str)
ist_vic["v"] = pd.to_numeric(ist_vic["OBS_VALUE"])
ist_vic["anno"] = ist_vic["TIME_PERIOD"].astype(int)
check("forbice: comuni nel vicinato", lav_vic["REF_AREA"].nunique(), 5, 0.5)
ALMENO = ["USE_IF", "BL", "ML_RDD"]
ANNI_15_24 = [2018, 2019, 2021, 2022, 2023, 2024]


def tasso_occ(quadro, anno, gen, terr=None):
    d = quadro[(quadro["AGE_NOCLASS"] == "Y15-24") & (quadro["GENDER"] == gen)
               & (quadro["CITIZENSHIP"] == "TOTAL") & (quadro["EDU_ATTAIN"] == "ALL")
               & (quadro["anno"] == anno)]
    if terr is not None:
        d = d[d["REF_AREA"] == terr]
    return 100 * d[d["CUR_ACT_STAT"] == "1"]["v"].sum() / d[d["CUR_ACT_STAT"] == "99"]["v"].sum()


def vantaggio_edu(quadro, anno, terr=None):
    d = quadro[(quadro["AGE_NOCLASS"] == "Y9-24") & (quadro["CITIZENSHIP"] == "TOTAL")
               & (quadro["anno"] == anno)]
    if terr is not None:
        d = d[d["REF_AREA"] == terr]
    def quota(gen):
        g = d[d["GENDER"] == gen]
        return 100 * g[g["EDU_ATTAIN"].isin(ALMENO)]["v"].sum() / g[g["EDU_ATTAIN"] == "ALL"]["v"].sum()
    return quota("F") - quota("M")


for anno, att in ((2018, (2.47, 3.13, 4.68)), (2023, (1.89, 3.92, 8.02)), (2024, (2.01, 4.19, 8.19))):
    tf, tm = tasso_occ(lav, anno, "F", B), tasso_occ(lav, anno, "M", B)
    check(f"forbice {anno}: rapporto M/F Bagheria", round(tm / tf, 2), att[0], 0.011)
    check(f"forbice {anno}: vantaggio educativo F Bagheria",
          round(vantaggio_edu(ist, anno, B), 2), att[1], 0.011)
    check(f"forbice {anno}: tasso occupazione F Bagheria", round(tf, 2), att[2], 0.011)
check("forbice 2023: rapporto M/F vicinato",
      round(tasso_occ(lav_vic, 2023, "M") / tasso_occ(lav_vic, 2023, "F"), 2), 2.06, 0.011)
check("forbice 2024: vantaggio educativo F vicinato",
      round(vantaggio_edu(ist_vic, 2024), 2), 0.52, 0.011)


def anni_in_testa(estremo, misura):
    """In quanti anni Bagheria occupa l'estremo che definisce la forbice."""
    conta = 0
    for anno in ANNI_15_24:
        v = {NOMI[t]: misura(lav, ist, anno, t) for t in QUATTRO}
        v["vicinato"] = misura(lav_vic, ist_vic, anno, None)
        conta += estremo(v, key=v.get) == "Bagheria"
    return conta


check("forbice: anni in cui Bagheria ha il tasso F minimo del panel",
      anni_in_testa(min, lambda l, i, a, t: tasso_occ(l, a, "F", t)), 6, 0.5)
check("forbice: anni in cui Bagheria ha il rapporto M/F massimo",
      anni_in_testa(max, lambda l, i, a, t: tasso_occ(l, a, "M", t) / tasso_occ(l, a, "F", t)), 4, 0.5)
check("forbice: anni in cui Bagheria ha il vantaggio educativo massimo",
      anni_in_testa(max, lambda l, i, a, t: vantaggio_edu(i, a, t)), 4, 0.5)

# (d) i CSV letti dalle figure devono riportare gli stessi numeri
d390 = pd.read_csv(PROCESSED / "genere_distribuzione_390.csv")
check("distribuzione_390.csv rho 2011 vs 2024",
      d390[d390["anno"] == 2011]["rho_vs_2024"].item(), 0.848, 0.0011)
check("distribuzione_390.csv percentile 2024",
      d390[d390["anno"] == 2024]["percentile"].item(), 16.9)
check("distribuzione_390.csv persistenza quintile 2011",
      d390[d390["anno"] == 2011]["quintile_basso_ancora_tale_nel_2024_pct"].item(), 74.0)
m2024 = pd.read_csv(PROCESSED / "genere_mappa_2011_2024.csv", dtype={"territorio": str})
check("mappa_2011_2024.csv righe", len(m2024), 390, 0.5)
check("mappa_2011_2024.csv Bagheria 2024",
      m2024[m2024["territorio"] == B]["occ_2024"].item(), 23.7)
check("mappa_2011_2024.csv vicini etichettati",
      (m2024["ruolo"] == "vicino").sum(), 5, 0.5)
rit = pd.read_csv(PROCESSED / "genere_ritenzione_decennale.csv", dtype={"territorio": str})
check("ritenzione_decennale.csv Bagheria F 2011-2021",
      rit[(rit["territorio"] == B) & (rit["genere"] == "F") & (rit["anno_da"] == 2011)
          & (rit["eta_da"] == "Y15-19")]["ritenzione_pct"].item(), 88.6)
fserie = pd.read_csv(PROCESSED / "genere_forbice_serie.csv", dtype={"territorio": str})
check("forbice_serie.csv righe", len(fserie), 30, 0.5)
check("forbice_serie.csv Bagheria 2023 rapporto M/F",
      fserie[(fserie["territorio"] == B) & (fserie["anno"] == 2023)]["rapporto_M_F_occupazione"].item(),
      1.89, 0.011)

# ----------------------------------------------------------------- riepilogo ---
falliti = [e for e in esiti if not e[0]]
print(f"\n{'=' * 70}\nTOTALE: {len(esiti)} controlli, {len(esiti) - len(falliti)} PASS, {len(falliti)} FAIL")
for _, nome, calc, att in falliti:
    print(f"  FAIL {nome}: {calc} != {att}")
raise SystemExit(1 if falliti else 0)

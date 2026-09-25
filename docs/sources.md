# Data sources

Append-only register. This document describes **the endpoints**: how they are structured, what they contain,
and where the pitfalls are.

The register of **individual downloads** is `data/raw/manifest.csv`, written automatically by
`pipeline/fetch.py` on every download: UTC date, filename, exact URL, bytes, sha256.
It lives there rather than here because a manually written row per download is easy to forget, and sha256 is needed to
distinguish "same file" from "same name".

---

## 1. ISTAT — 8milaCensus (ottomilacensus.istat.it)

**Survey: 2026-08-12** (network inspection at https://ottomilacensus.istat.it/comune/082/082006/)

### Result: no JSON API, but scraping is unnecessary

Municipal pages are TYPO3 server-rendered: during loading there are **zero XHR/fetch requests**,
and zero JSON endpoints. Topic accordions are Bootstrap collapse components over HTML that is already present.

**However**, every page exposes direct links to already-clean CSV/XLSX files, and the portal has a Download section
with aggregated files. Download with `requests`, read with `pandas`. **No HTML scraping, no Selenium.**

### ⚠️ Constraint that changes the plan: the data are from 2011, not 2021

8milaCensus covers the **1951–2011 Population Censuses**. The Bagheria page is labelled
"DATI 2011". **It does not contain the 2021 Permanent Census.**
Consequence: 8milaCensus is used as the source for the **1991/2001/2011 historical series**; for the 2021 baseline
defined in CLAUDE.md, another source is required (`esploradati.censimentopopolazione.istat.it`, SDMX)
— to be investigated separately.

### Useful endpoints

#### A. Series at 2011 boundaries, all municipalities in a region — **recommended primary source**
```
https://ottomilacensus.istat.it/fileadmin/download/{cod_regione}/confini/confini_{cod_regione}.csv
```
Sicily = `19` → https://ottomilacensus.istat.it/fileadmin/download/19/confini/confini_19.csv
(verified 2026-08-12: 200, `text/csv`, 1170 data rows = 390 municipalities × 3 years)

A single file covers both Bagheria **and** the Municipality of Palermo. An `.xlsx` variant exists at the same path.

#### B. Provinces, Regions, Italy — territorial benchmarks
```
https://ottomilacensus.istat.it/fileadmin/download/Province_Regioni_Italia_confini_2011.csv
```
Contains the Province of Palermo, Region of Sicily, and Italy. Same 99 indicator columns as file A.

#### C. Codebook for the 99 indicators — **download this first**
```
https://ottomilacensus.istat.it/fileadmin/download/Descrizione_degli_indicatori_serie_confini_2011.csv
```
99 rows: `Descrizione tema;Codice Indicatore;Nome indicatore;Descrizione`.
The operational definitions (age groups, denominators) are here — this is the code→meaning map.

#### D. Symbol legend
```
https://ottomilacensus.istat.it/fileadmin/download/Legenda_codici_e_simboli_indicatori_ai_confini_2011.csv
```

#### E. Historical series 1951–2011 at the boundaries of each period (for long-term trends only)
```
https://ottomilacensus.istat.it/fileadmin/download/19/confini-epoca/confini-epoca_19.csv
```
Subset of indicators, with many missing cells in older censuses (symbol for unavailable data).
Extra column `Flag comuni con variazioni`. Use only if analysis needs to go back before 1991.

#### F. Single municipality, long format (convenient but partial)
```
https://ottomilacensus.istat.it/fileadmin/dati/csv/{prov}/dati_{prov}_{com3}_{NNN}.csv
```
Bagheria: `prov=082`, `com3=006`, `NNN` = `001`…`015` (016 → 404). Variant `/xlsx/` + `.xlsx`.
Format: `Descrizione tema;Descrizione sottotema;Nome indicatore;Denominazione11;AnnoCP;Value`.
Territories included: **Bagheria (1991, 2001, 2011) + Sicily 2011 + Italy 2011** — the Municipality of Palermo is missing.

NNN → subtopic map (indicator counts sum to 99):

| NNN | Topic | Subtopic | no. indicators |
|-----|------|-----------|---------|
| 001 | Population | Demographic dynamics and territory | 7 |
| 002 | Population | Population structure | 7 |
| 003 | Integration of foreign residents | Presence and integration indicators | 10 |
| 004 | Families | Family structure | 3 |
| 005 | Families | Structure of young families | 4 |
| 006 | Families | Structure of elderly families | 4 |
| 007 | Housing conditions | Housing stock | 11 |
| 008 | Housing conditions | Housing conditions | 4 |
| 009 | Education | General level of education | 5 |
| 010 | Education | Education by age group | 4 |
| 011 | Labour market | Population activity | 5 |
| 012 | Labour market | Unemployment | 4 |
| 013 | Labour market | Employment | 13 |
| 014 | Mobility | Daily commuting | 9 |
| 015 | Material and social vulnerability | Potential material and social difficulties | 9 |

#### G. Municipal summary PDF report
```
https://ottomilacensus.istat.it/fileadmin/report/{prov}/report_{prov}{com3}.pdf
```
Bagheria: https://ottomilacensus.istat.it/fileadmin/report/082/report_082006.pdf
For human reading only — it is not a data source.

### Structure of files A/B (wide format)

Header: `AnnoCP;Livello territoriale;Codice Regione 2011;Codice Provincia 2011;Codice comune 2011;Denominazione del territorio;` + 99 indicator codes.

Indicator codes by topic: `P1–P14` population, `S1–S10` foreign residents, `F1–F11` families,
`A1–A15` housing, `I1–I9` education, `L1–L22` labour, `M1–M9` mobility, `V1–V9` vulnerability.

`Livello territoriale`: `1` municipality, `2` province, `3` region, `4` Italy.

**Parsing pitfalls** (all verified on the actual files):
- Encoding is **windows-1252**, not UTF-8 → `encoding="cp1252"`; otherwise "età" becomes "et�".
- Field separator `;`, **decimal `,`**, **thousands separator `.`** (`5.002.904`) → `decimal=","`, `thousands="."`.
- Municipality codes **without leading zero**: Bagheria = `82006`, Municipality of Palermo = `82053`, province = `82`.
  The canonical six-digit ISTAT code (`082006`) must be reconstructed with zero-padding in the pipeline.
- A/B files have **blank trailing rows** (Excel export artifact: `;;;;…`). Filter on non-null `AnnoCP`:
  in `confini_19.csv` → 3646 total lines, 1170 data rows.
- In file E, missing data are represented by a symbol, not an empty string → see legend (D).

### Verified territorial codes (2026-08-12)

| Territory | Level | Code in file | 6-digit ISTAT code |
|---|---|---|---|
| Bagheria | 1 | `82006` | `082006` ✔ |
| Municipality of Palermo | 1 | `82053` | `082053` ✔ (confirmed: 2011 pop. = 657,561) |
| Province of Palermo | 2 | reg `19`, prov `82` | — |
| Sicily | 3 | reg `19` | — |
| Italy | 4 | — | — |

Note: in file B, the `Level 2 / Palermo` row is the **province**, not the municipality. The Municipality of Palermo
appears only in file A at level 1.

### Indicators relevant to the 15-34 target

Available (⚠️ all from **2011**):

| Code | Indicator | Age group |
|---|---|---|
| `L4` | Young people not in education or employment (NEET) | **15-29** |
| `V8` | Young people outside the labour market and education/training | 15-29 |
| `L14` | Youth employment rate | 15-29 |
| `L9` | Youth unemployment rate | 15-24 |
| `L5` | Ratio of active to inactive young people | 15-24 |
| `L13` | Occupational replacement index (>45 over 15-29) | 15-29 |
| `I7` | Young people with university education | **30-34** |
| `I5` | Early leaving from education and training | 15-24 |
| `I8` | Education level of young people | 15-19 |
| `F4` | Young people living alone | **15-34** (denominator) |
| `F5`–`F7` | Single-parent families / young couples with and without children | <35 |

Gender indicators (`I1` higher-education differential, `L1`/`L2` labour-force participation,
`L6`/`L7` unemployment, `L10`/`L11` employment): **calculated for age 15+, not crossed with age.**

→ For the **Gender** thread this means: 8milaCensus provides the *overall* gender gap and youth data
*without gender*, but **not the gender gap within ages 15-34**. That cross-tab must be found elsewhere
(2021 data browser / dati.istat.it), or the thread must work with the overall gap while explicitly declaring the limitation.
There is no direct 15-34 age group for labour/education: only 15-29, 15-24, 30-34 → aggregation to the
15-34 target cannot be reconstructed from this source and must be documented as a methodological choice in the notebook.

### Spot-check values (Bagheria 2011, from `confini_19.csv`)

Use as regression assertions in the pipeline, not as figures to cite:
`L4 = 40.1` · `V8 = 23.4` · `L14 = 20.0` · `I7 = 14.4` · resident population `54,257`.

### Operational notes
- `HEAD` returns **403** on `/fileadmin/`; always use `GET`. This is not a block: `GET` returns 200.
- No authentication, no rate limit encountered.
- Files are static: download once into `data/raw/` with the date in the filename.

---

## 2. ISTAT — Permanent Population and Housing Census (IstatData, SDMX)

**Survey: 2026-08-12**

### The old host is dead — use IstatData

`esploradati.censimentopopolazione.istat.it` is **no longer reachable**: the served certificate is
`CN=*.istat.it` with SAN `*.istat.it, istat.it`, and the wildcard covers only one level → it does not match a
three-label subdomain. Chrome shows "Privacy error", `curl` returns error 60. This is not our issue
and must not be bypassed by disabling TLS verification.

The portal has been **migrated**: `01a-filtro.istat.it` returns `301` to
`https://esploradati.istat.it/databrowser/#/it/censpop`.

→ Correct host: **`esploradati.istat.it`**. The Permanent Census is a thematic node (`censpop`)
within IstatData, using the same SDMX API as the rest of ISTAT.

### SDMX REST API — works, no authentication

Base: `https://esploradati.istat.it/SDMXWS/rest/`

| Resource | Path | `Accept` header |
|---|---|---|
| Dataflow list | `dataflow/IT1` | `application/vnd.sdmx.structure+json;version=1.0` |
| DSD + codelists for a dataflow | `dataflow/IT1/{DF}/1.0?references=all&detail=full` | same |
| Single codelist | `codelist/IT1/{CL}/1.0` | same |
| Dataflow→category map | `categorisation/IT1` | same |
| **Data** | `data/IT1,{DF},1.0/{key}/ALL/?detail=full` | `application/vnd.sdmx.data+csv;version=1.0.0` |

Verified 2026-08-12: `dataflow/IT1` → 200, 4896 total dataflows; `categorisation/IT1` → 5098 rows.
Census dataflows are the **114** categorized under category scheme `IT1:Z1200CPA(1.0)`.

SDMX-CSV is the most convenient format: one row per observation, columns = dimensions + `OBS_VALUE`,
readable with `pd.read_csv` without an SDMX parser. **`pandasdmx` is not needed.**

**Building the `key`**: values are separated by `.`, in the exact order of the DSD dimensions;
an empty position means all values. Wrong number of positions → **HTTP 422**.
Dimensions are read from `dataStructureComponents.dimensionList.dimensions`.

Example (Bagheria, all other dimensions unrestricted), DSD with 10 dimensions:
```
data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_3,1.0/A.082006......../ALL/?detail=full
```

### Relevant dataflows (all at **municipal** level)

| Dataflow | Content | Key dimensions | Years |
|---|---|---|---|
| `DF_DCSS_ISTR_LAV_PEN_2_TV_3` | Pop. 15+ by **labour-force status** and age | GENDER, AGE_NOCLASS, CUR_ACT_STAT, EDU_ATTAIN, CITIZENSHIP | 2018–2024 |
| `DF_DCSS_ISTR_LAV_PEN_2_TV_1` | Pop. 9+ by **educational attainment** and age | GENDER, AGE_NOCLASS, EDU_ATTAIN | 2018–2024 |
| `DF_DCSS_POP_DEMCITMIG_SETA_1` | Resident pop. by **single year of age**, gender, citizenship | GENDER, AGE_NOCLASS (Y0…Y_GE100) | 2018–2024 |
| `DF_DCSS_POP_DEMCITMIG_TV_1` | Pop. by five-year age groups and gender | GENDER, AGE_CLASS | 2001, 2011, 2018–2024 |
| `DF_DCSS_EMPLP_1_COM` | Employed people by gender and employment status | GENDER, EMPLOYMENT_STATUS | **2021 only** |
| `DF_DCSS_ISTR_LAV_PEN_2_TV_5` | Daily commuting for study/work | LOC_DEST, REAS_COMMUTING | 2018–2024 |
| `DF_DCSS_POP_DEMCITMIG_TV_5` | Synthetic demographic indicators | — | — |
| `DCSS_BULK_ISTR_LAV_PEN_2` | Bulk download "Education, work, commuting and citizenship" | — | — |

Category `BULKDOWNLOAD` (8 dataflows) = bulk download, an alternative to point queries.
Category `DCSS_BEST_PPC` (BesT) = subjective well-being, but **only provinces and large cities** — not Bagheria.

### Territorial codes (codelist `CL_ITTER107`, 12471 codes)

| Territory | Code |
|---|---|
| Bagheria | `082006` (**with** leading zero) |
| Municipality of Palermo | `082053` |
| Sicily | `ITG1` |
| Italy | `IT` |

⚠️ **Difference from 8milaCensus**: there the municipality code has no leading zero (`82006`), here it does (`082006`).
Normalize in the pipeline to six-digit zero-padded codes.

Warning: `CL_ITTER107` also contains `SLL_2021_1906 = Bagheria` (Local Labour System) and
`T19039 = Distretto di Bagheria`. These are **different territories** from the municipality — do not confuse them.

### Useful codelists

- `CL_SEXISTAT1` → `M` male, `F` female, `T` total (legacy `1`/`2`/`9` also exist: use M/F/T).
- `CL_FORZE_LAV` (labour-force status): `1` employed · `12` unemployed · `22` labour force ·
  `23` not in labour force · `24` pension/annuity recipient · `5` student · `4` homemaker ·
  `7` other condition · `99` total.
- `CL_TITOLO_STUDIO`: `ALL` total · `NED` no qualification · `IL` illiterate · `LSE` lower-secondary certificate ·
  `USE_IF` upper-secondary diploma · `PSE` tertiary · `BL` degree · `ML` master's degree · `RDD`/`ML_RDD` doctorate.
- `CL_CITTADINANZA`: `TOTAL` · `ITL` Italian citizens · `FRGAPO` foreign citizens.

### ⚠️ Constraint that determines the analytical scope: age groups

In the **labour-force status** and **educational attainment** tables at municipal level, the only age groups
available are:

- `DF_..._TV_3` (labour): `Y15-24`, `Y25-49`, `Y50-64`, `Y_GE65`, `Y_GE15`
- `DF_..._TV_1` (education): `Y9-24`, `Y25-49`, `Y50-64`, `Y_GE65`, `Y_GE9`

**The 15-34 age group cannot be constructed** for labour and education: `Y25-49` extends far beyond the target and cannot
be decomposed. There are no 15-29, 25-34, or 30-34 groups at municipal level.
Operational consequences:
- The **15-29 NEET** defined in CLAUDE.md **cannot be calculated for Bagheria in 2021**. At most, a proxy can
  be constructed for `Y15-24` (not in labour force `23` minus students `5`, or `23` net of
  students depending on the convention) — it is a different measure and must be labelled as such, not presented as NEET.
- The 8milaCensus series gives NEET 15-29 **in 2011**; the 2021 source gives `Y15-24`. **They are not comparable**:
  any chart that places them on the same line is wrong.

**Where 15-34 does work**: `DF_DCSS_POP_DEMCITMIG_SETA_1` has **single ages** by gender,
so exact male/female population aged 15-34 is available for each year. It can be used as a denominator and to measure
youth population decline, not for labour/education indicators.

### ✔ Good news for the Gender thread

`GENDER` is a full dimension crossed with age and labour-force status at municipal level.
The gender gap among young people — unavailable in 8milaCensus — **does exist in 2021**, for age group `Y15-24`.
It can also be crossed with `EDU_ATTAIN` to decompose the gap by educational attainment.

### ✔ Second piece of good news: it is an annual series, not a single year

The Permanent Census publishes **2018–2024**, not only 2021. The recent trajectory can be shown
instead of a snapshot, and 2024 is much more current than the 2021 baseline envisaged in CLAUDE.md.
(On `SETA_1`, 2018 returned empty for Bagheria with `CITIZENSHIP=TOTAL`: verify in the pipeline,
do not assume it.)

### Parsing pitfalls

- **Double counting on `CITIZENSHIP`**: the CSV contains `TOTAL`, `ITL`, and `FRGAPO` as sibling rows.
  Summing without filtering `CITIZENSHIP == "TOTAL"` inflates totals by roughly 2×. The same risk applies to `GENDER`
  (`T` coexists with `M`/`F`) and every dimension with a total code.
- `OBS_VALUE` is plain numeric with decimal `.` — unlike 8milaCensus CSV files.
- `NOTE_*` columns are almost always empty; `detail=full` includes them anyway.
- The provider segment in the URL is `ALL`.

### Spot-check values (Bagheria, verified 2026-08-12)

Use as regression assertions:
- Pop. 15-34 (sum of single ages, `CITIZENSHIP=TOTAL`): **2021 → 12,174** (M 6,120 / F 6,054);
  **2024 → 11,861** (M 6,015 / F 5,846). Decline of 313 people in 3 years (−2.6%).
- Labour-force status `Y15-24` 2021: employed M **419** / F **176**; total M **3,039** / F **2,852**.
  → employment rate 15-24: M 13.8% · F 6.2%.

---
## 3. Local open-data portals — negative result for the gender focus

**Survey: 2026-08-12.** Question: do they add anything to the gender analysis of 15-34-year-olds in Bagheria?
**Answer: no.** This is documented because a negative result is as useful as a positive one — it prevents
someone else from repeating the same search.

### dati.regione.sicilia.it (CKAN, 192 datasets)

Standard REST API: `https://dati.regione.sicilia.it/api/3/action/package_search?q=...`

Searches for `genere`, `donne`, `femminile`, `sesso`, `occupazione`, `disoccupazione`, `giovani`,
`neet`, `istruzione`, `laureati`: **13 distinct datasets**, none useful for the analysis.
The only datasets disaggregated by sex (`Personale - Consistenza, categoria e sesso`,
`Personale - Fasce di età per sesso`) concern **Regional Government employees**, not the population.

**Useful instead for the policy-design part** (where services are, not how young people are doing):

| Dataset | Formats | Bagheria rows |
|---|---|---|
| Higher technical education pathways (ITS) — school registry, 2025/26 school year | CSV, JSON | **3** |
| Accredited employment-service providers | CSV | **4** |
| Job vacancies (Regional Employment Agency) | CSV, JSON, TTL | to be verified |
| ESF - List of beneficiaries | — | to be verified |

The three technical schools in Bagheria (2025/26 school year) and the four accredited employment-service locations
provide a factual base for an intervention: they show what already exists locally.
Download them when writing the proposal, not now.

### opendata.comune.palermo.it — not CKAN

`/api/3/action/*` returns **404**: this is a custom PHP portal, not CKAN.
The machine-readable catalog is **DCAT in Turtle** at `https://opendata.comune.palermo.it/dcat/dcat.php`
(~4.3 MB, `text/n3`). In the Turtle file the predicate is `dc:title`, not `dct:title`, and every dataset appears
twice (the second entry as `Distribuzione CSV del dataset ...`): 3451 titles → **1691 actual datasets**.

It contains data by sex and education — `STUDENTI UNIVERSITARI ISCRITTI PER SESSO, FACOLTA' E TIPO DI
CORSO`, `XIV CENSIMENTO ... OCCUPATI PER POSIZIONE NELLA PROFESSIONE E SESSO` — but:

1. they refer to **academic years 2008-2010** and the 2001 census, making them older than everything already available;
2. they cover **only the Municipality of Palermo**, never Bagheria.

As a benchmark, Palermo is already covered better by ISTAT (same definitions, same years, same sources).
**There is no reason to use this portal for the Gender thread.**

---

## 4. `data/processed/` interface — table schema

Produced by `pipeline/build.py`, reproducible with `uv run python -m pipeline.build`.
Long tables + lookups: no analytical choice is baked in; each thread filters what it needs.

| File | Rows | Columns |
|---|---|---|
| `territori.csv` | 521 | `territorio`, `nome_territorio`, `livello`, `fonti` |
| `indicatori.csv` | 99 | `indicatore`, `nome_indicatore`, `tema`, `descrizione` |
| `codici.csv` | 136 | `dimensione`, `codice`, `etichetta` |
| `ottomilacensus_long.csv` | 154,737 | `territorio`, `nome_territorio`, `livello`, `anno`, `indicatore`, `valore` |
| `censpop_istr_lav_long.csv` | 6,552 | `territorio`, `anno`, `tavola`, `genere`, `eta`, `eta_anni`, `cittadinanza`, `titolo_studio`, `condizione`, `valore` |
| `censpop_popolazione_long.csv` | 14,462 | `territorio`, `anno`, `genere`, `eta`, `eta_anni`, `stato_civile`, `cittadinanza`, `valore` |

- **`territorio` is the common key across the two sources.** Municipalities use six-digit ISTAT codes (`082006`),
  Sicily `ITG1`, Italy `IT` — the same codes as SDMX, so the tables can be joined without mappings.
  Provinces and regions other than Sicily, which do not exist in this SDMX scope, use the `PROV`/`REG` prefix.
- **`eta_anni`** is age as a number, populated only for single ages (`Y23` → 23). For age groups
  (`Y15-24`) and totals it remains blank: filter on `eta`, not `eta_anni`.
- **`tavola`** in `censpop_istr_lav_long` is either `lavoro` or `istruzione`: the two SDMX tables share
  the same DSD, so they are stored in one file.
- Long descriptions are stored in lookup tables rather than the data tables: repeating them row by row increased
  `ottomilacensus_long` from 5 to 40 MB.

**When reading in R, force code columns to character.** `condizione` contains `1`, `12`, `99`:
`readr` guesses them as integers and string filters then fail silently.

```r
library(tidyverse)
long    <- read_csv("data/processed/censpop_istr_lav_long.csv", col_types = cols(.default = "c", valore = "d", anno = "i"))
codici  <- read_csv("data/processed/codici.csv", col_types = cols(.default = "c"))

occupazione_giovanile <- long |>
  filter(tavola == "lavoro", eta == "Y15-24", cittadinanza == "TOTAL",
         titolo_studio == "ALL", genere %in% c("M", "F")) |>
  select(territorio, anno, genere, condizione, valore) |>
  pivot_wider(names_from = condizione, values_from = valore) |>
  mutate(tasso_occupazione = 100 * `1` / `99`)
```

Warning: `PSE` = *primary school certificate*, not "post-secondary": educational-attainment codes
cannot be inferred from their acronym; read them from `codici.csv`.

---

## 5. ISTAT — Administrative boundaries (cartography)

Added on 2026-08-12 for the municipal map in the Gender thread (`viz/fig04_mappa_sicilia.R`).

### Endpoint

```
https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/2026/Limiti01012026_g.zip
```

Downloaded on **2026-08-12** (10,450,609 bytes) to `data/raw/istat_confini_comuni_2026-08-12.zip`,
with the corresponding row in `data/raw/manifest.csv`. No parameters, no authentication.

### ⚠️ Only the current vintage is available

Historical years are **no longer available on this storage** (verified 2026-08-12: `2011`, `2012`, and
`archivio*` paths return 404). The only years served are 2024, 2025, and 2026. As a
result, a map of 2011 data uses 2026 boundaries: the mismatch is not assumed away, it is checked through the
join (the "Bagheria nella distribuzione siciliana" cell in `notebooks/genere.ipynb` does this).

Join result for Sicily: **391 municipalities in the 2026 boundaries, 390 in the 2011 data**. Every municipality
with data has a boundary; the only unmatched municipality is **Misiliscemi** (`081025`), created in 2021
from part of Trapani. It did not exist in 2011: it remains blank on the map; assigning Trapani's value
to it would be an imputation.

### ZIP structure

Four folders, one per level: `Com01012026_g/` (municipalities, 7,896 rows), `ProvCM01012026_g/`,
`Reg01012026_g/`, `RipGeo01012026_g/`. Each folder contains a complete shapefile (`.shp/.dbf/.shx/.prj`).
It can be read without unpacking: `gpd.read_file("zip://<zip>!Com01012026_g/Com01012026_g_WGS84.shp")`.

Useful columns: `PRO_COM_T` (six-digit municipality code, **already zero-padded**, matches `territorio`),
`COMUNE`, `COD_REG` (Sicily = `19`).

**The file CRS is EPSG:32632** (UTM 32N) despite the `_WGS84` suffix in the filename: the correct zone
for Sicily is 33N; `pipeline/build.py` reprojects to **EPSG:32633**.

### Why `data/processed/` contains vertices instead of GeoJSON

`sf` cannot be installed on these machines (it requires system GDAL/GEOS/PROJ libraries and root permissions).
`pipeline/build.py` therefore exports `comuni_sicilia_poligoni.csv` — one row per vertex, with
`territorio, nome_comune, parte, anello, ordine, x, y` — plus `comuni_sicilia_centroidi.csv` with an
internal label point for each municipality. In R they are drawn with `geom_polygon(group = comune ×
parte, subgroup = anello, rule = "evenodd")`: `parte` separates islands belonging to the same municipality, while `anello`
distinguishes the outer contour from holes. There are 15,702 vertices after `simplify(100 m)`, 0.6 MB.

---
## 6. ISTAT — Permanent Census, the five municipalities nearest to Bagheria (SDMX)

Downloaded on **2026-08-25** to include Bagheria's surrounding area in figures 1 and 7 of the Gender
thread. Same host and same dataflows as section 2: only the `key` changes, listing the
five **geographically closest municipalities** by distance between ISTAT centroids (the selection is
computed by `notebooks/genere.ipynb`, in the map cell, and written to
`data/processed/genere_mappa_etichette.csv`).

| Code | Municipality | Distance from Bagheria centroid |
|---|---|---|
| `082067` | Santa Flavia | 2.9 km |
| `082035` | Ficarazzi | 3.2 km |
| `082079` | Villabate | 4.7 km |
| `082023` | Casteldaccia | 7.9 km |
| `082048` | Misilmeri | 8.1 km |

Exact URLs (headers `Accept: application/vnd.sdmx.data+csv;version=1.0.0`, `Accept-Language: it`):

```
data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_3,1.0/A.082067+082035+082079+082023+082048......../ALL/?detail=full
data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_1,1.0/A.082067+082035+082079+082023+082048......../ALL/?detail=full
data/IT1,DF_DCSS_POP_DEMCITMIG_SETA_1,1.0/A.082067+082035+082079+082023+082048......./ALL/?detail=full
```

→ `data/raw/censpop_lavoro_vicini_2026-08-25.csv`, `censpop_istruzione_vicini_2026-08-25.csv`, and
`censpop_popolazione_vicini_2026-08-25.csv`, with the same structure as their four-territory counterparts
(section 2). Command: `uv run python -m pipeline.fetch --solo=vicini`.

**Why separate files instead of an expanded `TERRITORI`.** `pipeline/build.py` always takes the most
recent raw file for each prefix (`ultimo()`): re-downloading censpop with nine territories would have made them available
automatically to every thread, changing the results of code that aggregates without filtering by territory.
With distinct prefixes, the shared `censpop_*_long.csv` files remain limited to four territories, while the nearby municipalities
live in `censpop_istr_lav_vicini_long.csv` (labour + education, same schema as the shared table) and
`censpop_popolazione_vicini_long.csv`.

**Gender thread outputs** (all with the five municipalities kept separate and, where needed for figures, the
aggregated row `territorio = "VICINI5"` — anyone summing these files by territory must exclude it):
`genere_gap_occupazione_ci_vicini.csv` (fig01), `genere_composizione_stato_dettaglio_vicini.csv`
(fig02), `genere_coorti_vicini.csv` (fig03), `genere_forbice_vicini.csv` (fig05),
`genere_ritenzione_eta_vicini.csv` (fig07).

**Coverage verified on raw data**: 5 territories, years 2018-2024 with **2020 missing for the
15-24 age group** (the same source gap as for the benchmark territories), single-year ages available from 2021.

**Sample size**: municipalities with 10,000 to 28,000 residents, 580-800 women aged 15-24 per year, and
employed-women counts in the tens. Confidence intervals around the gap are much
wider than those for the four benchmark territories: these series provide local context, not estimates to
compare year by year.

**Timeout**: the single-age query takes more than 180 seconds to produce the response body
(verified 2026-08-25, three failed attempts). The `pipeline/fetch.py` timeout was raised to
600 seconds.

---

## 7. ISTAT — Permanent Census beyond 2011: matched peers, 390 municipalities, five-year age groups

Survey and download on **2026-08-25**. Starting question: `viz/fig10_muro_recente.R`
stops at 2011 because 8milaCensus is the last decennial census — can we get
closer to the present while staying within sources already catalogued? **Yes**, without changing source:
the same labour table from section 2 exposes the **age 15+** class.

### The bridge key: `AGE_NOCLASS = Y_GE15`

In `DF_DCSS_ISTR_LAV_PEN_2_TV_3`, class `Y_GE15` exists at municipal level and is crossed
with `GENDER` and `CUR_ACT_STAT`. It is **the same basis as the four labour indicators in
8milaCensus**, not an approximation: the codebook definitions (`indicatori.csv`)
match code by code.

| 8milaCensus (1991-2011) | Reconstruction from the Permanent Census (2018-2024) |
|---|---|
| `L11` female employment rate | `CUR_ACT_STAT=1` / `99`, `GENDER=F`, `Y_GE15` |
| `L10` male employment rate | `1` / `99`, `GENDER=M`, `Y_GE15` |
| `L2` female labour-force participation | `22` / `99`, `GENDER=F`, `Y_GE15` |
| `L7` female unemployment rate | `12` / `22`, `GENDER=F`, `Y_GE15` |

`I1` (M/F educational differential) **cannot be reconstructed**: 8milaCensus calculates it on the
population aged **6+**, while the Permanent Census education table starts at `Y_GE9` and has no
15+ class. It would be a different indicator rather than a continuation, so it remains fixed at 2011.

### ✔ The two surveys agree on employment — but not on unemployment

The 2011 → 2018 jump compares **two different survey designs**: a universal decennial
questionnaire census versus a sample-based Permanent Census supported by
administrative registers. This is not external validation (both sets of figures still come from ISTAT), but it
shows whether the level depends on the design. Bagheria:

| | 2011 (decennial) | 2018 (permanent) | difference |
|---|---|---|---|
| L11 female employment | 18.1 | 18.8 | +0.7 |
| L10 male employment | 43.1 | 40.4 | −2.7 |
| L2 female participation | 28.7 | 30.4 | +1.7 |
| L7 female unemployment | 36.9 | 38.1 | +1.2 |

⚠️ **The real break is not at the junction between the two sources: it is inside the Permanent Census, between
2019 and 2021**, and appears in every territory (Bagheria L7 38.1 → 22.6; Italy 15.1 → 10.6;
Sicily 30.1 → 17.3). The measurement of "seeking employment" changes, affecting **L7 and L2**
while leaving L10 and L11 intact; the latter cross 2019-2021 without discontinuities. Operational
consequence: **extend L11 and L10; use L2 and L7 only with the break explicitly marked**.
The complete table for the four territories is in `data/processed/genere_coerenza_fonti.csv`,
produced by `notebooks/genere.ipynb` (section "Il ponte fra i due censimenti").

### ⚠️ Constraint that determines how data are downloaded: IIS truncates the path segment

The SDMX server sits behind IIS, which rejects a **path segment** longer than roughly 260 characters with
`400 Bad Request - Invalid URL` (not `414`, and the body is HTML: without the check in
`pipeline/fetch.py`, an error page disguised as CSV would end up in `data/raw/`).
Verified on 2026-08-25 using the municipality key: **33 codes → 200, 35 → 400**.
Therefore the 390 Sicilian municipalities are downloaded in **12 blocks** of 33.

### The three added queries

Headers as in section 2 (`Accept: application/vnd.sdmx.data+csv;version=1.0.0`,
`Accept-Language: it`). Commands: `uv run python -m pipeline.fetch --solo=gemelle`,
`--solo=demografia_classi`, `--solo=15piu`.

**A. The ten structural peers** — `censpop_lavoro_gemelle_2026-08-25.csv`
```
data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_3,1.0/A.082070+082067+082020+082073+082048+082005+082071+081008+084028+084041......../ALL/?detail=full
```
Termini Imerese, Santa Flavia, Capaci, Trabia, Misilmeri, Altofonte, Terrasini, Erice,
Porto Empedocle, Sciacca — the Mahalanobis-matching comparison group, which previously
existed only for 2011. Full table (all age groups), 1.0 MB.
Warning: **Santa Flavia and Misilmeri are also among the five nearby municipalities** in section 6.
The two raw datasets remain separate; anyone combining them must deduplicate by territory.

**B. The 390 Sicilian municipalities for the 15+ class only** — `censpop_lavoro_15piu_sicilia_01..12_2026-08-25.csv`
```
data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_3,1.0/A.{33 codes separated by +}...Y_GE15.TOTAL.ALL.../ALL/?detail=full
```
Key restricted to `Y_GE15` / `CITIZENSHIP=TOTAL` / `EDU_ATTAIN=ALL`: 162 rows per municipality
instead of 819. Without this restriction there would be about 320,000 rows to use only one fifth of them.
This is the **denominator for regional percentiles**, which previously existed only for 2011.

⚠️ **390, not 391.** The list is the set of municipalities **at 2011 boundaries**, the same population on which the
notebook calculates 8milaCensus percentiles. **Misiliscemi** (`081025`), created in 2021
from part of Trapani, is deliberately excluded: including it would change the denominator between the
two periods and make percentiles non-comparable. Corollary to state explicitly: 2021-2024 values for
**Trapani** (`081021`) refer to a smaller territory than in 2011.

**C. Population by five-year age groups** — `censpop_demografia_classi_2026-08-25.csv`
```
data/IT1,DF_DCSS_POP_DEMCITMIG_TV_1,1.0/A.082006+082053+ITG1+IT......./ALL/?detail=full
```
DSD with **9 dimensions**: `FREQ, REF_AREA, INDICATOR, GENDER, AGE_CLASS, MARITAL_STATUS,
CITIZENSHIP, AREA_CONTRY_CITIZEN, USUAL_RESID_1Y`. Note that the age dimension here is
called `AGE_CLASS`, not `AGE_NOCLASS` as in the tables from section 2.

This is **the only municipal table covering 2001 and 2011 in addition to 2018-2024**: `SETA_1` starts in
2018 and single ages only in 2021. Classes `Y15-19`, `Y20-24`, `Y25-29`, `Y30-34`
reconstruct the **exact 15-34 target**, extending its demographic series by
twenty years. At municipal level, `MARITAL_STATUS`, `AREA_CONTRY_CITIZEN`, and `USUAL_RESID_1Y`
only take `ALL`, while `CITIZENSHIP` is only `TOTAL`: no cross-tabulations, only age structure.

### Timing and coverage

- Blocks of 33 municipalities: ~50-60 s each, ~12 minutes for all 390. `DF_DCSS_POP_DEMCITMIG_TV_1`
  for four territories: 70 s. The `pipeline/fetch.py` timeout (600 s) is sufficient.
- Years served on `Y_GE15`: **2018, 2019, 2021, 2022, 2023, 2024**. **2020 is missing**, as for
  every class containing ages 15-24 (the same source gap already known from section 2).
- `DF_DCSS_POP_DEMCITMIG_TV_1`: **2001, 2011, 2018-2024**; 2020 is present here.

### Outputs in `data/processed/`

| File | Content |
|---|---|
| `censpop_lavoro_gemelle_long.csv` | labour table for the 10 structural peers, same schema as `censpop_istr_lav_*_long` |
| `censpop_lavoro_15piu_sicilia_long.csv` | 390 municipalities × `Y_GE15`, 2018-2024 |
| `censpop_demografia_classi_long.csv` | population by five-year age group, 2001-2024 |
| `genere_coerenza_fonti.csv` | 2011 decennial vs 2018 permanent + 2019-2021 break, for the 4 territories |
| `genere_madri_recente.csv` | L2/L11/L10/L7 and percentile across the 390, 2018-2024 (recent counterpart of `genere_gap_madri.csv`) |
| `genere_pretrend_gemelle_recente.csv` | Bagheria L11 against the interquartile band of the matched peers, 2018-2024 |

`pipeline/build.py` skips these outputs without failing if the raw files are absent, so users who
have not yet re-run the fetch can still regenerate everything else.

### Rule for figures

The two sources remain two distinct sources. **Never draw a continuous line between 2011 and 2018**: show a visible break
and declare the source for each block. **Percentiles** cross the junction better than levels because
they are ranks calculated within each year, and the definitional shift moves all 390 municipalities
in the same direction; absolute levels do not, and must be read as two adjacent series.

---

## 8. Currency check of the claims: does the 2011 ranking still hold in 2024?

*Survey on 2026-08-25, with no new downloads.* Everything below is derived from raw files
already in `data/raw/` (sections 1, 2, 6, and 7). The purpose is to answer the question: "do the claims
rest on legacy data or on verifiable predictions?" before using them in the proposal.

### Persistence of the ranking across 390 municipalities

Same indicator (`L11`, female employment rate age 15+), same population (390 municipalities at
2011 boundaries), two periods and two survey designs. The comparison is between **ranks**, not
levels, for the reason already explained at the end of section 7.

| year pair | Spearman rho | bottom quintile still bottom quintile in 2024 |
|---|---|---|
| 2011 → 2024 (8milaCensus → permanent) | **0.848** | 74% |
| 2011 → 2018 | 0.883 | 83% |
| 2018 → 2024 (permanent only) | **0.919** | 83% |
| 2021 → 2024 (permanent only) | 0.942 | 87% |

Read this way, the municipal ranking is a stable structure, not annual noise. A
positioning claim built on the 2011 census **was borne out**, and rho quantifies that persistence.
The level, however, must be updated: Bagheria moves from 18.1% (12th percentile) to 23.7% (17th),
while the regional median rises from 23.6% to 28.3% — in other words, **in 2024 Bagheria reaches the level
of the Sicilian median in 2011**.

Necessary caveat: a high rho means that the *ordering* persists, not that the levels are
comparable. The two surveys do not measure exactly the same construct in exactly the same way, and on the
map the two years remain on two separate scales.

### Cohort retention in five-year steps

`DF_DCSS_POP_DEMCITMIG_TV_1` (section 7) serves 2001, 2011, and 2018-2024 in five-year
age groups: a cohort is followed by moving **one age band every five years**. Those aged
15-19 at *t* are aged 25-29 at *t+10*.

| female cohort aged 15-19 | Bagheria | Palermo | Sicily | Italy |
|---|---|---|---|---|
| 2001 → 2011 | **102.9%** | 87.6% | 97.8% | 113.1% |
| 2011 → 2021 | **88.6%** | 90.2% | 92.1% | 104.4% |

For men, the reversal is 98.4% → 83.9%. In both cases this is **about fourteen points
in a decade**, and in the second decade Bagheria is below Palermo for men.

**The 2011-2021 decade has one leg from each survey** (2011 decennial, 2021 permanent) and
must be marked as such. The known distortion, however, is conservative: the 2011 census counted fewer people
than the population register, so it appears in the *denominator* of the decade that collapses and in the *numerator* of
the decade that holds up — the gap between the two decades is therefore an **underestimate on both
legs**. Moreover, checks entirely internal to the Permanent Census (2018→2023 and 2019→2024)
recover the loss in the transition 20-24 → 25-29: women 92.8% and 93.3% in Bagheria
versus about 102% in Italy. The loss is datable and current.

### Stability of the “scissors” (fig05)

The two measures of the scissors pattern repeated over all available years (2018-2024, with 2020
missing), comparing Bagheria with the four benchmarks and the aggregated nearby area:

| measure | years in which Bagheria is at the extreme |
|---|---|
| female employment rate 15-24 (lowest) | **6 years out of 6** |
| female educational advantage 9-24 (largest) | 4 years out of 6 (in 2018-2019 it was Sicily) |
| M/F employment ratio (highest) | 4 years out of 6 (in 2022-2023 it was the nearby-area aggregate) |

Here the problem is not the age of the data — the snapshot is already from 2024 — but the risk of relying
on **a single year**. Bagheria's M/F ratio fluctuates (2.47 in 2018 → 1.89 in 2023 →
2.01 in 2024), and in 2023 it was the best in the local comparison group. The defensible claim is the
**female level**, the lowest in the panel every year, together with the widening scissors pattern
(female educational advantage from +3.1 to +4.2 while the nearby-area aggregate falls from +2.9 to +0.5).

### Outputs in `data/processed/`

| File | Content |
|---|---|
| `genere_distribuzione_390.csv` | by year: Bagheria, percentile, median, quartiles, rho vs 2011 and vs 2024, bottom-quintile persistence |
| `genere_mappa_2011_2024.csv` | 390 municipalities: value and percentile in the two years, centroid, role for labelling |
| `genere_ritenzione_decennale.csv` | cohort retention for all age groups and four periods (2001-2011, 2011-2021, 2018-2023, 2019-2024) |
| `genere_forbice_serie.csv` | the three scissors measures for 5 territories × 6 years (snapshot and series in the same table) |

### Rule for figures

A positioning claim must be written **with its rho**: saying "12th percentile in 2011"
without saying that the ranking predicts 2024 with rho 0.848 gives a reviewer the easiest
possible objection. Conversely, a recent snapshot built on a single year must
be accompanied by the series, otherwise an oscillation can be mistaken for a structural pattern.

---
## 9. ISTAT — Population by marital status and single year of age (DCIS_POPRES1, SDMX)

**Survey: 2026-08-26** — needed by the Gender thread to answer the question "are women in their twenties
classified as homemakers married?" (`notebooks/genere.ipynb`, section "Le casalinghe sono
coniugate?").

### Why not use the Permanent Census

The Permanent Census **does not cross-tabulate marital status at municipal level**: throughout the
`DF_DCSS_POP_DEMCITMIG_*` family, dimension `MARITAL_STATUS` is served only as
`ALL`, and an explicit key (e.g. `A.082006....2...` on `TV_1` or `SETA_1`) returns
**404 NoRecordsFound** (verified 2026-08-26). `DF_DCSS_HCUE_COM_1_COM` ("Population
by marital status - municipalities") includes marital status but **not age**. The correct table is outside
the Permanent Census:

- **Dataflow**: `22_289_DF_DCIS_POPRES1_26` — "All municipalities by single year of age and marital
  status", DCIS_POPRES1 family (resident population on **January 1**, census-based
  since 2019).
- **DSD with 6 dimensions**: `FREQ, REF_AREA, DATA_TYPE, SEX, AGE, MARITAL_STATUS`.
- **Query used** (`popres_stato_civile_eta` fetch, raw file dated 2026-08-26):
  `data/IT1,22_289_DF_DCIS_POPRES1_26,1.0/A.082006+082053+ITG1+IT..../ALL/?detail=full`
- Command: `uv run python -m pipeline.fetch --solo=stato_civile`. Processed output:
  `popres_stato_civile_long.csv` (sex codes normalized to M/F/T).

### ⚠️ This is a different source from the Permanent Census

Stock on **January 1** versus **annual average** (`SETA_1`, `INDICATOR=RESPOP_AV`): never place them
in a continuous series on the same chart. January 1, 2025 is the end-of-2024 snapshot, matching the
reference year of the labour table. Consistency check (in the notebook and in
`pipeline/verifica.py`): Bagheria women aged 15-24 on 2025-01-01 = **2,882**, identical to the
2024 annual average from `SETA_1`.

### Verified pitfalls

- `SEX` uses the **legacy codes** from `CL_SEXISTAT1`: `1` male, `2` female, `9` total.
  The pipeline normalizes them to M/F/T in `pipeline/build.py`.
- `DATA_TYPE` = `JAN` (only value): population on January 1.
- `MARITAL_STATUS` (codelist `CL_STATCIV2`): `1` never married · `2` married ·
  `3` divorced · `4` widowed · `15` in a civil union · `16`/`17` formerly in a
  civil union · `99` total.
- **Years 2019-2026, but detailed marital status is available only through 2025-01-01**: 2026-01-01 publishes
  only total `99`. The reference year must be selected among years with detailed categories.
- **Structural zeros, not missing values**: detailed marital status is not published below age 16
  (below 18 for civil unions). Where detail is absent, never-married = total
  exactly; with `fillna(0)` the partition reconstructs `99` to the hundredth (verified
  on all rows from 2019-2025).
- Marital status observes **formal marriage**: no cohabitation, no maternity.
  The next check on the family channel (births by mother's age, demo.istat) would require a
  new fetch, to be decided by the team.

---

## 10. Interface with the education thread (`titolo_condizione/`)

Added on 2026-08-27. The education thread (Saverio) lives in `titolo_condizione/` as a
standalone project with its own pipeline, raw data, and provenance: exact URLs, UTC timestamps,
licenses, and SHA-256 hashes in `titolo_condizione/data/raw/manifest.csv`, with endpoints declared in
`titolo_condizione/config/sources.yml`. Two sources are new relative to the rest of the repository:

- **MIUR school-site registry** — SPARQL at
  `https://dati.istruzione.it/opendata/SCUANAGRAFESTAT/query` (query in
  `titolo_condizione/config/technical_schools.sparql`), 2025/26 school year, Sicilian technical-school
  sites. Registry of sites, not outcomes.
- **AMAT Palermo GTFS** —
  `https://opendata.comune.palermo.it/js/server/uploads/dataset/gtfs/amat_gtfs.zip`
  (feed 20260727-20260831). Urban network: it does not cover the Bagheria-Palermo connection.
- Recorded negative result: the two regional datasets on job vacancies and accredited
  operators (`dati.regione.sicilia.it`) returned **HTTP 502** in the
  2026-08-25 run and are excluded from all quantitative results (failure recorded in the manifest).

Shared tables are copied into `data/processed/` with the `edu_` prefix using:

```bash
uv run python -m pipeline.edu
```

| file | content |
|---|---|
| `edu_youth_states_2018_2024.csv` | 15-24 states (gender total) for the four territories |
| `edu_change_decomposition_2018_2024.csv` | 2018→2024 shift-share of counts (Bagheria, T) |
| `edu_gaps_vs_sicily.csv` | Bagheria−Sicily gap by metric and year |
| `edu_matched_peers_2011.csv` | 10 peers (caliper 0.5-2×, features including educational profile) |
| `edu_model_robustness_2011.csv` | 2011 municipal regressions: Bagheria residuals with bootstrap CI |
| `edu_historical_bagheria.csv` | 8milaCensus indicators 1991-2011 with Sicilian percentile |
| `edu_historical_benchmarks_2011.csv` | 2011 benchmarks (I5/I6/I7/I8/L4/L14) |
| `edu_technical_schools.csv` | MIUR registry of technical-school sites (Sicily) |

⚠️ Shares from the labour table have a **measurement break between 2019 and 2021** (the
"seeking" component halves in every territory and counts become fractional:
a change in the Permanent Census estimation method, section 8): *gaps* between territories remain
comparable, while component *levels* do not. This must be stated whenever citing the
`edu_youth_states_2018_2024.csv` series or the 2018→2024 decomposition.

---

## 11. Commuting by gender — the dimension that had never been decomposed

Added on 2026-08-28. **No new download**: the table had already been downloaded by the
education thread (`uv run python -m pipeline.edu`, section 10) and used only at the gender-total level
as a contextual appendix (`edu_commuting_appendix.csv`). The `genere`
dimension was already present and corresponds to the request that the Gender thread had passed to the Mobility thread
(`docs/CONTEXT-fabio.md`).

**Starting file**: `data/processed/edu_census_commuting_long.csv`
Schema: `territorio, anno, genere (M/F/T), destinazione (ALL/SMPUR/OMPUR), motivo (ALL/STD/WK), valore`
Coverage: **2018 and 2019 only**, four benchmark territories.

Calculation convention, fixed in the "Il pendolarismo ha un genere" cell of
`notebooks/genere.ipynb`:

> share commuting outside the municipality = `OMPUR` / `ALL` × 100, **within a single reason** (WK or STD)

Verified that `SMPUR + OMPUR == ALL` for every cell used.

### Pitfalls

1. **`OMPUR` means "outside the municipality", not "towards Palermo".** The 2018-2019 table does not identify
   the destination municipality. No statement such as "they commute to Palermo" is
   supportable from this source: the origin-destination matrix is required, and it is not present here.
2. **The denominator is already conditioned on the reason.** Someone commuting *for work* already
   has a job: the share is not contaminated by the employment gap discussed elsewhere. This is
   why the result can serve as independent corroboration rather than a reformulation.
3. **Only two years.** It cannot be linked to the 2021-2024 series used in the rest of the thread and cannot be
   updated without a new survey. A KPI based on this measure is not repeatable:
   in the proposal it must be measured using service data, not this source.
4. `M4` (student mobility, 8milaCensus 2011) is an **outside/inside-municipality ratio**:
   a municipality with its own schools will mechanically have a low `M4`. Bagheria has 3 technical-school
   sites (MIUR registry). The 18th percentile is not inherently negative.

### Produced tables

| file | content |
|---|---|
| `genere_pendolarismo.csv` | outside-municipality share by territory × reason × year × gender, with `gap_M_meno_F` |
| `genere_mobilita_2011.csv` | Bagheria `M2`/`M4`/`M6` with median and percentile across the 390 municipalities (2011) |

---

## 12. ISTAT — Commuting matrices: the destination that no other source provides

Added on 2026-08-29 for the Mobility thread. **This overturns a limitation stated twice in the
report** (§5 and §9: "no available source identifies Palermo as the destination").
That limitation was true for the sources used at the time, but not in general.

### Why it was needed

The Permanent Census publishes municipal commuting only as inside/outside municipality.
Verified on 2026-08-28 using dataflow `DF_DCSS_ISTR_LAV_PEN_2_TV_5`: the DSD has ten
dimensions, including `AGE_NOCLASS`, `CUR_ACT_STAT`, `EDU_ATTAIN`, and `LOC_DEST` (codelist
`CL_PROV_DEST_Z`, 69 codes including `DMPURPCT` = "different municipality in the same province,
provincial capital"), but they are **served as a single value**: at municipal level and also for `ITG1`/`IT`,
only `TOTAL`/`ALL`/`99` and `LOC_DEST` ∈ {`ALL`, `SMPUR`, `OMPUR`} are returned, for 2018 and
2019 only. The dimensions exist in the structure; the data do not.

### Endpoints

| Year | URL | Bytes |
|---|---|---|
| 1991 | `https://www.istat.it/storage/cartografia/matrici_pendolarismo/matrici_pendolarismo_1991.zip` | 11,366,726 |
| 2001 | `https://www.istat.it/storage/cartografia/matrici_pendolarismo/matrici_pendolarismo_2001.zip` | 14,501,471 |
| 2011 | `https://www.istat.it/storage/cartografia/matrici_pendolarismo/matrici_pendolarismo_2011.zip` | 36,016,150 |
| 2021 (work only) | `https://esploradati.istat.it/databrowser/DWL/PERMPOP/MATPEN/matrix_pendoLAVORO_2021.zip` | 1,573,552 |
| 2021, readme | `https://esploradati.istat.it/databrowser/DWL/PERMPOP/MATPEN/leggimi_file_matrix_pendoLAVORO_2021.doc` | 48,128 |

The catalog page for the first three is `https://www.istat.it/non-categorizzato/matrici-del-pendolarismo/`
(the links in the HTML use `http://`; redirecting to https works).

**The 2021 file is not there.** It is an IstatData "bulk" dataflow, `DF_BULK_PEND_LAV_2021_1`, and
**the data API returns 404** (`doesn't contain a mapping set`): the actual file is in the
`ATTACHED_DATA_FILES` annotation of the dataflow structure, read through
`dataflow/IT1/DF_BULK_PEND_LAV_2021_1/1.0?detail=full`. The dataflow is marked `DATAFLOW_HIDDEN`
and does not appear when browsing the databrowser: it can only be found by listing `dataflow/IT1` and searching
by name. `DF_BULK_PEND_LAV_2021_2` is the readme, using the same mechanism.

### Record layout

**2011** — fixed layout, 61 characters, 4,876,242 records, 28,871,447 individuals. Fields
are space-separated and no label contains spaces: `str.split()` is sufficient and does not depend
on fixed positions. Order: record type, residence type, province and municipality of residence, sex
(1 = M, 2 = F), reason (1 = study **including nursery, kindergarten, and vocational training**,
2 = work), place (1 = same municipality, 2 = another municipality, 3 = abroad), province and municipality of
destination, foreign state, mode (01-12), departure time (1-4), travel time (1-4),
**sample estimate**, **exhaustive count**.

> **Two record types and two count variables that must not be mixed.** `S` records
> describe origin × destination × sex × reason strata using the
> **exhaustive count**; `L` records reopen the same strata by mode, departure time, and duration, but
> those three variables in municipalities **above 20,000 residents** — including Bagheria — are
> sample-based, and the count is an **estimate** (decimal values). The ISTAT readme
> prescribes the exhaustive count for everything in record type `S` and the estimate only
> when mode, departure time, or duration are needed. `pipeline/build.py` writes them to two
> separate tables specifically to make them difficult to confuse.
>
> In `S` records for people living in **collective households** (residence type 2, 18,726 in Italy), the
> estimate is `ND`: those people have no `L` records. There are also strata with estimate 0.00 and
> exhaustive count 1 — present in the enumeration but not selected into the sample.

**2001** — 3,870,728 records, 26,764,361 individuals, family-household residents only. Same field order
up to destination, followed by a flag indicating whether the person "travelled on the reference Wednesday"
(0/1) and, **only when the flag is 1**, mode/departure time/duration. Mode codes do not match
those from 2011 (code 10 groups walking, cycling, and other modes): only the
origin-destination portion is comparable across the two years, and that is the only part retained by `pipeline/build.py`.

**1991** — layout in `trapen91.txt` inside the ZIP. Six mode classes rather than twelve and,
most importantly, "professional status" 1 = *student or other*, which is not the reason for
travel. The methodological note also reports an **underestimation** of flows to the
"second ring" of provinces. Downloaded and retained for completeness, **not used**.

**2021** — tab-separated with header (`Prov_res, Procom_res, Prov_lav, Procom_lav,
Pendolari`), 523,949 rows, 19,565,808 individuals, municipality code already six digits. No sex,
no mode, no age: only the work OD matrix.

> ⚠️ **Definition break between 2011 and 2021.** 2011 counts people commuting *daily*;
> 2021 counts people going to work *at least three days per week* (a post-Covid accommodation).
> The levels do not form a time series. The `definizione` column in `pendolarismo_od_long.csv`
> carries the wording row by row specifically so no figure can omit it. What is comparable
> is the composition — where 100 outbound commuters go — not the level.

### ⚠️ No age dimension in either source

Neither the matrix nor the Permanent Census table has an age dimension. **The competition's
15-34 target cannot be isolated for commuting.** Travel reason provides only partial
age information and must be used as such: people leaving the municipality for *study* are
almost entirely in upper-secondary school or university, because earlier education cycles are available in Bagheria.

### Verification that serves as proof of the layout

A shifted field would produce plausible but wrong figures. `_verifica_pendolarismo` in
`pipeline/build.py` reconstructs **seven 8milaCensus `M` indicators** from the matrix for
Bagheria in 2011 and compares them with the published values: `M3` 76.1 · `M4` 19.6 · `M5` 65.2 ·
`M6` 8.4 · `M7` 25.7 · `M8` 83.3 · `M9` 3.6 — **seven out of seven to one decimal place** —
plus national totals for 2011 (28,871,447) and 2021 (19,565,808), identical to those declared in the
readme files. `M1` and `M2` cannot be reconstructed because their denominator is population up to age 64, which the
matrix does not contain.

Implication for the competition's **source constraint**: this verification shows that the matrix and
8milaCensus derive from the same survey. The matrix is the underlying level from which
`M1`-`M9` are calculated, not an alternative source. Substantive implication: `M6` ("public
mobility") **excludes** company or school buses — including them would produce 8.9 instead
of 8.4.

### Produced tables

| file | content |
|---|---|
| `pendolarismo_od_long.csv` | OD by year, origin, destination, gender, reason, place — Sicilian origins plus every origin with destination Bagheria; 2001, 2011, 2021 |
| `pendolarismo_mezzo_long.csv` | mode × departure time × duration by origin, gender, reason, place, and Palermo destination; **2011 only, sample estimate** |
| `pendolarismo_benchmark_long.csv` | the same flows aggregated to Italy and Sicily, providing the territorial comparison requested by the competition |
| `pendolarismo_mezzi.csv` | lookup from mode code → label and 8milaCensus class |

### The other two sources named in the competition brief, survey of 2026-08-29

- **Sicily Open Data** (`dati.regione.sicilia.it`, CKAN): **no mobility data**.
  `package_search?q=mobilita` returns 4 packages, all related to public finance; `q=pendolarismo` and
  `q=traffico` return 0; `q=trasporto` returns the list of public-transport operators (2020) and the
  Territorial Public Accounts. The only recent dataset useful for a proposal is **PNRR - Regione
  Siciliana** (updated 2025-12-30, `43c8b77c-6981-4ed2-9ee6-d42de512862a`): projects with
  municipal localization, i.e. an inventory of what is already funded. Not downloaded: it is useful
  for the proposal, not the analysis.
- **Municipality of Palermo** (`opendata.comune.palermo.it`, DCAT Turtle at `/dcat/dcat.php`,
  1,683 datasets): the only live mobility series is the **AMAT GTFS**, republished whenever
  timetables change (latest 2026-07-30). It is an **urban** network: it does not cover the
  Bagheria-Palermo route, but it measures the last mile from Palermo Centrale. The Mobility thread uses the
  file already downloaded by the Education thread (`data/raw/edu/palermo_gtfs_2026-08-25.zip`,
  §10), in read-only mode.

## 13. Robustness of the Gender thread: sources added on 2026-09-23

### 13.1 Permanent Census, 15-24 labour table for the 390 Sicilian municipalities

- **Dataflow**: `DF_DCSS_ISTR_LAV_PEN_2_TV_3`, the same labour table used for the four territories,
  restricted to `AGE_NOCLASS = Y15-24`, `CITIZENSHIP = TOTAL`, `EDU_ATTAIN = ALL`, all
  conditions and all three genders. Key: `A.<33 codes>...Y15-24.TOTAL.ALL...`, in **12 blocks**
  as for the 15+ download (§ IIS path-segment limit).
- **URL**: `https://esploradati.istat.it/SDMXWS/rest/data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_3,1.0/<key>/ALL/?detail=full`,
  one URL per block, all recorded in `data/raw/manifest.csv`. Downloaded on 2026-09-23 →
  `data/raw/censpop_lavoro_15_24_sicilia_01..12_2026-09-23.csv`; processed into
  `censpop_lavoro_15_24_sicilia_long.csv` (`pipeline/build.py`, which verifies that 324 cells for
  Bagheria and Palermo are identical to the four-territory table).
- **Use**: observed variability of changes among similarly sized municipalities (the benchmark for
  KPIs in `genere_mde.csv`), slopes without a binomial model (`genere_pretrend_390.csv`),
  Bagheria's rank (`genere_rango_390_15_24.csv`), and the nature of the cells
  (`genere_interi_condizione.csv`).
- ⚠️ **Unpublished empty cells.** In around twenty very small municipalities, the row for
  employed people (`CUR_ACT_STAT = 1`) is missing. There, labour force (`22`) and people seeking work (`12`) are equal,
  so the employed count is zero: the notebook and `pipeline/verifica.py` set it to zero after
  asserting this equality.
- ⚠️ **From 2021 onward, non-professional-status categories are estimates, not counts.** In 2018-2019,
  every cell is integer-valued; from 2021 onward only employed (`1`) and total (`99`) remain integer-valued, while
  seeking work, labour force, not in labour force, pensioners, students, homemakers, and other
  condition are almost never integers (Bagheria, female homemakers 15-24 in 2024: 386.84). This methodological
  change produces the 2019→2021 break.

### 13.2 ISTAT's method for labour-force and non-professional status (sources read, not downloaded into raw)

- Permanent Census 2018-2019 technical note,
  https://www.istat.it/it/files/2020/12/NOTA-TECNICA-CENSIPOP.pdf : education and professional/
  non-professional status are "thematic variables", with "values estimated
  through statistical models that jointly use survey data and
  information contained in administrative registers".
- ESMS metadata for the 2021 census, compiled by ISTAT for Eurostat,
  https://ec.europa.eu/eurostat/cache/metadata/EN/cens_21_esmscs21_it.htm : first it is estimated
  whether a person is employed (yes/no), then for non-employed people "the \"probabilities\" for the
  other modes of the CAS classification"; cell frequencies are sums of values in
  [0;1]; "The standard error was not calculated." Attachment
  `cens_21_esmscs21_it_an_4.xlsx`: status of non-employed people estimated using a "Multinomial
  Logistic Model".
- Chianella, Ciccaglioni, Ercolani (ISTAT), RIEDS 2024,
  https://www.rieds-journal.org/rieds/article/download/359/287 : "Summing these
  probabilities within a specific domain, such as a municipality (M), provides the
  estimated number of individuals in each category j"; "housewife" and "other condition"
  are in the same model category. The authors state that the paper does not
  necessarily represent ISTAT's position.
- No ISTAT methodological note was found for professional-status dissemination in
  2022-2024: assuming that the 2021 method remained unchanged is an assumption.

### 13.3 Labour Force Survey, regional NEET incidence

- **Dataflow**: `172_931_DF_DCCV_NEET1_11` ("Incidence of young NEETs - Regional data
  (%)"). DSD with 10 positions: FREQ, REF_AREA, DATA_TYPE (`NEET_I`), SEX (legacy codes
  **1 male, 2 female, 9 total**), AGE (`Y15-24`, `Y15-29`, `Y15-34`, `Y18-29`),
  LABPROF_STATUS_A, EURO_LABOUR_STATUS, EDU_LEV_HIGHEST, CITIZENSHIP, ROLE_IN_HOUSEHOLD.
- **URL**: `https://esploradati.istat.it/SDMXWS/rest/data/IT1,172_931_DF_DCCV_NEET1_11,1.0/A.ITG1+IT......../ALL/?detail=full`,
  downloaded on 2026-09-23 → `data/raw/rcfl_neet_regionale_2026-09-23.csv` (2018-2025),
  processed into `rcfl_neet_regionale_long.csv` and `genere_neet_rcfl.csv`.
- ⚠️ **Different source from the census**: sample survey, regional level only, European definition
  (not in employment, education, or training, including non-formal training). This is the competition's 15-34 NEET
  measure at regional scale; the municipal 15-24 proxy must never be placed in the same series. Dataflow
  `172_931_DF_DCCV_NEET1_6` (absolute values) provides sex only as total.

### 13.4 Pilot cost parameters (sources read, transcribed into `genere_costo_parametri.csv`)

- Ministry of Labour, Director's Decree no. 30 of June 14, 2024, labour costs for social cooperatives
  in the social-health, care, and education sector, table "JANUARY 2026", national
  values (no territorial tables exist):
  https://www.lavoro.gov.it/temi-e-priorita-rapporti-di-lavoro-e-relazioni-industriali/focus/dd-30-del-14-giugno-2024 .
  Level D2, "ANNUAL COST" row excluding shift allowance: €35,812.94; average hours
  worked 1,548. The printed hourly cost (€25.78) includes shift work, which does not apply here.
- Ministry of Labour, "Methodological note containing standard unit-cost tables
  – personnel costs" (D.D. 105 of 2026-04-03, updated by D.D. 130 of 2026-05-05),
  Table 1, Local Government, CCNL 2022-2024:
  https://pninclusione21-27.lavoro.gov.it/sites/default/files/2026-05/Nota_metodologica_UCS_EELL_Sanit%C3%A0_Uneba_6_maggio_2026.pdf .
  Gross annual cost for Officials and EQ area: €44,539.99 (Instructors €37,270.09), including contributions and
  IRAP at 8.50%; management costs at 15%, the flat rate under Article 54(1)(b)
  of Regulation (EU) 2021/1060.
- ANPAL, Extraordinary Commissioner's Resolution no. 5 of April 12, 2023, Annex B (UCS
  for the GOL programme): specialist guidance and job-search support €39.94
  per hour; pathway 4 allows up to 10 hours of guidance and 20 of support.
- Sicilian Regional Government Resolution no. 292 of July 19, 2017 (adopting the
  internship guidelines of 2017-05-25): minimum allowance of €300 gross per month; copy
  consulted: https://www.unipa.it/servizi/tirocini/tirociniextracurriculari/.content/Documenti-Normative/Deliberazione-n292-del-19-luglio-2017.pdf .
- The mapping between job profiles and levels in the social-cooperative collective agreement (D2: professional
  educator, social worker, information and guidance-services researcher)
  comes from a secondary source, the Province of Mantua summary sheet (rev.
  2026-04-24); the collective agreement text itself was not opened.

### 13.5 Residential moves: what is publicly available at municipal level (survey of 2026-09-23)

- SDMX `28_185_DF_DCIS_MIGRAZIONI_1` ("Internal migration - Italian and foreign citizens"):
  `availableconstraint` with 30 areas only down to region, `AGE` only `TOTAL`.
- demo.istat.it, "Monthly demographic balance" (D7B, https://demo.istat.it/app/?i=D7B&l=it,
  file `https://demo.istat.it/data/d7b/D7B2024.csv.zip`) and "Demographic balance" (P02):
  municipal detail by sex, with in-migrants from/out-migrants to another municipality and from/to
  abroad; **no age, no qualification, no destination municipality**.
- demo.istat.it, "Residential transfers" 2002-2025 (https://demo.istat.it/tavole/?t=apr4&l=it):
  tables by province and sex, balances for provincial capitals only; age and educational attainment only in
  regional series on graduates.
- ISTAT, "Territorial mobility: residential transfers and daily commuting"
  (February 2024), municipal file for **2021 only**: deregistrations by destination, sex,
  citizenship, and Italian graduates, with no age.
- ISTAT, Statistics report "Internal and international migration of the resident population.
  Years 2024-2025" (https://www.istat.it/wp-content/uploads/2026/08/Statistica-report_Migrazioni-interne-e-internazionali-della-popolazione-residente_ANNI-2024-2025.pdf):
  "The data are collected at municipal level. Statistics are available at
  national, geographical-area, regional, and provincial level"; "Microdata are
  made available to users who request them. These data are released in
  anonymized form."
- SDMX `56_1046` ("University students - municipality of residence"): by municipality, sex, and
  field of study, but only for 2015-2017.
- None of these files was downloaded into `data/raw/`: none includes age, so none
  measures departures of 15-34-year-olds.

## 14. Correction to the `CL_TITOLO_STUDIO` legend (2026-09-24)

The legend in the "Useful codelists" section contains two incorrect labels: **`PSE` is not
tertiary education**, and `BL` does not mean degree only. The official labels, read from raw file
`data/raw/codelist_titolo_studio_2026-08-12.json`, are:

| Code | ISTAT label |
|---|---|
| `NED` | no educational qualification (= `IL` illiterate + `LBNA` literate without qualification) |
| `PSE` | primary school certificate |
| `LSE` | lower-secondary school certificate or vocational-entry certificate |
| `USE_IF` | upper-secondary diploma or vocational qualification (3-4 year course), including IFTS |
| `BL` | ITS higher technical diploma or first-cycle tertiary qualification |
| `ML_RDD` | second-cycle tertiary qualification and research doctorate (= `ML` + `RDD`) |
| `BL_ML_RDD` | university or academic qualification (in the codelist, not in the downloaded data) |

- Exact partition of the total: `NED + PSE + LSE + USE_IF + BL + ML_RDD = ALL`, with a maximum
difference of 6 people across all cells in `censpop_istr_lav_long.csv` and
  `censpop_istr_lav_vicini_long.csv` (rounding at source). Check on `PSE`:
  Bagheria, 2018, F, 9-24, `NED + PSE` = 542 + 821 out of 4,699 = 29.0%, the
  `nessun_titolo_o_elementare_%` column in `genere_istruzione.csv`.
- Subcodes `IL`, `LBNA`, `ML`, `RDD` exist only for class `Y_GE9` and the four
  benchmark territories, not for youth age groups or nearby municipalities. There they sum to the
  parent codes within 2 people.
- The counting code was already correct: `pipeline/verifica.py` and the education cells
  in `notebooks/genere.ipynb` treat `PSE` as below lower-secondary level, and
  "at least upper-secondary diploma" as `USE_IF + BL + ML_RDD`. Only the legend was wrong.
- "Tertiary" (`BL + ML_RDD`) therefore also includes ITS diplomas: it must not be called "degree"
  without qualification.

## 14. Path errata (final pass on 2026-09-24)

This file is append-only: the lines above remain as originally written, and this section
corrects paths that changed in the meantime.

- §10: after migrating the education thread into the repository, `titolo_condizione/data/raw/manifest.csv`
  became `data/raw/edu/manifest.csv` (with download status in
  `data/raw/edu/download_status.json`), and `titolo_condizione/config/sources.yml` became
  `pipeline/edu/config/sources.yml`.
- §11: `docs/CONTEXT-fabio.md` is now `docs/team/CONTEXT-fabio.md`, and is an
  internal team document excluded from the jury package.
- Education-thread downloads are tracked in `data/raw/edu/manifest.csv`, not in
  `data/raw/manifest.csv`: together, the two manifests cover every file in `data/raw/`.

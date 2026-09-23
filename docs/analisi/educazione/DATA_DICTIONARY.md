# Dizionario degli output analitici

Tutte le quote sono percentuali; i campi con suffisso `_pp` sono differenze in punti
percentuali. Le definizioni integrali degli indicatori storici sono in
`data/processed/edu_indicator_dictionary.csv`.

I nomi brevi riportati sotto corrispondono ai file di `data/processed/` con prefisso
`edu_`: per esempio, `youth_states_2018_2024.csv` è `edu_youth_states_2018_2024.csv`.

## Tavole core

### `source_inventory.csv`

Inventario leggibile delle fonti. Per ogni dataset riporta stato al run, periodo, grana,
numero di righe pulite, dimensione raw, ruolo, uso e limite interpretativo.

### `youth_states_2018_2024.csv`

| Campo | Significato |
|---|---|
| `territorio`, `territorio_nome`, `anno` | chiave territoriale e temporale |
| `popolazione` | totale 15-24 nella tavola lavoro |
| `occupati`, `in_cerca`, `studenti` | conteggi per stato |
| `inattivi_non_studenti` | somma delle condizioni ufficiali 4, 7 e 24 |
| `fuori_lavoro_studio` | in cerca + inattivi non studenti |
| `quota_*` | conteggio / popolazione × 100 |
| `inattivi_su_fuori` | inattivi non studenti / fuori lavoro-studio × 100 |

### `adult_transition_2018_2024.csv`

Affianca `quota_almeno_diploma` e `quota_occupati_25_49` sulla stessa fascia 25-49. La colonna
`nota` ricorda che provengono da tavole aggregate separate.

### `gaps_vs_sicily.csv`

Contiene, per metrica e anno, il valore di Bagheria, il valore siciliano, il gap
Bagheria−Sicilia e la direzione favorevole dell'indicatore.

### `change_decomposition_2018_2024.csv`

| Campo | Significato |
|---|---|
| `variazione_conteggio` | differenza osservata 2024−2018 |
| `variazione_quota_pp` | differenza della quota in punti percentuali |
| `effetto_popolazione` | variazione attesa mantenendo il tasso 2018 |
| `effetto_tasso` | variazione dovuta al cambiamento di quota sulla popolazione 2024 |
| `check_decomposizione` | residuo numerico dell'identità; deve essere circa zero |

### `finding_summary.csv`

I cinque risultati che superano il filtro di evidenza. Per ciascuno conserva priorità,
risultato, evidenza numerica, implicazione e forza dell'evidenza.

## Tavole storiche e benchmark

### `historical_bagheria.csv`

Serie 1991-2011 con `indicatore`, `valore`, `percentile_sicilia` e `direzione`. Codici centrali:
I5 uscita precoce 15-24; I6 diploma/laurea 25-64; I7 università 30-34; I8 almeno licenza media
15-19; L4 NEET 15-29; L14 occupazione 15-29.

### `historical_change_1991_2011.csv`

Confronta inizio e fine periodo e distingue `miglioramento_assoluto` da
`convergenza_relativa`.

### `historical_benchmarks_2011.csv`

Valori 2011 di Bagheria, Palermo, Sicilia e Italia per gli indicatori storici selezionati.

### `matched_peers_2011.csv`

Bagheria e dieci comuni comparabili. `distanza_standardizzata` è calcolata sulle sole feature
di matching; gli outcome L14 e L4 non partecipano alla selezione.

## Tavole di contesto e appendice

### `education_context_2018_2024.csv`

Proxy “almeno diploma” per 9-24 e 25-49. `compatibilita` impedisce un raccordo improprio con
fasce o tavole diverse.

### `youth_population_15_34.csv`

Popolazione 15-34 dal 2021, indice con primo anno = 100 e variazione percentuale. Non è un
indicatore di migrazione.

### `commuting_appendix.csv`

Pendolarismo recente e indicatori storici M2/M6. `nota` specifica differenze di denominatore e
assenza della destinazione Palermo.

### `model_robustness_2011.csv`

| Campo | Significato |
|---|---|
| `outcome` | L14 o L4 |
| `modello` | specifica A, B o C |
| `n_comuni_training` | 389; Bagheria esclusa |
| `previsto_bagheria` | previsione comunale del modello |
| `residuo_bagheria` | osservato − previsto |
| `r2_cv_10fold` | prestazione media fuori campione |
| `residuo_ci95_*` | intervallo bootstrap percentile del residuo |

### `recent_analysis_panel.csv`

Vista larga che riunisce, solo su chiavi compatibili, stati 15-24, proxy 25-49 e popolazione
15-34. I valori non disponibili restano mancanti.

### `kpi_dashboard.csv`

Selezione di indicatori per periodo con valore di Bagheria, benchmark siciliano, gap,
direzione e definizione.

### `analysis_summary.json`

Oggetto macchina-legibile con domanda, headline, valori 2024, cambiamenti 2018-2024, gap,
peer summary e limiti.

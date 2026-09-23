# Branch `unison` — valutazione dell'Opzione B (assimilazione del thread educazione)

> Documento storico: percorsi, comandi e stato dei branch si riferiscono alla migrazione
> del 2026-08-27. Per la struttura corrente consultare la [mappa della documentazione](../README.md).

Scritto il 2026-08-27. Questo branch esegue davvero l'assimilazione totale di
`titolo_condizione/` nel repo condiviso, così la decisione si prende su fatti e non su
stime. **Main non è toccato**: lì vive l'Opzione A già applicata (copie `edu_*` via
`pipeline/edu.py`, sources.md §10). Qui il progetto di Saverio si dissolve nella
struttura standard.

## Mappa vecchio → nuovo

| prima (`titolo_condizione/`) | dopo (branch `unison`) |
|---|---|
| `src/datapolis_bagheria/*.py` | package `pipeline/edu/` (stesso comando: `uv run python -m pipeline.edu`) |
| `config/` (sources.yml, analysis.yml, SPARQL) | `pipeline/edu/config/` |
| `data/raw/*` (manifest e SHA-256 inclusi) | `data/raw/edu/` — append-only come il resto di data/raw |
| `data/processed/*` + `outputs/tables/*` | `data/processed/edu_*.csv` (26 file: l'interfaccia che gli altri thread già leggono) |
| `outputs/figures/*` | `figures/edu/` (13 PNG rigenerati) |
| `outputs/*.md` + `docs/*.md` + README | `docs/edu/` (report rigenerati dalla pipeline al run) |
| `notebooks/pipeline.ipynb` | `notebooks/educazione.ipynb` (un notebook per thread, eseguito) |
| `tests/test_pipeline.py` | `tests/test_edu_pipeline.py` (path adattati, criterio immagini su `image/png`) |
| `Makefile`, `pyproject.toml`, `uv.lock`, `requirements.txt` | eliminati: ambiente unico nella root (`+matplotlib +pyyaml +scikit-learn`) |
| `scripts/build_notebook.py`, `execute_notebook.py` | eliminati: `educazione.ipynb` eseguito sostituisce il flusso a notebook generato |

## Prove (tutte su questo branch)

- `uv run python -m pipeline.edu --skip-download`: verde end-to-end (cleaning 1,4s,
  analysis 5,2s, 11/11 controlli interni, 13 grafici, report rigenerati in docs/edu/).
- **Equivalenza**: le 8 tavole condivise sono **byte-identiche** alle copie di main
  (`diff` su edu_youth_states, edu_change_decomposition, edu_gaps_vs_sicily,
  edu_matched_peers, edu_model_robustness, edu_historical_*, edu_technical_schools).
- `notebooks/educazione.ipynb` eseguito top-to-bottom nel nuovo layout, 13 immagini.
- `uv run python -m unittest tests.test_edu_pipeline`: **14/14** (sul vecchio layout il
  quattordicesimo falliva: il notebook committato non era quello che README e test
  dichiaravano).
- Thread genere intatto: `uv run python -m pipeline.verifica` **558/558 PASS**.
- Un bug reale trovato e corretto dall'assimilazione: `run_analysis` apriva con un
  wipe `TABLES.glob(...)` che, con TABLES ≡ `data/processed/`, cancellava anche gli
  output della cleaning (nel layout a cartelle separate era innocuo). Rimosso: le
  tavole si sovrascrivono per nome esplicito.

## Il costo residuo, misurato

- **Figure in R**: il port dimostrativo `viz/edu_fig06_gap_sicilia.R` (tema condiviso,
  banda 2020, etichette dirette, caveat sulla rottura di misura 2019-2021 in
  sottotitolo) è costato ~55 righe. Portarne 12 ≈ mezza giornata abbondante; le 13
  matplotlib restano intanto in `figures/edu/` e dentro il notebook. Lo script è fuori
  dal glob di `build_all.R` finché il team non decide la numerazione.
- **Dedup dei long**: `edu_census_education_work_long.csv` e `edu_ottomilacensus_long.csv`
  duplicano concettualmente `censpop_istr_lav_long.csv` e `ottomilacensus_long.csv`
  (fetch e parsing diversi, valori identici — è la ridondanza che ha permesso la
  cross-validazione). Farvi leggere la pipeline edu dai long principali è la vera
  "unificazione profonda": da decidere con Saverio, non è meccanica.
- **docs/edu/**: i vecchi md citano ancora i path storici (`outputs/tables/…`,
  `make process`) nelle parti descrittive; i tre report rigenerati sono già coerenti.
- **Palette matplotlib**: la Bagheria blu delle 13 figure confligge col blu=maschi del
  tema condiviso; 3 costanti in `pipeline/edu/charts.py` da riallineare se quelle
  figure entrano nel deck.
- **Guscio su disco**: `titolo_condizione/` contiene solo `.venv` e `__pycache__`
  (ignorati da git, invisibili al repo): un `rm -rf titolo_condizione` a mano li toglie.

## Verdetto

L'assimilazione **funziona ed è già dimostrata** qui: risultati identici al byte, test
più onesti di prima, un bug in meno, un ambiente solo. Il costo rimanente è ordinato e
stimato (figure, dedup dei long, ritocchi ai docs). Resta una scelta di squadra, non
tecnica: farla richiede l'ok di Saverio (è il suo thread) e conviene solo se fatta
prima di congelare la proposal — a ridosso della deadline l'Opzione A su main è già
sufficiente e reversibile. Se si sceglie B: merge di questo branch, poi dedup dei long
e port delle figure come task separati.

# A Bagheria il diploma arriva, il lavoro no

DataPolis 2026, «Analisi e Visione per i Giovani di Bagheria»: analisi quantitativa sulla
condizione dei 15-34enni di Bagheria (PA) e proposta di intervento data-driven, **Ponte 19**.

**Da dove partire**: `LEGGIMI_GIURIA.md`. I deliverable impaginati sono in `dist/`: relazione
e policy proposal in PDF, le quattro schede tematiche in PDF, i quattro notebook in HTML
(leggibili senza Jupyter).

**Dove lavorare**: la [mappa della documentazione](docs/README.md) distingue relazione,
policy, presentazione, analisi, materiali del team e idee. I sorgenti ufficiali sono
in `docs/relazione/` e `docs/policy/`; le scelte interne in `docs/team/SCELTE_ANALITICHE.md`.

## Il brief

Realizzare un'analisi quantitativa sulla condizione dei 15-34enni a Bagheria e proporre una
soluzione (policy o servizio) data-driven per contrastare la fuga di talenti:

- **Profiling statistico e benchmarking**: istruzione, occupazione e NEET dei giovani di
  Bagheria, confrontati con Sicilia, Italia e Comune di Palermo;
- **analisi esplorativa** su almeno una dimensione fra titolo di studio e condizione
  lavorativa, differenze di genere, pendolarismo verso Palermo (qui: il genere come focus
  principale, le altre due come thread di supporto);
- **proposta di intervento** supportata dai dati.

Output richiesti: technical notebook riproducibile, 2-3 visualizzazioni avanzate, policy
proposal.

## Fonti usate

ISTAT (censimento permanente via API SDMX, 8milaCensus, matrici del pendolarismo, confini
amministrativi, rilevazione sulle forze di lavoro per il solo NEET regionale), Ministero dell'Istruzione e del Merito (anagrafe delle scuole), AMAT Palermo
(GTFS). Il portale open data della Regione Siciliana è stato esplorato con esito negativo.
Ogni download è tracciato in `docs/sources.md` e nei manifest `data/raw/manifest.csv` e
`data/raw/edu/manifest.csv` (URL, data, parametri).

## Requisiti

- [uv](https://docs.astral.sh/uv/): installa Python (3.12 o successivo) e le versioni esatte di `uv.lock`
  (il primo `uv sync` richiede rete, il resto no).
- Figure: R (testato 4.5.2) con i pacchetti `ggplot2`, `dplyr`, `tidyr`, `readr`, `tibble`,
  `patchwork`; font Lato consigliato. La geometria delle mappe la calcola Python, quindi non
  servono `sf` né le librerie di sistema GDAL/GEOS/PROJ.
- Documenti: `pandoc`; per `pipeline.pdf` anche LibreOffice e Chromium o Chrome.

## Riproduzione (circa 5 minuti, senza rete: i dati grezzi sono in `data/raw/`)

```bash
uv sync
uv run python -m pipeline.build                 # raw -> data/processed/
uv run python -m pipeline.edu --skip-download   # thread educazione -> edu_*.csv
uv run python -m unittest discover -s tests     # contratti della pipeline educazione
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/analisi.ipynb
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/genere.ipynb
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/educazione.ipynb
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/mobilita.ipynb
uv run python -m pipeline.verifica              # controlli automatici, exit 1 se uno fallisce
Rscript viz/build_all.R                         # tutte le figure in figures/ (PNG 300 dpi + SVG)
Rscript viz/dump_didascalie.R                   # titoli e didascalie -> figures/didascalie.csv
uv run python -m pipeline.schede                # le quattro schede HTML di docs/schede/
uv run python -m pipeline.relazione_docx        # docs/relazione/RELAZIONE_DATAPOLIS.docx
uv run python -m pipeline.policy_docx           # docs/policy/POLICY_PONTE_19.docx
uv run python -m pipeline.pdf                   # dist/: PDF, notebook in HTML e zip
```

L'ordine conta: `genere.ipynb` legge tavole prodotte da `analisi.ipynb` e da
`pipeline.edu`, e `mobilita.ipynb` ne legge due prodotte da `genere.ipynb`. Gli avvisi
«Kernel is running over TCP without encryption» di Jupyter e «Removed N rows containing
missing values» di ggplot2 sono attesi.

`pipeline/verifica.py` è il collaudo del progetto: ricalcola i numeri chiave direttamente dai
raw con implementazioni alternative, controlla che le tavole di `data/processed/` coincidano
e che le cifre scritte nella relazione e nella policy compaiano alla lettera nei documenti.

**Aggiornare le fonti** (facoltativo, serve rete): `uv run python -m pipeline.fetch` e
`uv run python -m pipeline.edu --refresh` scaricano raw nuovi, datati al giorno del download, e da quel
momento la build usa quelli. I numeri possono cambiare, e `pipeline.verifica` lo segnala.

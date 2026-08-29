# datapolis-2026-hackathon

## Setup

Il progetto gestisce le dipendenze tramite [`uv`](https://docs.astral.sh/uv/). Per inizializzare l'ambiente:

```bash
# Installa uv (se non già presente)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sincronizza le dipendenze dichiarate in pyproject.toml
uv sync
```

Questo creerà un virtualenv in `.venv/` e installerà tutti i pacchetti elencati nel `pyproject.toml`. Per aggiungere nuove dipendenze usa `uv add <pacchetto>`.

## Riproduzione completa

Da ambiente pulito, nell'ordine. `mobilita.ipynb` legge due tavole prodotte da
`genere.ipynb`, quindi va eseguito dopo; gli altri notebook sono indipendenti.

```bash
uv sync                                   # ambiente Python
uv run python -m pipeline.fetch           # scarica i raw da tutte le fonti
uv run python -m pipeline.build           # raw -> data/processed/
uv run python -m pipeline.edu             # thread educazione: raw -> edu_*.csv

uv run jupyter nbconvert --to notebook --execute notebooks/analisi.ipynb
uv run jupyter nbconvert --to notebook --execute notebooks/genere.ipynb
uv run jupyter nbconvert --to notebook --execute notebooks/educazione.ipynb
uv run jupyter nbconvert --to notebook --execute notebooks/mobilita.ipynb

Rscript viz/build_all.R                   # tutte le figure in figures/ (PNG 300dpi + SVG)
uv run python -m pipeline.schede          # le quattro schede HTML di docs/schede/
Rscript viz/dump_didascalie.R             # titoli e didascalie -> figures/didascalie.csv
uv run python -m pipeline.relazione_docx  # la relazione in .docx, con le figure dentro
uv run python -m pipeline.verifica        # 743 controlli indipendenti, exit 1 se uno fallisce
```

`pipeline/verifica.py` è il collaudo del progetto: ricalcola i numeri chiave
direttamente dai raw con implementazioni alternative, e verifica che le cifre
scritte nella relazione e nella proposal siano ancora quelle che i dati producono.
Se un raw cambia, fallisce finché notebook, tavole e documenti non sono riallineati.

Setup R: i pacchetti vanno nella libreria utente, dai binari P3M. Il dettaglio,
insieme ai limiti noti (`sf` e `svglite` non installabili senza root), sta in
`CLAUDE.md`.

# Obiettivo
Realizzare un’analisi quantitativa sulla condizione dei 15-34enni a Bagheria e proporre una soluzione (policy o servizio) data-driven per contrastare la fuga di talenti.


## Richieste
- Profiling Statistico & Benchmarking: costruire il profilo dei giovani locali (istruzione, occupazione, NEET) confrontando Bagheria con la media siciliana, nazionale e con il Comune di Palermo.

- Analisi Esplorativa (focus a scelta): approfondire almeno una dimensione critica tra:
    - Relazione tra titolo di studio e condizione lavorativa.
    - Impatto delle differenze di genere.
    - Dinamiche e ruolo del pendolarismo verso Palermo.
    
- Proposta di Intervento: tradurre le evidenze emerse in una proposta concreta (un nuovo servizio, una policy pubblica o una campagna mirata) supportata dai dati raccolti.

## Output richiesti
- Technical Notebook: analisi documentata (R, Python o simili) con codice pulito e riproducibile.
- Data Viz: 2-3 visualizzazioni avanzate (mappe o grafici complessi) di forte impatto comunicativo.
- Policy Proposal: sintesi di una proposta concreta (servizio o policy) basata sulle evidenze emerse.

## Fonti
- [ottomilacensus](https://ottomilacensus.istat.it/comune/082/082006/): Istruzione, occupazione, NEET e pendolarismo.
- [dati.regione.sicilia](https://dati.regione.sicilia.it): Indicatori territoriali sul mercato del lavoro.
- [opendata](https://opendata.comune.palermo.it): Dataset su mobilità e servizi urbani.

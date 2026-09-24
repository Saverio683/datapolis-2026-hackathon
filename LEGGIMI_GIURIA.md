# Guida alla lettura - DataPolis 2026, «Analisi e Visione per i Giovani di Bagheria»

Versione rivista del 24 settembre 2026, che sostituisce le versioni precedenti.

Questo pacchetto contiene i tre deliverable richiesti dal bando: il technical notebook,
le visualizzazioni e la policy proposal. Percorso di lettura consigliato, dal risultato
al metodo:

1. **`dist/RELAZIONE_DATAPOLIS.pdf`** - la relazione completa, con le figure incorporate.
   La sezione di apertura, «In una pagina», contiene tesi, proposta e la tabella che collega
   ogni richiesta del bando alla sezione che la soddisfa. Il testo è quello di
   `docs/relazione/RELAZIONE_DATAPOLIS.md`, che è la versione dentro il perimetro dei controlli
   automatici; il PDF ne è l'impaginazione.
2. **`dist/POLICY_PONTE_19.pdf`** - la policy proposal: «Ponte 19», servizio comunale di
   transizione e riattivazione per i 18-25enni, con evidenza, target, KPI in tasso,
   finestre di lettura dichiarate, disegno di valutazione e governance. Il nome viene dai
   19 anni, l'età di uscita dalla scuola superiore.
3. **Le data viz richieste (2-3)** - le tre figure principali sono
   `figures/fig05_forbice`, `figures/fig07_ritenzione_eta` e `figures/fig04_mappa_sicilia`
   (PNG 300 dpi + SVG, didascalia autosufficiente in coda a ogni figura). Il criterio di
   scelta sta nella sezione 8 della relazione; le altre figure di `figures/` sono apparato.
4. **Le schede** - quattro schede tematiche, una per richiesta del bando (profilo e
   benchmarking, genere, pendolarismo, proposta): in PDF in `dist/scheda1_profilo.pdf` ...
   `dist/scheda4_ponte19.pdf`, in HTML autoportante in `docs/schede/`.
5. **`notebooks/`** - il technical notebook: `analisi.ipynb` (definizioni condivise) e i
   tre thread `genere.ipynb`, `educazione.ipynb`, `mobilita.ipynb`, eseguiti e con gli
   output salvati. Le versioni HTML, leggibili senza Jupyter, sono in `dist/`.
6. **Riproduzione da ambiente pulito** - i comandi, nell'ordine, sono in `README.md`.
   I dati grezzi sono inclusi in `data/raw/`: dopo il primo `uv sync` la pipeline gira
   senza rete. Ogni download è tracciato in `docs/sources.md` e nei due manifest,
   `data/raw/manifest.csv` e `data/raw/edu/manifest.csv`, con URL, data e parametri.
7. **La verifica** - `uv run python -m pipeline.verifica` ricalcola i numeri chiave
   direttamente dai dati grezzi con implementazioni alternative e pretende che le cifre
   scritte nella relazione e nella policy compaiano nei documenti alla lettera; esce con
   errore se anche un solo controllo fallisce. Poche cifre lette da una cella di notebook e
   non ancora esportate in `data/processed/` sono elencate dalla verifica stessa.

Tutte le cifre dell'analisi provengono da statistica ufficiale pubblica (ISTAT, Ministero
dell'Istruzione e del Merito, Comune di Palermo/AMAT). I parametri di costo della proposta
vengono da atti del Ministero del Lavoro, dell'ANPAL, della Regione Siciliana e dell'Unione
europea, citati uno per uno in `data/processed/genere_costo_parametri.csv`.

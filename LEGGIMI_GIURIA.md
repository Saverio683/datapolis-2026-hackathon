# Guida alla lettura - DataPolis 2026, «Analisi e Visione per i Giovani di Bagheria»

Questo pacchetto contiene i tre deliverable richiesti dal bando: il technical notebook,
le visualizzazioni e la policy proposal. Percorso di lettura consigliato, dal risultato
al metodo:

1. **`docs/RELAZIONE_DATAPOLIS.docx`** - la relazione completa, con le figure incorporate.
   La sezione di apertura, «In una pagina», contiene tesi, proposta e la mappa che collega
   ogni richiesta del bando alla sezione che la soddisfa. Il testo è identico a
   `docs/RELAZIONE_DATAPOLIS.md`, che è la versione dentro il perimetro dei controlli
   automatici; il .docx ne è l'impaginazione.
2. **`docs/POLICY_PONTE_19.md`** - la policy proposal: «Ponte 19», servizio comunale di
   transizione e riattivazione 18-25, con evidenza, target, KPI in tasso, finestre di
   lettura dichiarate e disegno di valutazione.
3. **Le data viz richieste (2-3)** - la terna dichiarata è `figures/fig05_forbice`,
   `figures/fig07_ritenzione_eta`, `figures/fig04_mappa_sicilia` (PNG 300dpi + SVG,
   didascalia autosufficiente in coda a ogni figura). Il criterio di scelta, dichiarato
   perché sia contestabile, sta in `docs/RELAZIONE.md` §3; le altre figure sono apparato.
4. **`docs/schede/`** - quattro schede HTML autoportanti, una per richiesta del bando
   (profilo e benchmarking, genere, pendolarismo, proposta), stampabili in PDF.
5. **`notebooks/`** - il technical notebook: `analisi.ipynb` (definizioni condivise) e i
   tre thread `genere.ipynb`, `educazione.ipynb`, `mobilita.ipynb`, tutti eseguiti e con
   gli output salvati.
6. **Riproduzione da ambiente pulito** - i comandi, nell'ordine, sono in `README.md`
   (sezione «Riproduzione completa»). I dati grezzi sono inclusi in `data/raw/`, quindi
   la pipeline gira anche senza rete; ogni download è tracciato in `docs/sources.md`
   con URL, data e parametri.
7. **La garanzia** - `uv run python -m pipeline.verifica` ricalcola i numeri chiave
   direttamente dai dati grezzi con implementazioni alternative e pretende che le cifre
   scritte nella relazione e nella policy compaiano nei documenti alla lettera: 755
   controlli, esce con errore se anche uno solo fallisce.

Tutte le cifre provengono da statistica ufficiale pubblica (ISTAT, Ministero
dell'Istruzione, Comune di Palermo/AMAT); nessun numero dei documenti è scritto a mano.

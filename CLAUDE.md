# CLAUDE.md — Datapolis 2026 Hackathon

## Contesto
Analisi quantitativa sulla condizione dei 15-34enni a Bagheria (PA) e proposta di intervento data-driven contro la fuga di talenti. Team di 3 persone, ognuna con un proprio thread esplorativo su una pipeline dati condivisa.

Deliverable (in ordine di priorità):
1. **Technical notebook** riproducibile (Python) — deve girare top-to-bottom da ambiente pulito
2. **2-3 data viz avanzate** (R) — mappe o grafici complessi
3. **Policy proposal** — ogni claim quantitativo deve puntare a una cella del notebook che lo produce

## Stack e comandi
- **Analisi/pipeline**: Python 3.12+, gestito con `uv` — pandas, geopandas, requests, scipy, statsmodels
- **Visualizzazioni finali**: R — tidyverse, sf, ggplot2 (+ patchwork per composizioni)
- L'interfaccia tra i due mondi sono i file in `data/processed/` (CSV/GeoJSON): Python scrive, R legge. Mai logica di trasformazione in R.
- Setup R (verificato 2026-08-12, Ubuntu 26.04 + R 4.5.2): i pacchetti stanno nella libreria utente `~/R/x86_64-pc-linux-gnu-library/4.5`, installati dai binari P3M (`options(repos = c(P3M = "https://p3m.dev/cran/__linux__/noble/latest"))`) perché la site-library non è scrivibile. `svglite` e `ragg` non compilano (mancano gli header di fontconfig/freetype/harfbuzz): si usano i device cairo di base, che però convertono il testo in tracciati — se serve testo editabile nell'SVG installare prima le `-dev` di sistema e poi `svglite`.

```bash
uv sync                                   # setup ambiente Python
uv run python -m pipeline.fetch           # scarica raw da tutte le fonti
uv run python -m pipeline.build           # raw -> processed
uv run python -m pipeline.edu             # thread educazione: raw -> edu_*.csv
uv run jupyter nbconvert --to notebook --execute notebooks/analisi.ipynb     # SENSORE (19 celle)
uv run jupyter nbconvert --to notebook --execute notebooks/genere.ipynb      # SENSORE (133 celle)
uv run jupyter nbconvert --to notebook --execute notebooks/educazione.ipynb  # SENSORE (64 celle)
uv run jupyter nbconvert --to notebook --execute notebooks/mobilita.ipynb    # SENSORE (40 celle)
Rscript viz/build_all.R                   # genera tutte le figure in figures/
uv run python -m pipeline.schede          # data/processed -> docs/schede/ (4 schede HTML)
Rscript viz/dump_didascalie.R             # titoli e didascalie -> figures/didascalie.csv
uv run python -m pipeline.editor_testi fig06   # editor dei soli testi di una figura, anteprima live
uv run python -m pipeline.relazione_docx  # RELAZIONE_DATAPOLIS.md + figure -> .docx
uv run python -m pipeline.policy_docx     # POLICY_PONTE_19.md + figure e sinossi -> .docx
uv run python -m pipeline.verifica        # SENSORE: 755 controlli, exit 1 se uno fallisce
uv run python -m pipeline.pdf             # deliverable -> dist/: PDF + notebook in HTML
```

Prima di dichiarare completo qualunque task che tocca un notebook, esegui il nbconvert **di quel notebook** e quello di `analisi.ipynb`. Se fallisce, il task non è finito.

`analisi.ipynb` è il guscio condiviso (caricamento, verifica delle definizioni, export per le figure): da solo copre 19 celle su 256, l'analisi vera sta nei tre notebook di thread. Un nbconvert sul solo `analisi.ipynb` non è quindi la prova che il progetto gira.

Prima di dichiarare completo qualunque task che tocca `data/processed/`, i notebook o i documenti di `docs/`, esegui `pipeline.verifica`. Copre tre salti: raw -> notebook, notebook -> processed, e processed -> le cifre scritte a mano in `RELAZIONE.md`, `RELAZIONE_DATAPOLIS.md` e `POLICY_PONTE_19.md`. Quest'ultimo blocco non dichiara i numeri attesi: li rilegge da `data/processed/`, li formatta all'italiana e pretende che la frase compaia alla lettera nel documento, quindi fallisce sia se si muove il dato sia se si ritocca il testo a mano. Quando fallisce, la riga di FAIL stampa la frase da riscrivere.

## Struttura repo
```
data/raw/          # immutabile, mai editare — un file per download, mai sovrascrivere
data/processed/    # output della pipeline, rigenerabile, interfaccia Python->R
pipeline/          # moduli Python di fetch e trasformazione
notebooks/         # analisi.ipynb (condiviso) + un notebook per thread esplorativo
viz/               # script R, uno per figura + build_all.R
figures/           # output viz (PNG 300dpi + SVG) + didascalie.csv (titoli e
                   # didascalie estratti dagli script R, per chi incorpora le figure)
docs/schede/       # quattro schede tematiche HTML, generate da pipeline/schede.py:
                   # una per richiesta del bando, ogni cifra letta da data/processed/
                   # blocchi numerati («Figura 2.3») + didascalia a 3 blocchi; incorporano
                   # le figure di figures/ ritagliate al solo grafico, intere solo in appendice
docs/sources.md    # dettaglio endpoint, query, struttura dei dataset — leggilo prima di scrivere codice di fetch
```

## Regole dati (provenance)
- Ogni download in `data/raw/` è accompagnato da una riga in `docs/sources.md`: URL esatto, data, eventuale query/parametri.
- `data/raw/` è append-only: mai modificare, mai rinominare, mai "correggere" un raw. Le correzioni vivono in `pipeline/`.
- **dati.regione.sicilia.it** è CKAN: usa le API REST (`package_search`, `datastore_search`), non scraping HTML.
- **opendata.comune.palermo.it** *non* è CKAN (verificato 2026-08-12: `/api/3/action/*` risponde 404): è un portale PHP custom che espone il catalogo DCAT in Turtle su `/dcat/dcat.php`. Partire da lì, non da HTML.
- **ottomilacensus.istat.it** non ha API documentata: ispeziona le chiamate di rete della pagina per trovare gli endpoint JSON per indicatore prima di ripiegare su scraping. Non inventare endpoint: se non trovi la via programmatica, fermati e segnalalo.
- Se un dato necessario non esiste nelle fonti, dillo esplicitamente — non stimare né interpolare senza che la scelta sia discussa e documentata nel notebook.

## Definizioni fissate (non reinventarle a ogni sessione)

Aggiornate il 2026-08-12 dopo la ricognizione delle fonti — i dettagli e le verifiche stanno in `docs/sources.md`.

- **Territori di confronto**: Bagheria (`082006`), Comune di Palermo (`082053`), Regione Sicilia, Italia. Codici verificati su entrambe le fonti.
  - Le due fonti scrivono il codice comune in modo diverso: 8milaCensus senza zero iniziale (`82006`), SDMX con (`082006`). Normalizzare sempre a 6 cifre zero-padded in pipeline.
  - Sicilia e Italia in SDMX sono `ITG1` e `IT`, non codici numerici.
  - In `CL_ITTER107` esistono anche `SLL_2021_1906` e `T19039`, entrambi chiamati "Bagheria": sono il Sistema Locale del Lavoro e il Distretto, **territori diversi dal comune**. Mai usarli al posto di `082006`.
- **Anno di riferimento**: il Censimento permanente è una **serie annuale 2018-2024**, non una fotografia. Usare **2021 come anno di riferimento** per confrontabilità tra i thread, e mostrare la serie completa dove il trend è il punto. Il 2011 (8milaCensus) è una fonte separata, sempre etichettata con l'anno.
  - La copertura **non è uniforme** e va verificata per fascia d'età, non sulla tabella intera (la cella di verifica in `notebooks/analisi.ipynb` lo fa): il **2020 manca sulla classe 15-24** in tutti i territori, e le **età singole esistono solo dal 2021**, quindi la serie 15-34 è 2021-2024. Sono buchi alla fonte: non interpolare.
- **Fasce d'età**: dipendono dal dominio, perché le fonti non danno il 15-34 ovunque.
  - **Lavoro e istruzione**: `15-24`. È l'unica classe giovanile disponibile a livello comunale nel censimento permanente (le altre sono 25-49, 50-64, 65+). Il 25-49 sfora il target e non è scomponibile: non usarlo come proxy dei giovani.
  - **Demografia**: `15-34`, ricostruito sommando le età singole di `DF_DCSS_POP_DEMCITMIG_SETA_1`. Qui il target dell'hackathon è rispettato esattamente.
  - Ogni figura dichiara la fascia nel titolo o nell'asse. Mai due fasce nella stessa figura senza etichetta esplicita.
- **NEET**: il NEET ISTAT standard 15-29 **non è calcolabile al 2021 a livello comunale** — la fascia non esiste nei dati.
  - Al 2011 il NEET 15-29 c'è (8milaCensus, indicatore `L4`): usarlo come dato storico, etichettato "2011, 15-29".
  - Dal 2018 si costruisce un **proxy su 15-24** dalla condizione professionale (`CL_FORZE_LAV`); va chiamato per quello che è ("giovani 15-24 fuori da lavoro e istruzione"), mai "NEET" senza qualificazione, e la convenzione di calcolo va scritta nel notebook.
  - **I due non vanno mai uniti in una serie o in un grafico**: fasce diverse e definizioni diverse, non è un'approssimazione ma un errore.
- **Genere**: incrociabile con età, condizione professionale e titolo di studio a livello comunale nel censimento permanente (`GENDER` = `M`/`F`/`T`). In 8milaCensus il genere esiste solo su 15+ complessivo, mai incrociato con l'età: il gap di genere giovanile è un dato 2018+, non 2011.
- **Benchmarking**: riportare sia i valori assoluti sia il gap percentuale vs ciascun territorio di confronto; mai solo assoluti.
- **Totali nei dati SDMX**: ogni dimensione ha un codice "totale" (`T` genere, `TOTAL` cittadinanza, `99` condizione, `ALL` titolo di studio) che convive come riga sorella con i dettagli. Sommare senza filtrare i totali raddoppia i numeri.

## Thread esplorativi (ownership)
- **Genere** (Ale): gap di genere su occupazione (**15-24**) e istruzione (**9-24**), serie 2018-2024; confronto del gap locale con quello dei territori benchmark.
  - La **decomposizione del gap per titolo di studio non è fattibile** e va tolta dal piano: a livello comunale il censimento permanente non pubblica l'incrocio condizione professionale × titolo di studio. Nella tavola lavoro il titolo è solo `ALL`, in quella istruzione la condizione è solo il totale `99`. Dimostrato dalla cella di verifica in `notebooks/genere.ipynb`. Al suo posto i due gap si misurano separatamente e si confrontano i segni.
- **Educazione** (Saverio) e **Mobilità** (Fabio): thread degli altri componenti — non modificarne i notebook; i dati condivisi passano solo da `data/processed/`.
- Contesto per membro (stato del thread, fatti verificati, richieste incrociate): `docs/CONTEXT-ale.md`, `docs/CONTEXT-saverio.md`, `docs/CONTEXT-fabio.md`.
- Convenzioni comuni obbligatorie a tutti i thread: stesse definizioni (sezione sopra), stessi territori, stesso anno base. Serve perché i risultati siano confrontabili nella proposal finale.

## Convenzioni viz (R)
- Un tema ggplot condiviso in `viz/theme.R` — caricato da ogni script, mai stili inline duplicati.
- Palette: colorblind-safe (viridis per continue, Okabe-Ito per categoriche). Per il genere si usano blu (M) e rosa (F) — scelta del team del 2026-08-26, per la lettura immediata: i due valori restano dentro Okabe-Ito (`#0072B2` e `#CC79A7`), quindi la coppia è ancora distinguibile in protanopia e deuteranopia. Di conseguenza nessun territorio usa quei due colori: Palermo è viola, Sicilia ambra.
- Tipografia delle figure: tre livelli, una sola famiglia. Titolo della figura e sottotitolo prendono `tema_figura()`, i titoli dei singoli pannelli restano su `tema_datapolis()`. Mai un secondo font: solo Lato ha un fallback verificato e cairo converte comunque il testo in tracciati nell'SVG.
- Ogni figura: titolo che enuncia il finding (non la variabile), export sia PNG 300dpi sia SVG in `figures/`.
- **Il sottotitolo dice cosa mostra la figura** — metrica, unità, trasformazioni, fascia d'età, territori, anni; anche cosa la figura **non** dice, e quale altra figura lo dice. Sta in alto, a corpo pieno, ed è la prima cosa che si legge: è lì che serve. Sotto, il finding con le cifre. Testi lunghi passano da `sommario(..., LARGHEZZA)`, che manda a capo sulla larghezza dichiarata (le figure da 30 cm in su vanno a capo a mano: il budget in caratteri di `a_capo()` è una stima e su quelle misure sborda).
- **Didascalia autosufficiente, due blocchi** — `didascalia_2b()` in `viz/theme.R`, obbligatorio su ogni figura. Chi guarda dal fondo della sala non ha il notebook accanto: la figura deve dire da sola cosa significano le linee che non sono dati, e da dove viene il numero.
  - `lettura`: decodifica di tutto ciò che non è un dato — tratteggi, bande, strisce del dato mancante, colori, diametri, scale logaritmiche, ordinamenti non per valore. Qui vive anche il metodo di ciò che è disegnato (Wilson, Newcombe, bootstrap, tutti al 95%) e la cautela che serve a leggere il grafico: fasce non confrontabili, esclusioni, definizioni cambiate alla fonte.
  - `fonte`: fonte con anno, più il file di `data/processed/` che rigenera la figura.
  - Le **schede HTML stampano tre blocchi**: `mostra`, `lettura` e `fonte`. `blocco()` in `pipeline/schede.py` prende tutti e quattro (`base` compresa) come argomenti obbligatori senza default e rifiuta la stringa vuota, ma **`base` non viene resa a schermo** (2026-08-30): resta nel sorgente accanto ai numeri che descrive, così chi scrive un blocco deve comunque dichiarare N e metodo. `main()` verifica che ogni sezione stampi i tre blocchi e che «Base statistica» non compaia.
  - Quando una scheda o un .docx incorpora una figura di `figures/`, la didascalia del PNG si **ritaglia via** (`CODA_DIDASCALIA = 2` in `pipeline/schede.py` e `pipeline/relazione_docx.py`: sono le ultime due bande di inchiostro) e si rifà nella tipografia del documento, con il testo estratto da `figures/didascalie.csv`. Il PNG intero solo in appendice, a piena larghezza.
- Ogni script dichiara `LARGHEZZA <- n` una volta e la passa sia a `didascalia_2b()` sia a `salva()`: legate, un testo tagliato dal bordo del PNG non può passare inosservato. Alzare `altezza` quando il testo cresce.
- **Niente em-dash nel testo renderizzato**: parentesi tonde, due punti o virgole. Italiano formale. I commenti nel codice sono esenti.
- La regola «nessuna cifra scritta a mano» vale anche per titoli, sottotitoli e didascalie: ogni numero si legge da `data/processed/` dentro lo script.
- Mappe: confini ISTAT ufficiali (shapefile/GeoJSON delle unità amministrative), CRS documentato nello script.
  - `sf` **non è installabile** senza root (servono GDAL/GEOS/PROJ di sistema): la geometria la fa geopandas in `pipeline/build.py`, che esporta i poligoni come tabella di vertici già proiettata (`comuni_sicilia_poligoni.csv`, EPSG:32633). In R si disegna con `geom_polygon(group = interaction(territorio, parte), subgroup = anello, rule = "evenodd")` — `parte` separa le isole, `anello` i buchi. Esempio completo: `viz/fig04_mappa_sicilia.R`.

## Guardrail
- Nessun numero hardcodato nella policy proposal o nelle slide: ogni cifra si rigenera dal notebook.
- Non aggiungere dipendenze pesanti senza motivo (niente framework per quello che pandas fa in tre righe).
- Non toccare `data/raw/`, i notebook degli altri thread, né `docs/sources.md` se non per appendere.
- Per task non banali (nuova fonte dati, ristrutturazione pipeline, scelta del modello statistico): proponi prima un piano breve con le alternative e attendi conferma, poi implementa.

## Policy proposal — template
Ogni evidenza nella proposal segue la forma: **evidenza** (con riferimento alla cella/figura) → **intervento proposto** → **target** (chi, quanti) → **KPI misurabile**. Se un'evidenza non ha un intervento derivabile, resta nell'analisi ma non entra nella proposal.

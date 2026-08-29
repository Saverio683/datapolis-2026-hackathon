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
uv run jupyter nbconvert --to notebook --execute notebooks/analisi.ipynb  # SENSORE: il notebook DEVE passare questo comando
Rscript viz/build_all.R                   # genera tutte le figure in figures/
uv run python -m pipeline.schede          # data/processed -> docs/schede/ (4 schede HTML)
```

Prima di dichiarare completo qualunque task che tocca il notebook, esegui il comando nbconvert sopra. Se fallisce, il task non è finito.

## Struttura repo
```
data/raw/          # immutabile, mai editare — un file per download, mai sovrascrivere
data/processed/    # output della pipeline, rigenerabile, interfaccia Python->R
pipeline/          # moduli Python di fetch e trasformazione
notebooks/         # analisi.ipynb (condiviso) + un notebook per thread esplorativo
viz/               # script R, uno per figura + build_all.R
figures/           # output viz (PNG 300dpi + SVG)
docs/schede/       # quattro schede tematiche HTML, generate da pipeline/schede.py:
                   # una per richiesta del bando, ogni cifra letta da data/processed/
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
- **Didascalia autosufficiente, quattro blocchi** — `didascalia_4b()` in `viz/theme.R`, obbligatorio su ogni figura. Chi guarda dal fondo della sala non ha il notebook accanto: la figura deve dire da sola cosa misura, su quante persone, con che dispersione, e cosa significano le linee che non sono dati.
  - `mostra`: metrica, unità, trasformazioni, fascia d'età, territori, anni. Anche cosa la figura **non** dice, e quale altra figura lo dice.
  - `base`: N per gruppo, tendenza centrale, dispersione o intervalli **con il metodo esplicito** (Wilson sui tassi, Newcombe sulla differenza M−F, bootstrap sui residui, tutti al 95%), test e soglie, esclusioni e filtri. Dove non c'è incertezza campionaria si scrive perché (conteggi censuari, non stime).
  - `lettura`: decodifica di tutto ciò che non è un dato — tratteggi, bande, strisce del dato mancante, colori, diametri, scale logaritmiche, ordinamenti non per valore.
  - `fonte`: fonte con anno, più il file di `data/processed/` che rigenera la figura.
- Ogni script dichiara `LARGHEZZA <- n` una volta e la passa sia a `didascalia_4b()` sia a `salva()`: legate, un testo tagliato dal bordo del PNG non può passare inosservato. Alzare `altezza` quando la didascalia cresce.
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

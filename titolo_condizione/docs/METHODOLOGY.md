# Metodologia

## 1. Disegno dell'analisi

L'unità principale è il territorio-anno. Il disegno combina tre finestre informative senza
forzarle in una serie unica:

1. **1991-2011:** indicatori comunali 8milaCensus per la struttura storica;
2. **2018-2024:** titolo e condizione professionale IstatData per il quadro recente;
3. **2021-2024:** popolazione per età singola per il solo andamento demografico 15-34.

Il focus corrente è la popolazione 15-24 perché è la fascia più dettagliata comune alla tavola
recente sul lavoro. Per i 25-49 si affiancano titolo e occupazione sulla stessa fascia, ma come
aggregati distinti. Sono usati solo i totali di genere e cittadinanza.

## 2. Acquisizione e tracciabilità

Ogni fonte è dichiarata in `config/sources.yml`. Il downloader:

- conserva il raw con data di acquisizione nel nome;
- registra URL richiesto e finale, timestamp UTC, byte, licenza e SHA-256;
- verifica un marker minimo di contenuto;
- applica retry sugli errori transitori;
- distingue fonti core e opzionali.

I raw non vengono modificati. `data/raw/manifest.csv` è il registro di lineage; la validazione
ricalcola gli SHA-256 prima dell'analisi. Un endpoint opzionale non disponibile resta marcato
come tale e non viene sostituito con dati inventati o copie non verificabili.

## 3. Pulizia e normalizzazione

- I CSV 8milaCensus sono letti in `cp1252`, con separatore `;` e virgola decimale
  normalizzata.
- Le tavole SDMX sono trasformate in formato long e deduplicate sulle dimensioni ufficiali.
- I codici territoriali sono preservati come stringhe, inclusi gli zeri iniziali.
- I conteggi e le quote vengono convertiti in numerico; le categorie non pertinenti sono
  escluse esplicitamente.
- Il GTFS è controllato per la presenza di `feed_info`, `routes`, `stops`, `trips` e
  `stop_times`.
- I testi dell'anagrafe scolastica sono normalizzati in maiuscolo ASCII per il raccordo
  comunale.

Valori sentinella: 390 comuni siciliani nel 2011; L4 Bagheria 2011 = 40,1; L14 = 20,0;
occupati 15-24 Bagheria 2024 = 734; popolazione 15-34 Bagheria 2024 = 11.861.

## 4. Interlinking

Le chiavi territoriali canoniche sono `082006` Bagheria, `082053` Palermo, `ITG1` Sicilia e
`IT` Italia. I raccordi recenti usano:

`territorio × anno × fascia d'età × definizione`

Il join è ammesso solo quando territorio, anno e fascia sono compatibili. Il titolo 9-24 non
viene incrociato con il lavoro 15-24. Il titolo e il lavoro 25-49 sono affiancati per territorio
e anno, conservando una nota che ne vieta l'interpretazione individuale.

## 5. Indicatori recenti

Per ogni stato dei 15-24:

\[
q_{k,t}=100\,\frac{N_{k,t}}{N_t}
\]

Le categorie ufficiali della tavola lavoro sono ricondotte a quattro stati mutuamente
esclusivi:

- occupati: codice `1`;
- in cerca di lavoro: `12`;
- studenti: `5`;
- inattivi non studenti: somma di `4`, `7` e `24`.

“Fuori da lavoro e studio” è la somma di persone in cerca e inattivi non studenti. Non viene
chiamato NEET: la fascia e la costruzione non coincidono con l'indicatore storico L4.

Il proxy “almeno diploma” somma i titoli secondari superiori e terziari. È calcolato sulle
fasce ufficiali 9-24 e 25-49 e mantiene sempre la fascia nel nome.

## 6. Cambiamento, gap e scomposizione

Per una quota favorevole, il gap territoriale è:

\[
g_t=q_{Bagheria,t}-q_{Sicilia,t}
\]

Un miglioramento interno non implica convergenza: la convergenza richiede che il gap sfavorevole
si riduca. Per ogni stato, il cambiamento nel conteggio tra 2018 e 2024 è scomposto in:

\[
N_1-N_0=(P_1-P_0)q_0+P_1(q_1-q_0)
\]

Il primo termine è l'effetto della variazione della popolazione a tasso iniziale costante; il
secondo è l'effetto della variazione della quota sulla popolazione finale. L'identità è
verificata numericamente.

## 7. Storia e posizione relativa

I percentili sono calcolati sui 390 comuni siciliani per anno e indicatore. Valore assoluto e
posizione relativa vengono mostrati insieme. Per gli indicatori sfavorevoli, come uscita
precoce e NEET, un percentile grezzo alto indica maggiore criticità; la direzione è riportata
nella tabella.

## 8. Peer matching

Il confronto 2011 restringe i candidati ai comuni con popolazione compresa tra 0,5 e 2 volte
quella di Bagheria. Seleziona poi i dieci più vicini tramite distanza euclidea su feature
standardizzate: log popolazione, struttura demografica e abitativa, uscita precoce,
diploma/laurea e università. Gli outcome L14 (occupazione 15-29) e L4 (NEET 15-29) sono esclusi
dalla selezione e osservati soltanto dopo il match.

Il matching riduce l'arbitrarietà del confronto, ma non costruisce un controfattuale causale.

## 9. Robustezza in appendice

Tre regressioni lineari comunali del 2011 prevedono L14 e L4:

- A: I5, I6, I7;
- B: A + M2, L19;
- C: B + log popolazione, P10, P12, P13, A1.

Bagheria è esclusa dall'addestramento, che usa 389 comuni. Sono riportati previsione, residuo,
R² in-sample, R² medio in cross-validation 10-fold e intervallo bootstrap percentile al 95%
con 1.000 campioni e seed 2026. La capacità predittiva fuori campione è debole per
l'occupazione e moderata per il NEET storico: questi modelli restano un controllo di robustezza
e non fondano la conclusione principale.

## 10. Controlli automatici

La pipeline deve superare undici controlli: checksum raw, numero di comuni, somma al 100% degli
stati giovanili, assenza di interpolazione 2020, unicità delle chiavi, non negatività, valore
sentinella 2024, identità della scomposizione, disponibilità delle fonti core, esclusione di
Bagheria dai modelli e presenza di evidenza esplicita per ogni finding.

## 11. Confini dell'inferenza

L'analisi è territoriale e osservazionale. Non misura il rendimento individuale del titolo,
non segue coorti, non identifica la causa dell'inattività, non localizza i posti di lavoro e non
deduce migrazione dalla sola variazione demografica. La policy proposta include per questo un
dataset longitudinale e un rollout valutabile.

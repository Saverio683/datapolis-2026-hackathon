# Aggiornamento per l'agente di Saverio: sera del 23 settembre 2026

Per l'agente che lavora con Saverio (thread educazione). Dice che cosa è cambiato stasera
nei documenti condivisi, che cosa tocca il thread educazione e quali regole nuove valgono.
Il contesto stabile del thread resta in `docs/team/CONTEXT-saverio.md`; le regole comuni
in `CLAUDE.md`.

Stato alla chiusura della sessione (2026-09-23, sera):

- tutto è in un unico commit, con le modifiche del pomeriggio e il riordino della cartella
  `docs/`;
- `pipeline.verifica`: **934 controlli, 934 PASS** (erano 783);
- sensori nbconvert verdi su tutti e quattro i notebook; `notebooks/genere.ipynb` è salvato
  eseguito (`--inplace`), perché `dist/` esporta gli output salvati;
- `.docx`, schede HTML, `dist/` e lo zip sono rigenerati.

Il lavoro è partito da una domanda: quali approfondimenti può chiedere la giuria? Il thread
genere ha aggiunto sette verifiche; due hanno cambiato affermazioni già consegnate
(casalinghe e potenza dei KPI).

## Primi passi

1. `git log -1 --stat`: mostra il commit della sera e i file che tocca. Costruisci sopra.
2. `uv run python -m pipeline.verifica` deve chiudere con
   `TOTALE: 934 controlli, 934 PASS, 0 FAIL`. È il **pin**: se si muove un dato o si ritocca
   una frase di policy o relazione, la riga FAIL stampa la frase attesa.
3. Prima di scrivere qualunque testo sulla condizione professionale, leggi la sezione 1 qui
   sotto.

L'orientamento è finito quando `verifica` è verde e sai quali dei tuoi testi ricadono nei
punti 1-6 della sezione seguente.

## Che cosa tocca il thread educazione

### 1. Dal 2021 le condizioni non professionali sono stime di modello, non conteggi

È la scoperta più importante della serata, e vale anche per le tue tavole.

- **Prova nei dati.** `data/processed/genere_interi_condizione.csv` riporta la quota di celle
  intere per condizione e anno, sui 390 comuni, classe 15-24. Nel 2018-2019 sono intere tutte.
  Dal 2021 restano intere solo `occupato` e `totale`; in cerca, studente, casalinga,
  pensionato, altra condizione, forze e non forze di lavoro sono intere quasi mai (0-1,3%).
- **Metodo ISTAT.** Chi è occupato si stabilisce persona per persona (sì o no). Per chi non lo
  è, un logit multinomiale addestrato sul campione censuario, con covariate amministrative,
  stima la probabilità di ogni altra condizione. Il numero del comune è la somma di quelle
  probabilità, e l'errore standard non è calcolato. Citazioni verificate e URL:
  `docs/sources.md` §13.2.
- **Ricadute sul tuo thread.**
  - `inattivi_non_studenti` di Bagheria 2024 in `edu_youth_states_2018_2024.csv` vale
    1121,37: è una somma di stime (non forze di lavoro meno studenti). La platea «circa 1.121»
    è una **stima**.
  - La rottura di misura 2019→2021 su «in cerca» è questo cambio di metodo: tutte le
    condizioni non professionali passano da conteggi a stime nello stesso anno. I livelli si
    confrontano solo dentro il 2021-2024, come già fai.
  - Lessico da usare: «risulta», «il censimento classifica come», «stima» per le condizioni
    non professionali; «conteggio» solo per occupati e residenti.
- **I tuoi numeri non cambiano.** `notebooks/educazione.ipynb`, `pipeline/edu/` e i file
  `edu_*.csv` non sono stati toccati (il sensore li ha riscritti identici). Nel tuo notebook
  non c'è la formula «condizione dichiarata»; «coerenza dichiarata» in `pipeline/edu/policy.py`
  riguarda i dati del servizio e resta com'è.

### 2. I KPI di popolazione dicono la direzione, non provano l'effetto

La potenza dei due KPI ora si misura due volte (`genere_mde.csv`, figura `fig09b_potenza`):

| KPI | Finestra dichiarata | Potenza binomiale 1 · 2 · 3 anni | Potenza osservata 1 · 2 · 3 anni |
|---|---|---|---|
| occupazione F 15-24, +1,4 punti | triennio | 46 · 75 · 90% | 50 · 59 · 41% |
| casalinghe F 15-24, −2,1 punti | biennio | 68 · 93 · 99% | 57 · 82 · 58% |

«Osservata» significa contro quanto si muovono da soli i **33 comuni siciliani di taglia
simile** (fra metà e il doppio delle ragazze 15-24 di Bagheria). Il binomiale tratta ogni
anno come un campione nuovo; il censimento conta le stesse persone, e i comuni divergono fra
loro in modo persistente. Il «90% sul triennio» non è più una cifra della proposta: è
uscito da policy (§4-bis, §6), relazione (§7.4), copione e slide, e resta solo come termine
di confronto accanto alla potenza osservata nella scheda 4 e in `fig09b`. Il tasso comunale
ora si legge come **direzione** della convergenza; l'effetto del servizio si misura sui
partecipanti.

### 3. La valutazione del pilota ha quattro regole scritte (policy §7)

- Due coorti da 100, con ingresso al mese 0 e al mese 6: il confronto esiste sull'esito a sei
  mesi, non su quello a dodici.
- Chi abbandona resta nel gruppo assegnato.
- Se le domande non superano i posti, niente sorteggio: la valutazione diventa monitoraggio
  descrittivo.
- Con 100 persone per coorte il confronto vede effetti di 18-20 punti o più (26-28 con 50):
  `genere_potenza_pilota.csv`.

Anche la riga «Durata» della §3 e l'esito del servizio della §6 lo dicono.

### 4. Il costo ha un ordine di grandezza (policy §9-bis)

Fra 205.924 e 256.105 euro l'anno per la dotazione minima (cooperativa sociale livello D2
oppure personale comunale area Funzionari, più il 15% forfettario di costi indiretti), cioè
fra 1.030 e 1.281 euro per posto. Il percorso 4 del GOL paga fino a 1.198 euro per
partecipante. Le esperienze retribuite sono escluse. Parametri e fonti:
`genere_costo_parametri.csv` e `docs/sources.md` §13.4.

### 5. Il NEET del bando esiste a scala regionale

Dalla rilevazione sulle forze di lavoro (`genere_neet_rcfl.csv`, `docs/sources.md` §13.3):
Sicilia 2024, NEET 15-34 30,1% (F 35,3%, M 25,2%), Italia 17,3%. Sul 15-24 la Sicilia è al
19,5%, contro il 22,3% del proxy censuario «fuori da lavoro e studio», che viene dal tuo
thread: stesso ordine di grandezza. È una fonte diversa, campionaria e regionale: affiancata,
mai in serie con il dato comunale. È nel paragrafo NEET della policy e nella §1.1 della
relazione.

### 6. Il numero dei controlli è 934

Aggiornato in `CLAUDE.md`, nella relazione, nel copione (slide 3, risposta 15 della giuria)
e nella docstring di `pipeline/verifica.py`.

## Le parti di Saverio cambiate in copione e deck

| Dove | Che cosa è cambiato |
|---|---|
| Copione, slide 3 | «934 controlli automatici» |
| Copione, slide 16 | casalinghe senza «dichiarate»; i traguardi «dicono la direzione, non provano l'effetto»; valutazione in due gruppi da cento a sei mesi di distanza |
| Copione, giornalisti 5 «Quanto costa?» | risposta con l'ordine di grandezza del punto 4 |
| Copione, giuria 15 | 934 controlli |
| Copione, giuria 20 (nuova) | NEET regionale, punto 5 |
| Copione, giuria 22 (nuova) | «E se si presentano meno di 200 persone?», punto 3 |
| `docs/presentazione/presentazione_hackaton_v2.pptx`, slide 16 | «occupazione F 15-24, triennio (direzione)»; «casalinghe 15-24 (stima ISTAT), biennio»; gruppo B che parte sei mesi dopo |
| `docs/presentazione/presentazione_hackaton_v2.pptx`, slide 12 e 17 (Ale) | casalinghe «nel censimento», con il grafico rigenerato; «due coorti (mese 0 e 6)» |

Il PDF del copione (`docs/presentazione/COPIONE_PONTE_19.pdf`) è rigenerato dal `.md`.
`docs/presentazione/presentazione_hackaton_v2.pptx` è nel commit; la versione precedente alle modifiche di stasera non è mai stata
committata e resta solo nello scratchpad temporaneo della sessione.

## Il resto delle modifiche di stasera (thread genere)

| Verifica | Risultato | File | Nei documenti |
|---|---|---|---|
| Bagheria fra i 390 comuni | occupazione F 15-24 2024: 112ª dal basso su 390, 2ª su 34 simili; casalinghe 358ª su 390 | `genere_rango_390_15_24.csv` | policy §1, relazione §3.1 |
| Tetto sulle diplomate occupate (Fréchet) | al massimo 16,1% delle diplomate F lavora (M 35,7%), minimo zero | `genere_frechet.csv` | relazione §4, policy §10 |
| Tendenze parallele senza binomiale | distanza da Palermo −0,09 pp/anno, minore di quella del 67% dei simili | `genere_pretrend_390.csv` | policy §7, relazione §7.4 |
| Trasferimenti di residenza | nessuna tavola pubblica comune × età; ISTAT pubblica età e titolo fino alla provincia; i dati elementari si chiedono a ISTAT | `docs/sources.md` §13.5 | relazione §9, policy §10, copione |
| Figure | `fig02b` corretta (non più «autodichiarata»), `fig09b` rifatta con i due metri | `viz/fig02b_*.R`, `viz/fig09b_potenza.R` | policy, relazione, schede |

Il notebook di genere ha una sezione nuova, «Robustezza: le domande di approfondimento»
(celle `In [56]`-`[61]`), più una cella nella sezione «Trend paralleli» (`In [48]`). Le
celle da `In [48]` in poi sono scalate di uno.

## File e interfacce nuove

- **Raw** (append-only, in `data/raw/manifest.csv`):
  `censpop_lavoro_15_24_sicilia_01..12_2026-09-23.csv` (tavola lavoro 15-24 dei 390 comuni) e
  `rcfl_neet_regionale_2026-09-23.csv`. Si scaricano con
  `uv run python -m pipeline.fetch --solo=15_24_sicilia` e `--solo=rcfl_neet`.
- **Build**: `pipeline/build.py` produce `censpop_lavoro_15_24_sicilia_long.csv` (verifica 324
  celle identiche alla tavola a quattro territori) e `rcfl_neet_regionale_long.csv`.
- **Processed dal notebook di genere**: `genere_rango_390_15_24.csv`,
  `genere_interi_condizione.csv`, `genere_frechet.csv`, `genere_neet_rcfl.csv`,
  `genere_potenza_pilota.csv`, `genere_pretrend_390.csv`, `genere_costo_parametri.csv`,
  `genere_costo_pilota.csv`.
- **Schema cambiato**: in `genere_mde.csv`, `MDE 80% (pp)` è diventata
  `MDE binomiale 80% (pp)` e `potenza per il delta (%)` è diventata `potenza binomiale (%)`;
  si aggiungono le colonne osservate. Consumatori aggiornati: `viz/fig09b_potenza.R`,
  `pipeline/schede.py`, `pipeline/policy_docx.py`, `pipeline/verifica.py`. Il thread
  educazione non legge questo file.
- Nei 390 comuni, dove manca la riga degli occupati le forze di lavoro coincidono con chi
  cerca: gli occupati sono zero. Notebook e `verifica` li pongono a zero dopo averlo
  asserito.

## Trappole incontrate stasera

- **Ancore dei `.docx`.** `pipeline/policy_docx.py` e `pipeline/relazione_docx.py`
  inseriscono ogni figura subito dopo un frammento del `.md` (l'«ancora»), che deve comparire
  esattamente una volta. Una riga `→ file.csv, ...` che fa da ancora va lasciata com'è:
  metti i riferimenti nuovi dentro la frase precedente, altrimenti il testo aggiunto finisce
  dopo la figura. Se l'ancora sparisce, la build si ferma.
- **Nomi già usati nel notebook di genere.** `tassi_390` ed `etichette` vengono ridefiniti
  più avanti nel notebook; le celle nuove usano `tassi_15_24` e un lookup locale delle
  etichette. Prima di aggiungere una variabile, cerca se il nome esiste già.
- **`dist/` usa gli output salvati.** Dopo aver cambiato un notebook, eseguilo con
  `--inplace`, poi `uv run python -m pipeline.pdf`.

## Decisioni ancora aperte

- **Finestra del KPI sull'occupazione.** È dichiarato il triennio. Il biennio ha una potenza
  osservata più alta (59% contro 41%), ma il triennio disponibile nei dati attraversa la
  rottura del 2021, quindi il confronto non è pulito. Cambiarla è una decisione del team.
- **Il vecchio generatore del deck si ferma.** `pipeline/presentazione_pptx.py`,
  che produce `Datapolis_presentazione_finale.pptx`, legge le colonne di `genere_mde.csv` con i
  nomi vecchi. Il deck di riferimento del copione è `docs/presentazione/presentazione_hackaton_v2.pptx`.

## Modifiche del pomeriggio (nello stesso commit)

La revisione per il nuovo invio a giuria ha riscritto `README.md` e `LEGGIMI_GIURIA.md`
(«versione rivista del 23 settembre»). Ha anche fatto impacchettare lo zip a
`pipeline/pdf.py`, corretto etichette e testi di diverse figure (`fig04`, `fig05`, `fig05b`,
`fig07`, `fig07b`, `fig12`, `mob_fig01`-`mob_fig04`) e rieseguito `analisi.ipynb`. Il
dettaglio è in `git show` su quei file. Allo stesso commit appartiene il riordino di `docs/`
in sottocartelle (`relazione/`, `policy/`, `team/`, `presentazione/`, `analisi/`,
`archivio/`, `concorso/`, `idee/`): l'indice è `docs/README.md`.

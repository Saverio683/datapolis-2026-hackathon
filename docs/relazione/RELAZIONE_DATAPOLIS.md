# La transizione dalla formazione al lavoro dei giovani di Bagheria

## Profilo statistico, divario di genere e proposta di intervento. Relazione tecnica, DataPolis 2026

Bagheria, 2026-08-29, versione rivista del 2026-09-24. La relazione accompagna i tre
deliverable richiesti dal concorso: il **technical notebook** (`notebooks/analisi.ipynb`,
`notebooks/genere.ipynb`, `notebooks/educazione.ipynb`, `notebooks/mobilita.ipynb`), le
**visualizzazioni** (`figures/`) e la **policy proposal** (`docs/policy/POLICY_PONTE_19.md`).

Una nota per la lettura. Le frecce (→) in chiusura dei paragrafi indicano il file di
`data/processed/` o la cella di notebook che produce le cifre appena citate; la pipeline
che le rigenera è descritta nella sezione 1. Quando un numero richiede una cautela, la
cautela compare accanto al numero, non in fondo al documento.

---

## In una pagina

> **A Bagheria il diploma arriva, il lavoro no. La conversione fallisce soprattutto per le
> ragazze: sono più istruite dei coetanei, ma il loro tasso di occupazione 15-24 è
> dell'8,2%, il minimo dei quattro territori in 6 anni su 6. Dopo i 25 anni il divario non
> si chiude e diventa un tratto locale:
> le donne di 25-49 anni lavorano al 39,6%, 8,4 punti sotto Palermo, gli uomini a 1,3 punti.
> Nemmeno la generazione più giovane fa eccezione. Chi resta fuori, inoltre, non è chi
> cerca lavoro: dei 15-24enni fuori da lavoro e studio, il 70,6% non lo cerca nemmeno.**

I tre thread di analisi (genere, educazione, mobilità) non producono tre diagnosi diverse:
leggono **lo stesso passaggio, dalla formazione al lavoro, da tre angolature**. Genere ed
educazione interrogano le stesse tavole del censimento permanente con domande diverse;
mobilità usa una fonte propria, le matrici del pendolarismo. Sono misure aggregate sullo
stesso territorio e non seguono la traiettoria delle stesse persone, perché l'incrocio
individuale non è pubblicato (sezione 4).

La proposta (sezione 7) è **Ponte 19**: un servizio comunale di transizione e
riattivazione per i 18-25enni, con due finestre di ingaggio e un target esplicito sul
genere. Il nome richiama l'età di uscita dalla scuola superiore, 19 anni; l'analisi ha poi
fatto emergere una seconda finestra, fra i 22 e i 25 anni. La proposta ha anche un vincolo
di misura, che la distingue da un auspicio:

> **La platea femminile 15-24 cala del 15,5% entro il 2034, e chi ne farà parte è già nata.
> Portare il tasso di occupazione delle ragazze al livello di Palermo vale oggi 40 occupate
> in più. Lo stesso obiettivo, misurato sulla platea del 2029 e del 2034, vale +18,2 e −2,5
> (fig09). Per questo il KPI si scrive in tasso, non in teste.**

### La risposta al bando, in breve

| Richiesta del bando | Risposta | Dove |
|---|---|---|
| Profiling statistico & benchmarking (Sicilia, Italia, Palermo) | ✅ con intervalli di confidenza, percentili sui 390 comuni siciliani e due gruppi dichiarati di comuni pari | sezioni 2-3 |
| Focus: **impatto delle differenze di genere** | ✅ focus principale | sezione 3 |
| Focus: **titolo di studio × condizione lavorativa** | 🟡 l'incrocio non esiste nei dati comunali (verificato); la domanda è risolta con due misure parallele sulla stessa fascia | sezione 4 |
| Focus: **pendolarismo verso Palermo** | ✅ misurato con la matrice origine-destinazione ISTAT: va a Palermo il **91,1%** di chi esce per studio (2011) e il **65,1%** di chi esce per lavoro (2021), e lo scarto di genere si ribalta fra i due motivi | sezione 5 |
| NEET 15-34 | 🟡 non calcolabile a livello comunale: si usano due misure etichettate e mai fuse, con il valore regionale della rilevazione sulle forze di lavoro come riferimento | sezione 1.1 |
| Proposta di intervento | ✅ Ponte 19, con KPI misurabili e finestre di lettura dichiarate | sezione 7 |
| Technical notebook riproducibile | ✅ i quattro notebook girano da zero senza errori; i controlli automatici sono tutti superati | sezione 1 |
| 2-3 data viz avanzate | ✅ tre figure principali, più figure di supporto dichiarate come tali | sezione 8 |

I 🟡 non sono lavori a metà: indicano i punti in cui i dati pubblici finiscono, dichiarati
invece che aggirati. In un concorso sulla cultura del dato, sapere dove i dati non arrivano
è parte della risposta. È anche uno dei motivi della proposta, che quei dati mancanti li
produce (sezione 7.5).

---

## 1. Metodo: la relazione si rigenera da zero

L'intera analisi è una pipeline riproducibile. Da un ambiente pulito, la sequenza è:

```bash
uv sync                                         # ambiente Python
uv run python -m pipeline.build                 # raw -> data/processed/
uv run python -m pipeline.edu --skip-download   # thread educazione: raw -> edu_*.csv
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/analisi.ipynb
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/genere.ipynb
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/educazione.ipynb
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/mobilita.ipynb
uv run python -m pipeline.verifica              # controlli automatici
Rscript viz/build_all.R                         # tutte le figure in figures/
Rscript viz/dump_didascalie.R                   # titoli e didascalie -> figures/didascalie.csv
uv run python -m pipeline.schede                # le quattro schede HTML di docs/schede/
uv run python -m pipeline.relazione_docx        # questa relazione in .docx, figure incorporate
uv run python -m pipeline.policy_docx           # la policy proposal in .docx
uv run python -m pipeline.pdf                   # i PDF, i notebook in HTML e lo zip di dist/
```

I dati grezzi sono già in `data/raw/`, quindi dopo il primo `uv sync` la sequenza gira
senza rete. `pipeline.fetch`
serve solo ad aggiornarli: scarica file nuovi, datati al giorno del download. L'ordine dei
passaggi non è arbitrario: `genere.ipynb` legge tavole prodotte da `analisi.ipynb` e da
`pipeline.edu`, e `mobilita.ipynb` ne legge due prodotte da `genere.ipynb`
(`genere_gap_persone.csv` e `genere_pendolarismo.csv`).

La pipeline ha tre proprietà sostanziali:

- **Provenance completa.** Ogni file in `data/raw/` è append-only e ha una riga in
  `docs/sources.md` con URL esatto, data e parametri. Le correzioni stanno in
  `pipeline/`, mai nei raw.
- **Verifica indipendente.** `pipeline/verifica.py` esegue **1005 controlli automatici**,
  tutti superati. Ricalcola i numeri chiave **direttamente dai raw, con implementazioni
  alternative**: intervalli di Wilson e Newcombe riscritti, modello lineare di probabilità
  in forma analitica, matching rifatto, coorti dalle classi quinquennali. Anche la matrice
  del pendolarismo ha un parser proprio, che la legge in streaming dagli zip. Il modulo
  controlla poi che le tavole di `data/processed/` coincidano con quei ricalcoli e che le cifre
  scritte in questa relazione e nella policy compaiano alla lettera. Se un raw cambia, il
  controllo fallisce finché notebook, tavole e testo non vengono riallineati.
- **Separazione dei ruoli.** Python trasforma, R disegna. L'interfaccia fra i due sono i
  CSV di `data/processed/`, e negli script delle figure non c'è logica di trasformazione.

### 1.1 Le definizioni, fissate una volta

- **Territori**: Bagheria (`082006`), Comune di Palermo (`082053`), Sicilia (`ITG1`) e
  Italia (`IT`). A questi si aggiungono i **390 comuni siciliani**, per i percentili, e
  due gruppi di comuni pari (sezione 2.4).
- **Fasce d'età**: dipendono dal dominio, perché le fonti non danno il 15-34 ovunque. Per
  il lavoro la fascia è **15-24**, l'unica classe giovanile comunale della tavola lavoro
  del censimento permanente. La tavola istruzione ha come classe giovanile solo il
  **9-24**, sempre dichiarato; sotto i 15 anni un diploma non può esserci, quindi le
  diplomate 9-24 sono anche le diplomate 15-24, e il diploma si riporta sulla fascia del
  lavoro con il denominatore delle età singole (sezione 3.1). Per la demografia il
  **15-34** è esatto, ricostruito dalle età singole. Ogni figura dichiara la fascia.
- **Anni**: il censimento permanente copre il 2018-2024. Sulla classe 15-24 il **2020
  manca** e resta mancante, mai interpolato. 8milaCensus (1991/2001/2011) è una fonte
  storica separata e sempre etichettata. Fra il 2019 e il 2021 c'è una **rottura di
  misura** sulla componente «in cerca di occupazione»: i gap fra territori restano
  confrontabili, i livelli delle componenti no (`docs/sources.md` §7).
- **NEET**: il NEET 15-34 del bando **non è calcolabile a livello comunale**, perché la
  fascia non esiste nei dati. Si usano quindi due misure, etichettate e mai unite: il NEET
  **15-29 al 2011** (8milaCensus, `L4`) e il proxy **«fuori da lavoro e studio» 15-24,
  2018-2024** (censimento permanente). Hanno fasce e definizioni diverse, quindi si
  affiancano e non si mettono mai in serie. La cifra del bando esiste solo a scala
  regionale, nella rilevazione sulle forze di lavoro, fonte campionaria con definizione
  europea. Secondo questa rilevazione, nel 2024 il NEET 15-34 della Sicilia è al 30,1%
  (35,3% fra le donne, 25,2% fra gli uomini), contro il 17,3% dell'Italia. Sul 15-24 la
  stessa fonte dà 19,5% per la Sicilia, dove il proxy censuario dà 22,3%. Nel 2024
  l'ordine di grandezza è lo stesso, ma le due serie non si muovono insieme: dal 2021 la
  rilevazione campionaria scende di oltre dieci punti, il proxy censuario di poco più di
  tre. Il confronto conferma il livello di un anno, non la tendenza. Il dato regionale è
  un riferimento, non una misura di Bagheria. → `genere_neet_rcfl.csv`,
  `edu_youth_states_2018_2024.csv`
- **Percentili**: la posizione di Bagheria fra i 390 comuni siciliani, ordinati dal valore
  più basso al più alto (100° = valore più alto). Su occupazione e istruzione un
  percentile alto è favorevole; su NEET, uscita precoce e disoccupazione è sfavorevole;
  sulla mobilità il segno non è univoco (sezione 5.3).
- **Scarti**: sono calcolati sui valori non arrotondati, quindi possono differire di un
  decimale dalla differenza fra le cifre stampate.

### 1.2 I dati disponibili: che cosa è stato scaricato, da dove, quando

Nessuna cifra di questa relazione nasce da una raccolta propria. Tutte vengono da
statistica ufficiale pubblica, scaricata per via programmatica e conservata immutabile in
`data/raw/`. Un manifesto (`data/raw/manifest.csv`) registra per ogni file l'istante del
download e l'URL esatto. Le fonti entrate nell'analisi sono otto: una (il GTFS di AMAT)
serve solo come controllo, un'altra (la rilevazione sulle forze di lavoro) solo come
riferimento regionale. Il portale open data della Regione Siciliana è stato esplorato con
esito negativo, dichiarato come tale. Fanno eccezione i parametri di costo della sezione
7.4, trascritti da atti ministeriali e regionali e citati uno per uno
(`genere_costo_parametri.csv`, `docs/sources.md` §13.4).

| Fonte | Che cosa dà | Copertura | Ruolo |
|---|---|---|---|
| **ISTAT, 8milaCensus** (`ottomilacensus.istat.it`) | 99 indicatori comunali ai confini 2011, tutti i comuni siciliani più province, regioni e Italia | 1991, 2001, 2011 | Serie storica lunga, graduatorie, matching fra comuni pari |
| **ISTAT, Censimento permanente** (IstatData, API SDMX) | Condizione professionale, titolo di studio, popolazione per età singola, popolazione per classi quinquennali, pendolarismo dentro/fuori comune | 2018-2024 (età singole dal 2021, pendolarismo solo 2018-2019; le classi quinquennali anche 2001 e 2011) | Fotografia recente, serie annuale, tutti gli incroci di genere |
| **ISTAT, Rilevazione sulle forze di lavoro** (IstatData, SDMX) | Incidenza dei NEET per sesso ed età, solo regionale | 2018-2025 | Riferimento regionale per il NEET 15-34 del bando (sezione 1.1), mai in serie col dato comunale |
| **ISTAT, DCIS_POPRES1** (SDMX) | Popolazione residente per stato civile ed età singola | al 1.1.2025 | Verifica del canale «matrimonio precoce» (sezione 3.2) |
| **ISTAT, Matrici del pendolarismo** | Origine-destinazione comune per comune, con sesso, motivo, mezzo, fascia oraria e durata | 2001, 2011; solo lavoro nel 2021 (il 1991 è scaricato ma non usato) | La destinazione degli spostamenti (sezione 5) |
| **ISTAT, Confini amministrativi** (cartografia) | Poligoni dei comuni, vintage 01/01/2026 | corrente | Base geografica delle mappe e delle distanze |
| **Ministero dell'Istruzione e del Merito** | Anagrafe delle sedi degli istituti tecnici (276 sedi) | a.s. 2025/26 | Canali operativi della proposta, non esiti |
| Comune di Palermo / AMAT | GTFS della rete urbana | orario 2026 | Solo controllo dell'ultimo miglio (sezione 5.4) |
| Open Data Regione Siciliana (CKAN) | Nessun indicatore sulla popolazione giovanile di Bagheria (ricognizioni del 2026-08-12 e del 2026-08-29); i due dataset sui servizi al lavoro hanno risposto HTTP 502 al download del 2026-08-25 | - | **Esito negativo**, documentato in `docs/sources.md` §3, §10 e §12: esclusa da ogni conclusione |

Due precisazioni contano più di quanto sembri.

La prima: **l'assenza è documentata quanto la presenza**. La ricognizione su
`dati.regione.sicilia.it` e su `opendata.comune.palermo.it` è tracciata in
`docs/sources.md`, con le query eseguite e i conteggi ottenuti. Chi rifà il lavoro sa così
dove non conviene tornare. Il portale del Comune di Palermo, per esempio, non è un CKAN:
espone il catalogo in DCAT Turtle, e chi vi cerca le API standard ottiene 404. Sono
dettagli operativi, ma fanno la differenza fra «non c'è» e «non l'abbiamo trovato».

La seconda: **le fonti non sono intercambiabili**. 8milaCensus si ferma al 2011 e il
censimento permanente comincia nel 2018, con definizioni che non coincidono. Fra il 2019 e
il 2021, inoltre, c'è una rottura di misura sulla componente «in cerca di occupazione».
Per questo, quando le due fonti compaiono insieme, sono affiancate ed etichettate con
l'anno, mai concatenate in una serie unica.

### 1.3 Dal dato grezzo alla tavola d'analisi: le trasformazioni

`pipeline/build.py` trasforma i raw soprattutto in **tabelle lunghe, più alcune tabelle di
lookup**; le principali sono qui sotto. Nessuna scelta di analisi è incorporata
nell'interfaccia: ogni thread filtra ciò che gli serve. È questo che rende confrontabili
tre analisi indipendenti.

| Tavola | Righe | Che cosa contiene |
|---|---:|---|
| `ottomilacensus_long.csv` | 154.737 | territorio × anno × indicatore, i tre censimenti storici |
| `censpop_popolazione_long.csv` | 14.462 | territorio × anno × genere × età singola × stato civile × cittadinanza |
| `censpop_istr_lav_long.csv` | 6.552 | le due tavole del censimento permanente, lavoro e istruzione, in un file solo |
| `comuni_sicilia_poligoni.csv` | 15.702 | i vertici dei confini comunali, già proiettati |
| `territori.csv` | 521 | anagrafica dei territori, di cui **390 comuni siciliani** |
| `indicatori.csv` | 99 | codebook degli indicatori 8milaCensus |
| `codici.csv` | 164 | decodifica delle dimensioni SDMX |

Le operazioni non banali sono tutte in `pipeline/`; nessuna è fatta a mano sui raw.

- **Normalizzazione dei codici territoriali.** Le due fonti scrivono lo stesso comune in
  modo diverso (8milaCensus `82006`, SDMX `082006`). Tutti i codici sono portati a sei
  cifre con lo zero iniziale, così le tabelle si uniscono senza mappature. Sicilia e
  Italia mantengono i codici SDMX `ITG1` e `IT`.
- **Disambiguazione di «Bagheria».** Nella codelist territoriale esistono anche un Sistema
  Locale del Lavoro e un Distretto con lo stesso nome. Sono territori diversi dal comune, e
  confonderli è un errore silenzioso e plausibile. La pipeline usa solo `082006`.
- **Esclusione dei totali.** Ogni dimensione SDMX ha un codice di totale (`T` per il
  genere, `TOTAL` per la cittadinanza, `99` per la condizione, `ALL` per il titolo), che
  convive come riga sorella con i dettagli. Sommare senza filtrarli raddoppia i numeri,
  quindi la partizione è verificata cella per cella.
- **Ricostruzione della fascia 15-34.** La classe non esiste nelle tavole. Per età e
  genere si ottiene sommando le età singole, che esistono dal 2021. Le classi quinquennali
  la ricompongono anche per il 2001, il 2011 e il 2018-2019, e servono alla ritenzione
  decennale (sezione 3.3).
- **Geometria senza `sf`.** La libreria R per i dati spaziali richiede librerie di sistema
  (GDAL, GEOS, PROJ) che non si installano senza privilegi di amministratore. Per non
  imporle a chi riproduce, la geometria è calcolata in Python con geopandas, che esporta i
  poligoni già proiettati (EPSG:32633) come tabella di vertici. R li disegna poi come
  poligoni, con isole e buchi.
- **Lettura della matrice del pendolarismo.** Il tracciato è a campi fissi e senza
  intestazione: un campo sfalsato produrrebbe numeri plausibili ma sbagliati. I file sono
  letti in streaming dagli zip, senza mai espanderli, e il tracciato è controllato per
  prova (sezione 5).
- **Descrizioni fuori dalle tabelle.** Le etichette lunghe stanno nelle tabelle di lookup
  invece di ripetersi riga per riga: da sole portavano `ottomilacensus_long` da 5 a 40 MB.

### 1.4 Dalle tavole alle inferenze: i metodi

Dalle tavole si ricavano quantità che le tavole non contengono. Ogni passaggio usa un
metodo dichiarato, e ogni metodo è riscritto una seconda volta, in forma diversa, in
`pipeline/verifica.py`.

| Domanda | Metodo | Dove |
|---|---|---|
| Quanto è preciso un tasso? | Intervallo di **Wilson** al 95% | tassi di occupazione, quote |
| Quanto è preciso il divario fra due tassi? | Intervallo di **Newcombe** al 95% sulla differenza | gap M−F |
| Il divario di Bagheria differisce da quello dei territori di confronto? | **Modello lineare di probabilità** pooled 2022-2024, con test sui coefficienti | sezione 3.1 |
| Il divario si sta allargando? | Regressione del gap sull'anno, 2018-2024 | sezione 3.1 |
| Rispetto a chi si misura Bagheria? | **Percentili sui 390 comuni siciliani** e due gruppi di comuni pari costruiti per **matching**, su covariate strutturali o sul profilo di istruzione, mai su esiti del lavoro | sezione 2.4 |
| La graduatoria del 2011 dice ancora qualcosa nel 2024? | **rho di Spearman** fra le due graduatorie, più la persistenza per quintili | sezione 2.3 |
| Quanti giovani restano, e a che età se ne vanno? | **Ritenzione di coorte**: rapporto fra la stessa coorte a distanza di anni, a passo annuale e decennale | sezione 3.3 |
| L'anomalia è del comune o della sua taglia? | Regressione su **distanza dal capoluogo e dimensione**, lettura del **residuo** | sezione 5.3 |
| Quanto vale l'incertezza dei modelli comunali? | **Bootstrap** sui comuni, più validazione incrociata | sezione 2.4 |
| Le stime campionarie sono confrontabili con i conteggi? | **Calibrazione sui margini esatti** dei conteggi esaustivi, con errore relativo misurato | sezione 5.4 |
| In quanto tempo si potrà dire se l'intervento ha funzionato? | **Analisi di potenza** e minimo effetto rilevabile (MDE) con due metri: il modello binomiale e la variabilità osservata, senza interventi, nei 33 comuni siciliani di taglia simile | sezione 7.4 |
| Il pilota vede il proprio effetto? | Potenza del confronto fra due coorti da 100 partecipanti | sezione 7.4 |
| Il controfattuale scelto è ammissibile? | **Test di pre-trend** sulle pendenze 2018-2024, ripetuto senza modello binomiale contro le pendenze dei comuni simili | sezione 7.4 |
| Quante diplomate lavorano, senza l'incrocio individuale? | **Limiti di Fréchet** sui margini delle due tavole | sezione 4 |
| Una quota censuaria è un conteggio o una stima? | Quota di celle intere per condizione e anno sui 390 comuni | sezioni 1.5 e 3.2 |

Due proprietà rendono questi conti verificabili, e non solo dichiarati. La prima: **il
controllo di regressione è indipendente**. `pipeline/verifica.py` non rilegge i risultati
dei notebook: li **ricalcola dai raw con implementazioni alternative**. Riscrive da zero
gli intervalli, stima il modello in forma analitica, rifà il matching, prende le coorti
dalle classi quinquennali invece che dalle età singole e usa un secondo parser della
matrice del pendolarismo. Se le due strade divergono, il controllo fallisce.

La seconda: **il documento rientra nel perimetro dei controlli**. L'ultimo blocco rilegge
le cifre da `data/processed/`, le formatta all'italiana e pretende che la frase compaia
alla lettera in questa relazione. Un numero ritoccato a mano nel testo fa fallire la
pipeline esattamente come un errore di calcolo.

### 1.5 Che cosa le inferenze autorizzano a dire

I risultati che seguono non hanno tutti lo stesso statuto. Distinguerli è la premessa per
leggerli senza sopravvalutarli.

- **Descrittivo.** Conteggi e quote censuarie su Bagheria. Il censimento permanente li
  produce integrando registri amministrativi e rilevazioni campionarie, e a livello
  comunale ISTAT non pubblica un errore di stima. Dove compare un intervallo, quindi,
  misura la variabilità binomiale della proporzione, non l'incertezza della rilevazione.
  Dal 2021, inoltre, solo occupati e residenti sono conteggi. Le altre condizioni (in
  cerca di occupazione, casalinga, studente, pensionato, altra condizione) sono stime
  di modello: somme di probabilità individuali di cui ISTAT non calcola l'errore standard.
  Lo si vede nei dati, dove quelle celle non sono intere (sezione 3.2). Il censimento 2011
  è invece un'enumerazione, salvo le variabili rilevate su campione (sezione 5.4).
- **Comparativo.** Il confronto con Palermo, Sicilia, Italia, i 390 comuni siciliani e i
  due gruppi di pari. Qui è robusta l'affermazione che **sopravvive al cambio di lente**.
  Dove i due gruppi di pari divergono, la relazione lo dice invece di scegliere il più
  favorevole.
- **Ecologico.** Le correlazioni fra comuni (mobilità e occupazione femminile, mezzo
  collettivo e divario di genere). Orientano un'ipotesi e non la dimostrano: valgono sul
  comune, mai sulla persona. Sono sempre citate con questo limite, e una di esse è
  riportata proprio perché ha dato **esito negativo** (sezione 5.4).
- **Nessuna stima causale.** Nessun numero di questa relazione misura l'effetto di un
  intervento, perché nessun disegno lo consentirebbe. Per questo la proposta include un
  proprio disegno di valutazione (sezione 7.4), che serve a produrre l'evidenza che oggi
  manca, non a confermare quella che c'è.

Ciò che la relazione **non** afferma è raccolto in chiaro nella sezione 9.

---

## 2. Il profilo: un recupero vero che non converge

### 2.1 La fotografia 2024

Nel 2024 Bagheria conta **5.904 residenti di 15-24 anni**. Per condizione prevalente si
distribuiscono così:

| Condizione 2024 | Quota | Persone (stima) |
|---|---:|---:|
| Studenti | 60,7% | ~3.581 |
| Occupati | 12,4% | ~734 |
| In cerca di occupazione | 7,9% | ~467 |
| **Inattivi non studenti** | **19,0%** | **~1.121** |

→ `edu_youth_states_2018_2024.csv`, `analisi_condizione_15_24.csv`

Lo stesso profilo sui quattro territori del bando:

| 15-24, 2024 | Bagheria | Palermo | Sicilia | Italia |
|---|---:|---:|---:|---:|
| Occupati | **12,4%** | 13,2% | 15,6% | 22,3% |
| In cerca di occupazione | **7,9%** | 8,3% | 7,5% | 6,2% |
| Studenti | **60,7%** | 63,2% | 62,2% | 62,3% |
| Inattivi non studenti | **19,0%** | 15,3% | 14,8% | 9,2% |
| Fuori da lavoro e studio | **26,9%** | 23,6% | 22,3% | 15,3% |
| di cui non cercano lavoro | **70,6%** | 64,9% | 66,4% | 59,8% |

→ `edu_youth_states_2018_2024.csv`

Il confronto individua subito il punto critico. L'occupazione 15-24 di Bagheria (12,4%) è
**3,1 punti sotto la Sicilia** (15,6%), mentre gli inattivi non studenti (19,0%) sono **4,2
punti sopra** (14,8%). Nel complesso il 26,9% dei giovani è fuori sia dal lavoro sia dallo
studio, contro il 22,3% siciliano. → `edu_kpi_dashboard.csv`

Dentro quel 26,9% sta il dato che orienta tutta la proposta: **il 70,6% non è
classificato come persona in cerca di occupazione**, più che a Palermo (64,9%), in Sicilia
(66,4%) e in Italia (59,8%). Il livello di questa quota dipende dal metodo di stima in
vigore dal 2021 (sezione 2.2): si confronta quindi fra territori nello stesso anno, non
lungo la serie. Non sono giovani che cercano e non trovano: sono giovani che non arrivano
a cercare.

### 2.2 Il recupero c'è, la convergenza no

Fra il 2018 e il 2024 l'occupazione 15-24 (maschi e femmine insieme) sale dall'8,2% al
12,4%. Lo scarto dalla Sicilia, però, è di **−3,1 punti sia nel 2018 sia nel 2024**.
Bagheria migliora alla velocità del contesto, non di più. → `edu_finding_summary.csv`

Le componenti di chi è fuori da lavoro e studio richiedono una cautela. Fra il 2019 e il
2021 cambia la misura della condizione «in cerca di occupazione», e la sua quota cade in
un solo passaggio di 7,5 punti a Bagheria e di 7,1 in Sicilia (`docs/sources.md` §7). Il
confronto corretto resta quindi dentro la stessa definizione, cioè nel 2021-2024. In quel
periodo **chi cerca lavoro scende da 10,6% a 7,9%, gli inattivi non studenti restano fermi
(19,2% → 19,0%)**, e il loro scarto dalla Sicilia sale da 2,7 a 4,2 punti. Il
miglioramento, dove c'è, non raggiunge chi non cerca. → `edu_youth_states_2018_2024.csv`

La fascia adulta recupera un po' più in fretta, ma resta lontana. Fra i 25-49enni la quota
con almeno il diploma passa dal 56,2% al 62,4% e l'occupazione dal 43,0% al 53,6%. Gli
scarti dalla Sicilia si riducono di 1,1 e 1,6 punti, ma nel 2024 restano
rispettivamente di **−4,1 e −5,7 punti**. → `edu_adult_transition_2018_2024.csv`,
`edu_kpi_dashboard.csv`

### 2.3 Il lungo periodo: progresso assoluto, arretramento relativo

I censimenti del 1991, 2001 e 2011, con il ponte verso il censimento permanente, separano
due cose che di solito si confondono: Bagheria **migliora in assoluto e arretra in
posizione**.

- NEET 15-29: scende dal 42,9% (1991) al 40,1% (2011), ma fra i 390 comuni siciliani
  Bagheria passa **circa dal 17° all'88° percentile**. Qui un percentile alto è
  sfavorevole: molti altri comuni hanno ridotto il problema molto più in fretta.
  → `edu_historical_bagheria.csv`, verifica incrociata in `notebooks/genere.ipynb`
- Uscita precoce dalla scuola (`I5`, 15-24): scende dal 40,8% al 28,6%. Nei censimenti del
  1991, 2001 e 2011, però, il percentile passa dal **56° al 70° e poi all'83°**, e anche
  qui un percentile alto è sfavorevole. → `genere_frattura_istruzione.csv`
- Occupazione femminile 15+: sale dal 18,1% (2011) al 23,7% (2024), mentre la mediana
  regionale passa dal 23,6% al 28,3%. **Nel 2024 Bagheria arriva dove stava la mediana
  siciliana nel 2011** (fig04). Su questo indicatore il confronto fra le due rilevazioni
  regge: nel 2018 il censimento permanente dà a Bagheria il 18,8%, a meno di un punto dal
  2011. Lo scarto resta entro un punto anche per Palermo, Sicilia e Italia (sezione «Il
  ponte fra i due censimenti» di `notebooks/genere.ipynb`).
- Graduatoria dell'occupazione femminile: quella dei 390 comuni del 2011 predice quella del
  2024 con rho di Spearman **0,848**, e il 74% del quintile più basso del 2011 è ancora
  lì, Bagheria compresa. Il posizionamento del 2011 non era una fotografia scaduta, ma una
  previsione verificata. → `genere_mappa_2011_2024.csv`, sezione «I claim reggono al
  2024?» di `notebooks/genere.ipynb`
- Datazione: i due domini non arretrano allo stesso ritmo. Il muro sull'occupazione
  femminile si alza **nel decennio 2001-2011**: il percentile resta fermo fra il 1991 e il
  2001, poi crolla, e al 2024 non si è richiuso (fig10). L'uscita precoce invece perde
  posizione a passo costante già dal 1991, e il dato comunale si ferma al 2011.
  → `genere_gap_madri.csv`, `genere_madri_recente.csv`, `genere_frattura_istruzione.csv`

### 2.4 Le lenti di confronto: cosa sopravvive al cambio di «simile»

Oltre ai tre territori del bando, il benchmarking usa i **390 comuni siciliani** e due
gruppi di comuni pari, costruiti per rispondere a domande diverse. Le **10 gemelle
strutturali** vengono da un matching su dimensione, densità, età, stranieri, abitazioni e
distanza da Palermo, mai su esiti. I **10 pari a pari istruzione** vengono dal thread
educazione. I due gruppi si sovrappongono su un solo comune (Misilmeri). La figura di
posizionamento (fig08) li mostra affiancati, e da qui viene il criterio di lettura: **ciò
che si può affermare senza scegliere una lente è ciò che sopravvive a entrambe**. Su 8
indicatori, 6 danno lo stesso giudizio.

Il confronto usa gli indicatori 8milaCensus del 2011, e il numero fra parentesi indica
quanti dei 10 comuni pari hanno un valore più basso di Bagheria. Tre tratti reggono in
entrambe le letture, e per questo entrano nella proposta. Sono la disoccupazione femminile
estrema (8 su 10 sotto Bagheria, in entrambi i gruppi), l'occupazione 15-29 bassa (2 su
10) e la quota minima di giovani che vivono da soli (0 su 10).

La divergenza più informativa riguarda l'occupazione femminile 15+. Fra le gemelle
strutturali Bagheria è nella norma (3 su 10 sotto); fra i comuni ugualmente scolarizzati è
**penultima** (1 su 10). **A pari istruzione, il lavoro femminile non arriva: non è un
tratto di fascia territoriale.**

I modelli comunali del thread educazione confermano il segno: lo scarto fra occupazione
giovanile osservata e prevista è di **−5,9 punti** nel modello di contesto territoriale
(intervallo bootstrap da −7,7 a −4,3). Il loro potere esplicativo, però, è quasi nullo:
R² in validazione incrociata 0,05 in quel modello, negativo negli altri due, che danno
comunque un residuo dello stesso segno. Il risultato si cita quindi come conferma di
segno, mai come quantità attribuibile al comune.
→ `genere_posizionamento.csv`, `genere_pari_lenti.csv`, `edu_model_robustness_2011.csv`

---

## 3. Il focus di genere: il capitale umano che il territorio spreca di più è femminile

### 3.1 La forbice: più istruite, meno occupate

Nel 2024, a Bagheria:

| | Maschi | Femmine | Scarto M − F |
|---|---:|---:|---:|
| Almeno diploma (9-24) | 29,2% | 33,4% | **−4,2 pp** (F avanti) |
| Almeno diploma (15-24) | 46,2% | 51,0% | −4,8 pp (F avanti) |
| Occupazione (15-24) | 16,5% | 8,2% | **+8,3 pp** (F indietro) |

→ `genere_quadro_sintesi.csv`, `genere_forbice_quadrante.csv`

Il diploma compare su due fasce perché la tavola istruzione del censimento permanente
comincia a 9 anni. Sulla fascia 9-24 il vantaggio femminile di Bagheria (4,2 punti) è il
più ampio del panel: 1,8 punti a Palermo, 2,7 in Sicilia, 2,2 in Italia. Quella fascia,
però, comprende età in cui il diploma non può ancora esserci, e il suo valore risente della
composizione per età. Sulla **stessa fascia 15-24 dell'occupazione** il vantaggio è +4,8
punti, pari alla Sicilia (+4,7). Il gap di occupazione è di 8,3 punti [IC 95% 6,6-10,0].
→ `genere_gap_occupazione_ci.csv`

Il gap si può leggere su più scale (fig01), e un modello lineare di probabilità dice su
quale Bagheria è anomala. **In punti**, il gap di Bagheria non è un'anomalia locale: sul
pooled 2022-24 è 1,1 punti più ampio di quello di Palermo (p=0,03) e 1,8-1,9 punti più
stretto di quelli di Sicilia e Italia. Il pooled tratta come indipendenti annate che
contano in parte le stesse persone, quindi quel p è ottimistico: sul solo 2024 lo scarto
da Palermo non è significativo. **In rapporto** Bagheria è la peggiore del panel (M/F =
2,01 contro 1,56 nazionale), ma il rapporto oscilla da un'annata all'altra.

**Il tratto locale è il livello: il tasso di occupazione femminile all'8,2% [Wilson
7,2-9,2] è il minimo dei quattro territori in tutte e 6 le annate disponibili.** La
differenza è testata: il tasso è sotto Palermo di 1,2 punti, sotto la Sicilia di 1,9 e
sotto l'Italia di 8,9 (p < 0,001, pooled 2022-24). Anche il tasso maschile è il più basso
del panel in 5 annate su 6, ma a pochi decimi da Palermo; il distacco femminile è più
ampio (nel 2024 −1,4 punti da Palermo, contro −0,1 dei maschi, sezione 3.1-bis). Il gap
in punti tende ad allargarsi, con una stima di +0,21 punti l'anno sul 2018-2024. Su sei
annate, però, ciascuna con la propria variabilità, la tendenza non è acquisita: è una
direzione, non un risultato.
→ sezioni «Punti percentuali o rapporto?», «Modello lineare di probabilità» e «Trend
2018-2024» di `notebooks/genere.ipynb`

Il primato vale nel panel, non in tutta la Sicilia. Fra i 34 comuni siciliani con un
numero di ragazze 15-24 fra la metà e il doppio di quello di Bagheria (Bagheria compresa),
il comune è **secondo dal basso** (mediana 10,6%), fra tutti i 390 comuni è 112° dal
basso (mediana 9,7%). Sui 390 la posizione è meno estrema perché molti comuni piccoli
stanno sotto.
→ `genere_rango_390_15_24.csv`; sezione «Bagheria è anomala fra i comuni siciliani?» di
`notebooks/genere.ipynb`

Anche il vantaggio femminile nell'istruzione va letto con cura. Le ragazze di Bagheria sono
più istruite dei coetanei su ogni fascia, ma il loro vantaggio sui coetanei non è più ampio
di quello siciliano su ogni fascia: sulla 18-24 Sicilia e Italia hanno un vantaggio
femminile più ampio. Su ogni fascia regge invece
la coppia **distacco dal vicinato e mancata conversione**. Sui 18-24 il vantaggio femminile
è di +5,7 punti a Bagheria contro +2,5 nei cinque comuni più vicini; il tasso di
occupazione femminile, invece, è il più basso del panel.

Su 1.000 ragazze 15-24 di Bagheria, 510 hanno almeno il diploma e 82 lavorano; fra i
coetanei, 462 e 165 (fig11). Le due barre della figura hanno la stessa base ma **non sono
un funnel**: non dicono quante diplomate lavorano, perché l'incrocio individuale non è
pubblicato. I margini fissano solo un tetto (sezione 4).
→ `genere_per_1000.csv`, `genere_forbice_quadrante.csv`

A 15-24 anni, però, la forbice si osserverebbe anche se il vantaggio si convertisse più
tardi. Le ragazze studiano più a lungo (studentesse il 65,1% contro il 56,4% dei
coetanei), quindi a quell'età lavorano meno per costruzione. La prova della mancata
conversione va cercata dopo il percorso formativo (sezione 3.1-bis).
→ `genere_composizione_stato.csv`

### 3.1-bis Dopo i 25 anni il divario non si chiude, e diventa locale

Sul 15-24 due ipotesi sono compatibili con gli stessi dati. La prima è il **ritardo**: le
ragazze studiano più a lungo e recuperano dopo. La seconda è la **mancata conversione**:
finito lo studio, il lavoro non arriva. Per distinguerle serve guardare oltre la fascia
target. La tavola lavoro comunale ha una sola classe adulta sotto i 50 anni, 25-49: qui non
fa da proxy dei giovani, ma da test di che cosa succede dopo.

| Scarto di Bagheria sul tasso di occupazione, 2024 (punti) | F vs Palermo | M vs Palermo | F vs Sicilia | M vs Sicilia |
|---|---:|---:|---:|---:|
| 15-24 | −1,4 | −0,1 | −2,2 | −3,8 |
| 25-49 | **−8,4** | −1,3 | **−8,0** | −3,1 |

Fino ai 24 anni lo scarto dalla Sicilia non è di genere: i ragazzi, anzi, stanno più
indietro delle ragazze. Da Palermo le ragazze distano di più, ma di poco più di un punto.
Fra i 25 e i 49 anni lo scarto diventa femminile, e largo, rispetto a entrambi. Le donne di Bagheria
lavorano al 39,6% contro il 48,0% di Palermo e il 47,6% della Sicilia, gli uomini al 67,7%.
Lo scarto femminile sta fra −8,0 e −10,2 punti in ogni anno dal 2018 e non è un effetto
della composizione per età. Al tasso femminile di Palermo le occupate 25-49 sarebbero **695
in più**, contro le 40 in più della fascia 15-24. A Bagheria le casalinghe sono il 42,2%
delle donne 25-49 (Palermo 33,8%, Sicilia 33,2%, Italia 18,1%). → `genere_dopo_25.csv`,
`genere_dopo_25_scarti.csv`, fig13b

**La generazione giovane non ne è risparmiata.** La classe 25-49 mescola chi ha appena
finito di studiare con le generazioni precedenti, e sul 50-64 lo scarto femminile è ancora
più ampio. Lo scarto del 25-49 potrebbe quindi appartenere solo alle donne più anziane, e
il ricambio delle coorti permette di verificarlo. Se lo scarto fosse tutto delle donne che
nel 2018 avevano 35-49 anni, il ricambio l'avrebbe portato nel 2024 a −6,3 punti da
Palermo; è a −8,4 (z −3,3). Le nate dal 1984 in poi portano uno scarto di circa −6 punti,
i coetanei maschi −0,4. ⚠️ Il test non separa l'età dalla coorte, e lo scarto per
generazione viene da un modello a due gradini: si cita come ordine di grandezza.

A scala regionale, su un'altra fonte, il NEET femminile cambia posizione rispetto a quello
maschile fra le due fasce.
In Sicilia, nel 2024, la rilevazione sulle forze di lavoro lo dà sotto quello maschile a 15-24 anni
(17,4% contro 21,5%) e quasi il doppio a 25-34 (52,2% contro 28,9%, ricavato per
differenza). → `genere_dopo_25_generazioni.csv`, `genere_neet_25_34.csv`; sezioni «Dopo i
25 anni» e «La generazione successiva» di `notebooks/genere.ipynb`

Per la proposta la conseguenza è di perimetro. La parte più grande del problema femminile
di Bagheria riguarda donne sopra i 25 anni. La classe 25-49 dice che il problema c'è, ma
non permette di seguirlo età per età, né di isolare i 26-34enni del bando (sezione 7).

### 3.2 Dentro l'inattività: le casalinghe ventenni, non sposate

Nelle stime del censimento risulta **casalinga** il 13,4% delle ragazze 15-24 di Bagheria,
387 persone, contro l'11,3% di Palermo, il 10,1% della Sicilia e il 4,6% dell'Italia. Il
livello tiene nel tempo: dal 2021 la quota sta fra il 12,8% e il 14,8%.

**È una stima, non un conteggio né una dichiarazione.** Dal 2021 ISTAT stabilisce chi è
occupato; per chi non lo è, stima con un modello la probabilità di ciascuna altra
condizione. Il modello è un logit multinomiale addestrato sulle risposte del campione
censuario, con covariate amministrative come età, istruzione, segnali di lavoro, pensione e
redditi. Il numero comunale è la somma di quelle probabilità, a Bagheria 386,84 ragazze, e
il suo errore standard non è calcolato. La natura di stima si vede nei dati: sui 390
comuni, dal 2021 le celle di occupati e residenti sono tutte intere, quelle di tutte le
altre condizioni quasi mai. Nel 2018-2019, con un altro metodo, erano tutte intere.

Ne seguono tre conseguenze. La prima: nessuna covariata del modello misura il lavoro
domestico, quindi «casalinga» è l'etichetta che la stima assegna, non una misura della
cura. La seconda: la serie si legge solo dal 2021, perché fra il 2019 e il 2021, in
corrispondenza del cambio di metodo, la quota dei comuni di taglia simile salta in mediana
di 2,87 punti. La terza: la stabilità della quota dal 2021 è in parte costruita dal metodo,
che fra le covariate usa le stime comunali del censimento precedente.
→ `genere_interi_condizione.csv`, sezione «Il KPI si può misurare?» di
`notebooks/genere.ipynb`; fonti del metodo: metadati ESMS del censimento 2021 (ISTAT per
Eurostat) e Chianella, Ciccaglioni, Ercolani, RIEDS 2024

La tavola non dà l'età dentro la fascia, e sull'aggregato pesano le 15-17enni, quasi tutte
studenti. Due casi limite: se nessuna delle 387 avesse meno di 18 anni, la quota sulle
18-24enni sarebbe del 18,8%; se nessuna ne avesse meno di 20, sarebbe del 25,8% sulle
20-24enni. Rispetto all'incidenza italiana, l'eccesso vale 255 ragazze.
→ `genere_casalinghe.csv`, `genere_casalinghe_bounds.csv`

Chi sono queste ragazze? Il canale del matrimonio precoce **non regge i numeri**. Al
1.1.2025 le già coniugate 15-24 sono 41 (1,4%) contro 387 casalinghe: **almeno l'89% delle
casalinghe non è sposata**. La quota di coniugate 20-24 di Bagheria (2,7%) sta inoltre
*sotto* Palermo (3,2%) e Sicilia (2,9%). Lo stato civile esclude il matrimonio come
spiegazione, ma non osserva convivenze né figli: che cosa tenga a casa queste ragazze, i
dati pubblici non lo dicono. Per la policy basta il primo fatto: serve un servizio di
**attivazione**, non solo di conciliazione. → `genere_stato_civile.csv` (fonte
DCIS_POPRES1, denominatori coincidenti alla singola unità con la tavola censuaria)

Il gruppo degli «invisibili» (fuori da lavoro, studio e ricerca) **non è femminile nelle
dimensioni**: 573 ragazze e 549 ragazzi (51% F). In quota sulla propria popolazione le
ragazze stanno un po' sopra (19,9% contro 18,2% nel 2024, con lo stesso segno in ogni
annata), ma lo scarto sta fra 1,7 e 3,5 punti dal 2021. È femminile soprattutto
**nell'etichetta**. Fra le
ragazze prevale un'etichetta precisa: 387 casalinghe, contro 50 casalinghi fra i ragazzi.
Fra i ragazzi prevale il residuo senza nome, «altra condizione»: 485 ragazzi contro 183
ragazze.

Anche questi numeri sono stime di modello, non conteggi. Nel modello «casalinga» e «altra
condizione» sono una sola categoria, e la regola che le separa non è descritta nelle fonti
lette. La stessa divisione per genere c'era però già nel 2018-2019, con l'altro metodo
(casalinghe il 12,4% delle ragazze e lo 0,8% dei ragazzi nel 2018): non è un artefatto del
solo modello 2021.

A 15-24 anni, quindi, i dati sostengono **un'inattività di dimensioni simili con etichette
diverse**; l'eccesso femminile largo compare dopo i 25 anni (sezione 3.1-bis). L'outreach
deve perciò coprire entrambi i generi, con agganci diversi.
→ `genere_composizione_stato_dettaglio.csv`, `genere_composizione_stato.csv` (fig02)

### 3.3 La fuga avviene all'uscita dal percorso formativo, per entrambi i generi

La **ritenzione di coorte** misura la fuga senza bisogno di dati sulle migrazioni. È il
numero di residenti di una certa età nel 2024 in percentuale di quelli che avevano tre anni
di meno nel 2021: sotto 100 la coorte si è ridotta, sopra è cresciuta. È un saldo netto, e
non distingue chi parte da chi arriva. Sul 2021-2024 la ritenzione mostra due uscite
diverse per genere (fig03, fig07):

- **i ragazzi si perdono presto e a ondate** (età 17-19 e 23-24), con **rientri netti
  dopo i 26**;
- **le ragazze tengono fino ai 23-24 anni e si perdono dai 24-25 in poi, senza
  rientri.** La coorte femminile che nel 2021 aveva 25-29 anni è a **96,3**, contro 101,2
  dei coetanei maschi, 97,6 in Sicilia, 98,8 a Palermo e 103,0 in Italia (dove la coorte
  cresce per immigrazione). È proprio l'età in cui il vantaggio educativo dovrebbe
  convertirsi in occupazione, e non lo fa.

→ `genere_coorti.csv`, `genere_ritenzione_eta.csv`

**Nel triennio la curva femminile scende fra i 22 e i 25 anni** (età nel 2021): prima di
quelle età sta sopra la parità, dopo resta sotto. Chi aveva 22-25 anni nel 2021 ne ha
25-28 nel 2024, ed è in quel passaggio che la coorte si riduce. ⚠️ È una lettura **pooled
sul triennio**. Le transizioni annuali oscillano fino a 8 punti sulla stessa età (n ~290
per cella), e l'anno singolo è un controllo, non un titolo. Il tratto di genere, inoltre,
è la forma della curva, non il saldo: prese in blocco, le età 22-25 perdono fra le ragazze
di Bagheria quanto fra i coetanei maschi e fra le ragazze siciliane. A 21 anni, invece,
nessuno dei due generi perde residenti netti. → `genere_ritenzione_transizioni.csv`,
`genere_ritenzione_eta.csv`

**Su cinque anni la differenza di genere non si ripete.** Dentro il solo censimento
permanente le coorti si possono seguire su due quinquenni, 2018-2023 e 2019-2024. Quelle
che escono dal percorso formativo, da 20-24 a 25-29 anni, si riducono per entrambi i
generi, 9-12 punti sotto l'Italia. I maschi si riducono più delle femmine (89,2% e 91,8%
contro 92,8% e 93,3%), e le femmine di Bagheria stanno al livello di Palermo (90,9% e
92,9%).

Nei cinque comuni più vicini, inoltre, il cedimento femminile del triennio non c'è (coorte
25-29 al 102,4). Il cedimento di Bagheria o è specifico del comune, o è in parte un
trasloco a pochi chilometri, e la ritenzione netta non distingue i due casi. Regge dunque la
perdita all'uscita dal percorso formativo; il tempismo di genere resta la lettura di un
solo triennio. → `genere_ritenzione_decennale.csv`, `genere_coorti_vicini.csv`

Alla scala decennale la frattura è più netta, e risponde all'obiezione che tre anni non
bastino a parlare di fuga. La coorte 15-19 seguita per dieci anni passa, fra le femmine, da
**102,9% (2001-2011) a 88,6% (2011-2021)**, fra i maschi da 98,4% a **83,9%**. Sono circa
14 punti per entrambi i generi, contro 4-6 in Sicilia. A questa scala la fuga non ha
genere, e il suo decennio è quello **successivo** al muro sull'occupazione femminile
(2001-2011, sezione 2.3). ⚠️ Il decennio 2011-2021 unisce il censimento 2011 e il censimento
permanente: la distorsione nota va nel verso prudente ed è dichiarata in fig07b.
→ `genere_ritenzione_decennale.csv`

---

## 4. Titolo e condizione: la domanda a cui i dati comunali non rispondono

Il primo focus proposto dal bando è la relazione fra titolo di studio e condizione
lavorativa. A livello comunale questa relazione **non è misurabile sull'individuo**, e lo
abbiamo dimostrato prima di aggirarlo. Nelle tavole comunali del censimento permanente, la
tavola lavoro pubblica il titolo solo come `ALL` e la tavola istruzione pubblica la
condizione solo come totale `99` (cella «Verifica di fattibilità» di
`notebooks/genere.ipynb`). *«Quanti diplomati di Bagheria lavorano»* non è quindi una
domanda a cui i dati pubblici rispondono. Ci si avvicina alla domanda in tre modi: due
misure parallele sulla stessa fascia e sullo stesso denominatore (fig11, sezione 3.1), il
confronto territoriale (sezione 2) e la lente dei pari a pari istruzione (sezione 2.4).

**I margini, però, mettono un tetto.** Se tutte le occupate fossero diplomate, nel 2024
lavorerebbe al massimo il **16,1%** delle ragazze 15-24 con almeno il diploma (236
occupate su 1.469 diplomate), contro il 35,7% dei ragazzi. Il minimo, per entrambi, è
zero. Sono limiti di Fréchet, non stime. Valgono perché diplomati e occupati sono
sottoinsiemi della stessa popolazione 15-24: il totale della tavola lavoro, come verificato,
coincide con la somma delle età singole. Il tetto femminile di Bagheria è il più basso dei
quattro territori (Palermo 20,3%, Sicilia 20,4%, Italia 32,3%). Qualunque sia l'incrocio,
fra le diplomate lavora al più una su sei. → `genere_frechet.csv`

Resta da chiarire di quale titolo si parla, perché non è lo stesso a tutte le altezze.
Nella fascia 9-24 del 2024, a Bagheria, oltre il diploma si va di rado: dei **2.864
residenti con almeno il diploma, il 91,0% si ferma al diploma** di scuola secondaria, e i
titoli terziari sono **258 persone** in tutto. A quell'età è così ovunque (fra l'88,1%
dell'Italia e l'89,4% della Sicilia): il dato dice quale titolo la fascia detiene, non
quanto in alto arriverà, perché a 20 anni una laurea non può ancora esserci.
→ `censpop_istr_lav_long.csv`

Chi la laurea l'ha già conseguita si osserva al 2011, e lì la scala dei titoli regge solo
al primo gradino (`edu_fig02_catena_2011`). L'unico indicatore su cui Bagheria sta davanti
a Palermo e alla Sicilia è la competenza di base, `I8`: **96,7% dei 15-19enni con almeno
la licenza media**, contro 95,6 e 96,5 (Italia 97,9). Un gradino più su il segno si
inverte, e resta tale:

- adulti 25-64 con diploma o laurea (`I6`) al **42,5%** contro 48,2 in Sicilia, 51,2 a
  Palermo e 55,1 in Italia;
- trentenni con titolo universitario (`I7`) al **14,4%** contro 18,3, 20,6 e 23,2, nello
  stesso ordine.

Bagheria è ultima del panel su entrambi gli indicatori, e al 2024 il segno non cambia
(−4,1 punti dalla Sicilia sul diploma 25-49, sezione 2.2).
→ `edu_historical_benchmarks_2011.csv`

**Il collo di bottiglia, quindi, non è la scolarizzazione di base, che tiene. È tutto ciò
che viene dopo: la scala dei titoli, che a Bagheria si ferma presto, e la conversione in
lavoro, che non arriva nemmeno per i titoli che ci sono.** Le due letture non si sommano in
una catena individuale, perché l'incrocio sulla persona non esiste: restano due misure
aggregate dello stesso territorio.

La versione individuale della domanda resta la più importante per il territorio. Per
questo la proposta la trasforma in un output: il dataset di servizio della sezione 7.5
misura per la prima volta a Bagheria, sulla singola persona, la sequenza titolo → azione →
esito.

---

## 5. Il pendolarismo verso Palermo: una sola destinazione, e un divario di genere che si apre col lavoro

Il pendolarismo verso Palermo è il terzo focus del bando. Il censimento permanente lo
pubblica a livello comunale solo come dentro/fuori comune: la dimensione `LOC_DEST` del
dataflow distingue solo lo stesso comune da un altro comune, quindi non dice dove si va. La destinazione la
danno le *matrici del pendolarismo* di ISTAT, che riportano i flussi origine-destinazione
comune per comune, con sesso, motivo, mezzo, fascia oraria e durata. Esistono per i
censimenti 1991/2001/2011 e, per il solo lavoro, per il censimento permanente 2021.
→ `notebooks/mobilita.ipynb`, `docs/sources.md` §12

Il tracciato dei file è a campi fissi e senza intestazione, quindi un campo sfalsato
darebbe numeri plausibili e sbagliati. Per escluderlo, dalla matrice si **ricostruiscono
sette indicatori `M` di 8milaCensus già pubblicati**. Tutti e sette coincidono alla prima
cifra decimale: `M3` 76,1 · `M4` 19,6 · `M5` 65,2 · `M6` 8,4 · `M7` 25,7 · `M8` 83,3 · `M9` 3,6.
Anche i totali nazionali del 2011 e del 2021 coincidono con quelli dichiarati da ISTAT. Il
controllo mostra inoltre che la matrice **non è una fonte alternativa a 8milaCensus, ma il
livello sottostante** da cui quegli indicatori sono calcolati: un punto utile rispetto al
vincolo sulle fonti posto dal bando. → sezione «La fonte, e come si controlla che sia letta
bene» di `notebooks/mobilita.ipynb`

### 5.1 La destinazione ha un nome, ed è una sola

| Fra chi esce dal comune, quanti vanno a Palermo | quota | percentile sui 381 comuni non capoluogo |
|---|---:|---|
| **per studio**, 2011 | **91,1%** | 97° |
| **per lavoro**, 2011 | **67,5%** | 93° |
| **per lavoro**, 2021 | **65,1%** | 94° |

Il secondo comune di destinazione per lavoro è Santa Flavia, con il 6,8% nel 2011: **non
esiste una seconda direzione**. Il percentile è calcolato su una misura comparabile fra
comuni, la quota di chi esce diretta al *proprio* capoluogo di provincia. Per un comune del
Ragusano, infatti, «quanti vanno a Palermo» è zero per costruzione. → sezione 2 di
`notebooks/mobilita.ipynb`, `mob_flussi_bagheria.csv`, fig `mob_fig01`

Una destinazione unica rende la mobilità una leva di policy, non un dettaglio descrittivo:
non c'è da scegliere quale destinazione servire.

### 5.2 Il ribaltamento: lo scarto di genere cambia segno col motivo

La misura è la quota di chi **esce dal comune** sul totale di chi si sposta ogni giorno per
quel motivo, distinta per genere. Il denominatore è già condizionato al motivo: chi si
sposta per lavoro un lavoro ce l'ha. Lo scarto di genere è quindi **compatibile** con il
divario occupazionale della sezione 3, non una sua conferma indipendente. Se chi non può
spostarsi non lavora, le occupate sono per costruzione quelle con un lavoro vicino. Il
conteggio del 2011, infine, **non è una stima**: i record di tipo `S` sono un'enumerazione
esaustiva.

| Quota che esce dal comune, 2011, scarto F − M | Bagheria | Sicilia | Italia | Comune di Palermo |
|---|---:|---:|---:|---:|
| **per studio** | **+2,6** | +1,4 | +1,8 | −0,1 |
| **per lavoro** | **−12,1** | −4,6 | −4,8 | −2,0 |
| **il salto fra i due** | **14,7** | 6,0 | 6,5 | 1,9 |

→ `mob_ribaltamento.csv`, `mob_ribaltamento_territori.csv`, fig `mob_fig02`

Il cambio di verso col motivo non è solo di Bagheria: c'è anche in Sicilia e in Italia,
mentre a Palermo città i due scarti sono entrambi negativi e quasi nulli. La particolarità
di Bagheria è **l'ampiezza**: un salto due volte e mezza quello siciliano, e sul lavoro il
**15° percentile** dei comuni siciliani (14° al netto di taglia e distanza dal capoluogo).
⚠️ La fonte non ha l'età. Sullo studio pesano i giovani, sul lavoro gli adulti fino a 64
anni: il ribaltamento confronta quindi due popolazioni diverse, non il passaggio di vita
delle stesse ragazze. Il vantaggio femminile sullo studio, inoltre, è in parte meccanico:
più ragazze all'università, che è a Palermo.

**Il risultato si replica su una fonte diversa.** Sul censimento permanente 2018-2019, cioè
su un'altra rilevazione, con un altro metodo e sette anni dopo, lo stesso salto fra studio e
lavoro vale a Bagheria 11,3 e 10,9 punti. In Sicilia vale 5,6 e 5,9, in Italia 6,5 e 6,1.
Il salto è compatibile con la forbice della sezione 3.1 e viene da una terza tavola;
senza l'età, però, non colloca il passaggio nella vita delle stesse persone.
→ `genere_pendolarismo.csv`, fig12

### 5.3 «Bagheria si muove poco» è una lettura sbagliata di un numero giusto

A una prima lettura, gli indicatori 2011 dicono che Bagheria si muove poco: la mobilità
fuori comune (`M2`) è al 25° percentile dei 390 comuni. **Il percentile è esatto, la
lettura no.** `M2` rapporta chi esce all'intera popolazione fino a 64 anni, quindi è basso
anche perché a Bagheria lavorano in pochi. Inoltre si va fuori comune per mancanza di
lavoro dentro, e Bagheria è il comune più grande della corona di Palermo. Nel 2021 conta
quasi 12.000 pendolari per lavoro contro i circa 3.200 di Ficarazzi, che infatti manda
fuori tre pendolari su quattro, contro i due su cinque di Bagheria.

Controllando per **distanza dal capoluogo e dimensione**, due variabili geografiche e non
di comportamento, il residuo di Bagheria sulla quota di chi esce per lavoro nel 2021 è di
**−1,9 punti** (z = −0,13). Fra i 381 comuni non capoluogo il percentile passa dal 36°
grezzo al **48°**. Bagheria si muove esattamente quanto ci si aspetta da un comune della
sua taglia a quella distanza. → sezione 3 di `notebooks/mobilita.ipynb`,
`mob_taglia_distanza.csv`, fig `mob_fig04`

Lo stesso vale per la mobilità studentesca `M4`, al 18° percentile. Già la versione
precedente dell'analisi segnalava che non è di per sé un dato negativo: l'indicatore è un
rapporto fuori/dentro comune, e Bagheria ha scuole proprie (3 sedi tecniche, anagrafe MIUR).
Sulla quota di studenti che escono dal comune (2011), lo stesso modello di distanza e
taglia dà un residuo di −0,8 punti. → sezione 3 di `notebooks/mobilita.ipynb`,
`edu_technical_schools.csv`

**La particolarità di Bagheria non è quanto si muove. È chi si muove, e per quale motivo.**

### 5.4 Il treno è il canale femminile, e il vincolo non è l'offerta di trasporto

Mezzo, orario e durata sono rilevati su campione nei comuni sopra i 20.000 abitanti. Sono
quindi stime, e per questo stanno in una tabella separata dai conteggi esaustivi. La loro
precisione è misurata, non assunta: per gli stessi strati esistono sia il conteggio
esaustivo sia la stima. L'errore relativo è dello **0,9%** in mediana e arriva al massimo
all'8,6% sullo strato più piccolo. Le quote qui sotto sono inoltre **calibrate sui margini
esatti** dei conteggi esaustivi. La calibrazione non cambia la conclusione, la rafforza: lo
scarto di genere sul treno passa da 14,5 a 15,1 punti.

| Fra chi esce da Bagheria (2011) | donne | uomini |
|---|---:|---:|
| mezzo collettivo | **34,7%** | 18,9% |
| di cui treno | **31,5%** | 16,4% |
| mezzo privato a motore | 63,6% | **79,0%** |

→ `mob_mezzo_genere.csv`, fig `mob_fig03`

Il mezzo privato resta il primo per entrambi i generi, ma il **mezzo collettivo** pesa fra
le donne quasi il doppio che fra gli uomini, e il treno da solo porta quasi un terzo delle
donne che escono. Fra chi va a lavorare a Palermo, a circa 18 chilometri, le donne partono più
tardi: esce prima delle 7:15 il 54,4% di loro, contro il 65,0% degli uomini. Fra tutti
quelli che escono dal comune, le donne viaggiano anche più a lungo: 31-60 minuti per il
43,8%, contro il 36,1% degli uomini. → sezione 6 («Quando si parte») di
`notebooks/mobilita.ipynb`

**Il treno di Bagheria, però, non è sottoutilizzato: è già l'asset di mobilità più
distintivo del comune.** Bagheria è al 98° percentile siciliano per quota di chi esce che lo
usa (97° a parità di distanza e taglia). Aumentarne l'uso non è la leva che manca.

> **Un risultato negativo, riportato perché è stato testato.** L'ipotesi naturale è che
> dove il mezzo collettivo pesa di più il divario di genere sia più piccolo. Sui 381 comuni
> non capoluogo l'ipotesi **non trova sostegno**. Fra quota d'uso del mezzo collettivo e
> divario di genere il rho di Spearman è −0,10 (p = 0,06), cioè di segno opposto
> all'ipotesi, e il quartile con più mezzo collettivo ha il divario più ampio. Sul treno
> l'associazione è nulla (p = 0,29). Coerentemente, l'ultimo miglio a Palermo non è un collo
> di bottiglia. Secondo il GTFS di AMAT, la terza fonte indicata dal bando, le fermate
> «Stazione Centrale» hanno 18 linee e, fra le 7 e le 21, non meno di 125 passaggi l'ora,
> già nel servizio estivo ridotto del feed di agosto.
>
> **Conseguenza di progettazione.** L'assenza di un'associazione fra comuni non esclude che
> l'orario o il mezzo pesino sulla singola persona, ma toglie la base a un intervento
> infrastrutturale. La proposta quindi non finanzia trasporto. Verifica la raggiungibilità
> caso per caso (sezione 7.6, F2) e agisce sul passaggio studio→lavoro, dove il divario si
> apre: è la finestra B di Ponte 19 (sezione 7).

### 5.5 Il bersaglio, in persone

Portare le pendolari di Bagheria al divario **medio siciliano**, cioè al semplice
comportamento regionale e non alla parità, vale **+279 donne** che lavorano fuori comune.
La parità piena con gli uomini di Bagheria ne varrebbe 449. Il conto è sul 2011 e su tutte
le età: dà la scala del fenomeno, non un obiettivo per la fascia giovanile.
→ `mob_sintesi.csv`

**Le misure sul pendolarismo hanno cinque limiti.**

1. **Nessuna età.** Né la matrice né la tavola del censimento permanente hanno la dimensione
   età. È verificato: `AGE_NOCLASS` è servita solo come `TOTAL`, anche a livello
   nazionale. Il target 15-34 del bando **non è isolabile sul pendolarismo**. Il motivo
   dello spostamento dà un'informazione d'età parziale, da usare come tale: chi esce per
   studio frequenta quasi solo la secondaria superiore o l'università, perché i cicli
   precedenti a Bagheria ci sono tutti.
2. **Nessun livello in serie fra 2011 e 2021.** Il 2011 conta chi si sposta
   *giornalmente*, il 2021 chi si reca al lavoro *almeno tre giorni a settimana*. Il 2021,
   inoltre, copre il solo lavoro e non ha il sesso. Si confronta quindi la composizione
   (dove vanno, su cento che escono), mai il livello. La colonna `definizione` della
   tabella riporta la definizione riga per riga.
3. **Nessun dato sul rientro.** Si conosce solo l'orario di uscita di casa. Che le donne
   partano più tardi e viaggino più a lungo è un fatto; che dipenda dal carico di cura resta
   un'ipotesi.
4. **Correlazioni ecologiche.** Sui 390 comuni la mobilità fuori comune correla con
   l'occupazione femminile (Spearman +0,32): il dato orienta l'ipotesi, non la dimostra, ed
   è in parte meccanico, perché dove si lavora di più ci si sposta di più. L'`R²` dei
   modelli sui divari di genere, inoltre, è vicino a zero: lì «atteso» vuol dire poco più
   di «media siciliana». → sezione «La nuvola dei 390» di `notebooks/genere.ipynb`,
   `genere_mobilita_2011.csv`
5. **Palermo non è un termine di paragone su questa misura.** È un comune grande, e per
   costruzione compare con valori bassissimi.

---

## 6. Il denominatore si muove: la platea giovane si restringe

La «fuga di talenti» del bando si misura con la ritenzione di coorte (sezione 3.3). Questa
sezione guarda a un'altra conseguenza, che vale per qualunque obiettivo: la platea giovane
si restringe, e con essa il denominatore di ogni tasso di questa relazione.

La popolazione 15-34 passa da **12.174 (2021) a 11.861 (2024)**: −313 persone, −2,6% in
tre anni. Ma 266 di quelle 313 persone sono **ricambio d'età**: le coorti che compiono 15
anni sono più piccole di quelle che superano i 34. Dentro le stesse coorti il saldo è di
−47 persone, −0,39%, come in Sicilia (−0,38%). Sull'insieme dei 15-34, quindi, Bagheria
non perde più della regione: la perdita si concentra all'uscita dal percorso formativo
(sezione 3.3). → `analisi_popolazione_giovane.csv`, `genere_stock_coorti.csv`

Il ricambio dall'estero è debole: gli stranieri sono l'**1,6% del 15-34** (195 persone),
contro il 5,1% a Palermo, il 6,4% in Sicilia e il 12,4% in Italia. → `genere_stranieri.csv`

Chi avrà 15-24 anni nel 2029 e nel 2034 **è già nato**: la platea futura si conta oggi sui
residenti di 10-19 e 5-14 anni. Non è una proiezione demografica, ma il conto di chi è già
residente a migrazioni nulle; le partenze e gli arrivi dei prossimi anni lo sposteranno. Le
ragazze passano da 2.882 (2024) a 2.651 (2029, −8,0%) e a **2.435 (2034, −15,5%)**; i
ragazzi calano del 2,5% e del 5,8%. Nei territori di confronto il calo è simile fra i
generi, anzi un po' più forte fra i maschi; a Bagheria pesa soprattutto sulle ragazze.
→ `genere_platea.csv`

⚠️ L'asimmetria nasce da una sex ratio 5-14 anomala: 117 maschi per 100 femmine, contro
104-106 dei benchmark. Il valore è in salita dal 2011 ed è identico su due tavole
indipendenti. Il meccanismo resta aperto, e il dato si cita solo insieme al suo audit.
→ `genere_sex_ratio_5_14.csv`

La conseguenza per qualunque intervento è aritmetica, ed è il secondo pilastro della
proposta. Al tasso obiettivo di Palermo (9,59%), l'equivalente di «+40 occupate» misurato
sulla platea di ciascun anno vale **+18,2 nel 2029 e −2,5 nel 2034** (lordo +40,4; attrito
demografico −22,2 e −42,9). Un obiettivo scritto in teste si annulla da solo, senza che
nessuno abbia sbagliato nulla. **Il KPI va scritto in tasso.**
→ `genere_kpi_netto.csv` (fig09; ⚠️ da non confondere con lo scenario «non si fa
niente», −19/−37 a tasso 2024 costante: `genere_tetto_platea.csv`)

---

## 7. Dall'evidenza alla proposta: Ponte 19

La proposta completa, con modello operativo, decision gate e disegno di valutazione, sta in
`docs/policy/POLICY_PONTE_19.md`. Questa sezione ne ricostruisce la derivazione
dall'evidenza, nel formato fissato dal progetto: **evidenza → intervento → target → KPI**.

| | |
|---|---|
| **Evidenza** | Il 70,6% dei 15-24enni fuori da lavoro e studio non cerca lavoro (sez. 2.1). La conversione dei titoli in lavoro fallisce soprattutto sulle ragazze, e dopo i 25 anni il deficit di occupazione diventa femminile anche per la generazione giovane (sez. 3.1 e 3.1-bis). Le coorti si perdono all'uscita dal percorso formativo (sez. 3.3). Il pendolarismo ha lo stesso segno: le ragazze escono dal comune per studiare più dei coetanei (+2,6 punti), le donne escono per lavorare 12,1 punti meno degli uomini (sez. 5.2). La platea si restringe (sez. 6) |
| **Intervento** | **Ponte 19**: servizio comunale di transizione e riattivazione, con outreach attivo (non a domanda spontanea) e due finestre di ingaggio |
| **Target** | Finestra A: 18-20enni all'uscita dalla scuola o entro 30 giorni dall'interruzione. Finestra B: 22-25enni fuori da lavoro e studio. Le finestre sono i momenti dell'outreach, non requisiti d'accesso: chi ha 21 anni entra su segnalazione o richiesta. Quota di genere ≥50% F sui presi in carico. Capacità pilota: 200 persone l'anno, pari a ~18% dei 1.121 inattivi non studenti 15-24 (platea indicativa: il censimento non dà la fascia 18-25) |
| **KPI** | In **tasso**, con finestra di lettura dichiarata (sez. 7.4) |

Il servizio parte da 18 anni perché fino ai 18 vale il diritto-dovere all'istruzione e alla
formazione. Si ferma a 25 perché le finestre devono intercettare le uscite prima che si
compiano: nel triennio la coorte femminile si riduce fra i 25 e i 28 anni, e a cinque anni
entrambi i generi perdono nel passaggio da 20-24 a 25-29 (sezione 3.3). Fra le due
finestre resta il 21. A quell'età nessuno dei due generi perde residenti netti (sezione
3.3), quindi il servizio non ha un canale di ricerca dedicato; chi ha 21 anni ed è fuori da
lavoro e studio è comunque preso in carico, e si conta a parte fra gli indicatori di
processo. I 26-34enni del bando restano fuori dal target per una ragione di misura:
nessuna tavola comunale permette di seguirne la condizione professionale, perché la classe
25-49 non è scomponibile. Il deficit femminile più grande, però, sta sopra i 25 anni
(sezione 3.1-bis). Estendere il modulo di genere ai 26-34 è quindi un'opzione dichiarata,
ancora da decidere e misurabile solo sul dato di servizio.

### 7.0 Perché non è un intervento sui trasporti

Chi legge la sezione 5 si pone subito una domanda: se il mezzo collettivo verso Palermo
pesa tanto per le donne, perché non intervenire lì? Perché **i dati non lo sostengono**, per due
ragioni indipendenti. La prima: il treno di Bagheria è già al 98° percentile siciliano per
uso (sezione 5.4), quindi non c'è un'infrastruttura sottoutilizzata da attivare. La
seconda: sui 381 comuni non capoluogo una quota maggiore di mezzo collettivo **non** si
accompagna a un divario di genere più piccolo. L'associazione non trova sostegno
(p = 0,06), e la stima ha il segno opposto all'ipotesi.

Resta un vincolo operativo che il servizio deve rispettare. Fra chi esce da Bagheria, il
mezzo collettivo porta il 34,7% delle donne e il 18,9% degli uomini; il mezzo privato a
motore, il 79,0% degli uomini. **Un servizio che dia per scontata l'auto seleziona per
genere**, e
seleziona proprio contro la metà che la quota di genere vuole raggiungere (sezione 7.2).
Orari di convocazione, tirocini e sedi vanno quindi scelti fra ciò che è raggiungibile in
treno e in autobus, e la raggiungibilità va misurata, non assunta.

### 7.1 Perché due finestre

Le uscite hanno due tempi (sezione 3.3). Il primo è la fine della scuola. Il secondo è la
fine del percorso formativo, fra i 20 e i 29 anni. Lì le coorti di entrambi i generi si
riducono 9-12 punti più che in Italia, e lì il deficit di occupazione diventa femminile
(sezione 3.1-bis). Una sola finestra 18-20 mancherebbe questo secondo passaggio. La
finestra B esiste per coprirlo, e la quota di genere (sezione 7.2) la orienta verso le
ragazze.

### 7.2 Perché la quota di genere

Il gruppo da raggiungere è femminile al 51% nelle dimensioni, ma radicalmente diverso per
genere nell'etichetta (sezione 3.2). Un servizio formalmente neutro, con i canali di
contatto standard, riprodurrebbe l'asimmetria che deve correggere. La quota obbliga a
costruire i due agganci, senza escludere nessuno.

### 7.3 Perché l'outreach e non lo sportello

Sette giovani su dieci fuori da lavoro e studio non cercano lavoro. A definizione costante
(2021-2024) quel segmento è fermo, mentre chi cerca diminuisce (sezione 2.2). Un servizio a
domanda spontanea raggiunge per costruzione chi già cerca, cioè il segmento sbagliato. Per
le ragazze, inoltre, l'aggancio è l'**attivazione**, non la sola conciliazione: almeno l'89%
delle casalinghe non è sposata (sezione 3.2).

### 7.4 I KPI e le loro finestre di lettura

| KPI primario | Da | A | Lettura |
|---|---:|---:|---|
| Tasso di occupazione F 15-24 | 8,2% | 9,6% (Palermo) | **triennio pooled**, come direzione (potenza 41%) |
| Quota casalinghe F 15-24 | 13,4% | 11,3% (Palermo) | biennio (potenza 82%) |

**I KPI di popolazione dicono la direzione, non provano l'effetto.** La potenza è stata
misurata con due metri. Il modello binomiale tratta ogni annata come un campione
indipendente e promette che un triennio basti: 46% su un anno, 90% sul triennio. Le annate
però contano le stesse persone, e per questo serve un secondo metro: la variabilità che il
tasso mostra senza alcun intervento. Misurata nei 33 comuni siciliani di taglia simile a
Bagheria, dice altro: per +1,4 punti di occupazione la potenza è del 50% su un anno, del
59% sul biennio e del 41% sul triennio. Il triennio, nei dati disponibili, attraversa la
rottura di misura del 2021, quindi quel 41% è probabilmente pessimistico: le letture future
staranno tutte dopo la rottura. Resta la finestra dichiarata perché su questo KPI si legge
solo la direzione, e il triennio è quella in cui il rumore di conteggio pesa meno. Sulle
casalinghe (−2,1 punti) il biennio arriva all'82%.

La differenza fra i due metri sta nella struttura della variabilità. Da un anno all'altro
il tasso di occupazione di un comune oscilla attorno alla propria tendenza meno di un campione (0,36 volte
la varianza binomiale). I comuni però divergono fra loro in modo persistente, e accorpare
più anni non elimina quella divergenza.

Le finestre di lettura sono dichiarate prima dell'avvio, per non sceglierle a posteriori.
La lettura annuale non è ammessa: l'anno singolo spetta agli indicatori di processo, cioè
contatti entro 30 giorni, piani entro 15, utenza per età singola e genere confrontata con
la platea residente. Oggi nessuno li rileva; li produce il servizio. → `genere_mde.csv` (fig09b)

Il KPI deve portarsi dietro due precisazioni.

La prima riguarda il controfattuale. Il tasso femminile di Bagheria sale già da solo (+0,65
punti l'anno dal 2018) e, al ritmo attuale, toccherebbe il 9,6% in un paio d'anni. Il
successo quindi non è raggiungere quel livello, ma **chiudere lo scarto da Palermo** (oggi
−1,4 punti), dove il tasso sale anch'esso. Il KPI si legge come differenza nelle differenze
rispetto al controfattuale, non come soglia.

La seconda riguarda la scala: 40 occupate in più su una platea di 2.882 non si ottengono con
100 prese in carico l'anno, perché servirebbe un effetto netto irrealistico. Il tasso
comunale è quindi l'orizzonte di convergenza e il contesto della valutazione. L'effetto del
servizio si misura invece sui partecipanti, confrontandoli con chi entra più tardi (si veda
più avanti). I dati comunali, infine, escono con circa due anni di ritardo: un triennio
pooled si legge quattro o cinque anni dopo l'avvio.

Se la comunicazione pubblica richiede un equivalente in teste, si scrive: «+40 occupate
sulla platea 2024; il target si riparametra ogni anno come tasso-obiettivo × platea
dell'anno». La formula si pubblica insieme al numero (sezione 6).

La valutazione ha due livelli.

**Sui presi in carico** si usa un rollout scaglionato: a parità di priorità l'ordine di
avvio è casuale, e chi comincia più tardi fa da confronto. Perché il confronto esista
servono due coorti da 100, con ingresso al mese 0 e al mese 6. Il primo contatto entro 30
giorni vale per tutti: chi è assegnato alla seconda coorte riceve il colloquio e
l'indirizzamento alle misure esistenti, e comincia il percorso al mese 6. Il confronto
esiste quindi sull'esito a sei mesi, non su quello a dodici. Con 100
persone per coorte il confronto vede effetti di 18-20 punti o più (17,8 se l'esito senza
servizio è del 20%, 19,7 se è del 40%); con adesioni dimezzate la soglia sale a 26-28 punti.
Se le domande non superano i posti, il sorteggio non c'è e la valutazione diventa
descrittiva.

Le rassegne sui programmi attivi per il lavoro (Card, Kluve e Weber, *Journal of the
European Economic Association*, 2018) trovano effetti medi vicini a zero nel breve periodo.
Gli effetti diventano più positivi due-tre anni dopo la fine del programma, e sono più
grandi per le donne. A sei mesi, quindi, un confronto non significativo è l'esito atteso
anche per un servizio che funziona.
→ `genere_potenza_pilota.csv`

**Sui KPI di popolazione** il confronto è con un controfattuale **dichiarato in anticipo:
Palermo**. Il prerequisito è stato controllato. La pendenza del tasso femminile di Bagheria
nel 2018-2024 (+0,65 punti/anno) non si distingue da quelle di Palermo e dell'Italia (p =
0,29 / 0,33; la Sicilia è al margine, p = 0,054). Con sei annate il test ha poca potenza, quindi non prova tendenze parallele:
dice solo che i dati non le smentiscono.

Il test, inoltre, tratta ogni annata come un campione indipendente. Senza quel modello, la
distanza fra la pendenza di Bagheria e quella di Palermo (−0,09 punti l'anno) è più piccola
di quella del 67% dei comuni di taglia simile. Il confronto è indulgente, perché include le
divergenze reali fra comuni. Resta un limite: con un solo comune di confronto, uno shock
proprio di Bagheria o di Palermo non si separa dall'effetto. Il confronto si fa quindi anche
con un controllo sintetico costruito sui 33 comuni di taglia simile, con test placebo sugli
stessi comuni; Palermo resta il riferimento dichiarato. → `genere_pretrend.csv`,
`genere_pretrend_390.csv`

Il costo della dotazione minima, in ordine di grandezza, è fra 205.924 e 256.105 euro l'anno,
cioè fra 1.030 e 1.281 euro per posto, esperienze retribuite escluse. Parametri e voci
escluse sono dettagliati nella policy, §9-bis. → `genere_costo_pilota.csv`

### 7.5 Il dato che il servizio produce

Ogni presa in carico genera un record pseudonimizzato: titolo e indirizzo di studio → data
di uscita → condizione → genere ed età → barriera dichiarata → azione → esito a 3/6/12
mesi. È l'unico modo per misurare a Bagheria la relazione individuale fra titolo e
condizione lavorativa (sezione 4). La proposta, quindi, non si limita a consumare dati: **ne
produce dove le statistiche pubbliche finiscono**. L'impegno di accountability è una
dashboard trimestrale aggregata.

### 7.6 Rotta F: il modulo di genere

La quota di genere (sezione 7.2) impedisce al servizio di riprodurre l'asimmetria che deve
correggere, ma **non dice come correggerla**. Lo dice `docs/policy/POLICY_PONTE_19.md`
§4-bis, la parte di Ponte 19 che risponde al focus principale del bando. Qui se ne riassume
l'ossatura: una relazione che mette il genere al centro non può rimandare altrove l'unico
pezzo di intervento costruito su di esso.

Il meccanismo sta in una riga: **le ragazze di Bagheria si spostano per studiare e si
fermano per lavorare**. Le sezioni 3 e 5 mostrano rotti tre anelli della catena: il
contatto, la barriera e la domanda. Il modulo apre una componente su ciascuno.

**F1. Contatto: l'etichetta come canale, non come elenco.** Le 387 casalinghe **non sono
identificabili**: il censimento è aggregato, e nessuna lista nominativa esiste né va
costruita. L'etichetta dice dove cercare, non chi. Il contatto passa quindi dai luoghi dove
quella popolazione è già visibile: le sedi secondarie cittadine, i servizi sociali, i
consultori, le associazioni. È la traccia femminile delle due tracce di contatto. Per le
ragazze esiste già un'etichetta censuaria da cui aprire il colloquio; per i ragazzi
un'etichetta così non c'è (sezione 3.2). Che cosa ci sia dietro l'etichetta lo chiede il
colloquio, perché il censimento non lo osserva.

**F2. Barriera: non il collegamento, ma l'orario e il mezzo dati per scontati.** È la
componente controintuitiva: qui la proposta rinuncia alla soluzione che tutti si aspettano.
L'intervento infrastrutturale non è sostenuto dai dati (sezione 7.0), quindi F2 non si
appoggia all'offerta di trasporto e non finanzia trasporto. Quello che resta di genere è il
canale: fra chi esce dal comune le donne usano il treno quasi il doppio degli uomini (31,5%
contro 16,4%, sezione 5.4). Un servizio che dia per scontata l'auto seleziona per genere, e
lo fa in silenzio. Ne discende una sola regola operativa: nessuna opportunità entra nel
piano di transizione senza **verifica di raggiungibilità col mezzo collettivo negli orari
reali della posizione**. Costa istruttoria, non budget.

**F3. Domanda: la leva che il Comune ha già in mano.** La componente introduce criteri
**premiali** di pari opportunità nelle gare e nelle concessioni comunali, per l'assunzione
di donne e di under 36. Il modello è l'art. 47 del DL 77/2021 (appalti PNRR); per le gare
ordinarie la base sta nelle clausole sociali del Codice dei contratti pubblici (D.Lgs.
36/2023), da verificare con l'ufficio gare. Si tratta di premialità, non di riserva né di
requisito di residenza: il radicamento locale dell'esito si misura a valle, non si impone in
gara. La verifica dell'esito a 6 e 12 mesi si concentra sulle **donne 22-25**. È l'unica
delle tre componenti che non richiede una struttura nuova: riorienta su un target
dichiarato uno strumento amministrativo esistente. Cautela: il volume è piccolo per
costruzione, e F3 rende la domanda **verificabile**, non la crea (sezioni 2.4 e 3.1).

**Target.** La platea sono le **573** ragazze 15-24 inattive e non studenti (sezione 3.2).
La presa in carico pilota è la metà dei 200 previsti, secondo la quota di genere (sezione
7). Si concentra sulla finestra prioritaria **22-25**, cioè l'uscita dal percorso formativo,
dove il vantaggio educativo dovrebbe convertirsi in lavoro (sezione 3.3). L'estensione ai
26-34 è un'opzione da decidere (sezioni 3.1-bis e 7).

**KPI.** Il KPI primario del modulo è la **quota di casalinghe 15-24** (13,4% verso l'11,3%
di Palermo), non il tasso di occupazione. La ragione è la finestra di lettura, non una
preferenza. Contro la variabilità dei comuni di taglia simile, è l'unico dei due che supera
l'80% di potenza su una finestra che non attraversa la rottura del 2021: il biennio. È
quindi il primo a restituire un verdetto, con il ritardo di circa due anni dei dati
comunali.

L'indicatore ha però due limiti. È una stima di modello (sezione 3.2): si legge solo dentro
la definizione 2021+ e sempre accanto al tasso di occupazione, che è un conteggio. Inoltre
si può muovere anche senza lavoro: fra le covariate del modello c'è la frequenza di un corso
di studio risultante dai registri, quindi un'iscrizione registrata sposta una ragazza fuori
da «casalinga». L'occupazione femminile resta l'esito che dà senso al primo indicatore, e si
legge sul triennio pooled, come direzione (sezione 7.4).

**Cosa il modulo non promette**, con lo stesso metro della sezione 9:

- non identifica le 387 casalinghe;
- non attribuisce la condizione di casalinga a una scelta né a un vincolo familiare
  osservato: lo stato civile esclude il matrimonio precoce come canale, ma non osserva
  convivenze né maternità;
- non propone interventi sul trasporto;
- non sostiene alcuna tesi di segregazione per indirizzo di studio, perché l'anagrafe MIUR
  dà le sedi e non gli iscritti per genere e indirizzo.

Quel dato non esiste. Senza di esso, «gli indirizzi femminili non convertono» resterebbe
un'ipotesi travestita da evidenza.

---

## 8. Le figure

Il bando chiede 2-3 visualizzazioni avanzate. La terna consegnata copre la voce obbligatoria
(profilo e benchmarking), il focus esplorativo scelto (il genere) e l'obiettivo del bando
(la fuga di talenti):

1. **`fig05_forbice`**: il paradosso in un'immagine. Mostra il quadrante «più istruite, meno
   occupate» sulla stessa fascia 15-24; la forbice nel tempo sta in `fig05b`.
2. **`fig07_ritenzione_eta`**: il *quando* della fuga. È il profilo di ritenzione per età
   singola, con la finestra 22-25. La differenza di genere è del triennio 2021-2024; su
   cinque anni la perdita riguarda entrambi i generi (sezione 3.3). La scala decennale sta in
   `fig07b`.
3. **`fig04_mappa_sicilia`**: la scala. Unisce la coropleta dei 390 comuni e l'istogramma
   delle due distribuzioni: «nel 2024 Bagheria arriva dove stava la mediana siciliana nel
   2011». La persistenza della graduatoria (rho di Spearman) sta in `fig04b`.

Il criterio di scelta è dichiarato perché sia contestabile. La `fig04` mette Bagheria fra
390 comuni invece di trattarla come un caso isolato. La `fig05` porta il focus scelto al suo
punto più netto. La `fig07` è la figura che dice, età per età, **quando** si parte, ed è la
ragione per cui Ponte 19 ha due finestre.

Tre figure fanno da supporto. **`fig09_kpi_finestra`** traduce il KPI in persone e lo mette
di fronte al restringimento della platea (sezione 6). **`fig09b_potenza`** dichiara quanto
il tasso comunale può dire sull'intervento, con due metri di potenza affiancati (sezione
7.4). **`fig13b_occupazione_eta_genere`** mostra, per classe d'età e genere, il deficit
femminile che si apre dopo i 25 anni (sezione 3.1-bis).

Il terzo focus del bando ha una serie propria, aggiunta con il thread mobilità:

- **`mob_fig01_verso_palermo`**: la carta a flussi. Mostra dove vanno i pendolari di
  Bagheria, per studio e per lavoro, con il nome del comune di arrivo. È la risposta
  letterale alla domanda del bando, ed è la **prima riserva** della terna. Resta fuori per
  due ragioni: `fig04` è già una carta, e togliere `fig07` lascerebbe la finestra d'età
  della proposta senza la figura che la giustifica.
- **`mob_fig02_ribaltamento`**: il risultato del thread. Le due misure sono unite da una
  linea la cui pendenza è il risultato; accanto, la distribuzione dei 390 comuni.
- **`mob_fig03_treno_genere`**: mezzo e orario per genere, più il pannello che impedisce di
  leggere la figura come «serve più treno».
- **`mob_fig04_taglia_distanza`**: la figura che toglie di mezzo un'affermazione invece di
  aggiungerne una. Il basso percentile della mobilità fuori comune era un effetto di
  taglia e distanza.

**`fig12_pendolarismo`** resta come lettura sul censimento permanente 2018-2019: è la
replica indipendente della sezione 5.2. Le altre figure stanno nei notebook come apparato.

Tutte le figure hanno un titolo che enuncia il risultato, la fascia d'età dichiarata, fonte
e cautele in didascalia e una palette colorblind-safe. Sono esportate in PNG a 300 dpi e in
SVG in `figures/`.

---

## 9. Cosa questa relazione non afferma

1. **Il NEET 15-34 comunale non esiste** nei dati pubblici. Le due misure usate, il NEET
   15-29 al 2011 e la quota «fuori da lavoro e studio» 15-24 dal 2018, sono etichettate e
   mai fuse.
2. **Nessun tasso di occupazione per titolo di studio a Bagheria**: l'incrocio individuale
   non è pubblicato (sezione 4), quindi ogni affermazione del tipo «i diplomati di
   Bagheria…» sarebbe inventata.
3. **Nessuna età sul pendolarismo**: la matrice ISTAT dà la destinazione (sezione 5), ma né
   la matrice né il censimento permanente hanno la dimensione età. Il pendolarismo del
   target 15-34 non è quindi isolabile. Il motivo dello spostamento è un'informazione d'età
   parziale, e viene usata come tale. La ritenzione di coorte resta un saldo netto senza
   destinazioni, e le due misure non si sommano.
4. **Nessuna stima causale**: i confronti territoriali ed ecologici orientano la diagnosi, e
   il disegno di valutazione (sezione 7.4) serve a produrre l'evidenza che oggi manca.
   L'inattività non è attribuita a una singola causa non osservata.
5. **Nessuna interpolazione**: il 2020 mancante resta mancante, e la rottura di misura
   2019→2021 è dichiarata ogni volta che si cita la serie delle componenti.
6. **La finestra 22-25 è pooled**: sull'anno singolo oscilla, e per questo non si usa come
   lettura annuale.
7. **Nessuna associazione fra uso del mezzo collettivo e divario di genere**: è stata
   testata sui 381 comuni non capoluogo e **non è stata trovata** (sezione 5.4). È un
   risultato ecologico: non esclude un effetto sulla singola persona, ma nessuna parte della
   proposta si appoggia all'offerta di trasporto.
8. **Nessun primato sui titoli**: Bagheria non produce più istruzione dei territori di
   confronto. Sta davanti a Palermo e alla Sicilia solo sulla competenza di base del 2011
   (`I8`), comunque dietro l'Italia, ed è ultima del
   panel su diploma o laurea (`I6`) e su titolo universitario (`I7`). Ciò che si afferma è
   la mancata conversione, non un surplus di titoli da convertire (sezione 4).
9. **Nessuna misura diretta dell'emigrazione, né per titolo di studio**: la ritenzione di
   coorte è un saldo netto fra partenze e arrivi, senza destinazione e senza titolo. Sul
   totale dei 15-34, a parità di coorti, Bagheria perde quanto la Sicilia. La «fuga di
   talenti» che questa relazione documenta è quindi una perdita all'uscita dal percorso
   formativo, per entrambi i generi, non un'emorragia complessiva (sezioni 3.3 e 6). Il dato
   diretto esiste alla fonte, ma non è pubblicato per il comune. I trasferimenti di
   residenza sono rilevati comune per comune; ISTAT ne pubblica età e titolo di studio solo
   fino alla provincia, e per Bagheria solo i totali per sesso, verso un altro comune o
   verso l'estero. I dati elementari, anonimi, si possono chiedere a ISTAT.
10. **Le condizioni non professionali sono stime, non conteggi**: dal 2021 casalinghe,
   studenti, chi cerca lavoro e la platea degli inattivi non studenti sono somme di
   probabilità di un modello ISTAT, di cui non è pubblicato l'errore (sezione 3.2). Si
   leggono solo dal 2021, e sempre accanto al tasso di occupazione, che è un conteggio.
11. **Il tasso comunale non prova l'effetto del servizio**: contro la variabilità dei comuni
   di taglia simile, nessuna finestra di lettura arriva all'80% di potenza sul tasso di
   occupazione femminile (sezione 7.4). L'effetto si misura sui partecipanti, e nel primo
   anno il pilota vede solo effetti grandi.
12. **Il 25-49 non è una misura dei giovani**: serve solo a testare che cosa succede dopo la
   fascia target (sezione 3.1-bis). Il 26-34 resta non isolabile, e il test sulle
   generazioni non separa l'età dalla coorte.

---

## Appendice A - Mappa dei file

| Deliverable | File |
|---|---|
| Notebook condiviso (definizioni, popolazione, condizione 15-24) | `notebooks/analisi.ipynb` |
| Thread genere (focus principale) | `notebooks/genere.ipynb` |
| Thread educazione (transizione istruzione→lavoro) | `notebooks/educazione.ipynb` |
| Thread mobilità (pendolarismo verso Palermo) | `notebooks/mobilita.ipynb` |
| Policy proposal unificata | `docs/policy/POLICY_PONTE_19.md` |
| Documento di lavoro: tesi, scelta delle figure, limiti | `docs/team/SCELTE_ANALITICHE.md` |
| Provenance delle fonti (URL, date, query, trappole) | `docs/sources.md` |
| Figure (PNG 300dpi + SVG) | `figures/` |
| Interfaccia dati Python→R | `data/processed/` |

Stato delle verifiche al 2026-09-24. Il sensore `nbconvert` è **verde sui quattro notebook**
e `pipeline.verifica` dà **1005/1005 PASS**. La matrice del pendolarismo ricostruisce **sette
su sette** gli indicatori `M` pubblicati da 8milaCensus e i due totali nazionali dichiarati
da ISTAT. Nessun numero di questa relazione è scritto a mano: ogni cifra ha accanto il file
o la cella che la rigenera.


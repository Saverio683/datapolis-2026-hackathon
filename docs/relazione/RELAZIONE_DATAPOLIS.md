# A Bagheria il diploma arriva, il lavoro no

## Relazione tecnica e proposta di intervento - DataPolis 2026, «Analisi e Visione per i Giovani di Bagheria»

Bagheria, 2026-08-29, versione rivista del 2026-09-23. Questa relazione accompagna i tre deliverable richiesti dal
concorso: il **technical notebook** (`notebooks/analisi.ipynb`, `notebooks/genere.ipynb`,
`notebooks/educazione.ipynb`, `notebooks/mobilita.ipynb`), le **visualizzazioni**
(`figures/`) e la **policy proposal** (`docs/policy/POLICY_PONTE_19.md`).

Regola che vale in ogni riga: **nessuna cifra è scritta a mano**. Ogni numero citato
punta alla cella di notebook o al file di `data/processed/` che lo produce, e si
rigenera eseguendo la pipeline (sezione 1). Dove un numero ha una cautela, la cautela
sta accanto al numero, non in fondo.

---

## In una pagina

> **A Bagheria il diploma arriva e il lavoro no. La conversione fallisce soprattutto sulle
> ragazze: più istruite dei coetanei, hanno un tasso di occupazione 15-24 dell'8,2%, il
> minimo dei quattro territori in 6 anni su 6. Dopo i 24 anni le ragazze cominciano a
> perdersi mentre i coetanei rientrano (la coorte femminile che nel 2021 aveva 25-29 anni ne
> conserva il 96,3% tre anni dopo, quella maschile il 101,2%), e anche il pendolarismo
> femminile si ferma al passaggio dallo studio al lavoro. Chi resta fuori non è chi cerca lavoro: dei 15-24enni fuori da
> lavoro e studio, il 70,6% non cerca nemmeno.**

I tre thread di analisi (genere, educazione, mobilità) non danno tre diagnosi diverse:
leggono **lo stesso passaggio, dalla formazione al lavoro, da tre tavole diverse**. Sono
misure aggregate sullo stesso territorio, non la traiettoria delle stesse persone
(l'incrocio individuale non è pubblicato, sezione 4), ma poiché vengono da fonti distinte
nessuna è la riformulazione di un'altra.

La proposta (sezione 7) è **Ponte 19**, un servizio comunale di transizione e
riattivazione per i 18-25enni, con due finestre di ingaggio e un target esplicito sul
genere. Il nome viene dall'età di uscita dalla scuola superiore, 19 anni; l'analisi ha
fatto emergere una seconda finestra, fra 22 e 25. E la proposta ha un vincolo di misura
che la distingue da un auspicio:

> **La platea femminile 15-24 cala del 15,5% entro il 2034, e chi ne farà parte è già nata.
> Portare il tasso di occupazione delle ragazze al livello di Palermo vale oggi 40 occupate
> in più; lo stesso obiettivo, misurato sulla platea del 2029 e del 2034, vale +18 e −2
> (fig09). Per questo il KPI si scrive in tasso, non in teste.**

### La risposta al brief, in breve

| Richiesta della locandina | Risposta | Dove |
|---|---|---|
| Profiling statistico & benchmarking (Sicilia, Italia, Palermo) | ✅ con intervalli di confidenza, percentili sui 390 comuni siciliani e due gruppi di comuni pari dichiarati | sezioni 2-3 |
| Focus: **impatto delle differenze di genere** | ✅ focus principale | sezione 3 |
| Focus: **titolo di studio × condizione lavorativa** | 🟡 l'incrocio non esiste nei dati comunali (verificato); risolto con due misure parallele sulla stessa fascia | sezione 4 |
| Focus: **pendolarismo verso Palermo** | ✅ misurato con la matrice origine-destinazione ISTAT: va a Palermo il **91,1%** di chi esce per studio (2011) e il **65,1%** di chi esce per lavoro (2021), e lo scarto di genere si ribalta fra i due motivi | sezione 5 |
| NEET 15-34 | 🟡 non calcolabile a livello comunale: due misure etichettate, mai fuse; il valore regionale della rilevazione forze di lavoro come riferimento | sezione 1.1 |
| Proposta di intervento | ✅ Ponte 19, con KPI misurabili e finestre di lettura dichiarate | sezione 7 |
| Technical notebook riproducibile | ✅ i quattro notebook rieseguiti da zero senza errori; controlli automatici tutti superati | sezione 1 |
| 2-3 data viz avanzate | ✅ tre figure principali + sei di supporto | sezione 8 |

I 🟡 non sono lavori a metà: sono i punti in cui i dati pubblici finiscono, dichiarati
invece che aggirati. In un concorso sulla cultura del dato, sapere dove i dati non
arrivano è parte della risposta, ed è uno dei motivi della proposta, che quei dati
mancanti li produce (sezione 7.5).

---

## 1. Metodo: la relazione si rigenera da zero

L'intera analisi è una pipeline riproducibile. Da ambiente pulito:

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

I dati grezzi sono già in `data/raw/`, quindi la ricetta gira senza rete (`pipeline.fetch`
serve solo ad aggiornarli, e scarica file nuovi datati al giorno del download). L'ordine non
è arbitrario: `genere.ipynb` legge tavole prodotte da `analisi.ipynb` e da `pipeline.edu`,
e `mobilita.ipynb` ne legge due prodotte da `genere.ipynb` (`genere_gap_persone.csv` e
`genere_pendolarismo.csv`).

Tre proprietà non decorative:

- **Provenance completa.** Ogni file in `data/raw/` è append-only e ha una riga in
  `docs/sources.md` con URL esatto, data e parametri. Le correzioni vivono in
  `pipeline/`, mai nei raw.
- **Verifica indipendente.** `pipeline/verifica.py` esegue **934 controlli automatici**:
  ricalcola i numeri chiave **direttamente dai raw con implementazioni alternative**
  (intervalli di Wilson/Newcombe riscritti, modello lineare di probabilità in forma
  analitica, matching rifatto, coorti dalle classi quinquennali, e un riparsing proprio
  della matrice del pendolarismo letta in streaming dagli zip), controlla che le tavole di
  `data/processed/` coincidano con quei ricalcoli e che le cifre scritte in questa
  relazione e nella policy compaiano alla lettera. Tutti superati. Se un raw cambia, il
  controllo fallisce finché notebook, tavole e testo non vengono riallineati.
- **Separazione dei ruoli.** Python trasforma, R disegna: l'interfaccia sono i CSV di
  `data/processed/`, e nessuna logica di trasformazione vive negli script delle figure.

### 1.1 Le definizioni, fissate una volta

- **Territori**: Bagheria (`082006`), Comune di Palermo (`082053`), Sicilia (`ITG1`),
  Italia (`IT`); più i **390 comuni siciliani** per i percentili e due gruppi di comuni
  pari (sezione 2.4).
- **Fasce d'età**: dipendono dal dominio, perché le fonti non danno il 15-34 ovunque.
  Lavoro e istruzione: **15-24** (unica classe giovanile comunale del censimento
  permanente); istruzione da tavola: **9-24** (fascia della fonte, sempre dichiarata);
  demografia: **15-34** esatto, dalle età singole. Ogni figura dichiara la fascia.
- **Anni**: censimento permanente 2018-2024 (il **2020 manca** sulla classe 15-24 ed è
  lasciato mancante, mai interpolato); 8milaCensus 1991/2001/2011 come fonte storica
  separata, sempre etichettata. Fra 2019 e 2021 c'è una **rottura di misura** sulla
  componente «in cerca di occupazione»: i gap fra territori restano confrontabili, i
  livelli delle componenti no (`docs/sources.md` §7).
- **NEET**: il NEET 15-34 della locandina **non è calcolabile a livello comunale** - la
  fascia non esiste nei dati. Si usano due misure etichettate e mai unite: il NEET
  **15-29 al 2011** (8milaCensus, `L4`) e il proxy **«fuori da lavoro e istruzione»
  15-24, 2018-2024** (censimento permanente). Fasce e definizioni diverse: affiancate,
  mai in serie. La cifra del bando esiste solo a scala regionale, nella rilevazione sulle
  forze di lavoro (fonte campionaria, definizione europea): nel 2024 il NEET 15-34 della
  Sicilia è al 30,1% (35,3% fra le donne, 25,2% fra gli uomini), contro il 17,3%
  dell'Italia. Sul 15-24 la stessa fonte dà 19,5% per la Sicilia, dove il proxy censuario dà
  22,3%: stesso ordine di grandezza, che fa da controllo esterno del proxy. Riferimento,
  non misura di Bagheria. → `genere_neet_rcfl.csv`
- **Percentili**: posizione di Bagheria fra i 390 comuni siciliani ordinati dal valore più
  basso al più alto (100° = valore più alto). Su occupazione, istruzione e mobilità un
  percentile alto è favorevole; su NEET, uscita precoce e disoccupazione è sfavorevole.
- **Scarti**: sono calcolati sui valori non arrotondati, quindi possono differire di un
  decimale dalla differenza fra le cifre stampate.

### 1.2 I dati disponibili: che cosa è stato scaricato, da dove, quando

Nessuna delle cifre di questa relazione nasce da una raccolta propria: tutte vengono da
statistica ufficiale pubblica, scaricata per via programmatica e conservata immutabile in
`data/raw/`, con un manifesto (`data/raw/manifest.csv`) che registra per ogni file
l'istante del download e l'URL esatto. Le fonti effettivamente entrate nell'analisi sono
sette, una delle quali (il GTFS di AMAT) usata solo come controllo; il portale open data
della Regione Siciliana è stato esplorato con esito negativo, dichiarato come tale.

| Fonte | Che cosa dà | Copertura | Ruolo |
|---|---|---|---|
| **ISTAT, 8milaCensus** (`ottomilacensus.istat.it`) | 99 indicatori comunali ai confini 2011, tutti i comuni siciliani più province, regioni e Italia | 1991, 2001, 2011 | Serie storica lunga, graduatorie, matching fra comuni pari |
| **ISTAT, Censimento permanente** (IstatData, API SDMX) | Condizione professionale, titolo di studio, popolazione per età singola, popolazione per classi quinquennali, pendolarismo dentro/fuori comune | 2018-2024 | Fotografia recente, serie annuale, tutti gli incroci di genere |
| **ISTAT, DCIS_POPRES1** (SDMX) | Popolazione residente per stato civile ed età singola | al 1.1.2025 | Verifica del canale «matrimonio precoce» (sezione 3.2) |
| **ISTAT, Matrici del pendolarismo** | Origine-destinazione comune per comune, con sesso, motivo, mezzo, fascia oraria e durata | 1991, 2001, 2011; solo lavoro nel 2021 | La destinazione degli spostamenti (sezione 5) |
| **ISTAT, Confini amministrativi** (cartografia) | Poligoni dei comuni, vintage 01/01/2026 | corrente | Base geografica delle mappe e delle distanze |
| **Ministero dell'Istruzione e del Merito** | Anagrafe delle sedi degli istituti tecnici (276 sedi) | a.s. 2025/26 | Canali operativi della proposta, non esiti |
| Comune di Palermo / AMAT | GTFS della rete urbana | orario 2026 | Solo controllo dell'ultimo miglio (sezione 5.4) |
| Open Data Regione Siciliana (CKAN) | Nessun indicatore sulla popolazione giovanile di Bagheria (ricognizioni del 2026-08-12 e del 2026-08-29); i due dataset sui servizi al lavoro hanno risposto HTTP 502 al download del 2026-08-25 | - | **Esito negativo**, documentato in `docs/sources.md` §3: esclusa da ogni conclusione |

Due precisazioni che contano più di quanto sembri.

La prima: **l'assenza è documentata quanto la presenza**. La ricognizione su
`dati.regione.sicilia.it` e su `opendata.comune.palermo.it` è tracciata in
`docs/sources.md` con le query eseguite e i conteggi ottenuti, così che chi rifà il
lavoro sappia dove non conviene tornare. Il portale del Comune di Palermo, per esempio,
non è un CKAN: espone il catalogo in DCAT Turtle, e cercarvi le API standard restituisce
404. Sono dettagli operativi, ma sono la differenza fra «non c'è» e «non l'abbiamo
trovato».

La seconda: **le fonti non sono intercambiabili**. 8milaCensus si ferma al 2011 e il
censimento permanente comincia nel 2018; le definizioni non coincidono; fra 2019 e 2021
c'è per di più una rottura di misura sulla componente «in cerca di occupazione». Ogni
volta che le due fonti compaiono insieme, compaiono affiancate e etichettate con l'anno,
mai concatenate in una serie unica.

### 1.3 Dal dato grezzo alla tavola d'analisi: le trasformazioni

`pipeline/build.py` trasforma i raw in un piccolo insieme di **tabelle lunghe più
tabelle di lookup**, e null'altro: nessuna scelta di analisi è cotta dentro
l'interfaccia, ogni thread filtra ciò che gli serve. È la ragione per cui tre analisi
indipendenti restano confrontabili.

| Tavola | Righe | Che cosa contiene |
|---|---:|---|
| `ottomilacensus_long.csv` | 154.737 | territorio × anno × indicatore, i tre censimenti storici |
| `censpop_popolazione_long.csv` | 14.462 | territorio × anno × genere × età singola × stato civile × cittadinanza |
| `censpop_istr_lav_long.csv` | 6.552 | le due tavole del censimento permanente, lavoro e istruzione, in un file solo |
| `comuni_sicilia_poligoni.csv` | 15.702 | i vertici dei confini comunali, già proiettati |
| `territori.csv` | 521 | anagrafica dei territori, di cui **390 comuni siciliani** |
| `indicatori.csv` | 99 | codebook degli indicatori 8milaCensus |
| `codici.csv` | 164 | decodifica delle dimensioni SDMX |

Le operazioni non banali, tutte in `pipeline/`, mai a mano sui raw:

- **Normalizzazione dei codici territoriali.** Le due fonti scrivono lo stesso comune in
  modo diverso (8milaCensus `82006`, SDMX `082006`): tutto viene portato a sei cifre con
  lo zero iniziale, così le tabelle si uniscono senza mappature. Sicilia e Italia restano
  i codici SDMX `ITG1` e `IT`.
- **Disambiguazione di «Bagheria».** Nella codelist territoriale esistono anche un
  Sistema Locale del Lavoro e un Distretto che portano lo stesso nome: sono territori
  diversi dal comune, ed è un errore silenzioso e plausibile. La pipeline usa solo
  `082006`.
- **Esclusione dei totali.** Ogni dimensione SDMX ha un codice di totale (`T` per il
  genere, `TOTAL` per la cittadinanza, `99` per la condizione, `ALL` per il titolo) che
  convive come riga sorella con i dettagli. Sommare senza filtrarli raddoppia i numeri:
  la partizione è verificata cella per cella.
- **Ricostruzione della fascia 15-34.** La classe non esiste nelle tavole: viene sommata
  dalle età singole, e solo dove le età singole esistono, cioè dal 2021.
- **Geometria senza `sf`.** La libreria R per i dati spaziali richiede librerie di
  sistema (GDAL, GEOS, PROJ) che non si installano senza privilegi di amministratore. Per
  non imporle a chi riproduce, la geometria la fa geopandas in Python, che esporta i
  poligoni già proiettati (EPSG:32633) come tabella di vertici; R li disegna come poligoni
  con isole e buchi.
- **Lettura della matrice del pendolarismo.** Il tracciato è a campi fissi e senza
  intestazione: un campo sfalsato produrrebbe numeri plausibili e sbagliati. I file
  vengono letti in streaming dagli zip, senza mai espanderli, e il tracciato è
  controllato per prova (sezione 5).
- **Descrizioni fuori dalle tabelle.** Le etichette lunghe stanno nei lookup e non
  ripetute riga per riga: da sole portavano `ottomilacensus_long` da 5 a 40 MB.

### 1.4 Dalle tavole alle inferenze: i metodi

Dalle tavole si ricavano quantità che nelle tavole non ci sono. Ogni passaggio usa un
metodo dichiarato, e ogni metodo è riscritto una seconda volta, in forma diversa, dentro
`pipeline/verifica.py`.

| Domanda | Metodo | Dove |
|---|---|---|
| Quanto è preciso un tasso? | Intervallo di **Wilson** al 95% | tassi di occupazione, quote |
| Quanto è preciso il divario fra due tassi? | Intervallo di **Newcombe** al 95% sulla differenza | gap M−F |
| Il divario di Bagheria differisce da quello dei territori di confronto? | **Modello lineare di probabilità** pooled 2022-2024, con test sui coefficienti | sezione 3.1 |
| Il divario si sta allargando? | Regressione del gap sull'anno, 2018-2024 | sezione 3.1 |
| Rispetto a chi si misura Bagheria? | **Percentili sui 390 comuni siciliani** e due gruppi di comuni pari costruiti per **matching** su covariate strutturali, mai su esiti | sezione 2.4 |
| La graduatoria del 2011 dice ancora qualcosa nel 2024? | **rho di Spearman** fra le due graduatorie, più la persistenza per quintili | sezione 2.3 |
| Quanti giovani restano, e a che età se ne vanno? | **Ritenzione di coorte**: rapporto fra la stessa coorte a distanza di anni, a passo annuale e decennale | sezione 3.3 |
| L'anomalia è del comune o della sua taglia? | Regressione su **distanza dal capoluogo e dimensione**, lettura del **residuo** | sezione 5.3 |
| Quanto vale l'incertezza dei modelli comunali? | **Bootstrap** sui residui, più validazione incrociata | sezione 2.4 |
| Le stime campionarie sono confrontabili con i conteggi? | **Calibrazione sui margini esatti** dei conteggi esaustivi, con errore relativo misurato | sezione 5.4 |
| In quanto tempo si potrà dire se l'intervento ha funzionato? | **Analisi di potenza** e minimo effetto rilevabile (MDE) con due metri: il modello binomiale e la variabilità osservata, senza interventi, nei 33 comuni siciliani di taglia simile | sezione 7.4 |
| Il pilota vede il proprio effetto? | Potenza del confronto fra due coorti da 100 partecipanti | sezione 7.4 |
| Il controfattuale scelto è ammissibile? | **Test di pre-trend** sulle pendenze 2018-2024, ripetuto senza modello binomiale contro le pendenze dei comuni simili | sezione 7.4 |
| Quante diplomate lavorano, senza l'incrocio individuale? | **Limiti di Fréchet** sui margini delle due tavole | sezione 4 |
| Una quota censuaria è un conteggio o una stima? | Quota di celle intere per condizione e anno sui 390 comuni | sezioni 1.5 e 3.2 |

Due proprietà rendono questi conti verificabili invece che dichiarati. La prima è che
**il pin di regressione è indipendente**: `pipeline/verifica.py` non rilegge i risultati
dei notebook, li **ricalcola dai raw con implementazioni alternative** (gli intervalli
riscritti da zero, il modello in forma analitica, il matching rifatto, le coorti prese
dalle classi quinquennali invece che dalle età singole, un secondo parser della matrice
del pendolarismo). Se le due strade divergono, il controllo fallisce. La seconda è che
**il documento è dentro il perimetro del pin**: l'ultimo blocco di controlli rilegge le
cifre da `data/processed/`, le formatta all'italiana e pretende che la frase compaia alla
lettera in questa relazione. Ritoccare un numero a mano nel testo fa fallire la pipeline
esattamente come lo farebbe un errore di calcolo.

### 1.5 Che cosa le inferenze autorizzano a dire

I risultati che seguono non hanno tutti lo stesso statuto, e la distinzione è la
premessa per leggerli senza sopravvalutarli.

- **Descrittivo.** Conteggi e quote censuarie su Bagheria. Il censimento permanente li
  produce integrando registri amministrativi e rilevazioni campionarie, e a livello
  comunale ISTAT non pubblica un errore di stima: dove un intervallo compare, misura la
  variabilità binomiale della proporzione, non l'incertezza della rilevazione. Dal 2021,
  inoltre, solo occupati e residenti sono conteggi: le condizioni non professionali (in
  cerca, casalinga, studente, pensionato, altra condizione) sono stime di modello, somme di
  probabilità individuali di cui ISTAT non calcola l'errore standard, e lo si vede nei
  dati, dove quelle celle non sono intere (sezione 3.2). Il censimento 2011 è invece
  un'enumerazione, salvo le variabili rilevate su campione (sezione 5.4).
- **Comparativo.** Il confronto con Palermo, Sicilia, Italia, i 390 comuni siciliani e i
  due gruppi di pari. Qui l'affermazione robusta è quella che **sopravvive al cambio di
  lente**: dove i due gruppi di pari divergono, la relazione lo dice invece di scegliere
  il più favorevole.
- **Ecologico.** Le correlazioni fra comuni (mobilità e occupazione femminile, mezzo
  collettivo e divario di genere). Orientano un'ipotesi e non la dimostrano: valgono sul
  comune, mai sulla persona. Sono citate con questo limite ogni volta, e una di esse è
  riportata proprio perché ha dato **esito negativo** (sezione 5.4).
- **Nessuna stima causale.** Nessun numero di questa relazione misura l'effetto di un
  intervento, perché nessun disegno lo permetterebbe. È il motivo per cui la proposta
  include un proprio disegno di valutazione (sezione 7.4): serve a produrre l'evidenza
  che oggi manca, non a confermare quella che c'è.

Il perimetro di ciò che la relazione **non** afferma è raccolto in chiaro nella sezione 9.

---

## 2. Il profilo: un recupero vero che non converge

### 2.1 La fotografia 2024

Bagheria conta **5.904 residenti di 15-24 anni** (2024). La loro condizione prevalente:

| Condizione 2024 | Quota | Persone (stima) |
|---|---:|---:|
| Studenti | 60,7% | ~3.581 |
| Occupati | 12,4% | ~734 |
| In cerca di occupazione | 7,9% | ~467 |
| **Inattivi non studenti** | **19,0%** | **~1.121** |

→ `edu_youth_states_2018_2024.csv`, `analisi_condizione_15_24.csv`

Lo stesso profilo sui quattro territori del brief:

| 15-24, 2024 | Bagheria | Palermo | Sicilia | Italia |
|---|---:|---:|---:|---:|
| Occupati | **12,4%** | 13,2% | 15,6% | 22,3% |
| In cerca di occupazione | **7,9%** | 8,3% | 7,5% | 6,2% |
| Studenti | **60,7%** | 63,2% | 62,2% | 62,3% |
| Inattivi non studenti | **19,0%** | 15,3% | 14,8% | 9,2% |
| Fuori da lavoro e studio | **26,9%** | 23,6% | 22,3% | 15,3% |
| di cui non cercano lavoro | **70,6%** | 64,9% | 66,4% | 59,8% |

→ `edu_youth_states_2018_2024.csv`

Il confronto colloca subito il punto critico: l'occupazione 15-24 di Bagheria (12,4%) è
**3,1 punti sotto la Sicilia** (15,6%), e gli inattivi non studenti (19,0%) sono **4,2
punti sopra** (14,8%). Complessivamente il 26,9% dei giovani è fuori sia dal lavoro sia
dallo studio, contro il 22,3% siciliano. → `edu_kpi_dashboard.csv`

Dentro quel 26,9% sta il dato che orienta tutta la proposta: **il 70,6% non è
classificato come persona in cerca di occupazione**, più che a Palermo (64,9%), in Sicilia
(66,4%) e in Italia (59,8%). Non sono giovani che cercano e non trovano: sono giovani che
non arrivano a cercare. Il livello di questa quota dipende dal metodo di stima in vigore dal
2021 (sezione 2.2), quindi si confronta fra territori nello stesso anno e non lungo la serie.

### 2.2 Il recupero c'è, la convergenza no

Fra 2018 e 2024 l'occupazione 15-24 (totale) sale da 8,2% a 12,4%, ma il gap
occupazionale con la Sicilia è **−3,1 punti sia nel 2018 sia nel 2024**: Bagheria
migliora alla velocità del contesto, non di più. → `edu_finding_summary.csv`

Le componenti di chi è fuori da lavoro e studio vanno lette con una cautela: fra 2019 e
2021 cambia la misura della condizione «in cerca di occupazione», e la sua quota cade in
un solo passaggio di 7,5 punti a Bagheria e di 7,1 in Sicilia (`docs/sources.md` §7). Il
confronto onesto è quindi dentro la stessa definizione, 2021-2024: **chi cerca lavoro
scende da 10,6% a 7,9%, gli inattivi non studenti restano fermi (19,2% → 19,0%)**, e il
loro scarto dalla Sicilia sale da 2,7 a 4,2 punti. Il miglioramento, dove c'è, non
raggiunge chi non cerca. → `edu_youth_states_2018_2024.csv`

Lo stesso pattern sulla fascia adulta: fra i 25-49enni la quota con almeno il diploma
passa da 56,2% a 62,4% e l'occupazione da 43,0% a 53,6%, ma nel 2024 i divari con la
Sicilia restano **−4,1 e −5,7 punti**. → `edu_kpi_dashboard.csv`

### 2.3 Il lungo periodo: progresso assoluto, arretramento relativo

I tre censimenti 1991/2001/2011 e il ponte verso il censimento permanente separano due
cose che di solito si confondono: Bagheria **migliora in assoluto e arretra in
posizione**.

- NEET 15-29: dal 42,9% (1991) al 40,1% (2011), ma la posizione fra i 390 comuni
  siciliani passa **circa dal 17° all'88° percentile** (qui un percentile alto è
  sfavorevole): molti altri comuni hanno ridotto il problema molto più in fretta.
  → `edu_historical_bagheria.csv`, verifica incrociata in `notebooks/genere.ipynb`
- Uscita precoce dalla scuola (`I5`, 15-24): 40,8% → 28,6%, ma **56° → 70° → 83°
  percentile** nei tre censimenti 1991, 2001 e 2011 (anche qui alto è sfavorevole).
  → `genere_frattura_istruzione.csv`
- Occupazione femminile 15+: 18,1% (2011) → 23,7% (2024), ma la mediana regionale sale
  da 23,6% a 28,3%. **Nel 2024 Bagheria arriva dove stava la mediana siciliana nel
  2011** (fig04). Il confronto fra due rilevazioni diverse regge su questo indicatore:
  nel 2018 il censimento permanente dà a Bagheria il 18,8%, a meno di un punto dal 2011, e
  lo scarto resta entro un punto anche per Palermo, Sicilia e Italia (sezione «Il ponte fra
  i due censimenti» di `notebooks/genere.ipynb`). La graduatoria dei 390 comuni del 2011 predice quella del 2024 con rho
  di Spearman **0,848**, e il 74% del quintile più basso del 2011 è ancora lì, Bagheria
  compresa: il posizionamento del 2011 non era una fotografia scaduta ma una previsione
  verificata. → `genere_mappa_2011_2024.csv`, sezione «I claim reggono al 2024?» di `notebooks/genere.ipynb`
- La datazione è convergente da due domini indipendenti: sia il muro sull'occupazione
  femminile sia la frattura sull'uscita precoce si aprono **nel decennio 2001-2011** e
  non si richiudono (fig10). → `genere_madri_recente.csv`, `genere_frattura_istruzione.csv`

### 2.4 Le lenti di confronto: cosa sopravvive al cambio di «simile»

Oltre ai tre territori del brief, il benchmarking usa i **390 comuni siciliani** e due
gruppi di comuni pari costruiti con domande diverse, le **10 gemelle strutturali**
(matching su dimensione, densità, età, stranieri, abitazioni, distanza da Palermo, mai
su esiti) e i **10 pari a pari istruzione** del thread educazione. L'overlap fra i due
gruppi è un solo comune (Misilmeri), e la figura di posizionamento (fig08) li mostra
affiancati: **ciò che si può affermare senza scegliere una lente è ciò che sopravvive a
entrambe** - 6 indicatori su 8 danno lo stesso giudizio.

Il confronto è sugli indicatori 8milaCensus del 2011, e il numero fra parentesi dice
quanti dei 10 comuni pari hanno un valore più basso di Bagheria. Tre tratti reggono a
tutte e due le letture e vanno in proposta: disoccupazione femminile estrema (8 su 10
sotto Bagheria, in entrambi i gruppi), occupazione 15-29 bassa (2 su 10), quota di
giovani che vivono da soli al minimo (0 su 10). E la divergenza più informativa è
sull'occupazione femminile 15+: dentro le gemelle strutturali Bagheria è nella norma (3
su 10 sotto), fra i comuni ugualmente scolarizzati è **penultima** (1 su 10). **A pari
istruzione, il lavoro femminile non arriva: non è un tratto di fascia territoriale.** I
modelli comunali del thread educazione confermano il segno (occupazione giovanile
osservata meno prevista **−5,9 punti**, intervallo bootstrap da −7,7 a −4,3), ma con un
potere esplicativo quasi nullo (R² in validazione incrociata 0,05): si cita come conferma
di segno, mai come quantità attribuibile al comune.
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
più ampio del panel (1,8 a Palermo, 2,7 in Sicilia, 2,2 in Italia), ma quella fascia contiene età in cui
il diploma non può esserci e risente della composizione per età. Sulla **stessa fascia
15-24 dell'occupazione** il vantaggio è +4,8 punti, pari alla Sicilia (+4,7). Il gap
occupazionale è 8,3 punti [IC 95% 6,6-10,0]. → `genere_gap_occupazione_ci.csv`

La scala su cui leggere il gap è stata scelta con un modello, non a occhio (fig01).
**In punti** il gap di Bagheria non è un'anomalia locale: sul pooled 2022-24 è 1,1 punti
più ampio di quello di Palermo (p=0,03) e 1,8-1,9 punti più stretto di quelli di Sicilia e
Italia. **In rapporto** (M/F = 2,01 contro 1,56 nazionale) Bagheria è la peggiore del
panel, ma il rapporto oscilla fra le annate.
**Il tratto locale è il livello: il tasso di occupazione femminile all'8,2% [Wilson
7,2-9,2] è il minimo dei quattro territori in tutte e 6 le annate disponibili**, ed è
testato, sotto Palermo di 1,2 punti, sotto la Sicilia di 1,9, sotto l'Italia di 8,9
(p ≤ 0,0001 pooled 2022-24). Il gap in punti **tende ad allargarsi** (stima di +0,21
punti l'anno sul 2018-2024), ma su sei annate, ciascuna con il suo errore campionario, la
tendenza non è acquisita: è una direzione, non un risultato. Il primato vale nel panel e
fra i comuni della stessa taglia, non in tutta la Sicilia: fra i 34 comuni siciliani con un
numero di ragazze 15-24 fra la metà e il doppio di quello di Bagheria è **secondo dal
basso** (mediana 10,6%), fra tutti i 390 comuni è 112° dal basso (mediana 9,7%), perché
molti comuni piccoli stanno sotto. → `genere_rango_390_15_24.csv`; sezioni «Punti
percentuali o rapporto?», «Modello lineare di probabilità», «Bagheria è anomala fra i
comuni siciliani?» e «Trend 2018-2024» di `notebooks/genere.ipynb`

Il dato sull'istruzione va quindi maneggiato con cura: le ragazze di Bagheria sono più istruite
dei coetanei su ogni fascia, ma non più istruite delle ragazze siciliane (sulla fascia
18-24 Sicilia e Italia hanno un vantaggio femminile più ampio). Ciò che regge su ogni
fascia è la coppia **distacco dal vicinato e mancata conversione**: sui 18-24 il
vantaggio femminile è +5,7 punti a Bagheria contro +2,5 nei cinque comuni più vicini, e
il tasso di occupazione femminile è il più basso del panel. Su 1.000 ragazze 15-24 di
Bagheria, 510 hanno almeno il diploma e 82 lavorano; fra i coetanei, 462 e 165 (fig11).
Le due barre hanno la stessa base e **non sono un funnel**: non dicono quante diplomate
lavorano, perché l'incrocio individuale non è pubblicato; i margini mettono solo un tetto
(sezione 4).
→ `genere_per_1000.csv`, `genere_forbice_quadrante.csv`

### 3.2 Dentro l'inattività: le casalinghe ventenni, non sposate

Nelle stime del censimento risulta **casalinga** il 13,4% delle ragazze 15-24 di Bagheria:
387 persone, contro l'11,3% di Palermo, il 10,1% della Sicilia e il 4,6% dell'Italia; dal
2021 la quota sta fra il 12,8% e il 14,8%.

**È una stima, non un conteggio né una dichiarazione.** Dal 2021 ISTAT stabilisce chi è
occupato e, per chi non lo è, stima con un modello (un logit multinomiale addestrato sulle
risposte del campione censuario, con covariate amministrative come età, istruzione, segnali
di lavoro, pensione e redditi) la probabilità di ciascuna altra condizione; il numero
comunale è la somma di quelle probabilità, a Bagheria 386,84 ragazze, e l'errore standard
non è calcolato. Si vede nei dati: sui 390 comuni, dal 2021 le celle di occupati e
residenti sono tutte intere, quelle delle condizioni non professionali quasi mai; nel
2018-2019, con un altro metodo, lo erano tutte. Due conseguenze. Nessuna covariata del
modello misura il lavoro domestico: «casalinga» è l'etichetta che la stima assegna, non una
misura della cura. E la serie si legge solo dal 2021: fra il 2019 e il 2021 la quota dei
comuni di taglia simile salta in mediana di 2,87 punti per il solo cambio di metodo.
→ `genere_interi_condizione.csv`, `genere_mde.csv`; fonti del metodo: metadati ESMS del
censimento 2021 (ISTAT per Eurostat) e Chianella, Ciccaglioni, Ercolani, RIEDS 2024

La tavola non dà l'età dentro la fascia, e sull'aggregato pesano le 15-17enni, quasi
tutte studenti: se nessuna delle 387 avesse meno di 18 anni la quota sulle 18-24enni
sarebbe del 18,8%, se nessuna ne avesse meno di 20 del 25,8% sulle 20-24enni. L'eccesso
sull'incidenza italiana vale **254 ragazze**. → `genere_casalinghe.csv`,
`genere_casalinghe_bounds.csv`

Chi sono? Il canale del matrimonio precoce **non regge i numeri**: al 1.1.2025 le già
coniugate 15-24 sono 41 (1,4%) contro 387 casalinghe (**almeno l'89% non è sposata**), e
la quota di coniugate 20-24 di Bagheria (2,7%) sta *sotto* Palermo (3,2%) e Sicilia
(2,9%). Lo stato civile esclude il matrimonio come spiegazione, ma non osserva
convivenze né figli: che cosa tenga a casa queste ragazze i dati pubblici non lo dicono.
Per la policy basta il primo fatto: serve un servizio di **attivazione**, non solo di
conciliazione. → `genere_stato_civile.csv` (fonte DCIS_POPRES1, denominatori coincidenti
alla singola unità con la tavola censuaria)

Il gruppo degli «invisibili» (fuori da lavoro, studio e ricerca) **non è femminile nelle
dimensioni**: 573 ragazze e 549 ragazzi (51% F). È femminile **nell'etichetta**: fra le
ragazze prevale un'etichetta precisa (387 casalinghe, contro 50 casalinghi fra i
ragazzi), fra i ragazzi il residuo senza nome («altra condizione»: 485 ragazzi contro
183 ragazze). Anche questi sono stime di modello, non conteggi. Qualunque outreach deve
coprire entrambi i generi con agganci diversi: per le ragazze esiste già un'etichetta
censuaria da cui partire, per i ragazzi non c'è neppure quella.
→ `genere_composizione_stato_dettaglio.csv` (fig02)

### 3.3 La fuga ha un tempismo di genere: la finestra 22-25

La **ritenzione di coorte** misura la fuga senza bisogno di dati sulle migrazioni: è il
numero di residenti di una certa età nel 2024 in percentuale di quelli che avevano tre
anni di meno nel 2021 (sotto 100 la coorte si è ridotta, sopra è cresciuta). È un saldo
netto: non distingue chi parte da chi arriva. La ritenzione 2021-2024 mostra due uscite
diverse (fig03, fig07):

- **i ragazzi si perdono presto e a ondate** (età 17-19 e 23-24), con **rientri netti
  dopo i 26**;
- **le ragazze tengono fino ai 23-24 anni e si perdono dai 24-25 in poi, senza
  rientri**: la coorte femminile che nel 2021 aveva 25-29 anni è a **96,3**, contro 101,2
  dei coetanei maschi, 97,6 in Sicilia, 98,8 a Palermo e 103,0 in Italia (che cresce per
  immigrazione). È esattamente l'età in cui il vantaggio educativo dovrebbe convertirsi in
  occupazione e non lo fa.

→ `genere_coorti.csv`, `genere_ritenzione_eta.csv`

**La finestra utile per intervenire sulle ragazze è 22-25 anni** (età nel 2021): prima la
curva è sopra la pari, dopo la perdita è già avvenuta, e chi aveva 22-25 anni nel 2021 se
ne va fra i 25 e i 28. ⚠️ È una lettura **pooled sul triennio**:
le transizioni annuali oscillano fino a 8 punti sulla stessa età (n ~290 per cella);
l'anno singolo è un controllo, non un titolo. → `genere_ritenzione_transizioni.csv`

Alla scala decennale la frattura è più netta, e risponde all'obiezione che tre anni non
bastano a chiamarla fuga: la coorte 15-19 seguita per dieci anni passa, sulle femmine, da
**102,9% (2001-2011) a 88,6% (2011-2021)**, e sui maschi da 98,4% a **83,9%**. Sono circa
14 punti per entrambi i generi, contro 4-6 in Sicilia: a questa scala la fuga non ha
genere, e il suo decennio è quello **successivo** al muro sull'occupazione femminile
(2001-2011, sez. 2.3). ⚠️ Il decennio 2011-2021 unisce il censimento 2011 e il censimento
permanente; la distorsione nota va nel verso prudente ed è dichiarata in fig07b.
→ `genere_ritenzione_decennale.csv`

---

## 4. Titolo e condizione: la domanda a cui i dati comunali non rispondono

Il primo focus proposto dalla locandina - la relazione fra titolo di studio e condizione
lavorativa - a livello comunale **non è misurabile sull'individuo**, e lo abbiamo
dimostrato prima di aggirarlo: nelle tavole comunali del censimento permanente la tavola
lavoro pubblica il titolo solo come `ALL` e la tavola istruzione pubblica la condizione
solo come totale `99` (cella «Verifica di fattibilità» di `notebooks/genere.ipynb`).
*«Quanti diplomati di Bagheria lavorano»* non è una domanda a cui i dati pubblici
rispondono.

Quello che si può dire, si dice con due misure parallele sulla stessa fascia e sullo
stesso denominatore (fig11, sezione 3.1), con il confronto territoriale (sezione 2) e
con la lente dei pari a pari istruzione (sezione 2.4).

**I margini, però, mettono un tetto.** Se tutte le occupate fossero diplomate, nel 2024
lavorerebbe al massimo il **16,1%** delle ragazze 15-24 con almeno il diploma (236
occupate su 1.469 diplomate), contro il 35,7% dei ragazzi; il minimo, per entrambi, è
zero. Sono limiti di Fréchet, non stime, e valgono perché diplomati e occupati sono
sottoinsiemi della stessa popolazione 15-24 (il totale della tavola lavoro coincide con la
somma delle età singole, verificato). Il tetto femminile di Bagheria è il più basso dei
quattro territori (Palermo 20,3%, Sicilia 20,4%, Italia 32,3%): qualunque sia l'incrocio,
fra le diplomate lavora al più una su sei. → `genere_frechet.csv`

**Prima però va detto di quale titolo si parla, perché non è lo stesso a tutte le
altezze.** Nella fascia 9-24 del 2024 il titolo di Bagheria è il diploma: dei **2.864
residenti con almeno il diploma, il 91,0% si ferma al diploma** di scuola secondaria, e i
titoli terziari sono **258 persone** in tutto. Il dato dice quale titolo la fascia
detiene, non quanto in alto arriverà: a 20 anni una laurea non può ancora esserci.
→ `censpop_istr_lav_long.csv`

Chi la laurea l'ha finita si legge al 2011, e lì la scala regge solo al primo gradino
(`edu_fig02_catena_2011`). L'unico indicatore su cui Bagheria sta davanti a Palermo e alla
Sicilia è la competenza di base, `I8`: **96,7% dei 15-19enni con almeno la licenza media**,
contro 95,6 e 96,5 (Italia 97,9). Un gradino più su il segno si inverte e non torna:
adulti 25-64 con diploma o laurea (`I6`) al **42,5%** contro 48,2 in Sicilia, 51,2 a
Palermo e 55,1 in Italia; trentenni con titolo universitario (`I7`) al **14,4%** contro
18,3, 20,6 e 23,2. Ultima del panel su entrambi, e al 2024 il segno non cambia (sezione
2.2: −4,1 punti sul diploma 25-49). → `edu_historical_benchmarks_2011.csv`

**Il collo di bottiglia quindi non è la scolarizzazione di base, che tiene, ma tutto ciò
che viene dopo: la scala dei titoli, che a Bagheria si ferma presto, e la conversione in
lavoro, che non arriva nemmeno per i titoli che ci sono.** Le due letture non si sommano
in una catena individuale, perché l'incrocio sulla persona non esiste: restano due misure
aggregate dello stesso territorio.

La versione individuale della domanda resta la più importante del territorio, ed è per
questo che la proposta la trasforma in un output: il dataset di servizio della sezione
7.5 misura, per la prima volta a Bagheria, titolo → azione → esito sulla singola
persona.

---

## 5. Il pendolarismo verso Palermo: una sola destinazione, e un divario di genere che si apre col lavoro

Il terzo focus del brief. Il censimento permanente pubblica il pendolarismo comunale solo
come dentro/fuori comune (la dimensione `LOC_DEST` del dataflow è servita come valore
unico), quindi non dice dove si va. La destinazione la danno le *matrici del
pendolarismo* di ISTAT: l'origine-destinazione comune per comune, con sesso, motivo,
mezzo, fascia oraria e durata (censimenti 1991/2001/2011), rifatta sul solo lavoro col
censimento permanente 2021. → `notebooks/mobilita.ipynb`, `docs/sources.md` §12

Il tracciato è a campi fissi e senza intestazione: un campo sfalsato darebbe numeri
plausibili e sbagliati. Il controllo è sostanziale: dalla matrice si **ricostruiscono
sette indicatori `M` di 8milaCensus già pubblicati** (`M3` 76,1 · `M4` 19,6 · `M5` 65,2 ·
`M6` 8,4 · `M7` 25,7 · `M8` 83,3 · `M9` 3,6, **sette su sette alla prima cifra decimale**) e i
totali nazionali del 2011 e del 2021 coincidono con quelli dichiarati da ISTAT. Il che
dimostra anche una cosa utile al vincolo di fonti della locandina: la matrice **non è una
fonte alternativa a 8milaCensus, è il livello sottostante** da cui quegli indicatori sono
calcolati. → sezione «La fonte, e come si controlla che sia letta bene» di
`notebooks/mobilita.ipynb`

### 5.1 La destinazione ha un nome, ed è una sola

| Fra chi esce dal comune, quanti vanno a Palermo | quota | percentile sui 381 comuni non capoluogo |
|---|---:|---|
| **per studio**, 2011 | **91,1%** | 97° |
| **per lavoro**, 2011 | **67,5%** | 93° |
| **per lavoro**, 2021 | **65,1%** | 94° |

Il secondo comune di destinazione per lavoro è Santa Flavia (6,8% nel 2011): **non esiste
una seconda direzione**. Il percentile è calcolato sulla misura comparabile, cioè la quota
di chi esce diretta al *proprio* capoluogo di provincia, perché «quanti vanno a Palermo»
per un comune del Ragusano è zero per costruzione. → sezione 2 di
`notebooks/mobilita.ipynb`, `mob_flussi_bagheria.csv`, fig `mob_fig01`

È il fatto che rende la mobilità una leva di policy e non un dettaglio descrittivo: non c'è
da scegliere quale destinazione servire.

### 5.2 Il ribaltamento: lo scarto di genere cambia segno col motivo

La misura è la quota di chi **esce dal comune** sul totale di chi si sposta quotidianamente
per quel motivo, letta per genere. Il denominatore è già condizionato al motivo (chi si
sposta per lavoro un lavoro ce l'ha), quindi lo scarto **non è un riflesso del divario
occupazionale** della sezione 3: è una misura indipendente sullo stesso passaggio. E il
conteggio del 2011 **non è una stima**: i record di tipo `S` sono enumerazione esaustiva.

| Quota che esce dal comune, 2011, scarto F − M | Bagheria | Sicilia | Italia | Comune di Palermo |
|---|---:|---:|---:|---:|
| **per studio** | **+2,6** | +1,4 | +1,8 | −0,1 |
| **per lavoro** | **−12,1** | −4,6 | −4,8 | −2,0 |
| **il salto fra i due** | **14,7** | 6,0 | 6,5 | 1,9 |

→ `mob_ribaltamento.csv`, `mob_ribaltamento_territori.csv`, fig `mob_fig02`

In Sicilia e in Italia il verso cambia col motivo (a Palermo città i due scarti sono
entrambi negativi e quasi nulli); la particolarità di Bagheria è **l'ampiezza**: due volte e
mezza il salto siciliano, e sul lavoro il **15° percentile** dei comuni siciliani (14° al
netto di taglia e distanza dal capoluogo). Le ragazze di Bagheria si muovono. Smettono quando il motivo diventa il
lavoro.

**La replica tiene, su una fonte diversa.** Lo stesso salto fra studio e lavoro, misurato
sul censimento permanente 2018-2019 (altra rilevazione, altro metodo, sette anni dopo), vale
a Bagheria 11,3 e 10,9 punti, contro 5,6 e 5,9 in Sicilia e 6,5 e 6,1 in Italia. Il punto
di rottura è lo stesso della forbice (sezione 3.1) e della finestra 22-25 (sezione 3.3), da
una terza tavola. → `genere_pendolarismo.csv`, fig12

### 5.3 «Bagheria si muove poco» è una lettura sbagliata di un numero giusto

La lettura immediata degli indicatori 2011 è che Bagheria si muova poco: mobilità fuori
comune `M2` al 25° percentile dei 390 comuni. **Il percentile è esatto, la lettura no.** `M2` rapporta chi esce all'intera popolazione
fino a 64 anni, quindi è basso anche perché a Bagheria lavorano in pochi. E fuori comune si
va per mancanza di lavoro dentro, e Bagheria è il comune più grande della
corona di Palermo: 12.000 pendolari contro i 3.000 di Ficarazzi, che infatti manda fuori
tre pendolari su quattro contro i due su cinque di Bagheria.

A parità di **distanza dal capoluogo e di dimensione** (due variabili geografiche, non di
comportamento), sulla quota di chi esce per lavoro nel 2021 il residuo di Bagheria è di
**−1,9 punti** (z = −0,13) e il percentile passa dal 36° grezzo al **48°** fra i 381 comuni
non capoluogo. Bagheria si muove esattamente quanto ci si aspetta da un comune della sua
taglia a quella distanza. → sezione 3 di `notebooks/mobilita.ipynb`,
`mob_taglia_distanza.csv`, fig `mob_fig04`

Vale anche per `M4` (mobilità studentesca al 18° percentile), che già la versione precedente
segnalava non essere di per sé un dato negativo: è un rapporto fuori/dentro comune e Bagheria
ha scuole proprie (3 sedi tecniche, anagrafe MIUR). Il modello lo conferma: residuo −0,8
punti. → `edu_technical_schools.csv`

**La particolarità di Bagheria non è quanto si muove. È chi si muove, e per quale motivo.**

### 5.4 Il treno è il canale femminile, e il vincolo non è l'offerta di trasporto

Mezzo, orario e durata sono rilevati su campione nei comuni sopra i 20.000 abitanti: sono
stime, e stanno in una tabella separata dai conteggi esaustivi apposta. La precisione è
misurata e non assunta: per gli stessi strati esistono sia il conteggio esaustivo sia la
stima, e l'errore relativo è dello **0,9%** in mediana, dell'8,6% al massimo sullo strato
più piccolo.

Le quote qui sotto sono **calibrate sui margini esatti** dei conteggi esaustivi: la
calibrazione non cambia la conclusione, la rafforza (lo scarto sul treno passa da 14,5 a
15,1 punti).

| Fra chi esce da Bagheria (2011) | donne | uomini |
|---|---:|---:|
| mezzo collettivo | **34,7%** | 18,9% |
| di cui treno | **31,5%** | 16,4% |
| mezzo privato a motore | 63,6% | **79,0%** |

→ `mob_mezzo_genere.csv`, fig `mob_fig03`

Le donne raggiungono Palermo **sul mezzo collettivo**, gli uomini in auto. Fra chi va a
lavorare a Palermo, a 17 chilometri, le donne partono più tardi (esce prima delle 7:15 il
54,4% contro il 65,0% degli uomini); fra tutti quelli che escono dal comune viaggiano anche
più a lungo (31-60 minuti per il 43,8% contro il 36,1%). → cella «fascia oraria di uscita»
della sezione 5 di `notebooks/mobilita.ipynb`

**Ma il treno di Bagheria non è sottoutilizzato: è già l'asset di mobilità più distintivo che
il comune abbia**, al 98° percentile siciliano per quota di chi esce che lo usa (97° a parità
di distanza e taglia). Aumentarne l'uso non è la leva che manca.

> **Un risultato negativo, riportato perché è stato testato.** L'ipotesi naturale (dove il
> mezzo collettivo pesa di più, il divario di genere è più piccolo) **non trova sostegno**
> sui 381 comuni non capoluogo: rho di Spearman −0,10 (p = 0,06) fra quota d'uso del mezzo
> collettivo e divario di genere, cioè di segno opposto all'ipotesi, e il
> quartile con più mezzo collettivo ha il divario più ampio; sul treno l'associazione è
> nulla (p = 0,29). Coerentemente, l'ultimo miglio a Palermo non è un collo di bottiglia: dal
> GTFS di AMAT (la terza fonte indicata dalla locandina) le fermate «Stazione Centrale» hanno
> 18 linee e ~125-130 passaggi l'ora dalle 7 alle 21.
>
> **Conseguenza di progettazione**: un'associazione assente fra comuni non esclude che
> l'orario o il mezzo pesino sulla singola persona, ma toglie la base a un intervento
> infrastrutturale. La proposta non finanzia trasporto: verifica la raggiungibilità caso per
> caso (sezione 7.6, F2) e agisce sul passaggio studio→lavoro, dove il divario si apre, cioè
> la finestra B di Ponte 19 (sezione 7).

### 5.5 Il bersaglio, in persone

Portare le pendolari di Bagheria al divario **medio siciliano** (non alla parità, al semplice
comportamento regionale) vale **+279 donne** che lavorano fuori comune; la parità piena con
gli uomini di Bagheria ne varrebbe 449. Il conto è sul 2011 e su tutte le età: dà la scala
del fenomeno, non un obiettivo per la fascia giovanile. → `mob_sintesi.csv`

**I limiti, per primi.**

1. **Nessuna età.** Né la matrice né la tavola del censimento permanente hanno la dimensione
   età (verificato: `AGE_NOCLASS` servita solo come `TOTAL`, anche a livello nazionale). Il
   target 15-34 del brief **non è isolabile sul pendolarismo**. Il motivo è un'informazione
   d'età parziale e va usata come tale: chi esce per studio è quasi solo secondaria superiore
   e università, perché i cicli precedenti a Bagheria ci sono tutti.
2. **Nessun livello in serie fra 2011 e 2021.** Il 2011 conta chi si sposta *giornalmente*, il
   2021 chi si reca al lavoro *almeno tre giorni a settimana*, e il 2021 copre il solo lavoro
   e non ha il sesso. Si confronta la composizione (dove vanno, su cento che escono), mai il
   livello; la colonna `definizione` della tabella lo porta scritto riga per riga.
3. **Nessun dato sul rientro.** Si conosce solo l'orario di uscita di casa. Che le donne
   partano più tardi e viaggino più a lungo è un fatto; il carico di cura resta un'ipotesi.
4. **Correlazioni ecologiche.** Sui 390 comuni la mobilità fuori comune correla con
   l'occupazione femminile (Spearman +0,32): orienta l'ipotesi, non la dimostra. E l'`R²` dei
   modelli sui divari di genere è vicino a zero: «atteso» lì vuol dire poco più di «media
   siciliana». → `genere_mobilita_2011.csv`
5. **Palermo non è un termine di paragone su questa misura**: è un comune grande e compare con
   valori bassissimi per costruzione.

---

## 6. Il denominatore si muove: la platea giovane si restringe

La «fuga di talenti» del brief si misura con la ritenzione di coorte (sezione 3.3). Qui
conta un'altra conseguenza, che vale per qualunque obiettivo: la platea giovane si
restringe, e con essa il denominatore di ogni tasso di questa relazione.

- La popolazione 15-34 passa da **12.174 (2021) a 11.861 (2024)**: −313 persone, −2,6%
  in tre anni. Ma 266 di quelle 313 persone sono **ricambio d'età** (le coorti che compiono
  15 anni sono più piccole di quelle che superano i 34): dentro le stesse coorti il saldo è
  di −47 persone, −0,39%, come in Sicilia (−0,38%). Sull'insieme dei 15-34 Bagheria non
  perde più della regione; la sua specificità è chi si perde e quando (sez. 3.3).
  → `analisi_popolazione_giovane.csv`, `genere_stock_coorti.csv`
- Il ricambio dall'estero è debole: gli stranieri sono l'**1,6% del 15-34** (195
  persone) contro 5,1% a Palermo, 6,4% in Sicilia, 12,4% in Italia.
  → `genere_stranieri.csv`
- Chi avrà 15-24 anni nel 2029 e nel 2034 **è già nato**: la platea si conta oggi sui
  residenti di 10-19 e 5-14 anni. Non è una proiezione demografica ma il conto di chi è
  già residente, a migrazioni nulle: le partenze e gli arrivi dei prossimi anni lo
  sposteranno. Le ragazze passano da 2.882 (2024)
  a 2.651 (2029, −8,0%) a **2.435 (2034, −15,5%)**; i ragazzi −2,5% e −5,8%. Nei
  territori di confronto il calo è simmetrico fra i generi; a Bagheria no.
  → `genere_platea.csv`
  (⚠️ l'asimmetria origina da una sex ratio 5-14 anomala, 117 maschi per 100 femmine
  contro 104-106 dei benchmark, in salita dal 2011, identica su due tavole indipendenti;
  il meccanismo è aperto e il dato si cita solo insieme al suo audit:
  `genere_sex_ratio_5_14.csv`)

La conseguenza per qualunque intervento è aritmetica, ed è il secondo pilastro della
proposta: al tasso obiettivo di Palermo (9,59%), l'equivalente di «+40 occupate»
misurato sulla platea di ciascun anno vale **+18 nel 2029 e −2 nel 2034** (lordo +40,4;
attrito demografico −22,2 e −42,9). Un obiettivo scritto in teste si annulla da solo
senza che nessuno abbia sbagliato nulla. **Il KPI va scritto in tasso.**
→ `genere_kpi_netto.csv` (fig09; ⚠️ da non confondere con lo scenario «non si fa
niente», −19/−37 a tasso 2024 costante: `genere_tetto_platea.csv`)

---

## 7. Dall'evidenza alla proposta: Ponte 19

La proposta completa, con modello operativo, decision gate e disegno di valutazione, è
`docs/policy/POLICY_PONTE_19.md`. Qui la sua derivazione dall'evidenza, nel formato fissato dal
progetto: **evidenza → intervento → target → KPI**.

| | |
|---|---|
| **Evidenza** | Il 70,6% dei 15-24enni fuori da lavoro e studio non cerca (sez. 2.1); la conversione titoli→lavoro fallisce soprattutto sulle ragazze (sez. 3.1), che si perdono dopo i 24 anni (sez. 3.3); il pendolarismo ha lo stesso segno: le ragazze escono dal comune per studiare più dei coetanei (+2,6 punti) e le donne escono per lavorare 12,1 punti meno degli uomini (sez. 5.2); la platea si restringe (sez. 6) |
| **Intervento** | **Ponte 19**: servizio comunale di transizione e riattivazione con outreach attivo (non a domanda spontanea) e due finestre di ingaggio |
| **Target** | Finestra A: 18-20enni all'uscita dalla scuola o entro 30 giorni dall'interruzione. Finestra B: 22-25enni fuori da lavoro e studio. Quota di genere ≥50% F sui presi in carico. Capacità pilota: 200 persone/anno, pari a ~18% dei 1.121 inattivi non studenti 15-24 (platea indicativa: il censimento non dà la fascia 18-25) |
| **KPI** | In **tasso**, con finestra di lettura dichiarata (7.4) |

Il servizio parte da 18 anni perché fino a 18 vale il diritto-dovere all'istruzione e
alla formazione, e si ferma a 25 perché è lì che i dati collocano le due uscite (sez. 3.3). I 26-34enni
del brief restano fuori dal target per una ragione di misura: nessuna tavola comunale
permette di seguirne la condizione professionale (la classe 25-49 non è scomponibile).

### 7.0 Perché non è un intervento sui trasporti

La domanda arriva da sola leggendo la sezione 5: se il collegamento con Palermo è il canale
delle donne, perché non intervenire lì? Perché **i dati non lo sostengono**, in due modi
indipendenti. Il treno di Bagheria è già al 98° percentile siciliano per uso (sez. 5.4):
non c'è un'infrastruttura sottoutilizzata da attivare. E sui 381 comuni non capoluogo una maggiore
quota di mezzo collettivo **non** si accompagna a un divario di genere più piccolo: l'associazione è
nulla, e di segno opposto all'ipotesi.

Resta però un vincolo operativo che il servizio deve rispettare: per le donne di Bagheria il
canale verso Palermo è il mezzo collettivo (34,7% contro 18,9%), per gli uomini è l'auto
(79,0%). **Un servizio che dia per scontata l'auto seleziona per genere**, e selezionerebbe
proprio contro la metà che la quota di 7.2 vuole raggiungere: gli orari di convocazione, i
tirocini e le sedi vanno scelti su ciò che è raggiungibile in treno e autobus, e la cosa va
misurata, non assunta.

### 7.1 Perché due finestre

Le uscite hanno due tempi (sez. 3.3): un servizio con una sola finestra 18-24 prende
l'onda maschile precoce e manca le ragazze che se ne andranno a 26. La finestra B esiste
per loro.

### 7.2 Perché la quota di genere

Il gruppo da raggiungere è 51% femminile nelle dimensioni ma radicalmente diverso
nell'etichetta (sez. 3.2): un servizio formalmente neutro, coi canali di contatto
standard, riprodurrebbe l'asimmetria che deve correggere. La quota impone di costruire
i due agganci; non esclude nessuno.

### 7.3 Perché l'outreach e non lo sportello

Sette giovani su dieci fuori da lavoro e studio non cercano, e a definizione costante
(2021-2024) quel segmento è fermo mentre chi cerca diminuisce (sez. 2.2). Un servizio a
domanda spontanea raggiunge per costruzione chi già cerca, cioè il segmento sbagliato. E
poiché almeno l'89% delle casalinghe non è sposata, l'aggancio femminile è
l'**attivazione**, non la sola conciliazione (sez. 3.2).

### 7.4 I KPI e le loro finestre di lettura

| KPI primario | Da | A | Lettura |
|---|---:|---:|---|
| Tasso di occupazione F 15-24 | 8,2% | 9,6% (Palermo) | **triennio pooled**, come direzione (potenza 41%) |
| Quota casalinghe F 15-24 | 13,4% | 11,3% (Palermo) | biennio (potenza 82%) |

**I KPI di popolazione dicono la direzione, non provano l'effetto.** La potenza si misura
due volte. Il modello binomiale tratta ogni annata come un campione indipendente e
promette che un triennio basti: 46% su un anno, 90% sul triennio. Ma le annate contano le
stesse persone, e il secondo metro, la variabilità che mostrano senza interventi i 33 comuni
siciliani di taglia simile a Bagheria, dice altro: per +1,4 punti di occupazione la potenza
è del 50% su un anno, del 59% sul biennio e del 41% sul triennio (che nei dati disponibili
attraversa la rottura di misura del 2021). Da un anno all'altro il tasso di un comune
oscilla attorno alla propria tendenza meno di un campione (0,36 volte la varianza
binomiale), ma i comuni divergono fra loro in modo persistente, e accorpare anni non toglie
quella divergenza. Sulle casalinghe (−2,1 punti) il biennio arriva all'82%. Le finestre
restano dichiarate prima dell'avvio, per non sceglierle dopo, e la lettura annuale non è
ammessa: spetta agli indicatori di processo (contatti nei 30 giorni, piani nei 15, utenza
per età singola e genere contro la platea residente), che oggi nessuno rileva e che il
servizio produce. → `genere_mde.csv` (fig09b)

Due precisazioni che il KPI deve portarsi dietro. La prima: il tasso femminile di Bagheria
sale già da solo (+0,65 punti l'anno dal 2018), e al ritmo attuale toccherebbe il 9,6% in
un paio d'anni. Il successo non è raggiungere quel livello, è **chiudere lo scarto da
Palermo** (oggi −1,4 punti), che sale anch'essa: il KPI si legge come differenza nelle
differenze rispetto al controfattuale, non come soglia. La seconda: 40 occupate in più su
una platea di 2.882 non si ottengono con 100 prese in carico l'anno, che richiederebbero un
effetto netto irrealistico. Il tasso comunale è l'orizzonte di convergenza e il contesto
della valutazione; l'effetto del servizio si misura sui partecipanti, contro chi entra più
tardi (sotto). E i dati comunali escono con circa due anni di ritardo: un triennio pooled
si legge quattro o cinque anni dopo l'avvio.

Se serve un equivalente in teste per la comunicazione: «+40 occupate sulla platea 2024;
il target si riparametra ogni anno come tasso-obiettivo × platea dell'anno», con la
formula pubblicata (sez. 6).

La valutazione ha due livelli. **Sui presi in carico**, rollout scaglionato: a parità di
priorità l'ordine di avvio è casuale e chi comincia più tardi fa da confronto. Perché il
confronto esista servono due coorti da 100, con ingresso al mese 0 e al mese 6: chi
aspetta, aspetta almeno sei mesi, quindi il confronto c'è sull'esito a sei mesi e non su
quello a dodici. Con 100 persone per coorte vede effetti di 18-20 punti o più (17,8 se
l'esito senza servizio è del 20%, 19,7 se è del 40%); con adesioni dimezzate la soglia sale
a 26-28 punti, e se le domande non superano i posti il sorteggio non c'è e la valutazione
diventa descrittiva. → `genere_potenza_pilota.csv`

**Sui KPI di popolazione**, il confronto è con un controfattuale **dichiarato in anticipo:
Palermo**. Il prerequisito è stato controllato: la pendenza del tasso femminile di Bagheria
2018-2024 (+0,65 punti/anno) non si distingue da quelle di Palermo e dell'Italia (p = 0,29 /
0,33). Con sei annate il test ha poca potenza, quindi non prova tendenze parallele: dice
solo che i dati non le smentiscono. E tratta ogni annata come un campione indipendente:
senza quel modello, la distanza fra la pendenza di Bagheria e quella di Palermo (−0,09 punti
l'anno) è più piccola di quella del 67% dei comuni di taglia simile, un confronto indulgente
perché include le divergenze reali fra comuni. → `genere_pretrend.csv`,
`genere_pretrend_390.csv`

Il costo, in ordine di grandezza, è fra 205.924 e 256.105 euro l'anno per la dotazione
minima, fra 1.030 e 1.281 euro per posto, esperienze retribuite escluse: il dettaglio dei
parametri e delle voci escluse è nella policy, §9-bis. → `genere_costo_pilota.csv`

### 7.5 Il dato che il servizio produce

Ogni presa in carico genera un record pseudonimizzato, titolo/indirizzo → data di
uscita → condizione → genere ed età → barriera dichiarata → azione → esito a 3/6/12
mesi. È l'unico modo per misurare a Bagheria la relazione individuale fra titolo e
condizione lavorativa (sez. 4): la proposta non consuma soltanto dati, **ne produce
dove le statistiche pubbliche finiscono**, con una dashboard trimestrale aggregata come
impegno di accountability.

### 7.6 Rotta F: il modulo di genere

La quota di genere (7.2) impedisce al servizio di riprodurre l'asimmetria che deve
correggere, ma **non dice come la si corregge**. Lo dice `docs/policy/POLICY_PONTE_19.md` §4-bis,
che è la parte di Ponte 19 che risponde al focus principale del bando: qui se ne riassume
l'ossatura, perché una relazione che mette il genere al centro non può rimandare altrove
l'unico pezzo di intervento costruito su di esso.

Il meccanismo in una riga: **le ragazze di Bagheria si spostano per studiare e si fermano
per lavorare**. Il modulo apre una componente su ciascuno dei tre anelli che le sezioni 3 e
5 mostrano rotti, il contatto, la barriera e la domanda.

**F1 - Contatto: l'etichetta come canale, non come elenco.** Le 387 casalinghe **non sono
identificabili**: il censimento è aggregato, nessuna lista nominativa esiste né va
costruita. L'etichetta dice dove cercare, non chi. Il contatto passa quindi dai luoghi dove
quella popolazione è già visibile: le sedi secondarie cittadine, i servizi sociali, i
consultori, le associazioni, ed è la traccia femminile delle due tracce di contatto: per le
ragazze esiste già un'etichetta censuaria da cui aprire il colloquio, per i ragazzi
un'etichetta così non c'è (sez. 3.2). Che cosa ci sia dietro l'etichetta lo chiede il
colloquio: il censimento non lo osserva.

**F2 - Barriera: non il collegamento, ma l'orario e il mezzo dati per scontati.** È la
componente controintuitiva, ed è il punto in cui la proposta rinuncia alla soluzione che
tutti si aspettano: l'intervento infrastrutturale non è sostenuto dai dati (7.0), quindi
F2 non si appoggia all'offerta di trasporto e non finanzia trasporto. Quello che resta di genere è
il canale: verso Palermo le donne vanno sul mezzo collettivo e gli uomini in auto (treno
31,5% contro 16,4%, sez. 5.4). Un servizio che dia per scontata l'auto seleziona per genere,
e lo fa in silenzio. La regola operativa che ne discende è una sola: nessuna opportunità
entra nel piano di transizione senza **verifica di raggiungibilità col mezzo collettivo
negli orari reali della posizione**. Costa istruttoria, non budget.

**F3 - Domanda: la leva che il Comune ha già in mano.** Criteri **premiali** di pari
opportunità nelle gare e nelle concessioni comunali per l'assunzione di donne e di under 36,
sul modello dell'art. 47 del DL 77/2021 (appalti PNRR); per le gare ordinarie la base è nelle
clausole sociali del Codice dei contratti pubblici (D.Lgs. 36/2023), da verificare con
l'ufficio gare. La verifica dell'esito a 6 e 12 mesi si concentra sulle **donne 22-25**. Premialità, non riserva né requisito di residenza: il
radicamento locale dell'esito si misura a valle, non si impone in gara. È l'unica delle tre
componenti che non richiede una struttura nuova: è uno strumento amministrativo esistente
riorientato su un target dichiarato. Cautela: il volume è piccolo per costruzione, e F3 rende
la domanda **verificabile**, non la crea (sez. 2.4, 3.1).

**Target.** La platea sono le **573** ragazze 15-24 inattive e non studenti (sez. 3.2); la
presa in carico pilota è la metà dei 200 previsti dalla quota (7), concentrata sulla
finestra prioritaria **22-25**, dove il vantaggio educativo non si converte e la ritenzione
si rompe senza rientri (sez. 3.3).

**KPI.** Il primario del modulo è la **quota di casalinghe 15-24** (13,4% verso l'11,3% di
Palermo), non il tasso di occupazione. La ragione è la finestra di lettura e non la
preferenza: fra i due è l'unico che, contro la variabilità dei comuni di taglia simile,
supera l'80% di potenza su una finestra che non attraversa la rottura del 2021, il biennio,
quindi il primo a restituire un verdetto (con il ritardo di circa due anni dei dati
comunali). È però una stima di modello (sez. 3.2): si legge solo dentro la definizione
2021+ e sempre accanto al tasso di occupazione, che è un conteggio. L'occupazione femminile
resta l'esito che dà senso al primo e si legge sul triennio pooled, come direzione (7.4).

**Cosa il modulo non promette**, con lo stesso metro della sezione 9: non identifica le
387; non attribuisce la condizione di casalinga a una scelta né a un vincolo familiare
osservato, perché lo stato civile esclude il matrimonio precoce come canale ma non osserva
convivenze né maternità; non propone interventi sul trasporto; e non sostiene alcuna tesi
di segregazione per indirizzo di studio, perché l'anagrafe MIUR dà le sedi e non gli
iscritti per genere e indirizzo. Quel dato non esiste, e senza di esso «gli indirizzi
femminili non convertono» resterebbe un'ipotesi travestita da evidenza.

---

## 8. Le figure

La locandina chiede 2-3 visualizzazioni avanzate. La terna consegnata copre la voce
obbligatoria della locandina (profilo e benchmarking), il focus esplorativo scelto (il
genere) e l'obiettivo del brief (la fuga di talenti):

1. **`fig05_forbice`** - il paradosso in un'immagine: il quadrante «più istruite, meno
   occupate» sulla stessa fascia 15-24. La forbice nel tempo sta in `fig05b`.
2. **`fig07_ritenzione_eta`** - il *quando* della fuga, per genere: profilo di
   ritenzione per età singola con la finestra 22-25. La scala decennale sta in `fig07b`.
3. **`fig04_mappa_sicilia`** - la scala: coropleta dei 390 comuni e istogramma delle due
   distribuzioni, «nel 2024 Bagheria arriva dove stava la mediana siciliana nel 2011».
   La persistenza della graduatoria (rho di Spearman) sta in `fig04b`.

Il criterio di scelta, dichiarato perché sia contestabile: `fig04` mette Bagheria fra
390 comuni invece di trattarla come un caso isolato, `fig05` porta il focus scelto al suo
punto più netto, `fig07` è l'unica figura che dice **a che età** si parte, ed è la ragione
per cui Ponte 19 ha due finestre.

A supporto: **`fig09_kpi_finestra`** traduce il KPI in persone e lo mette di fronte al
restringimento della platea (sezione 6); **`fig09b_potenza`** dichiara quanto il tasso
comunale può dire sull'intervento, con due metri di potenza affiancati (sezione 7.4).

Il terzo focus del brief ha una serie propria, aggiunta con il thread mobilità:

- **`mob_fig01_verso_palermo`** - la carta a flussi: dove vanno i pendolari di Bagheria,
  per studio e per lavoro, col nome del comune di arrivo. È la risposta letterale alla
  domanda della locandina, ed è la **prima riserva** della terna: resta fuori perché
  `fig04` è già una carta e perché togliere `fig07` lascerebbe la finestra d'età della
  proposta senza la figura che la giustifica.
- **`mob_fig02_ribaltamento`** - il risultato del thread: le due misure unite da una linea
  la cui pendenza è il risultato, più la distribuzione dei 390 comuni.
- **`mob_fig03_treno_genere`** - mezzo e orario per genere, e il pannello che impedisce di
  leggere la figura come «serve più treno».
- **`mob_fig04_taglia_distanza`** - la figura che toglie di mezzo un'affermazione invece di
  aggiungerne uno: l'anomalia di `M2` era un effetto della taglia.

**`fig12_pendolarismo`** resta come lettura sul censimento permanente 2018-2019, cioè la
replica indipendente della sezione 5.2. Le altre stanno nei notebook come apparato.

Tutte le figure: titolo che enuncia il risultato, fascia d'età dichiarata, fonte e
cautele in caption, palette colorblind-safe, PNG 300dpi + SVG in `figures/`.

---

## 9. Cosa questa relazione non afferma

1. **Il NEET 15-34 comunale non esiste** nei dati pubblici: le due misure usate (15-29
   al 2011, «fuori da lavoro e istruzione» 15-24 dal 2018) sono etichettate e mai fuse.
2. **Nessun tasso di occupazione per titolo di studio a Bagheria**: l'incrocio
   individuale non è pubblicato (sez. 4); ogni affermazione del tipo «i diplomati di
   Bagheria…» sarebbe inventata.
3. **Nessuna età sul pendolarismo**: la destinazione ora c'è (sez. 5, matrice ISTAT), ma
   né la matrice né il censimento permanente hanno la dimensione età. Il pendolarismo del
   target 15-34 non è isolabile; il motivo dello spostamento è un'informazione d'età
   parziale e viene usata come tale. La ritenzione di coorte resta un saldo netto senza
   destinazioni: le due misure non si sommano.
4. **Nessuna stima causale**: confronti territoriali ed ecologici orientano la diagnosi;
   il disegno di valutazione (sez. 7.4) serve proprio a produrre l'evidenza che oggi
   manca. L'inattività non è attribuita a una singola causa non osservata.
5. **Nessuna interpolazione**: il 2020 mancante resta mancante; la rottura di misura
   2019→2021 è dichiarata ogni volta che si cita la serie delle componenti.
6. **La finestra 22-25 è pooled**: sull'anno singolo oscilla, e come lettura annuale non
   verrebbe usata.
7. **Nessuna associazione fra uso del mezzo collettivo e divario di genere**: testata sui
   381 comuni non capoluogo e **non trovata** (sez. 5.4). È un risultato ecologico: non
   esclude un effetto sulla singola persona, ma nessuna parte della proposta si appoggia
   all'offerta di trasporto.
8. **Nessun primato sui titoli**: Bagheria non produce più istruzione dei territori di
   confronto. Sta davanti solo sulla competenza di base del 2011 (`I8`), ed è ultima del
   panel su diploma o laurea (`I6`) e titolo universitario (`I7`). Ciò che si afferma è la mancata
   conversione, non un surplus di titoli da convertire (sez. 4).
9. **Nessuna misura diretta dell'emigrazione, né per titolo di studio**: la ritenzione di
   coorte è un saldo netto fra partenze e arrivi, senza destinazione e senza titolo. Sul
   totale dei 15-34, a parità di coorti, Bagheria perde quanto la Sicilia: la «fuga di
   talenti» che questa relazione documenta è un tempismo di genere, non un'emorragia
   complessiva (sez. 3.3 e 6). Il dato esiste alla fonte ma non è pubblicato per il comune: i
   trasferimenti di residenza sono rilevati comune per comune, ISTAT ne pubblica età e titolo
   di studio solo fino alla provincia, e per Bagheria solo i totali per sesso, verso un altro
   comune o verso l'estero. I dati elementari, anonimi, si possono chiedere a ISTAT.
10. **Le condizioni non professionali sono stime, non conteggi**: dal 2021 casalinghe,
   studenti, chi cerca e la platea degli inattivi non studenti sono somme di probabilità di
   un modello ISTAT di cui non è pubblicato l'errore (sez. 3.2). Si leggono solo dal 2021,
   e mai senza il tasso di occupazione accanto, che è un conteggio.
11. **Il tasso comunale non prova l'effetto del servizio**: contro la variabilità dei
   comuni di taglia simile nessuna finestra di lettura arriva all'80% di potenza sul tasso
   di occupazione femminile (sez. 7.4). L'effetto si misura sui partecipanti, e nel primo
   anno il pilota vede solo effetti grandi.

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

Stato delle verifiche al 2026-09-23: sensore `nbconvert` **verde sui quattro notebook**;
`pipeline.verifica` **934/934 PASS**; la matrice del pendolarismo ricostruisce **sette su
sette** gli indicatori `M` pubblicati da 8milaCensus e i due totali nazionali dichiarati da
ISTAT; nessun numero di questa relazione è scritto a mano - ogni cifra ha accanto il file o
la cella che la rigenera.

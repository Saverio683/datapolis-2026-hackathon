# Bagheria produce titoli e non li converte

## Relazione tecnica e proposta di intervento - DataPolis 2026, «Analisi e Visione per i Giovani di Bagheria»

Bagheria, 2026-08-28. Questa relazione accompagna i tre deliverable richiesti dal
concorso: il **technical notebook** (`notebooks/analisi.ipynb`, `notebooks/genere.ipynb`,
`notebooks/educazione.ipynb`), le **visualizzazioni** (`figures/`) e la **policy
proposal** (`docs/POLICY_PONTE_19.md`). Le decisioni editoriali che questa relazione non
rimette in discussione - tesi, figure candidate, limiti dichiarati - stanno in
`docs/RELAZIONE.md`.

Regola che vale in ogni riga: **nessuna cifra è scritta a mano**. Ogni numero citato
punta alla cella di notebook o al file di `data/processed/` che lo produce, e si
rigenera eseguendo la pipeline (sezione 1). Dove un numero ha una cautela, la cautela
sta accanto al numero, non in fondo.

---

## In una pagina

> **Bagheria produce titoli e non li converte. La conversione fallisce soprattutto sulle
> ragazze (più istruite del panel, 8,2% di occupazione, il minimo dei quattro territori
> in 6 anni su 6), in una finestra d'età stretta (22-25, ritenzione 96,3 contro ~103 in
> Italia), e il vincolo di mobilità ha lo stesso segno. Chi resta fuori non è chi cerca
> lavoro: il 70,6% dei giovani fuori da lavoro e studio non cerca nemmeno.**

I tre thread di analisi - genere, educazione, mobilità - non danno tre diagnosi diverse:
danno **una diagnosi in tre punti della stessa catena**, formazione → conversione →
permanenza. Ogni anello viene da una tavola diversa, quindi nessuno è la riformulazione
di un altro.

La proposta (sezione 7) è un servizio comunale di transizione e riattivazione con due
finestre di ingaggio e un target esplicito sul genere. E ha un vincolo di misura che la
distingue da un auspicio:

> **La platea femminile 15-24 è già nata e cala del 15,5% al 2034. Le "+40 occupate"
> valgono +18 nel 2029 e −2 nel 2034 (fig09). Cioè il KPI va scritto in tasso, non in
> teste, un dettaglio che di solito nessuno vede prima di scriverlo male.**

### La risposta al brief, in breve

| Richiesta della locandina | Risposta | Dove |
|---|---|---|
| Profiling statistico & benchmarking (Sicilia, Italia, Palermo) | ✅ con intervalli di confidenza, percentili sui 390 comuni siciliani e due gruppi di comuni pari dichiarati | sezioni 2-3 |
| Focus: **impatto delle differenze di genere** | ✅ focus principale | sezione 3 |
| Focus: **titolo di studio × condizione lavorativa** | 🟡 l'incrocio non esiste nei dati comunali (verificato); risolto con due misure parallele sulla stessa fascia | sezione 4 |
| Focus: **pendolarismo verso Palermo** | ✅ misurato con la matrice origine-destinazione ISTAT: **91,1%** di chi esce per studio e **65,1%** di chi esce per lavoro va a Palermo, e lo scarto di genere si ribalta fra i due motivi | sezione 5 |
| NEET 15-34 | 🔴→🟡 non calcolabile a livello comunale: due misure etichettate, mai fuse | sezione 2 |
| Proposta di intervento | ✅ Ponte 19, con KPI misurabili e finestre di lettura dichiarate | sezione 7 |
| Technical notebook riproducibile | ✅ sensore `nbconvert` verde sui quattro notebook; 650 controlli indipendenti PASS | sezione 1 |
| 2-3 data viz avanzate | ✅ tre candidate + sei di supporto | sezione 8 |

I 🟡 non sono lavori a metà: sono i punti in cui i dati pubblici finiscono, dichiarati
invece che aggirati. In un concorso sulla cultura del dato, sapere dove i dati non
arrivano è parte della risposta, ed è uno dei motivi della proposta, che quei dati
mancanti li produce (sezione 7.5).

> **Un 🟡 è diventato ✅, e vale la pena dire come.** Fino al 2026-08-28 questa relazione
> dichiarava il pendolarismo verso Palermo non misurabile. Lo era con le fonti allora
> usate — il censimento permanente pubblica solo il «fuori comune» aggregato — ma non in
> generale: la matrice origine-destinazione di ISTAT dà il comune di arrivo, e nessuno era
> andato a cercarla. Un limite dichiarato resta un'ipotesi sulle fonti, non un fatto sul
> mondo: va riaperto quando qualcuno ha tempo di riaprirlo (sezione 5).

---

## 1. Metodo: la relazione si rigenera da zero

L'intera analisi è una pipeline riproducibile. Da ambiente pulito:

```bash
uv sync                                   # ambiente Python
uv run python -m pipeline.fetch           # scarica i raw da tutte le fonti
uv run python -m pipeline.build           # raw -> data/processed/
uv run jupyter nbconvert --to notebook --execute notebooks/analisi.ipynb
uv run jupyter nbconvert --to notebook --execute notebooks/genere.ipynb
uv run jupyter nbconvert --to notebook --execute notebooks/educazione.ipynb
Rscript viz/build_all.R                   # tutte le figure in figures/
uv run python -m pipeline.verifica        # 650 controlli indipendenti
```

Tre proprietà non decorative:

- **Provenance completa.** Ogni file in `data/raw/` è append-only e ha una riga in
  `docs/sources.md` con URL esatto, data e parametri. Le correzioni vivono in
  `pipeline/`, mai nei raw.
- **Verifica indipendente.** `pipeline/verifica.py` ricalcola **650 numeri chiave
  direttamente dai raw con implementazioni alternative** (intervalli di Wilson/Newcombe
  riscritti, modello lineare di probabilità in forma analitica, matching rifatto, coorti
  dalle classi quinquennali): 650/650 PASS al 2026-08-28. Se un raw cambia, il pin
  fallisce finché notebook e attesi non vengono riallineati.
- **Separazione dei ruoli.** Python trasforma, R disegna: l'interfaccia sono i CSV di
  `data/processed/`, e nessuna logica di trasformazione vive negli script delle figure.

### Le definizioni, fissate una volta

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
  livelli delle componenti no (`docs/sources.md` §8).
- **NEET**: il NEET 15-34 della locandina **non è calcolabile a livello comunale** - la
  fascia non esiste nei dati. Si usano due misure etichettate e mai unite: il NEET
  **15-29 al 2011** (8milaCensus, `L4`) e il proxy **«fuori da lavoro e istruzione»
  15-24, 2018-2024** (censimento permanente). Fasce e definizioni diverse: affiancate,
  mai in serie.

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

Il confronto colloca subito il punto critico: l'occupazione 15-24 di Bagheria (12,4%) è
**3,1 punti sotto la Sicilia** (15,6%), e gli inattivi non studenti (19,0%) sono **4,2
punti sopra** (14,8%). Complessivamente il 26,9% dei giovani è fuori sia dal lavoro sia
dallo studio, contro il 22,3% siciliano. → `edu_kpi_dashboard.csv`

Dentro quel 26,9% sta il dato che orienta tutta la proposta: **il 70,6% non è
classificato come persona in cerca di occupazione**. Non sono giovani che cercano e non
trovano: sono giovani che non arrivano a cercare.

### 2.2 Il recupero c'è, la convergenza no

Fra 2018 e 2024 l'occupazione 15-24 (totale) sale da 8,2% a 12,4% e la quota fuori da
lavoro e studio scende da 37,7% a 26,9%. Ma la scomposizione dice da dove viene il
miglioramento: **chi cerca lavoro cala di 10,2 punti (18,1% → 7,9%), gli inattivi non
studenti di 0,6 (19,6% → 19,0%)**. E il gap occupazionale con la Sicilia è **−3,1 punti
sia nel 2018 sia nel 2024**: Bagheria migliora alla velocità del contesto, non di più.
→ `edu_finding_summary.csv` (⚠️ sulla serie vale la rottura di misura 2019→2021: i gap
reggono, i livelli delle componenti no)

Lo stesso pattern sulla fascia adulta: fra i 25-49enni la quota con almeno il diploma
passa da 56,2% a 62,4% e l'occupazione da 43,0% a 53,6%, ma nel 2024 i divari con la
Sicilia restano **−4,1 e −5,7 punti**. → `edu_kpi_dashboard.csv`

### 2.3 Il lungo periodo: progresso assoluto, arretramento relativo

I tre censimenti 1991/2001/2011 e il ponte verso il censimento permanente separano due
cose che di solito si confondono: Bagheria **migliora in assoluto e arretra in
posizione**.

- NEET 15-29: dal 42,9% (1991) al 40,1% (2011), ma la posizione fra i 390 comuni
  siciliani passa **circa dal 17° all'88° percentile**: molti altri comuni hanno ridotto
  il problema molto più in fretta. → `edu_historical_bagheria.csv`, verifica incrociata
  in `notebooks/genere.ipynb`
- Uscita precoce dalla scuola (`I5`): 40,8% → 28,6%, ma **56° → 70° → 83° percentile**.
  → `genere_frattura_istruzione.csv`
- Occupazione femminile 15+: 18,1% (2011) → 23,7% (2024), ma la mediana regionale sale
  da 23,6% a 28,3%. **Nel 2024 Bagheria arriva dove stava la mediana siciliana nel
  2011** (fig04). La graduatoria dei 390 comuni del 2011 predice quella del 2024 con rho
  di Spearman **0,848**, e il 74% del quintile più basso del 2011 è ancora lì, Bagheria
  compresa: il posizionamento del 2011 non era una fotografia scaduta ma una previsione
  verificata. → `genere_mappa_2011_2024.csv`, sezione «I claim reggono al 2024?»
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

Tre tratti reggono a tutte e due le letture e vanno in proposta: disoccupazione
femminile estrema (8/10 comuni sotto), occupazione giovanile bassa (2/10 sotto),
autonomia abitativa giovanile al minimo (0/10 sotto). E la divergenza più informativa è
sull'occupazione femminile: dentro le gemelle strutturali Bagheria è nella norma (3/10),
fra i comuni ugualmente scolarizzati è **penultima** (1/10). **A pari istruzione, il
lavoro femminile non arriva: non è un tratto di fascia territoriale.** I modelli
comunali del thread educazione confermano il segno (occupazione giovanile
osservata−prevista **−5,9 punti** [bootstrap −7,7, −4,3], CV R² 0,05: si cita come
conferma di segno, mai come quantità attribuibile al comune).
→ `genere_posizionamento.csv`, `genere_pari_lenti.csv`, `edu_model_robustness_2011.csv`

---

## 3. Il focus di genere: il capitale umano che il territorio spreca di più è femminile

### 3.1 La forbice: più istruite, meno occupate

Nel 2024, a Bagheria:

| | Maschi | Femmine | Scarto |
|---|---:|---:|---:|
| Almeno diploma (9-24) | 29,2% | 33,4% | **−4,2 pp** (F avanti) |
| Occupazione (15-24) | 16,5% | 8,2% | **+8,3 pp** (F indietro) |

→ `genere_quadro_sintesi.csv`

Il vantaggio educativo femminile sulla fascia 9-24 è il più ampio del panel (Palermo
−1,8, Sicilia −2,7, Italia −2,2); il gap occupazionale è 8,3 punti [IC 95% 6,6-10,0].
→ `genere_gap_occupazione_ci.csv`

La scala su cui leggere il gap è stata scelta con un modello, non a occhio (fig01).
**In punti** il gap di Bagheria non è un'anomalia locale (pooled 2022-24: +1,1 verso
Palermo, p=0,03; −1,8/−1,9 verso Sicilia e Italia). **In rapporto** (M/F = 2,01 contro
1,56 nazionale) Bagheria è la peggiore del panel, ma il rapporto oscilla fra le annate.
**Il tratto locale è il livello: il tasso di occupazione femminile all'8,2% [Wilson
7,2-9,2] è il minimo dei quattro territori in tutte e 6 le annate disponibili**, ed è
testato, sotto Palermo di 1,2 punti, sotto la Sicilia di 1,9, sotto l'Italia di 8,9
(p ≤ 0,0001 pooled 2022-24). Il gap inoltre **si sta allargando**: +0,21 punti/anno
(IC 0,06-0,35, p=0,008). → sezioni «Punti percentuali o rapporto?», «Modello lineare di
probabilità» e «Trend 2018-2024» di `notebooks/genere.ipynb`

Sulle cautele dell'istruzione la relazione è esplicita, perché il claim va maneggiato:
sulla **stessa fascia 15-24** il vantaggio educativo femminile di Bagheria (+4,8) è un
pareggio con la Sicilia (+4,7), e sul bound 18-24 il primato non regge. Il claim
robusto non è «le più istruite d'Italia»: è la coppia **distacco dal vicinato** (+5,7
contro +2,5) **e mancata conversione**. Su 1.000 ragazze 15-24 di Bagheria, 510 hanno
almeno il diploma e 82 lavorano; fra i coetanei, 462 e 165 (fig11). Le due barre hanno
la stessa base e **non sono un funnel**: l'incrocio individuale non esiste (sezione 4).
→ `genere_per_1000.csv`, `genere_forbice_quadrante.csv`

### 3.2 Dentro l'inattività: le casalinghe ventenni, nubili

Il 13,4% delle ragazze 15-24 di Bagheria si dichiara **casalinga**: 387 persone, contro
il 4,6% nazionale, serie 2018-2024 stabile. Sull'aggregato pesa la struttura per età: i
bounds vanno dal 18,8% delle 18-24enni al 25,8% delle 20-24enni; l'eccesso
sull'incidenza italiana vale **254 ragazze**. → `genere_casalinghe.csv`,
`genere_casalinghe_bounds.csv`

Chi sono? Il canale del matrimonio precoce **non regge i numeri**: al 1.1.2025 le già
coniugate 15-24 sono 41 (1,4%) contro 387 casalinghe - **almeno l'89% è nubile** - e la
quota di coniugate 20-24 di Bagheria (2,7%) sta *sotto* Palermo (3,2%) e Sicilia
(2,9%). Il canale è la famiglia d'origine, non la famiglia propria: la risposta di
policy è un servizio di **attivazione**, non solo di conciliazione.
→ `genere_stato_civile.csv` (fonte DCIS_POPRES1, denominatori coincidenti alla singola
unità con la tavola censuaria)

Il gruppo degli «invisibili» - fuori da lavoro, studio e ricerca - **non è femminile
nelle dimensioni**: 573 ragazze e 549 ragazzi (51% F). È femminile **nell'etichetta**:
fra le ragazze prevale una condizione dichiarata (387 casalinghe contro 50), fra i
ragazzi il residuo senza nome («altra condizione»: 485 contro 183). Qualunque outreach
deve coprire entrambi i generi con agganci diversi - per le ragazze il carico di cura ha
già un nome censuario, per i ragazzi non c'è neppure quello.
→ `genere_composizione_stato_dettaglio.csv` (fig02)

### 3.3 La fuga ha un tempismo di genere: la finestra 22-25

La ritenzione di coorte 2021-2024 mostra due uscite diverse (fig03, fig07):

- **i ragazzi si perdono presto e a ondate** (età 17-19 e 23-24), con **rientri netti
  dopo i 26**;
- **le ragazze tengono fino ai 23-24 e si perdono dai 24-25 in poi, senza rientri**:
  coorte 25-29 a **96,3** contro 103,0 in Italia, esattamente l'età in cui il vantaggio
  educativo dovrebbe convertirsi in occupazione e non lo fa.

→ `genere_coorti.csv`, `genere_ritenzione_eta.csv`

**La finestra utile per intervenire sulle ragazze è 22-25 anni** - prima la curva è
sopra la pari, dopo la perdita è già avvenuta. ⚠️ È una lettura **pooled sul triennio**:
le transizioni annuali oscillano fino a 8 punti sulla stessa età (n ~290 per cella);
l'anno singolo è un controllo, non un titolo. → `genere_ritenzione_transizioni.csv`

Alla scala decennale la frattura è più netta, e risponde all'obiezione che tre anni non
bastano: la coorte 15-19 seguita per dieci anni passa, sulle femmine, da **102,9%
(2001-2011) a 88,6% (2011-2021)**, e sui maschi da 98,4% a **83,9%**, ~14 punti di
ribaltamento, nello stesso decennio del muro sul lavoro (sez. 2.3).
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
con la lente dei pari a pari istruzione (sezione 2.4). Tutto converge sulla stessa
conclusione: **il collo di bottiglia non è la produzione di titoli - quasi universale
alla base già nel 2011, con il 96,7% dei 15-19enni almeno alla licenza media - ma la
conversione dei titoli in lavoro.** → `edu_historical_benchmarks_2011.csv`

La versione individuale della domanda resta la più importante del territorio, ed è per
questo che la proposta la trasforma in un output: il dataset di servizio della sezione
7.5 misura, per la prima volta a Bagheria, titolo → azione → esito sulla singola
persona.

---

## 5. Il pendolarismo verso Palermo: si esce per studiare, non per lavorare

Il terzo focus del brief, e l'unica sezione in cui questa relazione ha **cambiato idea su
sé stessa**. Fino al 2026-08-28 dichiarava che «nessuna fonte disponibile identifica Palermo
come destinazione». Era vero per le fonti allora usate — il censimento permanente pubblica il
pendolarismo comunale solo come dentro/fuori comune, e la dimensione `LOC_DEST` del dataflow
è servita come valore unico — **e non in generale**: ISTAT pubblica le *matrici del
pendolarismo*, l'origine-destinazione comune per comune con sesso, motivo, mezzo, fascia
oraria e durata (censimenti 1991/2001/2011), rifatta sul solo lavoro col censimento
permanente 2021. → `notebooks/mobilita.ipynb`, `docs/sources.md` §12

Il tracciato è a campi fissi e senza intestazione: un campo sfalsato darebbe numeri
plausibili e sbagliati. Il controllo non è stilistico — dalla matrice si **ricostruiscono
sette indicatori `M` di 8milaCensus già pubblicati** (`M3` 76,1 · `M4` 19,6 · `M5` 65,2 ·
`M6` 8,4 · `M7` 25,7 · `M8` 83,3 · `M9` 3,6, **sette su sette alla prima cifra decimale**) e i
totali nazionali del 2011 e del 2021 coincidono con quelli dichiarati da ISTAT. Il che
dimostra anche una cosa utile al vincolo di fonti della locandina: la matrice **non è una
fonte alternativa a 8milaCensus, è il livello sottostante** da cui quegli indicatori sono
calcolati. → cella «La fonte, e come si controlla che sia letta bene»

### 5.1 La destinazione ha un nome, ed è una sola

| Fra chi esce dal comune, quanti vanno a Palermo | quota | percentile sui 381 comuni non capoluogo |
|---|---:|---|
| **per studio**, 2011 | **91,1%** | 93° |
| **per lavoro**, 2011 | **67,5%** | 93° |
| **per lavoro**, 2021 | **65,1%** | 91° |

Il secondo comune di destinazione è Santa Flavia al 6,8%: **non esiste una seconda
direzione**. Il percentile è calcolato sulla misura comparabile — quota di chi esce diretta
al *proprio* capoluogo di provincia — perché «quanti vanno a Palermo» per un comune di Ragusa
è zero per costruzione. → `mob_flussi_bagheria.csv`, `mob_sintesi.csv`, fig `mob_fig01`

È il fatto che rende la mobilità una leva di policy e non un dettaglio descrittivo: non c'è
da scegliere quale destinazione servire.

### 5.2 Il ribaltamento: lo scarto di genere cambia segno col motivo

La misura è la quota di chi **esce dal comune** sul totale di chi si sposta quotidianamente
per quel motivo, letta per genere. Il denominatore è già condizionato al motivo — chi si
sposta per lavoro un lavoro ce l'ha — quindi lo scarto **non è un riflesso del divario
occupazionale** della sezione 3: è una misura indipendente sullo stesso passaggio. E il
conteggio del 2011 **non è una stima**: i record di tipo `S` sono enumerazione esaustiva.

| Quota che esce dal comune, 2011, scarto F − M | Bagheria | Sicilia | Italia | Comune di Palermo |
|---|---:|---:|---:|---:|
| **per studio** | **+2,6** | +1,4 | +1,8 | −0,1 |
| **per lavoro** | **−12,1** | −4,6 | −4,8 | −2,0 |
| **il salto fra i due** | **14,7** | 6,0 | 6,5 | 1,9 |

→ `mob_ribaltamento.csv`, `mob_ribaltamento_territori.csv`, fig `mob_fig02`

Il verso cambia ovunque; la particolarità di Bagheria è **l'ampiezza**: due volte e mezza il
salto siciliano, e sul lavoro il **13° percentile** dei comuni siciliani. Le ragazze di
Bagheria si muovono. Smettono quando il motivo diventa il lavoro.

**La replica tiene, su una fonte che non condivide niente.** La stessa misura sul censimento
permanente 2018-2019 — altra rilevazione, altro metodo, sette anni dopo — dà per Bagheria
+11,3 e +10,9 contro +5,6/+5,9 siciliano e +6,5/+6,1 italiano. È lo stesso punto di rottura
della forbice (sezione 3.1) e della finestra 22-25 (sezione 3.3), da una terza tavola.
→ `genere_pendolarismo.csv`, fig12

**E non è il divario occupazionale travestito.** Controllando il tasso di occupazione
femminile `L11` e il divario occupazionale del comune, il residuo di Bagheria passa da −8,7 a
−7,0 punti: la misura resta in piedi da sola.

### 5.3 «Bagheria si muove poco» era una lettura sbagliata di un numero giusto

La versione precedente di questa sezione scriveva: «contesto assoluto, Bagheria si muove
poco — mobilità fuori comune `M2` al 25° percentile». **Il percentile è esatto, la lettura
no.** Fuori comune si va per mancanza di lavoro dentro, e Bagheria è il comune più grande
della corona di Palermo: 12.000 pendolari contro i 3.000 di Ficarazzi, che infatti manda
fuori tre pendolari su quattro contro i due su cinque di Bagheria.

A parità di **distanza dal capoluogo e di dimensione** — due variabili geografiche, non di
comportamento — il residuo di Bagheria è di **−1,9 punti** (z = −0,13) e il percentile passa
dal 36° grezzo al **48°**. Bagheria si muove esattamente quanto ci si aspetta da un comune
della sua taglia a quella distanza. → `mob_taglia_distanza.csv`, fig `mob_fig04`

Vale anche per `M4` (mobilità studentesca al 18° percentile), che già la versione precedente
segnalava non essere di per sé un dato negativo: è un rapporto fuori/dentro comune e Bagheria
ha scuole proprie (3 sedi tecniche, anagrafe MIUR). Il modello lo conferma: residuo −0,8
punti. → `edu_technical_schools.csv`

**La particolarità di Bagheria non è quanto si muove. È chi si muove, e per quale motivo.**

### 5.4 Il treno è il canale femminile — e il vincolo non è l'offerta di trasporto

Mezzo, orario e durata sono rilevati su campione nei comuni sopra i 20.000 abitanti: sono
stime, e stanno in una tabella separata dai conteggi esaustivi apposta. La precisione è
misurata e non assunta — il file porta la propria misura d'errore, perché per gli stessi
strati esistono sia il conteggio esaustivo sia la stima: errore relativo mediano **0,9%**,
massimo 8,6% sullo strato più piccolo.

Le quote qui sotto sono **calibrate sui margini esatti** dei conteggi esaustivi: la
calibrazione non cambia la conclusione, la rafforza — lo scarto sul treno passa da 14,5 a
15,1 punti.

| Fra chi esce da Bagheria (2011) | donne | uomini |
|---|---:|---:|
| mezzo collettivo | **34,7%** | 18,9% |
| di cui treno | **31,5%** | 16,4% |
| mezzo privato a motore | 63,6% | **79,0%** |

→ `mob_mezzo_genere.csv`, fig `mob_fig03`

Le donne raggiungono Palermo **sul mezzo collettivo**, gli uomini in auto. Partono anche più
tardi (prima delle 7:15 il 54,4% contro il 65,0%) e viaggiano più a lungo (31-60 minuti per
il 43,8% contro il 36,2%), per 17 chilometri.

**Ma il treno di Bagheria non è sottoutilizzato: è già l'asset di mobilità più distintivo che
il comune abbia**, al 98° percentile siciliano per quota di chi esce che lo usa (97° a parità
di distanza e taglia). Una proposta del tipo «portare il treno a Bagheria» risolverebbe un
problema che non esiste.

> **Un risultato negativo, riportato perché è stato testato.** L'ipotesi naturale — dove il
> mezzo collettivo pesa di più il divario di genere è più piccolo — **non regge** sui 390
> comuni: rho di Spearman −0,10 (p = 0,06) con il segno sbagliato, e il quartile con più
> mezzo collettivo ha il divario più ampio; sul treno l'associazione è nulla (p = 0,29).
> Coerentemente, l'ultimo miglio a Palermo non è un collo di bottiglia: dal GTFS di AMAT — la
> terza fonte indicata dalla locandina — le fermate «Stazione Centrale» hanno 18 linee e
> ~125-130 passaggi l'ora dalle 7 alle 21.
>
> **Conseguenza di progettazione**: l'intervento infrastrutturale è escluso *dai dati*, non
> per preferenza. La leva è il passaggio studio→lavoro, che è dove il divario si apre — cioè
> esattamente la finestra B di Ponte 19 (sezione 7).

### 5.5 Il bersaglio, in persone

Portare le pendolari di Bagheria al divario **medio siciliano** — non alla parità, al semplice
comportamento regionale — vale **+279 donne** che lavorano fuori comune; la parità piena con
gli uomini di Bagheria ne varrebbe 449. È lo stesso ordine di grandezza degli scenari
occupazionali della sezione 3 (+239 con la parità coi coetanei, +262 col tasso femminile
italiano), su misure che non condividono denominatore. → `mob_sintesi.csv`, `genere_gap_persone.csv`

**I limiti, per primi.**

1. **Nessuna età.** Né la matrice né la tavola del censimento permanente hanno la dimensione
   età (verificato: `AGE_NOCLASS` servita solo come `TOTAL`, anche a livello nazionale). Il
   target 15-34 del brief **non è isolabile sul pendolarismo**. Il motivo è un'informazione
   d'età parziale e va usata come tale: chi esce per studio è quasi solo secondaria superiore
   e università, perché i cicli precedenti a Bagheria ci sono tutti.
2. **Nessun livello in serie fra 2011 e 2021.** Il 2011 conta chi si sposta *giornalmente*, il
   2021 chi si reca al lavoro *almeno tre giorni a settimana*, e il 2021 copre il solo lavoro
   e non ha il sesso. Si confronta la composizione — dove vanno, su cento che escono — mai il
   livello; la colonna `definizione` della tabella lo porta scritto riga per riga.
3. **Nessun dato sul rientro.** Si conosce solo l'orario di uscita di casa. Che le donne
   partano più tardi e viaggino più a lungo è un fatto; il carico di cura resta un'ipotesi.
4. **Correlazioni ecologiche.** Sui 390 comuni la mobilità fuori comune correla con
   l'occupazione femminile (Spearman +0,32): orienta l'ipotesi, non la dimostra. E l'`R²` dei
   modelli sui divari di genere è vicino a zero — «atteso» lì vuol dire poco più di «media
   siciliana». → `genere_mobilita_2011.csv`
5. **Palermo non è un termine di paragone su questa misura**: è un comune grande e compare con
   valori bassissimi per costruzione.

---

## 6. La fuga, contata: il denominatore si muove

La «fuga di talenti» del brief non è un aneddoto: sta nel denominatore di ogni tasso di
questa relazione.

- La popolazione 15-34 passa da **12.174 (2021) a 11.861 (2024)**: −313 persone, −2,6%
  in tre anni. → `analisi_popolazione_giovane.csv`
- Il ricambio migratorio non c'è: gli stranieri sono l'**1,6% del 15-34** (195 persone)
  contro 5,1% a Palermo, 6,4% in Sicilia, 12,4% in Italia. Fra 2021 e 2024: −350
  italiani (di cui −219 ragazze), +37 stranieri. **La fuga è al netto di niente.**
  → `genere_stranieri.csv`
- Chi avrà 15-24 anni nel 2029 e nel 2034 **è già nato e già residente**: nessuna
  proiezione, un conteggio. Le ragazze passano da 2.882 (2024) a 2.651 (2029, −8,0%) a
  **2.435 (2034, −15,5%)**; i ragazzi −2,5% e −5,8%. Nei territori di confronto il calo
  è simmetrico fra i generi; a Bagheria no. → `genere_platea.csv`
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
`docs/POLICY_PONTE_19.md`. Qui la sua derivazione dall'evidenza, nel formato fissato dal
progetto: **evidenza → intervento → target → KPI**.

| | |
|---|---|
| **Evidenza** | Il 70,6% dei giovani fuori da lavoro e studio non cerca (sez. 2.1); la conversione titoli→lavoro fallisce soprattutto sulle ragazze (sez. 3.1) in una finestra 22-25 (sez. 3.3); il vincolo di mobilità ha lo stesso segno e lo stesso tempismo - le ragazze escono dal comune per studiare più dei coetanei (+2,6 punti) e le donne escono per lavorare 12,1 punti meno degli uomini (sez. 5.2); la platea si restringe (sez. 6) |
| **Intervento** | **Ponte 19**: servizio comunale di transizione e riattivazione con outreach attivo - non a domanda spontanea - e due finestre di ingaggio |
| **Target** | Finestra A: 18-20enni all'uscita dalla scuola o entro 30 giorni dall'interruzione. Finestra B: 22-25enni fuori da lavoro e studio. Quota di genere ≥50% F sui presi in carico. Capacità pilota: 200 persone/anno (~18% degli inattivi non studenti) |
| **KPI** | In **tasso**, con finestra di lettura dichiarata (7.4) |

### 7.0 Perché non è un intervento sui trasporti

La domanda arriva da sola leggendo la sezione 5: se il collegamento con Palermo è il canale
delle donne, perché non intervenire lì? Perché **i dati lo escludono**, e in due modi
indipendenti. Il treno di Bagheria è già al 98° percentile siciliano per uso (sez. 5.4):
non c'è un'infrastruttura sottoutilizzata da attivare. E sui 390 comuni una maggiore quota di
mezzo collettivo **non** si accompagna a un divario di genere più piccolo — l'associazione è
nulla, e col segno sbagliato.

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

Il segmento che cerca lavoro si sta già riducendo da sé (−10,2 punti dal 2018); quello
inattivo è fermo (−0,6). Un servizio a domanda spontanea raggiunge il segmento
sbagliato per costruzione (sez. 2.2). E poiché almeno l'89% delle casalinghe è nubile,
l'aggancio femminile è l'**attivazione** dalla famiglia d'origine, non la sola
conciliazione (sez. 3.2).

### 7.4 I KPI e le loro finestre di lettura

| KPI primario | Da | A | Lettura |
|---|---:|---:|---|
| Tasso di occupazione F 15-24 | 8,2% | 9,6% (Palermo) | **triennio pooled** (potenza 90%) |
| Quota casalinghe F 15-24 | 13,4% | 11,3% (Palermo) | biennio (93%) o triennio (99%) |

**La lettura annuale non è ammessa sui KPI primari**: il delta da rilevare (+1,4 punti)
sta sotto il minimo rilevabile in un anno (MDE 2,14 punti, potenza 46%). Dichiararlo
prima dell'avvio è parte della proposta. La lettura annuale spetta agli indicatori di
processo (contatti nei 30 giorni, piani nei 15, utenza per età singola e genere contro
la platea residente), che oggi nessuno rileva e che il servizio produce.
→ `genere_mde.csv` (fig09)

Se serve un equivalente in teste per la comunicazione: «+40 occupate sulla platea 2024;
il target si riparametra ogni anno come tasso-obiettivo × platea dell'anno», con la
formula pubblicata (sez. 6).

La valutazione è a rollout scaglionato con controfattuale **dichiarato in anticipo:
Palermo**, e il prerequisito è testato, non assunto: la pendenza del tasso femminile di
Bagheria 2018-2024 (+0,65 punti/anno) è indistinguibile da Palermo e Italia
(p = 0,29 / 0,33). → `genere_pretrend.csv`

### 7.5 Il dato che il servizio produce

Ogni presa in carico genera un record pseudonimizzato, titolo/indirizzo → data di
uscita → condizione → genere ed età → barriera dichiarata → azione → esito a 3/6/12
mesi. È l'unico modo per misurare a Bagheria la relazione individuale fra titolo e
condizione lavorativa (sez. 4): la proposta non consuma soltanto dati, **ne produce
dove le statistiche pubbliche finiscono**, con una dashboard trimestrale aggregata come
impegno di accountability.

---

## 8. Le figure

La locandina chiede 2-3 visualizzazioni avanzate. La terna candidata (proposta in
`docs/RELAZIONE.md` §3, da congelare a revisione delle figure conclusa):

1. **`fig05_forbice`** - il paradosso in un'immagine: il quadrante «più istruite, meno
   occupate» sulla stessa fascia 15-24, e la forbice nel tempo col cuneo dal 2021.
2. **`fig07_ritenzione_eta`** - il *quando* della fuga, per genere: profilo di
   ritenzione per età singola con la finestra 22-25, e i due decenni a confronto.
3. **`fig04_mappa_sicilia`** - la scala: coropleta dei 390 comuni, «nel 2024 Bagheria
   arriva dove stava la mediana siciliana nel 2011».

A supporto: **`fig09_kpi_finestra`** vive dentro la policy proposal (è la figura che
dichiara quando si potrà dire se l'intervento ha funzionato, con la cascata del KPI netto).

Il terzo focus del brief ha una serie propria, aggiunta con il thread mobilità:

- **`mob_fig01_verso_palermo`** - la carta a flussi: dove vanno i pendolari di Bagheria,
  per studio e per lavoro, col nome del comune di arrivo. È la risposta letterale alla
  domanda della locandina, ed è **il quarto candidato alla terna**: la scelta resta al team.
- **`mob_fig02_ribaltamento`** - il risultato del thread: le due misure unite da una linea
  la cui pendenza è il finding, più la distribuzione dei 390 comuni.
- **`mob_fig03_treno_genere`** - mezzo e orario per genere, e il pannello che impedisce di
  leggere la figura come «serve più treno».
- **`mob_fig04_taglia_distanza`** - la figura che toglie di mezzo un claim invece di
  aggiungerne uno: l'anomalia di `M2` era un effetto della taglia.

**`fig12_pendolarismo`** resta come lettura sul censimento permanente 2018-2019, cioè la
replica indipendente della sezione 5.2. Le altre stanno nei notebook come apparato.

Tutte le figure: titolo che enuncia il finding, fascia d'età dichiarata, fonte e
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
   *Questo punto, fino al 2026-08-28, diceva «nessun pendolarismo verso Palermo». Era una
   proprietà delle fonti che avevamo consultato, scritta come se fosse una proprietà dei
   dati pubblici. Resta qui, corretto, invece che cancellato.*
4. **Nessuna stima causale**: confronti territoriali ed ecologici orientano la diagnosi;
   il disegno di valutazione (sez. 7.4) serve proprio a produrre l'evidenza che oggi
   manca. L'inattività non è attribuita a una singola causa non osservata.
5. **Nessuna interpolazione**: il 2020 mancante resta mancante; la rottura di misura
   2019→2021 è dichiarata ogni volta che si cita la serie delle componenti.
6. **La finestra 22-25 è pooled**: sull'anno singolo oscilla, e come lettura annuale non
   verrebbe usata.
7. **Nessun effetto dell'offerta di trasporto sul divario di genere**: testato sui 390
   comuni e **non trovato** (sez. 5.4). Nessuna parte della proposta vi si appoggia.

---

## Appendice - mappa dei file

| Deliverable | File |
|---|---|
| Notebook condiviso (definizioni, popolazione, condizione 15-24) | `notebooks/analisi.ipynb` |
| Thread genere (focus principale) | `notebooks/genere.ipynb` |
| Thread educazione (transizione istruzione→lavoro) | `notebooks/educazione.ipynb` |
| Thread mobilità (pendolarismo verso Palermo) | `notebooks/mobilita.ipynb` |
| Policy proposal unificata | `docs/POLICY_PONTE_19.md` |
| Decisioni editoriali (tesi, figure, limiti) | `docs/RELAZIONE.md` |
| Provenance delle fonti (URL, date, query, trappole) | `docs/sources.md` |
| Figure (PNG 300dpi + SVG) | `figures/` |
| Interfaccia dati Python→R | `data/processed/` |

Stato delle verifiche al 2026-08-29: sensore `nbconvert` **verde sui quattro notebook**;
`pipeline.verifica` **650/650 PASS**; la matrice del pendolarismo ricostruisce **sette su
sette** gli indicatori `M` pubblicati da 8milaCensus e i due totali nazionali dichiarati da
ISTAT; nessun numero di questa relazione è scritto a mano - ogni cifra ha accanto il file o
la cella che la rigenera.

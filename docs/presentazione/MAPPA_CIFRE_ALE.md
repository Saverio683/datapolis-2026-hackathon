# Mappa delle cifre · parte di Ale

Serve a studiare `notebooks/genere.ipynb` accanto al copione (`COPIONE_PONTE_19.md`). Per ogni cifra che Ale pronuncia (slide 1, 2, 9-13, 17, 18) e per quelle delle sue risposte: cosa misura esattamente, dove nasce, con quale metodo, cosa rispondere se chiedono.

**Come trovare le celle.** Cerca nel notebook il titolo della sezione (Ctrl+F). Tra parentesi c'è il numero `In [n]` della cella di codice nella versione rieseguita la sera del 23 settembre, dopo le verifiche di robustezza: se viene rieseguito, i numeri `In [n]` possono cambiare, i titoli no.

**Da dove parte quasi tutto.** La tabella `giovani`, caricata in «Caricamento» (In [1]) da `analisi_condizione_15_24.csv`: tavola lavoro del censimento permanente, classe 15-24, per territorio, anno e genere (popolazione, occupati e le altre condizioni). Ogni tasso di questa mappa è una divisione fra due colonne di quella tabella.

Tutte le cifre qui sotto sono state rilette negli output del notebook il 23 settembre.

---

## Percorso di studio (circa 50 minuti)

Nell'ordine in cui le cifre arrivano nel discorso.

| # | Sezione del notebook | Cella | Minuti | Perché |
|---|---|---|---|---|
| 1 | Verifica di fattibilità del thread | In [2] | 5 | perché si lavora sul 15-24 e perché l'incrocio titolo-lavoro non c'è |
| 2 | Gap di genere sull'occupazione, 15-24 · Quanto è preciso il gap? | In [3]-[5] | 10 | i tassi, i divari e gli intervalli di confidenza |
| 3 | Punti percentuali o rapporto? · Il gap di Bagheria è un'anomalia locale? | In [6]-[7] | 10 | **la più importante per la giuria**: cosa distingue davvero Bagheria |
| 4 | Su 1.000 ragazze: istruzione e lavoro sulla stessa fascia | In [36] | 5 | 510/462 e 82/165 |
| 5 | Dentro gli "altri inattivi": casalinghe · Le casalinghe sono coniugate? | In [11], [13] | 5 | 13,4% e lo stato civile |
| 6 | Il pendolarismo ha un genere | In [18] | 3 | 16,3/13,6 e 33,0/41,2 |
| 7 | Chi se ne va? · La ritenzione per età · La finestra 22-25 regge? · Lo stock non è la fuga | In [22]-[24], [30] | 10 | la curva della slide 13 e la domanda sulla fuga |
| 8 | Il KPI si può misurare? · Trend paralleli | In [21], [47]-[48] | 7 | potenza, finestre di lettura, Palermo |
| 9 | I claim reggono al 2024? (parte 3) | In [55] | 3 | la serie 2018-2024 della slide 11 |
| 10 | Robustezza: le domande di approfondimento | In [56]-[61] | 10 | rango fra i 390 comuni, casalinghe come stima, tetto sulle diplomate, NEET regionale, potenza e costo del pilota |

---

## Slide 1 · Apertura

| Cifra detta | Cosa misura | Dove nasce | Metodo |
|---|---|---|---|
| «Una su dodici» = **8,2%** (8,19) | ragazze 15-24 occupate ÷ ragazze 15-24 residenti, Bagheria, 2024 | «I claim reggono al 2024?», In [55] → `genere_forbice_serie.csv`; anche «Quanto è preciso il gap?», In [5] | tasso di occupazione: al denominatore c'è tutta la fascia, studentesse comprese. 1 ÷ 8,19% = 12,2 |
| «Quasi una su dieci» = Palermo **9,6** (9,59) | stessa misura, Palermo | stessa cella | 1 ÷ 9,59% = 10,4 |
| «Più di una su sei» = Italia **17,3** (17,27) | stessa misura, Italia | stessa cella | 1 ÷ 17,27% = 5,8 |
| «Sono loro ad avere più spesso il diploma» | anticipa la slide 10 | vedi slide 10 | |

---

## Slide 2 · Il problema è una catena

| Cosa dici | Dove si vede | Cosa sapere |
|---|---|---|
| «L'unica fascia giovane su studio e lavoro è 15-24» | «Verifica di fattibilità del thread», In [2] | Le classi d'età della tavola lavoro sono 15-24, 25-49, 50-64, 65+ e 15+. La tavola istruzione ha 9-24, 25-49, 50-64, 65+. La classe 15-24 esiste per 2018, 2019 e 2021-2024: **il 2020 manca alla fonte**. |
| Incrocio titolo × lavoro non pubblicato | stessa cella | Nella tavola lavoro il titolo di studio è solo `ALL` (totale); nella tavola istruzione la condizione professionale è solo `99` (totale). Le due tavole si toccano solo sui totali. |
| «Il NEET 15-29 si ferma al 2011» | non è nel notebook di genere: indicatore L4 di 8milaCensus, filone educazione (`edu_kpi_dashboard.csv`) | Bagheria 40,1% nel 2011. È una cifra di Saverio: se chiedono, gliela passi. |
| Il proxy di oggi, «fuori da lavoro e studio» | cella In [35], commento iniziale «Il proxy del NEET secondo la convenzione di repo» → `genere_fuori_lavoro_istruzione.csv` | Giovani 15-24 né occupati né studenti. Non si chiama mai «NEET» da solo e non si mette mai in serie con il dato 2011. |

---

## Slide 10 · Più diploma, meno lavoro

**Sezione:** «Su 1.000 ragazze: istruzione e lavoro sulla stessa fascia», In [36] → `genere_per_1000.csv`

| Cifra detta | Cosa misura | Metodo |
|---|---|---|
| **510 vs 462** | ogni 1.000 residenti 15-24 dello stesso genere, quanti hanno almeno il diploma (F vs M), Bagheria 2024 | Numeratore dalla tavola istruzione 9-24: sotto i 15 anni nessuno ha il diploma, quindi i diplomati 9-24 sono i diplomati 15-24. Denominatore: residenti 15-24 sommati dalle età singole. Un `assert` nella cella controlla che le due tavole abbiano la stessa popolazione. |
| **82 vs 165** | ogni 1.000 residenti 15-24 dello stesso genere, quanti sono occupati | Occupati dalla tavola lavoro 15-24, stesso denominatore. |
| **«La metà»** | 82 ÷ 165 = 0,50 | Il rapporto M/F dei tassi è **2,01**: sezione «Punti percentuali o rapporto?», In [6]. |

Da sapere se chiedono:

- **Gli stessi numeri negli altri territori** (per 1.000, diploma F/M · occupati F/M): Palermo 473/445 · 96/165; Sicilia 509/462 · 104/203; Italia 534/495 · 173/269.
- **Il limite sui 18-24** (risposta 4 della giuria): vantaggio femminile di +5,7 punti (71,6% contro 65,9%). Ma sul 18-24 Sicilia (+7,1) e Italia (+6,2) superano Bagheria. **Mai dire che le ragazze di Bagheria hanno il vantaggio educativo più alto.** Il notebook lo scrive in chiaro: «il primato di fig05 non regge fuori dal 9-24».
- **Il rapporto M/F 2,01 è il peggiore dei quattro** (Palermo 1,72, Sicilia 1,95, Italia 1,56). È robusto contro Palermo e Italia, non contro la Sicilia: lo scarto è dentro il rumore, e nel 2023 l'ordine era invertito (1,89 contro 1,94).

---

## Slide 11 · Il tasso cresce, il divario resta

**Sezioni:** «I claim reggono al 2024?» parte (3), In [55] → `genere_forbice_serie.csv`; «Gap di genere sull'occupazione, 15-24», In [4] → `genere_gap_occupazione.csv`

| Cifra detta | Valore esatto | Nota |
|---|---|---|
| **4,7%** nel 2018 → **8,2%** nel 2024 | 4,68 → 8,19 | 8,19 è il massimo della serie di Bagheria (2023: 8,02). Mai «minimo storico». |
| Palermo **9,6** · Sicilia **10,4** · Italia **17,3** (2024) | 9,59 · 10,41 · 17,27 | |
| «Ultima in tutte e sei le annate» | la cella stampa: «Bagheria in 6 anni su 6» | anni 2018, 2019, 2021-2024; il 2020 manca |
| Scarto da Palermo sempre sotto i 2 punti | 1,66 · 1,78 · 1,36 · 0,94 · 1,19 · 1,40 | «non si chiude», mai «si allarga» |

- **La rottura di misura non tocca questa serie.** Fra 2019 e 2021 cambia la misura di chi è «in cerca», non quella degli occupati (`docs/sources.md`, righe 545-549). Il confronto 2018-2024 dell'occupazione regge.
- **Il tasso maschile** sale da 11,5% a 16,5%. Il divario in punti passa da 6,9 a 8,3 (In [5]).

### Il test su «ultima» (risposta 5 della giuria)

**Sezione:** «Il gap di Bagheria è un'anomalia locale? Modello lineare di probabilità», In [7]. Lo stesso modello dà due risposte diverse, e vanno tenute separate.

| Domanda | Risultato | Come dirlo |
|---|---|---|
| Il **livello** femminile di Bagheria è più basso? | Palermo − Bagheria = **1,40 punti [0,35; 2,45], p = 0,009** (2024). Aggregando 2022-2024: 1,18 [0,58; 1,78], p = 0,0001. Sicilia: 2,22; Italia: 9,09. Tutti significativi. | «Il livello sì: è più basso di tutti e tre, e il test lo conferma.» |
| Il **divario** ragazzi-ragazze di Bagheria è più largo? | Sul solo 2024 nessuna differenza fra divari è significativa. Aggregando 2022-2024: più largo di Palermo di 1,1 punti (p = 0,03), **più stretto** di Sicilia (−1,8) e Italia (−1,9). | «In punti il divario non è un'anomalia locale. Il tratto distintivo di Bagheria è il livello femminile, non l'ampiezza del divario.» |

- **Intervalli di Wilson 2024** (In [5]): Bagheria 7,2-9,2, Palermo 9,3-9,9. Si toccano quasi, a tre centesimi di distanza: non usarli come prova, usa il test qui sopra.
- **Divario 8,3 punti, intervallo di Newcombe 6,6-10,0** (In [5]): lontano da zero in ogni anno e in ogni territorio.
- **Precisione comunale ±1,5-1,7 punti:** le oscillazioni da un anno all'altro (7,7 → 7,2 → 8,3) sono rumore, non peggioramenti né recuperi.

---

## Slide 12 · Casalinghe nel censimento

**Sezione:** «Dentro gli "altri inattivi": casalinghe a 15-24 anni», In [11] → `genere_casalinghe.csv`, `genere_composizione_stato_dettaglio.csv`

| Cifra detta | Cosa misura | Metodo |
|---|---|---|
| **13,4%** (circa 387 ragazze) | ragazze 15-24 che il censimento classifica come casalinghe ÷ tutte le ragazze 15-24, Bagheria 2024. Dal 2021 è una stima di modello: il conteggio è 386,84 («Le casalinghe sono un conteggio o una stima?», In [57]) | Gli «altri inattivi» della tavola lavoro divisi nei tre codici che li compongono (casalinghe/i, percettori di pensione, altra condizione). La quota è sull'intera popolazione 15-24 dello stesso genere. |
| Palermo **11,3** · Sicilia **10,1** · Italia **4,6** | stessa misura | |
| «Quasi il triplo della media italiana» | 13,4 ÷ 4,6 = 2,9 | |
| (in Q&A) ragazzi di Bagheria **1,7%** | stessa misura sui maschi | per i ragazzi gli «altri inattivi» sono quasi tutti «in altra condizione» (16,1%) |

Da sapere se chiedono:

- **La serie attraversa la rottura di misura.** 2018 12,4 · 2019 10,9 · 2021 14,8 · 2022 12,8 · 2023 14,6 · 2024 13,4. Il salto 2019 → 2021 compare in tutti i territori: le casalinghe stanno fra gli inattivi, e la rottura sposta persone fra «in cerca» e «inattivi». I livelli si confrontano solo dal 2021. Il numero di ragazze resta sempre fra 320 e 420.
- **Età: limiti, non stime** («Chi sono le casalinghe?», In [12]). Se nessuna avesse meno di 18 anni, sarebbero il 18,8% delle 18-24enni; se nessuna ne avesse meno di 20, il 25,8% delle 20-24enni. L'eccesso sull'incidenza italiana vale 254 ragazze. L'età vera non è osservata.
- **Stato civile** («Le casalinghe sono coniugate?», In [13]). Al 1° gennaio 2025 le ragazze 15-24 già coniugate sono 41 (1,4%), contro 387 casalinghe: almeno l'89% delle casalinghe non è sposata. Il matrimonio sotto i 25 anni a Bagheria è **più raro** che a Palermo e in Sicilia (20-24: 2,7% contro 3,2 e 2,9). Lo stato civile dice solo questo: niente su convivenze, figli o ruolo della famiglia.

---

## Slide 13 · Mobilità e finestra

### Pannello sinistro: pendolarismo

**Sezione:** «Il pendolarismo ha un genere», In [18] → `genere_pendolarismo.csv`

| Cifra detta | Cosa misura | Metodo |
|---|---|---|
| Studio: **16,3%** donne vs **13,6%** uomini (2019) | fra chi si sposta ogni giorno per studiare, quota che esce dal comune | spostamenti con destinazione fuori comune ÷ tutti gli spostamenti per quel motivo, per genere. Fonte: tavola pendolarismo del censimento permanente, solo 2018-2019, **senza età e senza destinazione** |
| Lavoro: **33,0%** donne vs **41,2%** uomini (2019) | stessa misura, motivo lavoro | chi sta al denominatore «lavoro» un lavoro ce l'ha già: non è il tasso di occupazione travestito |

- **Benchmark dello scarto uomini meno donne sul lavoro:** Bagheria 8,2 punti, Sicilia 4,1, Italia 4,7, Palermo 1,5. È il doppio della Sicilia.
- **Vantaggio femminile sullo studio:** Bagheria +2,7, Sicilia +1,8, Italia +1,4. Stabile nel 2018 e nel 2019.

### Pannello destro: ritenzione per età

**Sezione:** «La ritenzione per età: quando esattamente, e chi resta», In [23] → `genere_ritenzione_eta.csv`

**Metodo.** Per ogni età *a*: residenti di età *a*+3 nel 2024 ÷ residenti di età *a* nel 2021, × 100. La curva è una media mobile centrata su tre età (somme dei conteggi, non media dei rapporti). 100 = la generazione ha lo stesso numero di persone tre anni dopo. È un **saldo netto**: arrivi meno partenze meno decessi. Non dice chi parte né dove va.

| Età nel 2021 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | **24** | 25 | 26 | 27 | 28 | 29 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ragazze di Bagheria | 100,5 | 100,3 | 101,0 | 103,3 | 101,5 | 103,3 | 100,5 | **99,6** | 97,1 | 96,9 | 97,6 | 96,7 | 97,9 | 98,4 |

- **Quello che dici:** «dai 17 ai 23 anni sopra il cento; dai 24 sotto, e non ci torna più». Dopo il minimo di 28 anni la curva risale a 98,4, ma resta sotto 100: mai «non risale».
- **L'Italia sta sopra 100 a ogni età** (fra 101 e 103), per effetto dell'immigrazione.
- **I ragazzi di Bagheria** scendono sotto la pari a 17-19 e a 23-24, poi hanno rientri netti dopo i 26 (27 anni: 102,7; 28: 103,7). Le ragazze no.
- **La finestra 22-25** è l'età in cui intervenire: il calo parte fra i 24 e i 25 anni del 2021 e riguarda le 27-32enni del 2024.

Da sapere se chiedono:

- **Le transizioni annuali ballano** («La finestra 22-25 regge?», In [24]). Sulla stessa età si arriva a 8 punti di escursione: le 24enni fanno 100,7, 104,5 e 96,5 nei tre passaggi annuali, su celle di circa 290 ragazze. Il solo rumore di conteggio darebbe ±0,8. Per questo la finestra 22-25 è una lettura triennale, mai il titolo di un anno solo.
- **Il 96,3** («Chi se ne va?», In [22] → `genere_coorti.csv`) è la coorte femminile 25-29 del 2021 (contro 103,0 in Italia). È un'altra misura: **non agganciarla alla finestra 22-25**. I ragazzi 15-19: 98,5 contro 104,8.
- **Su dieci anni** («I claim reggono al 2024?» parte 2, In [54]): la generazione 15-19 seguita per dieci anni passa, fra le ragazze, da 102,9 (2001-2011) a 88,6 (2011-2021); fra i ragazzi da 98,4 a 83,9. Solo se chiedono «tre anni bastano?».

---

## Slide 16 · Cifre che dice Saverio, domande che prendi tu

### Potenza e finestre di lettura

**Sezione:** «Il KPI si può misurare? Potenza statistica e finestre di lettura», In [21] → `genere_mde.csv`

| KPI | Oggi → obiettivo | Anni aggregati per lato | Potenza osservata (comuni simili) | Potenza binomiale |
|---|---|---|---|---|
| Occupazione F 15-24 | 8,2 → 9,6 (+1,4 punti) | 1 · 2 · 3 | **50%** · 59% · **41%** | 46% · 75% · 90% |
| Casalinghe F 15-24 | 13,4 → 11,3 (−2,1 punti) | 1 · 2 · 3 | 57% · **82%** · 58% | 68% · 93% · 99% |

- **Due metri.** Il binomiale confronta due proporzioni (prima e dopo) come se ogni anno fosse un campione nuovo: *n* = 2.882 ragazze × anni aggregati. Il metro osservato è quanto si muovono, senza interventi, i 33 comuni siciliani con un numero di ragazze 15-24 fra metà e il doppio di Bagheria (tavola lavoro dei 390 comuni): soglia = 2,8 × la deviazione standard delle loro variazioni.
- **Perché il triennio non aiuta.** Anno su anno il tasso di un comune oscilla meno di un campione (0,36 volte la varianza binomiale), ma i comuni divergono fra loro in modo persistente, e accorpare anni non toglie quella divergenza. Il triennio disponibile, inoltre, attraversa il cambio di metodo del 2021.
- **Come dirlo:** «il tasso comunale dice la direzione, non prova l'effetto; l'effetto si misura sui partecipanti». Il vecchio «90% sul triennio» non si dice più.
- **Gli obiettivi** 9,6 e 11,3 sono i valori di Palermo nel 2024.

### Le altre cifre della slide

- **«+40 occupate»** («Il gap in persone», In [19]): 2.882 × (9,59% − 8,19%) ≈ 40. Si dice solo come «tasso-obiettivo × platea dell'anno», mai come «occupate prodotte dal servizio». Nella stessa cella: parità con i coetanei +239, tasso italiano +262. Sono la misura del problema, non obiettivi.
- **Perché i KPI sono in tasso** («Il bilancio dei giovani», In [25]). A saldo migratorio zero le ragazze 15-24 passano da 2.882 (2024) a 2.651 (2029, −8,0%) e a 2.435 (2034, −15,5%); i ragazzi calano del 2,5% e del 5,8%. Un obiettivo in teste si consumerebbe da solo.

### Palermo come riferimento (risposta 9 della giuria)

**Sezione:** «Trend paralleli: il controfattuale, testato sul passato», In [47] → `genere_pretrend.csv`

- **Metodo.** Stesso modello lineare di probabilità, con anno × territorio.
- **Pendenza di Bagheria:** +0,65 punti l'anno [0,48; 0,81].
- **Differenze di pendenza rispetto a Bagheria:** Palermo −0,10 (p = 0,29), Sicilia −0,17 (p = 0,054), Italia −0,08 (p = 0,33).
- **Come dirlo:** «Non rifiutato non vuol dire dimostrato». Sei punti e potenza bassa: lo scrive il notebook stesso.
- **Senza il modello binomiale** (cella In [48], `genere_pretrend_390.csv`): la distanza di pendenza fra Palermo e Bagheria, −0,09 punti l'anno, è più piccola di quella del 67% dei comuni simili, le cui pendenze si disperdono di 0,19 punti l'anno. È un confronto indulgente, perché include le divergenze reali fra comuni.
- **Contro le gemelle strutturali** (occupazione femminile 15+): identica nel 1991 (10,9 contro 10,8) e nel 2001 (15,1 contro 15,0); se ne stacca nel 2011 (18,1 contro una mediana di 19,8).

---

## Le cifre delle risposte di Ale

| Domanda (copione) | Cifre | Dove |
|---|---|---|
| Giornalisti 1 · «I giovani scappano?» | vedi riquadro sotto | «Lo stock non è la fuga», In [30] → `genere_stock_coorti.csv` |
| Giornalisti 3 · «È la famiglia?» | 13,4% ragazze contro 1,7% ragazzi | In [11] |
| Giuria 4 · diploma dalla tavola 9-24 | limite 18-24: 71,6 contro 65,9 (+5,7) | In [36] |
| Giuria 5 · «significativo?» | livello: 1,40 [0,35; 2,45], p = 0,009; divario: non anomalo; 2ª su 34 comuni simili, 112ª su 390 | In [7], In [56] |
| Giuria 6 · «si risolve da solo?» | serie 4,68 → 8,19; ultima 6 anni su 6; scarto da Palermo sotto 2 | In [55] |
| Giuria 8 · «perché tre anni?» | potenza osservata 50 · 59 · 41% (binomiale 46 · 75 · 90%); casalinghe biennio 82% | In [21] |
| Giuria 9 · «Palermo controfattuale?» | p = 0,29; −0,09 punti l'anno, più vicina del 67% dei comuni simili; gemelle 1991-2011 | In [47], In [48] |
| Giuria 11 · «la curva dimostra la fuga?» | saldo netto; escursione 8 punti su n ≈ 290; 96,3 = coorte 25-29 | In [23], [24], [22] |
| Giuria 18 · «quante diplomate lavorano?» | tetto 16,1% (ragazzi 35,7%), minimo zero | In [58] → `genere_frechet.csv` |
| Giuria 19 · «le casalinghe sono dichiarate?» | 386,84 casalinghe: stima di modello, celle non intere dal 2021 | In [57] → `genere_interi_condizione.csv` |
| Giuria 21 · «che effetto vede il pilota?» | 18-20 punti con 100 per coorte (26-28 con 50) | In [60] → `genere_potenza_pilota.csv` |
| Giuria 23 · «Bagheria è anomala in Sicilia?» | 112ª dal basso su 390, 2ª su 34 simili; casalinghe 358ª su 390 | In [56] → `genere_rango_390_15_24.csv` |
| Giuria 14 · «quota 50% se la platea è 51% F?» | 573 ragazze e 549 ragazzi fuori da lavoro, studio e ricerca: 51,1% F | In [23], fondo della cella → `genere_composizione_stato_dettaglio.csv` |
| Giuria 17 · pendolarismo e età | nessuna età; Palermo 91,1% (studio 2011) e 65,1% (lavoro 2021) dalle matrici origine-destinazione | In [18]; le matrici stanno in `notebooks/mobilita.ipynb` → `mob_sintesi.csv` |

**Cella nuova di oggi: «Lo stock non è la fuga» (In [30]).** Non è ancora nel copione né nei documenti consegnati, e `genere_stock_coorti.csv` non è ancora committato: decidete in due se usarla.

- **Metodo:** chi ha 15-34 anni nel 2024 ne aveva 12-31 nel 2021. Confrontando le stesse generazioni si separa il ricambio d'età dal saldo.
- **Cifre:** 15-34 in meno fra 2021 e 2024 = **−313**, di cui **−266 ricambio d'età** e **−47 saldo dentro le stesse generazioni** (−0,39%). Sicilia −0,38%, Palermo −0,56%, Italia +3,10% per immigrazione.
- **Risposta possibile:** «Dei 313 giovani in meno, 266 sono ricambio d'età: le classi che compiono 15 anni sono più piccole di quelle che superano i 34. Dentro le stesse generazioni il saldo è −47, lo 0,4%, come la Sicilia. Bagheria non si svuota più della Sicilia: la distingue chi perde e quando, le ragazze dopo i 24 anni. E anche questo è un saldo, non un conteggio di partenze.»

---

## I metodi in una frase

- **Tasso di occupazione 15-24.** Occupati ÷ residenti 15-24 dello stesso genere. Al denominatore ci sono anche gli studenti: per questo è basso ovunque.
- **Punti o rapporto.** In punti: tasso maschile meno femminile. In rapporto: tasso maschile diviso femminile. Quando i tassi sono bassi, gli stessi punti pesano di più. Bagheria sta nel mezzo in punti ed è ultima in rapporto: ogni affermazione deve dire quale scala usa.
- **Intervallo di Wilson.** Intervallo di confidenza al 95% per una proporzione. È più affidabile del classico «più o meno 1,96 errori standard» quando la proporzione è piccola o il comune è piccolo.
- **Intervallo di Newcombe.** Intervallo per la differenza fra due proporzioni, costruito combinando i due intervalli di Wilson.
- **Modello lineare di probabilità.** Regressione binomiale con link identità sui conteggi aggregati: i coefficienti si leggono direttamente in punti percentuali. L'effetto del territorio misura la differenza fra i tassi femminili; l'interazione con il genere misura la differenza fra i divari.
- **Anni aggregati (pooled).** Si sommano più anni per avere più precisione. Si contano più volte le stesse persone, e i comuni divergono fra loro in modo persistente: la precisione guadagnata è molto meno di quella che il binomiale promette.
- **Differenza minima rilevabile (MDE) e potenza.** La MDE è il cambiamento più piccolo che il test vede con probabilità dell'80%. La potenza è la probabilità di vedere un cambiamento che c'è davvero. 50% vuol dire lanciare una moneta.
- **Potenza osservata.** Invece di assumere un modello, si guarda quanto si muovono da soli i comuni della stessa taglia: se un cambiamento di quella misura è frequente anche senza interventi, la fonte non lo distingue.
- **Stima di modello (casalinghe).** Dal 2021 ISTAT stabilisce chi è occupato e, per gli altri, stima la probabilità di ogni condizione; il numero del comune è la somma delle probabilità. Per questo i conteggi non sono interi, e l'errore non è pubblicato.
- **Limiti di Fréchet.** Con due margini noti (diplomate, occupate) e l'incrocio ignoto, si calcolano il minimo e il massimo possibili dell'incrocio: qui, al massimo il 16,1% delle diplomate lavora.
- **Ritenzione di coorte.** Quante persone di una generazione ci sono tre anni dopo, su 100 di partenza. È un saldo netto: non separa partenze, arrivi e decessi.
- **Ricambio d'età e saldo.** Lo stock 15-34 cambia sia perché entrano ed escono generazioni di taglia diversa, sia perché dentro le stesse generazioni qualcuno parte o arriva. Solo il secondo pezzo ha a che fare con la mobilità.
- **Rottura di misura 2019-2021.** Il censimento cambia il modo di contare chi è «in cerca». Tocca in cerca, inattivi e casalinghe; non tocca gli occupati né i titoli di studio.
- **Trend paralleli.** Se prima dell'intervento Bagheria e Palermo crescevano allo stesso passo, Palermo è un riferimento credibile. Il test non rifiuta il parallelismo, ma non lo dimostra.
- **Limiti (bounds).** Quando una variabile non è osservata (qui l'età delle casalinghe), si calcolano i casi estremi invece di inventare una stima.

---

## Cosa leggerai nel notebook e non devi dire a voce

Il notebook è un documento di lavoro: in alcuni punti scrive più di quanto il copione permetta di dire.

| Nel notebook | Dove | A voce |
|---|---|---|
| (corretto il 23 settembre) casalinghe «autodichiarate» | risultato chiave della sezione casalinghe (dopo In [11]) | «etichetta del censimento, stimata da un modello», mai «dichiarata» né «carico di cura» |
| «famiglia d'origine» come possibile canale | dopo In [13] | lo stato civile non osserva famiglia, convivenze o figli |
| «la fuga è databile», «talent trap» | dopo In [47] e In [55] | la ritenzione è un saldo, non un conteggio di partenze |
| «il controfattuale dichiarato in anticipo è Palermo» | dopo In [47] | «riferimento per i KPI di popolazione»; l'effetto lo misura la lista d'attesa |
| «minimo del panel in ognuno dei sei anni» | dopo In [55] | corretto, ma significa «il più basso fra i territori», mai «minimo storico» |
| «+239», «+262» occupate | dopo In [19] | misura del problema, mai obiettivi del servizio |

# Ponte 19 - Bagheria

## Servizio comunale di transizione e riattivazione, 18-25, con due finestre di ingaggio

Versione unificata di progetto, 2026-08-28, aggiornata il 2026-08-29. Sostituisce, ai fini della proposal, la
versione del solo thread educazione (`docs/edu/POLICY_PONTE_19_BAGHERIA.md`, rigenerata
dalla pipeline: **non modificarla a mano**). Rispetto a quella cambia in quattro punti, tutti
derivati dai dati e non da preferenze di design:

1. il target ha **due finestre d'età**, non una, perché le uscite hanno due tempi;
2. il target è **esplicito sul genere**, perché la popolazione è asimmetrica e un
   intervento neutro su una popolazione asimmetrica ne conserva l'asimmetria;
3. il KPI primario è un **tasso**, perché la platea si restringe e un obiettivo in teste
   si annulla da solo entro il 2034;
4. il genere ha un **modulo nominato** (sezione 4-bis), perché una quota dice chi va raggiunto, non come lo si raggiunge.

Nessuna cifra qui è scritta a mano: ognuna punta al file che la produce.

**Una parola sul NEET, perché è il termine con cui la locandina apre.** Il bando parla di
«alto tasso di NEET (15-34enni)». Quella misura, a livello comunale, **non esiste nei dati
pubblici**: il censimento permanente non pubblica la fascia 15-34 sulla condizione
professionale, e l'unica classe giovanile disponibile per comune è la 15-24. Questo
servizio non aggira il problema stimando il numero mancante: usa due misure dichiarate e
mai fuse, il **NEET 15-29 al 2011** (8milaCensus, indicatore `L4`) come termine storico e
il proxy **«fuori da lavoro e istruzione» 15-24, 2018-2024** come misura corrente. Dove
qui si legge «inattivi non studenti» o «fuori da lavoro e studio» si intende il secondo:
è il NEET della locandina per sostanza, non per definizione ISTAT, e la differenza di
fascia è la ragione per cui il target del servizio parte da 18 e non da 15. La
ricostruzione completa sta in `docs/RELAZIONE_DATAPOLIS.md` §1 e §9.

---

## 1. L'evidenza che motiva l'intervento

**Il problema non è chi cerca lavoro.** Nel 2024 il **19,0%** dei 15-24enni di Bagheria è
inattivo non studente, circa **1.121 persone**, **4,2 punti sopra la Sicilia**. Fra 2018
e 2024 quella quota scende di **0,6 punti**, mentre chi cerca lavoro cala di **10,2**. Il
70,6% dei giovani fuori da lavoro e studio **non cerca nemmeno**. Un servizio a domanda
spontanea raggiungerebbe il segmento che si sta già risolvendo da sé.
→ `edu_finding_summary.csv`, `edu_kpi_dashboard.csv`

**Il capitale umano c'è, la conversione no.** Le ragazze di Bagheria arrivano al diploma
**+4,2 punti** più dei coetanei e hanno un tasso di occupazione dell'**8,2%**: il minimo
dei quattro territori, in **6 anni su 6**. Fra comuni ugualmente scolarizzati Bagheria è
**penultima su 10** per occupazione femminile - a pari istruzione il lavoro non arriva,
e non è un tratto di fascia territoriale.
→ `genere_quadro_sintesi.csv`, `genere_forbice_serie.csv`, `genere_posizionamento.csv`

**Il vincolo di mobilità ha lo stesso segno.** Fra chi già si sposta per lavorare, esce
dal comune il **41,2% degli uomini** e il **33,0% delle donne**: 8,2 punti, circa il
doppio dello scarto siciliano (4,1) e nazionale (4,7). Ma **per studiare il segno si
inverte** (F 16,3% contro M 13,6%, il vantaggio femminile più ampio del panel). Le
ragazze si muovono; smettono quando il motivo diventa il lavoro.
→ `genere_pendolarismo.csv`

**Le uscite hanno due tempi diversi.** I ragazzi si assottigliano presto e a ondate (17-19
e 23-24) **con rientri netti dopo i 26**; le ragazze si perdono **dai 24-25 in poi, senza
rientri**, cioè esattamente quando il vantaggio educativo dovrebbe convertirsi in lavoro
e non lo fa (ritenzione F 25-29 = **96,3** contro 103,0 in Italia).
→ `genere_coorti.csv`, `genere_ritenzione_eta.csv`

> **Conseguenza di progettazione**: un intervento che agisce sui 18-19enni non tocca le
> ragazze che se ne andranno a 26. Servono due leve, o una leva con due finestre.

---

## 2. Obiettivo

Ridurre la durata dell'inattività dei giovani residenti e rendere osservabile la
transizione fra titolo posseduto, attivazione e primo esito, con un obiettivo di
**convergenza** verso un benchmark dichiarato, non di solo miglioramento assoluto.

## 3. Target, quote e capacità

| | |
|---|---|
| **Finestra A - uscita** | residenti **18-20** all'uscita dalla secondaria o entro 30 giorni dall'interruzione |
| **Finestra B - mancata conversione** | residenti **22-25** fuori da lavoro e studio, o occupati che rifiutano opportunità fuori comune |
| **Target primario** | chi **non cerca attivamente** (il 70,6% dell'area fuori lavoro-studio) |
| **Quota di genere** | **minimo 50% donne** sui presi in carico, con monitoraggio trimestrale |
| **Capacità pilota** | 200 partecipanti nel primo anno (~18% dei 1.121 inattivi non studenti) |
| **Durata** | 90 giorni di preparazione, 12 mesi di erogazione, follow-up a 3, 6 e 12 mesi |
| **Dotazione minima** | 4 case manager, 1 data manager, coordinamento Comune-scuole-CPI |

### Perché la quota, e perché non è un servizio "per ragazze"

Il gruppo dei ~1.121 invisibili **non è femminile nelle dimensioni**: 573 ragazze e 549
ragazzi, 51% F. È femminile **nell'etichetta**: 387 casalinghe contro 50, e 183 contro
485 in "altra condizione". L'outreach deve quindi coprire **entrambi i generi con agganci
diversi** - per le ragazze il carico di cura ha già un nome censuario su cui costruire il
contatto, per i ragazzi non c'è neppure quello e il canale va costruito.
→ `genere_composizione_stato_dettaglio.csv`

La quota serve a impedire che un servizio formalmente neutro riproduca l'asimmetria che
deve correggere; non serve a escludere nessuno.

⚠️ **Le casalinghe sono nubili.** Al 1.1.2025 le già coniugate 15-24 sono **41 (1,4%)**
contro 387 casalinghe: almeno l'**89% è nubile**, e il matrimonio under-25 a Bagheria è
*sotto* Palermo e Sicilia. Il canale non è il matrimonio precoce ma la famiglia
d'origine, quindi serve un servizio di **attivazione**, non solo di conciliazione.
→ `genere_stato_civile.csv`

---

## 4. Modello operativo

### A. Intercettazione prima del vuoto (finestra A)
Le scuole secondarie e le 3 sedi tecniche di Bagheria propongono il servizio nell'ultimo
anno e al momento dell'interruzione. Con consenso e minimizzazione dei dati, ogni giovane
riceve un appuntamento prima che trascorrano 30 giorni senza studio o lavoro.
→ canali in `edu_technical_schools.csv` (anagrafe MIUR: 3 sedi a Bagheria, 23 a Palermo)

### B. Outreach verso chi non cerca (entrambe le finestre)
Il servizio non attende l'iscrizione allo sportello. Il primo colloquio registra titolo e
indirizzo, data di uscita, esperienze, canali già usati, **distanza e accessibilità delle
opportunità**, carico di cura, obiettivo. Due tracce di contatto distinte per i due
gruppi-etichetta descritti sopra.

### C. Piano di transizione entro 15 giorni
Una sola prossima azione verificabile: rientro in istruzione, qualifica breve collegata a
una posizione reale, ricerca assistita, esperienza retribuita. Scadenza, responsabile,
esito osservabile.

### D. Esperienze retribuite solo su domanda verificata
Nei primi 90 giorni il Comune fa l'audit dei datori locali e metropolitani. Ogni
esperienza deve avere attività reale, mentor, compenso, competenze attese e disponibilità
a registrare l'esito. Senza posti verificati non si convertono risorse in formazione
generica.

### E. Componente mobilità - un vincolo di progettazione, non un capitolo di spesa
Riguarda l'accesso alle opportunità fuori comune **nella finestra B** e **sul motivo
lavoro**: sullo studio la mobilità femminile funziona già meglio di quella maschile, e
replicarvi un incentivo sarebbe spesa su un problema che non c'è.

⚠️ **L'ipotesi infrastrutturale è esclusa dai dati, non rinviata a un gate.** La
correlazione `M2 × L11` sui 390 comuni (Spearman **+0,32**) che orientava l'ipotesi è caduta
da due lati. Il primo: il basso percentile di `M2` era un **effetto della taglia**, e a parità
di distanza dal capoluogo e di dimensione il residuo di Bagheria è **−1,9 punti** (z = −0,13).
Il secondo: il canale «più mezzo collettivo, meno divario di genere» è stato testato sugli
stessi 390 comuni e **non regge** (Spearman **−0,10**, p = 0,06, per giunta col segno
sbagliato; sul treno l'associazione è nulla, p = 0,29), mentre il treno di Bagheria sta al
**98° percentile siciliano**. Il vincolo non è l'offerta di trasporto.

La componente vive quindi come **verifica di raggiungibilità col mezzo collettivo negli orari
reali della posizione**, dentro l'istruttoria di ogni piano di transizione, e il sostegno
economico all'abbonamento resta subordinato: si attiva su chi l'opportunità ce l'ha già.
Regole operative, gate e KPI nella sezione 4-bis, componente F2.
→ `mob_taglia_distanza.csv`, `mob_treno_390.csv`, `mob_sintesi.csv`, mob_fig03, mob_fig04

---

## 4-bis. Rotta F - il modulo di genere

Nella finestra B il servizio incontra una popolazione che il titolo ce l'ha già, che per
ottenerlo si è già mossa, e che si ferma quando il motivo dello spostamento diventa il
lavoro. La quota della sezione 3 impedisce al servizio di riprodurre l'asimmetria; questo
modulo dice **come** la si corregge. Tre componenti, una per ciascun anello che i dati
mostrano rotto: il contatto, la barriera, la domanda.

> **Il meccanismo in una riga**: le ragazze di Bagheria si spostano per studiare e si
> fermano per lavorare.

### L'evidenza, un anello per componente

**Il contatto esiste già, ma come etichetta.** Nel 2024 sono **387** le 15-24enni che si
dichiarano casalinghe, il **13,4%** della fascia, contro l'**11,3%** di Palermo, il
**10,1%** della Sicilia e il **4,6%** dell'Italia; la serie 2018-2024 è stabile. Se
nessuna ha meno di 18 anni la quota reale sale al **18,8%**, se nessuna ne ha meno di 20
al **25,8%**. Al 1.1.2025 le già coniugate 15-24 sono **41 (1,4%)**: almeno l'**89%** è
nubile, quindi il canale non è il matrimonio ma la famiglia d'origine.
→ `genere_casalinghe.csv`, `genere_casalinghe_bounds.csv`, `genere_stato_civile.csv`, fig02b

**La barriera è di genere per costruzione.** Fra chi già si sposta **per lavoro** esce dal
comune il **41,2%** dei maschi e il **33,0%** delle femmine (**8,2 punti**, contro 4,1 in
Sicilia e 4,7 in Italia). Sullo **studio il segno si inverte**: F **16,3%** contro M
**13,6%**, il vantaggio femminile più ampio del panel. Il denominatore è già condizionato
al motivo (chi si sposta per lavoro un lavoro ce l'ha), quindi la misura non è un riflesso
del gap occupazionale: è una conferma indipendente dello stesso punto di rottura.
→ `genere_pendolarismo.csv`, fig12

Il thread mobilità lo **replica su un censimento diverso**: sulla matrice origine-destinazione
2011 (conteggio esaustivo, altra tavola e altro denominatore) il divario è **+2,6 punti** sullo
studio e **−12,1** sul lavoro, un ribaltamento di **14,7 punti** contro 6,0 in Sicilia, 6,5 in
Italia e 1,9 nel Comune di Palermo, con Bagheria al **13° percentile dei 381 comuni non
capoluogo** (15° sui 390). E lo **controlla**:
tenendo fermi tasso di occupazione femminile e divario occupazionale il residuo passa da −8,7 a
**−7,0 punti**. Che il divario di pendolarismo non sia un riflesso di quello occupazionale non è
più solo un argomento sul denominatore: è misurato.
→ `mob_ribaltamento_territori.csv`, `mob_sintesi.csv`, mob_fig02
⚠️ Le due tavole usano **convenzioni di segno opposte** (`gap_M_meno_F` nella prima,
`gap_lavoro_F_M` nella seconda): stessa grandezza, segno invertito. Se fig12 e mob_fig02 stanno
vicine nel deck, la convenzione va detta.

**La domanda non arriva a chi il titolo ce l'ha.** Le ragazze raggiungono il diploma
**+4,2 punti** più dei coetanei (33,4% contro 29,2%) e hanno un tasso di occupazione
dell'**8,2%** contro il **16,5%** dei maschi. Fra i comuni a pari istruzione Bagheria è
**penultima su 10** per occupazione femminile: a pari titolo il lavoro non arriva.
→ `genere_quadro_sintesi.csv`, `genere_pari_lenti.csv`, `genere_posizionamento.csv`, fig05b, fig08

> **Perché il modulo non finanzia altra istruzione.** È la metà che già funziona: il
> vantaggio educativo femminile **cresce** (da +3,1 a +4,2) mentre nel vicinato crolla
> (da +2,9 a +0,5), la base scolastica era quasi universale già nel 2011 (I8 = 96,7%), e
> sui 390 comuni dove le donne sono relativamente più istruite l'occupazione femminile è
> di solito più alta (Spearman I1 × L11 = **−0,24**, p<0,001) mentre Bagheria contraddice
> il pattern. Un incentivo allo studio pagherebbe l'anello intatto.
> → `genere_forbice_serie.csv`, `genere_nuvola_390.csv`, fig05b, fig06b

### Le tre componenti

**F1 - Contatto: l'etichetta come canale, non come elenco.**
Il censimento è aggregato: le 387 non sono identificabili, nessuna lista nominativa esiste
né va costruita. L'etichetta dice **dove cercare**, non chi. Il contatto passa dai luoghi
che quella popolazione già la vedono: le sedi secondarie cittadine, i servizi sociali, i
consultori, le associazioni. È la traccia femminile delle due tracce di contatto della
sezione 4B, e si distingue perché per le ragazze il carico di cura ha già un nome
censuario su cui aprire il colloquio, mentre per i ragazzi quel nome non c'è.
→ `edu_technical_schools.csv` (anagrafe MIUR: 3 sedi tecniche a Bagheria, 23 a Palermo)

**F2 - Barriera: non il collegamento, ma l'orario e il mezzo che si dà per scontato.**
L'ipotesi ovvia è già stata testata sui 390 comuni ed è stata **respinta**: «più mezzo
collettivo, meno divario di genere» non regge (Spearman **−0,10**, p = 0,06, per giunta col
segno sbagliato; sul treno l'associazione è nulla, p = 0,29). Il treno a Bagheria è al **97°
percentile siciliano**, quindi non è sottoutilizzato, e l'ultimo miglio dentro Palermo non è un
collo di bottiglia. **Il vincolo non è l'offerta di trasporto**, e questo modulo non ci si
appoggia: F2 **riformula** la componente E della sezione 4 invece di ereditarne il gate. Sul
lato femminile la leva non è il collegamento.
→ `mob_treno_390.csv`, `notebooks/mobilita.ipynb` (sezione 7)

Quello che resta di genere, e che i dati mostrano, è un'altra cosa:

- **il mezzo**: fra chi esce da Bagheria il treno vale il **31,5%** degli spostamenti delle donne e il **16,4%** di quelli degli uomini (mezzo privato 63,7% contro 79,0%). Il canale femminile verso Palermo è collettivo, quello maschile è l'auto;
- **l'orario**: prima delle 7:15 esce il **65,0%** degli uomini e il **54,4%** delle donne, e il **43,8%** delle donne impiega 31-60 minuti contro il 36,1% degli uomini, per 17 km. Sullo studio la differenza quasi scompare: **la divergenza oraria nasce col lavoro**.

Quindi F2 non finanzia trasporto: **vincola il servizio**, e costa istruttoria invece che budget.

1. Nessuna opportunità entra nel piano di transizione senza **verifica di raggiungibilità col mezzo collettivo negli orari reali della posizione**. Un servizio che dà per scontata l'auto seleziona per genere, e lo fa in silenzio.
2. L'**orario di ingresso richiesto dal datore** si registra nell'audit della sezione 4D e si confronta con le corse esistenti: è lì che passa la selezione, non sui chilometri.
3. Il sostegno economico all'abbonamento resta ammesso ma **subordinato**: si attiva su chi ha già l'opportunità in mano, non per creare un'accessibilità che esiste già.

⚠️ Il gate che la componente E poneva («il trasporto è la barriera primaria?») **ha già una
risposta, ed è no**: non va rispeso nei 90 giorni. La domanda che lo sostituisce riguarda
l'offerta di lavoro, non il trasporto (sotto, nel decision gate).
→ `mob_mezzo_genere.csv`, `mob_orario_genere.csv`, `mob_sintesi.csv`, mob_fig03

**F3 - Domanda: la leva che il Comune ha già in mano.**
Criteri **premiali** di pari opportunità nelle gare e nelle concessioni comunali - il modello
normativo esiste: l'art. 47 del DL 77/2021 lega gli appalti PNRR ad assunzioni di donne e di
under 36 - orientati qui alle **donne 22-25**, con verifica dell'esito a 6 e 12 mesi; l'audit
dei datori della sezione 4D raccoglie le posizioni reali su cui il criterio può mordere.
Premialità, non riserva né requisito di residenza: un vincolo di residenza nelle gare sarebbe
giuridicamente fragile, quindi il radicamento locale dell'esito si misura a valle, non si
impone in gara. È l'unica delle tre componenti che non richiede una struttura nuova: è uno
strumento amministrativo esistente riorientato su un target dichiarato.
⚠️ Il volume è piccolo per costruzione: F3 rende la domanda **verificabile**, non la crea.

### Target e capacità

| | |
|---|---|
| **Platea di riferimento** | **573** ragazze 15-24 fuori da lavoro e studio nel 2024 (387 casalinghe, 183 in altra condizione, 3 in pensione) |
| **Finestra prioritaria** | **22-25**, dove il vantaggio educativo non si converte e la ritenzione si rompe senza rientri |
| **Presa in carico pilota** | **100** donne nel primo anno (la quota del 50% sui 200 della sezione 3, pari al 17% delle 573) |
| **Componente F2** | tutte le prese in carico con un'opportunità fuori comune: è un filtro sull'istruttoria, non un sottogruppo finanziato |
| **Componente F3** | fornitori e concessionari del Comune, senza tetto di platea |

→ `genere_composizione_stato_dettaglio.csv`, `genere_ritenzione_eta.csv`

### KPI del modulo

Valgono le finestre di lettura della sezione 6: la lettura annuale non è ammessa sugli
outcome primari.

| KPI | Da | A | Delta | Finestra di lettura |
|---|---|---|---|---|
| Quota casalinghe F 15-24 | 13,4% | 11,3% (Palermo) | −2,1 pp | **biennio** (potenza 93%), triennio 99% |
| Tasso di occupazione F 15-24 | 8,2% | 9,6% (Palermo) | +1,4 pp | **triennio pooled** (potenza 90%) |

Il primario del modulo è la **quota casalinghe**, non l'occupazione. Stesso obiettivo di
convergenza, ma è l'unico dei due che si legge già su un biennio, quindi l'unico che
restituisce un verdetto dentro la durata di un mandato. L'occupazione resta l'outcome che
dà senso al primo e si legge sul triennio.
→ `genere_mde.csv`, fig09b

**Processo (lettura annuale; oggi nessuno lo rileva)**: utenza F per età singola contro la
platea residente della stessa cella; quota di prese in carico avviate entro 30 giorni;
copertura della finestra 22-25 sul totale femminile preso in carico.

**F2**: quota di partecipanti F che accedono a un'opportunità **fuori comune** entro 6 mesi,
riferimento **33,0% → 41,2%** (il livello dei coetanei). Accanto, la misura del filtro:
quota di posizioni entrate nel piano di transizione che hanno **superato la verifica di
raggiungibilità col mezzo collettivo**, e quota di quelle scartate per orario di ingresso
incompatibile.
⚠️ Misurabile **solo sul dato di servizio**: la fonte scomposta per genere copre 2018 e 2019
e su quella misura «fuori comune» è aggregato. La matrice origine-destinazione identifica
Palermo ma è ferma ai censimenti (e il 2021 è senza sesso), quindi non regge una lettura
annuale.

**F3**: procedure con criterio premiale attivo, assunzioni di donne 22-25 residenti verificate a 6 e
12 mesi, quota sul totale degli affidamenti del periodo.

⚠️ **In tasso e non in teste, e qui più che altrove.** La platea femminile 15-24 passa da
**2.882** (2024) a 2.651 (2029) e **2.435** (2034), **−15,5%**, mentre quella maschile
perde il 5,8%: nei benchmark il calo è simmetrico fra i generi, qui no. Un obiettivo in
teste si annullerebbe da solo, e sul lato femminile più in fretta.
→ `genere_platea.csv`, fig09

### Righe che il modulo aggiunge al decision gate

| Evidenza raccolta | Decisione |
|---|---|
| Meno del 30% delle prese in carico F arriva dalla traccia F1 a 90 giorni | Il canale di contatto è sbagliato: rivedere i luoghi prima di aumentare la capacità |
| Posizioni verificate raggiungibili col mezzo collettivo negli orari richiesti | F2 opera come filtro dell'istruttoria; l'abbonamento si attiva solo sul già occupato |
| Posizioni verificate raggiungibili di fatto solo in auto | Il vincolo è l'orario del datore, non il trasporto: rinegoziare l'ingresso prima di finanziare mobilità |
| Nessuna gara utile nei 12 mesi di erogazione | F3 resta dichiarata ma non si contabilizza fra le leve attive |

### Cosa il modulo non promette

- Non identifica le 387: il censimento è aggregato, nessuna lista nominativa esiste o va costruita.
- Non attribuisce la condizione di casalinga a una scelta né a un vincolo familiare osservato. Lo stato civile esclude il matrimonio precoce come canale, ma non osserva convivenze né maternità.
- Non afferma un flusso femminile «verso Palermo» corrente: la destinazione per genere esiste solo al 2011 (matrice ISTAT), la serie annuale 2018-2019 dà «fuori comune» aggregato e il 2021 non ha il sesso. Il KPI di F2 si legge sul dato di servizio (sezione 6).
- Non promette che F3 sposti da sola il KPI di popolazione: rende la domanda verificabile, il resto resta appeso a F1 e F2.
- Non propone interventi sul trasporto. L'ipotesi è stata testata sui 390 comuni e respinta, il treno di Bagheria è al 98° percentile siciliano, e «portare il treno a Bagheria» risolverebbe un problema che non esiste.
- Non sostiene alcuna tesi di segregazione per indirizzo di studio. L'anagrafe MIUR dà le sedi, non gli iscritti per genere e indirizzo: il dato non esiste, e senza quello «gli indirizzi femminili non convertono» resta un'ipotesi, non un'evidenza.

---

## 5. Decision gate dei primi 90 giorni

| Evidenza raccolta | Decisione |
|---|---|
| ≥30 esperienze retribuite con domanda e mentor verificati | Attivare il modulo esperienza |
| Gap di competenza ricorrente associato a posizioni reali | Progettare un modulo breve e mirato |
| Posizioni verificate raggiungibili di fatto solo in auto | Rinegoziare l'orario d'ingresso col datore: il trasporto non è la barriera (sezione 4-bis, F2) |
| Carico di cura barriera primaria nel sottogruppo femminile | Attivare la conciliazione **oltre** l'attivazione, non al suo posto |
| Domanda insufficiente o non verificabile | Concentrare su outreach, orientamento e mercato metropolitano |
| Quota di genere sotto il 40% a 90 giorni | Rivedere i canali di contatto prima di aumentare la capacità |

---

## 6. KPI - scritti in tasso, con la loro finestra di lettura

### Il motivo per cui non sono in teste

La platea femminile 15-24 **è già nata** e cala: 2.882 (2024) → 2.651 (2029) → **2.435
(2034), −15,5%**; nei benchmark il calo è simmetrico fra i generi, qui no. Al tasso
obiettivo di Palermo (9,59%), le stesse "+40 occupate" misurate sulla platea di ciascun
anno valgono **+18 al 2029 e −2 al 2034** (lordo +40,4, attrito −22,2 e −42,9).
Un obiettivo in teste si annullerebbe da solo senza che nessuno abbia sbagliato nulla.
→ `genere_platea.csv`, `genere_kpi_netto.csv`, `fig09_kpi_finestra`

⚠️ Da non confondere con l'altro attrito: **−19/−37** è lo scenario «non si fa niente»
(tasso 2024 fermo, `genere_tetto_platea.csv`); **−22/−43** è lo stesso conto al tasso
obiettivo.

### Outcome primario (di popolazione)

| KPI | Da | A | Delta | Finestra di lettura |
|---|---|---|---|---|
| Tasso di occupazione F 15-24 | 8,2% | 9,6% (Palermo) | +1,4 pp | **triennio pooled** (potenza 90%) |
| Quota casalinghe F 15-24 | 13,4% | 11,3% (Palermo) | −2,1 pp | biennio (93%) o triennio (99%) |

**La lettura annuale non è ammessa sui KPI primari**: il delta da rilevare (1,4 pp) sta
sotto l'MDE annuale (2,14 pp, potenza 46%). Dichiararlo prima dell'avvio è parte della
proposta, non una nota tecnica.
→ `genere_mde.csv`

Se serve un equivalente in teste per la comunicazione, si scrive così e non altrimenti:
**«+40 occupate sulla platea 2024; il target si riparametra ogni anno come
tasso-obiettivo × platea dell'anno»**, con la formula pubblicata.

### Outcome del servizio (sui presi in carico)
Quota di partecipanti occupati, in istruzione o in formazione qualificante **a sei mesi,
con esito ancora attivo al dodicesimo**.

### KPI di processo - la lettura annuale spetta a questi
Oggi **nessuno li rileva**: il servizio deve produrli.
- primo contatto entro 30 giorni dalla segnalazione;
- assessment e piano entro 15 giorni;
- quota che avvia l'azione concordata entro 30 giorni;
- giorni medi consecutivi fuori da lavoro, studio e formazione;
- **utenza per età singola e genere**, contro la platea residente della stessa cella;
- copertura delle due finestre (18-20 e 22-25) separatamente.

### KPI di qualità
Durata e tipologia del contratto; coerenza dichiarata fra indirizzo e attività; continuità
a 6 e 12 mesi; ricaduta nell'inattività; esiti aggregati per titolo e indirizzo, senza
pubblicare celle piccole.

### KPI della componente mobilità
Quota di partecipanti F che accedono a un'opportunità **fuori comune** entro 6 mesi,
riferimento 33,0% → 41,2% (il livello dei coetanei).
⚠️ **Non aggiornabile dalla fonte**: il pendolarismo **scomposto per genere** esiste solo
per 2018-2019 e su quella misura la destinazione è «fuori comune» aggregato. La matrice
origine-destinazione ISTAT *sì* identifica Palermo (91,1% di chi esce per studio nel 2011,
65,1% per lavoro nel 2021) ma è ferma ai censimenti, e il 2021 è senza sesso: nessuna delle
due serve a leggere un intervento anno per anno. Questo KPI si misura sul **dato di
servizio**, mai sulla statistica ufficiale.
→ `mob_flussi_bagheria.csv`, `mob_sintesi.csv`, mob_fig01

---

## 7. Valutazione dell'impatto

Rollout scaglionato. Fra persone con uguale priorità l'ordine di avvio è assegnato
casualmente quando eticamente possibile; chi inizia più tardi è il confronto temporaneo.
Protocollo, outcome primario, finestre temporali ed esclusioni pubblicati **prima**
dell'avvio. Il prima-dopo da solo non basta.

**Il controfattuale è dichiarato in anticipo: Palermo.** Il prerequisito è testato, non
assunto: la pendenza del tasso femminile di Bagheria 2018-2024 (+0,65 pp/anno) è
indistinguibile da Palermo e Italia (p = 0,29 / 0,33; Sicilia al margine, 0,054). Le dieci
gemelle strutturali fanno da ancora dei target.
→ `genere_pretrend.csv`, `genere_gemelle.csv`

⚠️ Bagheria sta **sotto la mediana delle gemelle in tutti gli anni 2018-2024** (di 2,1-3,1
punti, contro −1,7 nel 2011): lo stacco aperto nel decennio 2001-2011 non si è chiuso. Il
disegno deve poter distinguere l'effetto dell'intervento dalla prosecuzione di quel
divario.

---

## 8. Il dataset che il servizio produce

Ogni record pseudonimizzato:

> **titolo/indirizzo → data di uscita → condizione iniziale → genere ed età singola →
> durata inattività → barriera dichiarata → azione → esito a 3, 6 e 12 mesi**

Questo è l'unico modo per misurare a Bagheria il rapporto fra **titolo e condizione
lavorativa a livello individuale**: l'incrocio non esiste nelle tavole comunali pubbliche
(verificato - nella tavola lavoro il titolo è solo `ALL`, in quella istruzione la
condizione è solo `99`). Il servizio non consuma soltanto dati: ne genera di nuovi, ed è
parte del suo valore.

## 9. Accountability pubblica

Dashboard trimestrale con soli indicatori aggregati: persone contattate, piani attivati,
esiti a 3/6/12 mesi, durata media dell'inattività, **composizione per genere e finestra**,
differenza rispetto al gruppo di confronto. Celle piccole non pubblicate.

Il successo non è il numero di iscritti. È una transizione stabile, e una convergenza
misurata sul triennio.

## 10. Cosa questa proposta non promette

- Non stima il rendimento occupazionale individuale di un titolo: il dato non esiste, il
  servizio lo creerà.
- Non attribuisce il calo della popolazione 15-34 a emigrazione misurata: la ritenzione di
  coorte è un **saldo netto senza destinazione**.
- Non mette in serie il pendolarismo «verso Palermo»: la destinazione c'è (matrice
  origine-destinazione ISTAT, sezione 4-bis), ma è ferma ai censimenti, il 2021 non ha il
  sesso e la serie annuale per genere dà solo «fuori comune» aggregato.
- Non attribuisce l'inattività a una singola causa non osservata.
- Non tratta la finestra 22-25 come un dato annuale: è una lettura pooled su triennio,
  con oscillazioni fino a 8 pp sulla singola età.

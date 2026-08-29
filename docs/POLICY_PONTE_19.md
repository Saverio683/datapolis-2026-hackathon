# Ponte 19 - Bagheria

## Servizio comunale di transizione e riattivazione, 18-25, con due finestre di ingaggio

Versione unificata di progetto, 2026-08-28. Sostituisce, ai fini della proposal, la
versione del solo thread educazione (`docs/edu/POLICY_PONTE_19_BAGHERIA.md`, rigenerata
dalla pipeline: **non modificarla a mano**). Rispetto a quella cambia in tre punti, tutti
derivati dai dati e non da preferenze di design:

1. il target ha **due finestre d'età**, non una, perché le uscite hanno due tempi;
2. il target è **esplicito sul genere**, perché la popolazione è asimmetrica e un
   intervento neutro su una popolazione asimmetrica ne conserva l'asimmetria;
3. il KPI primario è un **tasso**, perché la platea si restringe e un obiettivo in teste
   si annulla da solo entro il 2034.

Nessuna cifra qui è scritta a mano: ognuna punta al file che la produce.

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

### E. Componente mobilità - calibrata sul lavoro, non sullo studio
È una **leva sullo stesso KPI occupazionale**, non un contorno: supporto all'accesso alle
opportunità fuori comune (abbonamento, orari, accompagnamento alla prima settimana) offerto
**nella finestra B** e **sul motivo lavoro**. Sullo studio la mobilità femminile funziona
già meglio di quella maschile: replicarvi un incentivo sarebbe spesa su un problema che
non c'è.
⚠️ Attivabile solo se il decision gate conferma il trasporto come barriera primaria su un
sottogruppo con offerta coerente già identificata: la correlazione `M2 × L11` sui 390
comuni (Spearman **+0,32**) è **ecologica**, orienta l'ipotesi, non la dimostra.

---

## 5. Decision gate dei primi 90 giorni

| Evidenza raccolta | Decisione |
|---|---|
| ≥30 esperienze retribuite con domanda e mentor verificati | Attivare il modulo esperienza |
| Gap di competenza ricorrente associato a posizioni reali | Progettare un modulo breve e mirato |
| Trasporto barriera primaria **e** offerta coerente identificata | Attivare il supporto mobilità sulla finestra B |
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
⚠️ **Non aggiornabile dalla fonte**: il pendolarismo per genere esiste solo per 2018-2019
e la destinazione non è identificata. Questo KPI si misura sul **dato di servizio**,
mai sulla statistica ufficiale.

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
- Non afferma un pendolarismo "verso Palermo": la fonte dà «fuori comune» aggregato.
- Non attribuisce l'inattività a una singola causa non osservata.
- Non tratta la finestra 22-25 come un dato annuale: è una lettura pooled su triennio,
  con oscillazioni fino a 8 pp sulla singola età.

# Modifiche da fare a `presentazione_hackaton_v3.pptx`

Revisione del 2026-09-24. Riguarda le 22 slide di `docs/presentazione/presentazione_hackaton_v3.pptx`
e porta nel deck ciò che è cambiato nel notebook genere, nella relazione, nella policy e nelle
figure. Ogni cifra qui sotto viene da un file di `data/processed/`, indicato accanto, ed è
controllata da `pipeline.verifica` (986 controlli, tutti superati il 2026-09-24).

Le modifiche sono di due tipi:

- **A. Revisione del 2026-09-24**: il test «dopo i 25 anni», la ritenzione su cinque anni, le
  casalinghe come etichetta e il pendolarismo come misura compatibile, non come conferma.
- **B. Allineamenti già dovuti**: cifre del deck che i documenti avevano già corretto il
  2026-09-23 e che nel pptx sono rimaste alla versione precedente.

Due slide contengono immagini da sostituire, non testo da ritoccare: la **12** è un'immagine
unica (anche il titolo è dentro l'immagine) e la **13** contiene due grafici di una versione
precedente delle figure. I PNG aggiornati sono in `figures/`.

---

## A. Revisione del 2026-09-24

### Slide 2 - Introduzione

- **Ora**: «Il divario femminile non nasce da minore istruzione: emerge nel passaggio verso
  lavoro e mobilità.»
- **Diventa**: «Il divario femminile non nasce da minore istruzione: emerge dopo lo studio. A
  25-49 anni le donne di Bagheria lavorano 8,4 punti meno di quelle di Palermo, gli uomini 1,3.»
- **Perché**: il test crucis fra «ritardo» e «mancata conversione» (relazione §3.1-bis).
  → `genere_dopo_25_scarti.csv`

### Slide 11 - «Il tasso femminile cresce, ma il divario non si chiude»

Resta com'è. Dopo di lei va **una slide nuova**, 11-bis.

### Slide 11-bis (nuova) - Dopo i 25 anni il divario diventa locale

- **Titolo**: «Dopo i 25 anni il divario non si chiude: diventa locale, e femminile»
- **Figura**: `figures/fig13b_occupazione_eta_genere.png`, ritagliata al solo grafico, oppure
  una tabellina a due righe:

  | Scarto di Bagheria, 2024 | Donne vs Palermo | Uomini vs Palermo | Donne vs Sicilia | Uomini vs Sicilia |
  |---|---:|---:|---:|---:|
  | 15-24 | −1,4 | −0,1 | −2,2 | −3,8 |
  | 25-49 | **−8,4** | −1,3 | **−8,0** | −3,1 |

- **Tre cifre in evidenza**:
  - **39,6%** occupazione delle donne 25-49 (Palermo 48,0%, Sicilia 47,6%);
  - **+695** occupate al tasso femminile di Palermo, contro le **+40** del 15-24;
  - **42,2%** casalinghe fra le donne 25-49 (Palermo 33,8%, Sicilia 33,2%, Italia 18,1%).
- **Riga sulla generazione giovane**: «Non è solo la generazione delle madri: con il ricambio
  delle coorti lo scarto si sarebbe dovuto chiudere a −6,3 punti, resta a −8,4. Le nate dal
  1984 in poi portano circa −6 punti, i coetanei maschi quasi nulla.»
- **Piè di pagina**: «Classe 25-49: test di che cosa succede dopo la fascia target, non misura
  dei giovani. Il test non separa età e generazione. ISTAT, Censimento permanente 2018-2024.»
- **Note del relatore**: in Sicilia il NEET femminile è sotto quello maschile a 15-24 anni
  (17,4% contro 21,5%) e quasi il doppio a 25-34 (52,2% contro 28,9%, ricavato per differenza
  dalla rilevazione sulle forze di lavoro).
- → `genere_dopo_25.csv`, `genere_dopo_25_scarti.csv`, `genere_dopo_25_generazioni.csv`,
  `genere_neet_25_34.csv`; notebook genere, sezioni «Dopo i 25 anni» e «La generazione
  successiva ha lo stesso problema?»

### Slide 12 - Casalinghe (immagine unica, da rifare)

- **Titolo, ora**: «Casalinghe dichiarate: un'etichetta censuaria utile per l'outreach».
  **Diventa**: «Casalinghe secondo il censimento: stessa inattività, etichetta diversa».
- **Titolo del grafico, ora**: «Casalinghe dichiarate: a Bagheria 13,4%».
  **Diventa**: «Classificate come casalinghe dal censimento: a Bagheria 13,4%».
- **Riga sopra il grafico, ora**: «Condizione dichiarata al censimento: non misura ore di cura
  né intenzioni.» **Diventa**: «Stima di modello ISTAT, non una dichiarazione della persona: non
  misura ore di cura né intenzioni.»
- **Piè di pagina, ora**: «Condizione dichiarata al censimento, non misura delle ore di cura.»
  **Diventa**: «Stima di modello del censimento, non una misura delle ore di cura.»
- **Sottotitolo della slide** («A Bagheria la quota è quasi tripla rispetto all'Italia; non
  misura ore di cura.»): resta.
- **Colonna di destra**, al posto dei tre punti attuali:
  1. «È una stima del censimento: casalinga e altra condizione sono una sola categoria del
     modello, e la regola che le separa non è pubblicata.»
  2. «Stessa inattività, etichetta diversa: fuori da lavoro, studio e ricerca ci sono 573
     ragazze e 549 ragazzi. La divisione per genere c'era già nel 2018 (12,4% contro 0,8%).»
  3. «L'eccesso femminile di inattività compare dopo i 25 anni: casalinghe al 42,2% delle
     donne 25-49.»
- **Perché**: relazione §3.2; il punto «È però un punto di contatto» non regge, perché una
  stima aggregata non identifica nessuno.
- → `genere_casalinghe.csv`, `genere_composizione_stato_dettaglio.csv`, `genere_dopo_25.csv`

### Slide 13 - Mobilità e finestra di intervento

- **Sottotitolo, ora**: «Le ragazze si spostano per studiare; il nodo emerge nel lavoro e
  nella fascia 22-25.» **Diventa**: «Fra chi esce dal comune le donne prevalgono per studio e
  restano indietro per lavoro; nel triennio 2021-2024 la coorte femminile cede fra 22 e 25
  anni.»
- **Grafico di sinistra**, titolo ora «La mobilità cambia segno quando il motivo diventa
  lavoro»: aggiungere sotto, in piccolo, «Tutte le età, solo chi si sposta: compatibile con la
  forbice, non una conferma». In alternativa si sostituisce con `figures/fig12_pendolarismo.png`
  ritagliata, che porta già il nuovo titolo.
- **Grafico di destra**, titolo ora «Le ragazze: la finestra utile è prima dei 25 anni»:
  sostituirlo con `figures/fig07_ritenzione_eta.png` ritagliata. Il nuovo titolo è «Nel triennio
  2021-2024 la coorte femminile di Bagheria cede fra i 22 e i 25 anni», e la figura aggiunge il
  vicinato, dove il cedimento femminile non c'è.
- **Riga in fondo, ora**: «Uso progettuale: reclutare prima che la finestra 22-25 si chiuda, e
  verificare la raggiungibilità reale delle opportunità.» Resta. Aggiungere: «Su cinque anni la
  perdita all'uscita dal percorso formativo è di entrambi i generi.»
- → `genere_pendolarismo.csv`, `genere_ritenzione_eta.csv`, `genere_ritenzione_decennale.csv`

### Slide 15 - Evidenza → intervento → KPI

| Riga | Ora | Diventa |
|---|---|---|
| 3 | Finestra critica 22-25 → Seconda finestra di ingaggio mirata | Uscita dal percorso formativo, 20-29 anni, per entrambi i generi → Seconda finestra di ingaggio (22-25) |
| 4 | Mobilità studio/lavoro con segno diverso → Raggiungibilità verificata caso per caso | Invariata; «segno diverso» fra studio e lavoro resta, ma senza età |
| nuova | - | Dopo i 25 anni il deficit diventa femminile (−8,4 punti da Palermo) → Finestra B orientata alle donne; estensione ai 26-34 da decidere |

### Slide 16 - Target: due finestre

- **Finestra B, ora**: «È la finestra di riattivazione, coerente con la perdita di ritenzione
  femminile.» **Diventa**: «È la finestra di riattivazione: all'uscita dal percorso formativo si
  perdono coorti di entrambi i generi, e dopo i 25 anni il deficit di lavoro diventa femminile.»
- **Perimetro da dichiarare**, aggiungere in coda: «Il deficit femminile più grande sta sopra i
  25 anni: l'estensione del modulo di genere ai 26-34 è un'opzione dichiarata, da decidere.»

### Slide 19 - KPI territoriali

- **KPI casalinghe**: aggiungere sotto «13,4 → 11,3%»: «Si muove anche con le sole iscrizioni a
  un corso di studio (covariata del modello ISTAT): sempre accanto all'occupazione.»
  → policy §4-bis, KPI del modulo

### Slide 20 - Misurazione

- **Disegno di valutazione, ora**: «Per i KPI territoriali, Palermo è il confronto esterno
  dichiarato.» **Diventa**: «Per i KPI territoriali il confronto dichiarato è Palermo, più un
  controllo sintetico sui 33 comuni di taglia simile con test placebo.»
- **Aggiungere al disegno di valutazione**: «A sei mesi il pilota vede solo effetti di 18-20
  punti; le rassegne trovano effetti medi vicini a zero nel breve periodo e più grandi per le
  donne (Card, Kluve e Weber 2018). Un confronto non significativo al primo anno è atteso anche
  se il servizio funziona.»
- → `genere_potenza_pilota.csv`, policy §7

### Slide 22 - Conclusione

- **Primo punto, ora**: «Il perimetro è dichiarato: 15-24 osservabile, 18-25 target del
  servizio.» **Diventa**: «Il perimetro è dichiarato: 15-24 osservabile, 18-25 target del
  servizio; il deficit femminile più grande è dopo i 25 anni.»

---

## B. Allineamenti già dovuti (cifre ferme alla versione precedente)

### Slide 17 - «Perché outreach e non solo sportello»

- **Ora**: «La componente "in cerca" scende di 10,2 punti; gli inattivi non studenti solo di
  0,6.»
- **Problema**: è il confronto 2018-2024, che attraversa la rottura di misura 2019→2021 sulla
  condizione «in cerca» (18,1% → 7,9%). I documenti lo leggono solo dentro la stessa
  definizione.
- **Diventa**: «Fra 2021 e 2024 chi cerca scende da 10,6% a 7,9%; gli inattivi non studenti
  restano fermi (19,2% → 19,0%).»
- → `edu_youth_states_2018_2024.csv`, policy §1

### Slide 20 - «Perché non basta un anno» e figura

- **Ora**: «Sul triennio pooled la potenza arriva circa al 90%; la quota casalinghe si legge già
  su biennio/triennio.»
- **Problema**: il 90% è il calcolo binomiale, già smentito dalla variabilità dei comuni simili
  (il copione lo elenca fra le cose da non dire).
- **Diventa**: «Contro la variabilità dei 33 comuni simili la potenza è del 50% su un anno, del
  59% sul biennio e del 41% sul triennio: il tasso comunale dice la direzione, non prova
  l'effetto. La quota casalinghe arriva all'82% sul biennio.»
- **Figura**: il grafico mostra solo le potenze binomiali (46%, 75%, 90%). Va sostituito con
  `figures/fig09b_potenza.png` ritagliata, che affianca i due metri.
- → `genere_mde.csv`

### Slide 19 - finestra di lettura delle casalinghe

- **Ora**: «lettura biennio/triennio». **Diventa**: «lettura sul biennio», come in policy §6.

---

## Fuori dal pptx, da allineare nello stesso passaggio

- **Copione** (`COPIONE_PONTE_19.md`):
  - righe 48, 154 e 570: «934 controlli» diventa «986 controlli»;
  - risposta 11 della giuria (righe 725-726): aggiungere che su cinque anni la perdita
    all'uscita dal percorso formativo è di entrambi i generi (femmine 92,8 e 93,3, maschi 89,2
    e 91,8), e che nel vicinato il cedimento femminile del triennio non c'è (coorte 25-29 al
    102,4);
  - riga 776: la relazione non aggancia più il 96,3 alla finestra 22-25 in apertura, perché
    l'apertura ora cita il 25-49. La riga si può togliere;
  - una risposta nuova per la domanda «La fuga è femminile?», con le stesse cifre della
    risposta 11 e il risultato 25-49 della slide 11-bis.
- **Generatore del deck** (`pipeline/presentazione_pptx.py`), se si rigenera da lì:
  - «Casalinghe dichiarate» nel titolo di riga 403 e «Condizione dichiarata al censimento»
    nella nota di riga 406 e nella terza scheda delle tre evidenze;
  - il titolo della slide di fig07, «Le ragazze restano fino ai 23 anni, poi la coorte si
    riduce», va affiancato al dato maschile.

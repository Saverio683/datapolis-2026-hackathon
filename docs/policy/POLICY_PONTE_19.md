# Ponte 19 - Bagheria

## Servizio comunale di transizione e riattivazione, 18-25, con due finestre di ingaggio

Policy proposal del progetto DataPolis 2026, 2026-08-29, versione rivista del 2026-09-23.

**Ponte 19 è un servizio comunale che va a cercare i giovani di Bagheria fuori da lavoro e
studio, invece di aspettarli a uno sportello, e li accompagna verso un primo esito
verificabile.** Il nome viene dall'età di uscita dalla scuola superiore, 19 anni; l'analisi
ha fatto emergere una seconda finestra, fra 22 e 25, e il servizio copre quindi i 18-25.
Quattro scelte di progetto, tutte derivate dai dati e non da preferenze di design:

1. il target ha **due finestre d'età**, non una, perché le uscite hanno due tempi;
2. il target è **esplicito sul genere**, perché la popolazione è asimmetrica e un
   intervento neutro su una popolazione asimmetrica ne conserva l'asimmetria;
3. il KPI primario è un **tasso**, perché la platea si restringe e un obiettivo in teste
   si annulla da solo entro il 2034;
4. il genere ha un **modulo nominato** (sezione 4-bis), perché una quota dice chi va
   raggiunto, non come lo si raggiunge.

Nessuna cifra qui è scritta a mano: ognuna punta al file che la produce. L'analisi da cui
la proposta discende è `docs/relazione/RELAZIONE_DATAPOLIS.md`.

**Una parola sul NEET, perché è il termine con cui la locandina apre.** Il bando parla di
«alto tasso di NEET (15-34enni)». Quella misura, a livello comunale, **non esiste nei dati
pubblici**: il censimento permanente non pubblica la fascia 15-34 sulla condizione
professionale, e l'unica classe giovanile disponibile per comune è la 15-24. Questo
servizio non aggira il problema stimando il numero mancante: usa due misure dichiarate e
mai fuse, il **NEET 15-29 al 2011** (8milaCensus, indicatore `L4`) come termine storico e
il proxy **«fuori da lavoro e istruzione» 15-24, 2018-2024** come misura corrente: i
15-24enni che non lavorano e non studiano (26,9% nel 2024), cioè chi cerca lavoro (7,9%) più
gli **inattivi non studenti** (19,0%), che non lo cercano. È la misura più vicina al NEET
della locandina, ma non la sua definizione ISTAT. La cifra del bando esiste solo a scala
regionale, nella rilevazione sulle forze di lavoro, che è una fonte diversa e campionaria:
nel 2024 il NEET 15-34 della Sicilia è al **30,1%** (35,3% fra le donne, 25,2% fra gli
uomini), contro il 17,3% dell'Italia; sul 15-24 la stessa fonte dà 19,5% per la Sicilia,
dove il proxy censuario dà 22,3%. È un riferimento, mai in serie con il dato comunale
(`genere_neet_rcfl.csv`). Il target del servizio
parte da 18 anni perché fino a 18 vale il diritto-dovere all'istruzione e alla
formazione, e si ferma a 25 perché è lì che i dati collocano le due uscite; i 26-34enni
restano fuori perché nessuna tavola comunale ne segue la condizione professionale. La
ricostruzione completa sta in `docs/relazione/RELAZIONE_DATAPOLIS.md` §1 e §9.

---

## 1. L'evidenza che motiva l'intervento

**Il problema non è chi cerca lavoro.** Nel 2024 il **19,0%** dei 15-24enni di Bagheria è
inattivo non studente, circa **1.121 persone**, **4,2 punti sopra la Sicilia**. Il
70,6% dei giovani fuori da lavoro e studio **non cerca nemmeno**. A definizione costante
(2021-2024, dopo il cambio di misura della condizione «in cerca») chi cerca scende da
**10,6% a 7,9%**, mentre gli inattivi non studenti restano fermi (**19,2% → 19,0%**) e il
loro scarto dalla Sicilia sale da 2,7 a 4,2 punti. Un servizio a domanda spontanea
raggiungerebbe chi già cerca, non il segmento che non si muove.
→ `edu_youth_states_2018_2024.csv`, `edu_kpi_dashboard.csv`

**Il capitale umano c'è, la conversione no.** Le ragazze di Bagheria hanno il diploma più
spesso dei coetanei (**+4,8 punti** sulla fascia 15-24, +4,2 sulla 9-24) e hanno un tasso
di occupazione 15-24 dell'**8,2%**: il minimo dei quattro territori, in **6 anni su 6**,
e il secondo più basso fra i 34 comuni siciliani della sua taglia (fra tutti i 390 comuni è
112° dal basso: molti comuni piccoli stanno sotto). Fra i comuni siciliani ugualmente scolarizzati Bagheria è **penultima** (un solo comune su 10 fa peggio) per
occupazione femminile (15+, censimento 2011): a pari istruzione il lavoro non arriva, e
non è un tratto di fascia territoriale.
→ `genere_forbice_quadrante.csv`, `genere_quadro_sintesi.csv`, `genere_forbice_serie.csv`,
`genere_posizionamento.csv`, `genere_rango_390_15_24.csv`

**Il pendolarismo ha lo stesso segno.** Fra chi già si sposta per lavorare, nel 2019
esce dal comune il **41,2% degli uomini** e il **33,0% delle donne**: 8,2 punti, il
doppio dello scarto siciliano (4,1) e quasi il doppio di quello nazionale (4,7). Ma **per
studiare il segno si inverte** (F 16,3% contro M 13,6%, il vantaggio femminile più ampio
dei quattro territori). Le ragazze si muovono; smettono quando il motivo diventa il lavoro.
→ `genere_pendolarismo.csv`

**Le uscite hanno due tempi diversi.** I ragazzi si assottigliano presto e a ondate (17-19
e 23-24 anni) **con rientri netti dopo i 26**; le ragazze si perdono **dai 24-25 in poi,
senza rientri**, cioè esattamente quando il vantaggio educativo dovrebbe convertirsi in
lavoro e non lo fa (la coorte femminile che nel 2021 aveva 25-29 anni è a **96,3** tre anni
dopo, contro 101,2 dei coetanei, 97,6 in Sicilia e 103,0 in Italia).
→ `genere_coorti.csv`, `genere_ritenzione_eta.csv`

> **Conseguenza di progettazione**: un intervento che agisce sui 18-19enni non tocca le
> ragazze che si perdono dopo i 24 anni. Servono due leve, o una leva con due finestre.

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
| **Capacità pilota** | 200 partecipanti nel primo anno (~18% dei 1.121 inattivi non studenti), contati sui 15-24enni: capacità progettata su una platea indicativa, perché il censimento non dà la fascia 18-25 |
| **Durata** | 90 giorni di preparazione, 12 mesi di erogazione in due coorti da 100 (ingresso al mese 0 e al mese 6, sezione 7), follow-up a 3, 6 e 12 mesi dall'ingresso |
| **Dotazione minima** | 4 case manager, 1 data manager, coordinamento Comune-scuole-CPI |

### Perché la quota, e perché non è un servizio "per ragazze"

Il gruppo dei ~1.121 invisibili **non è femminile nelle dimensioni**: 573 ragazze e 549
ragazzi, 51% F. È femminile **nell'etichetta**: casalinghe e casalinghi sono 387 contro 50
(F contro M), e in "altra condizione" 183 contro 485. L'outreach deve quindi coprire
**entrambi i generi con agganci diversi**: per le ragazze esiste già un'etichetta censuaria
(casalinga) da cui partire nel contatto, per i ragazzi non c'è neppure quella e il canale va
costruito.
→ `genere_composizione_stato_dettaglio.csv`

La quota serve a impedire che un servizio formalmente neutro riproduca l'asimmetria che
deve correggere; non serve a escludere nessuno.

⚠️ **Le casalinghe non sono giovani spose.** Al 1.1.2025 le già coniugate 15-24 sono
**41 (1,4%)** contro 387 casalinghe: almeno l'**89% non è sposata**, e il matrimonio
under-25 a Bagheria è *sotto* Palermo e Sicilia. Il matrimonio precoce non spiega il
fenomeno; convivenze e figli non sono osservati dalla fonte. Serve quindi un servizio di
**attivazione**, non solo di conciliazione.
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

⚠️ **I dati non sostengono un intervento infrastrutturale.** La correlazione fra mobilità
fuori comune (`M2`) e occupazione femminile (`L11`) sui 390 comuni (Spearman **+0,32**: dove si esce di più dal comune, le donne lavorano di
più) suggeriva che Bagheria soffrisse di scarsa mobilità. Non regge per due ragioni. La
prima: il basso percentile di `M2` era un **effetto della taglia**, e a parità di distanza
dal capoluogo e di dimensione il residuo di Bagheria è **−1,9 punti** (z = −0,13). La
seconda: il canale «più mezzo collettivo, meno divario di genere» è stato testato sugli
stessi 390 comuni e **non trova sostegno** (Spearman **−0,10**, p = 0,06, di segno opposto
all'ipotesi; sul treno l'associazione è nulla, p = 0,29), mentre il treno di Bagheria sta al
**98° percentile siciliano**. Il vincolo non è l'offerta di trasporto. Un'associazione
assente fra comuni non esclude che orario e mezzo pesino sulla singola persona: per questo
la raggiungibilità si verifica caso per caso.

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

**Il contatto esiste già, ma come etichetta.** Nel 2024 il censimento classifica come
casalinghe **387** 15-24enni, il **13,4%** della fascia, contro l'**11,3%** di Palermo, il
**10,1%** della Sicilia e il **4,6%** dell'Italia; dal 2021 la quota sta fra il 12,8% e il
14,8%. Non è una
dichiarazione né un conteggio: dal 2021 ISTAT stima la condizione di chi non è occupato con
un modello, sommando per comune probabilità individuali (a Bagheria 386,84 ragazze), e la
tavola comunale non ne riporta l'errore (`genere_interi_condizione.csv`). Il 2018-2019 viene
da un altro metodo e non si mette in serie. La tavola
non dà l'età dentro la fascia: se nessuna avesse meno di 18 anni la quota sulle 18-24enni
sarebbe del **18,8%**, se nessuna ne avesse meno di 20 del **25,8%** sulle 20-24enni. Al
1.1.2025 le già coniugate 15-24 sono **41 (1,4%)**: almeno l'**89%** non è sposata, quindi
il canale non è il matrimonio precoce.
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
Italia e 1,9 nel Comune di Palermo, con Bagheria al **15° percentile dei comuni
siciliani** sul lavoro (14° al netto di taglia e distanza dal capoluogo). Attenzione ai segni: qui lo scarto è F − M (negativo quando le
donne escono meno), mentre la misura del 2019 citata sopra è M − F; la grandezza è la stessa.
→ `mob_ribaltamento_territori.csv`, `mob_sintesi.csv`, mob_fig02

**La domanda non arriva a chi il titolo ce l'ha.** Le ragazze hanno il diploma più spesso
dei coetanei (**+4,8 punti** sulla fascia 15-24; +4,2 sulla 9-24, 33,4% contro 29,2%) e
hanno un tasso di occupazione 15-24 dell'**8,2%** contro il **16,5%** dei maschi. Fra i
comuni a pari istruzione Bagheria è **penultima** (un solo comune su 10 fa peggio) per occupazione femminile (15+,
2011): a pari titolo il lavoro non arriva.
→ `genere_forbice_quadrante.csv`, `genere_quadro_sintesi.csv`, `genere_pari_lenti.csv`,
`genere_posizionamento.csv`, fig05, fig08

> **Perché il modulo non finanzia altra istruzione.** Il problema delle ragazze di
> Bagheria non è l'istruzione rispetto ai coetanei, è la conversione: il vantaggio
> educativo femminile **cresce** (da +3,1 a +4,2 sulla 9-24) mentre nei cinque comuni più
> vicini si chiude (da +2,9 a +0,5), la base scolastica era quasi universale già nel 2011
> (quota di 15-19enni con almeno la licenza media, `I8`: 96,7%), e sui 390 comuni dove le
> donne sono relativamente più istruite l'occupazione femminile è di solito più alta
> (correlazione di Spearman fra il rapporto uomini/donne sui diplomati, `I1`, e il tasso di
> occupazione femminile, `L11`: **−0,24**, p<0,001),
> mentre Bagheria contraddice il pattern. Resta vero che Bagheria è indietro sui titoli più
> alti per entrambi i generi (diploma e laurea degli adulti, `docs/relazione/RELAZIONE_DATAPOLIS.md`
> §4): è un tema reale, ma non è la leva di questo modulo.
> → `genere_forbice_serie.csv`, `genere_nuvola_390.csv`, fig05b, fig06b

### Le tre componenti

**F1 - Contatto: l'etichetta come canale, non come elenco.**
Il censimento è aggregato: le 387 non sono identificabili, nessuna lista nominativa esiste
né va costruita. L'etichetta dice **dove cercare**, non chi. Il contatto passa dai luoghi
dove quella popolazione è già visibile: le sedi secondarie cittadine, i servizi sociali, i
consultori, le associazioni. È la traccia femminile delle due tracce di contatto della
sezione 4B, e si distingue perché per le ragazze esiste già un'etichetta censuaria
(casalinga) da cui aprire il colloquio, mentre per i ragazzi un'etichetta così non c'è.
Che cosa ci sia dietro l'etichetta (cura, figli, scelta, vincolo) il censimento non lo
osserva: lo chiede il colloquio.
→ `edu_technical_schools.csv` (anagrafe MIUR: 3 sedi tecniche a Bagheria, 23 a Palermo)

**F2 - Barriera: non il collegamento, ma l'orario e il mezzo che si dà per scontato.**
L'ipotesi ovvia è già stata testata sui 390 comuni e **non trova sostegno**: «più mezzo
collettivo, meno divario di genere» non regge (Spearman **−0,10**, p = 0,06, di segno
opposto all'ipotesi; sul treno l'associazione è nulla, p = 0,29). Il treno a Bagheria è al
**98° percentile siciliano** (97° a parità di distanza e taglia), quindi non è
sottoutilizzato, e l'ultimo miglio dentro Palermo non è un collo di bottiglia. **Il vincolo
non è l'offerta di trasporto**, e questo modulo non ci si appoggia: F2 è la forma operativa
della componente E della sezione 4.
→ `mob_treno_390.csv`, `notebooks/mobilita.ipynb` (sezioni 5 e 8)

Quello che resta di genere, e che i dati mostrano, è un'altra cosa:

- **il mezzo**: fra chi esce da Bagheria (2011) il treno vale il **31,5%** degli spostamenti delle donne e il **16,4%** di quelli degli uomini (mezzo privato 63,6% contro 79,0%). Le donne usano il treno quasi il doppio degli uomini, gli uomini l'auto;
- **l'orario**: fra chi va a lavorare a Palermo, a 17 km, prima delle 7:15 esce il **65,0%** degli uomini e il **54,4%** delle donne; fra chi va a studiare a Palermo la differenza quasi scompare: **la divergenza oraria nasce col lavoro**. Fra tutti quelli che escono dal comune, il **43,8%** delle donne impiega 31-60 minuti contro il 36,1% degli uomini.

Quindi F2 non finanzia trasporto: **vincola il servizio**, e costa istruttoria invece che budget.

1. Nessuna opportunità entra nel piano di transizione senza **verifica di raggiungibilità col mezzo collettivo negli orari reali della posizione**. Un servizio che dà per scontata l'auto seleziona per genere, e lo fa in silenzio.
2. L'**orario di ingresso richiesto dal datore** si registra nell'audit della sezione 4D e si confronta con le corse esistenti: è lì che passa la selezione, non sui chilometri.
3. Il sostegno economico all'abbonamento resta ammesso ma **subordinato**: si attiva su chi ha già l'opportunità in mano, non per creare un'accessibilità che esiste già.

La domanda «il trasporto è la barriera primaria?» non va quindi riaperta nei 90 giorni di
preparazione: quella che resta aperta riguarda l'orario d'ingresso chiesto dai datori
(sotto, nel decision gate).
→ `mob_mezzo_genere.csv`, `mob_sintesi.csv`, cella «fascia oraria di uscita» di
`notebooks/mobilita.ipynb`, mob_fig03

**F3 - Domanda: la leva che il Comune ha già in mano.**
Criteri **premiali** di pari opportunità nelle gare e nelle concessioni comunali per
l'assunzione di donne e di under 36. Il modello normativo esiste: l'art. 47 del DL 77/2021
lega gli appalti PNRR ad assunzioni di donne e di under 36; per le gare ordinarie la base
sono le clausole sociali del Codice dei contratti pubblici (D.Lgs. 36/2023), da verificare
con l'ufficio gare. La verifica dell'esito a 6 e 12 mesi si concentra sulle **donne 22-25**;
l'audit dei datori della sezione 4D raccoglie le posizioni reali su cui il criterio può
mordere.
Premialità, non riserva né requisito di residenza: un vincolo di residenza nelle gare sarebbe
giuridicamente fragile, quindi il radicamento locale dell'esito si misura a valle, non si
impone in gara. È l'unica delle tre componenti che non richiede una struttura nuova: è uno
strumento amministrativo esistente riorientato su un target dichiarato.
⚠️ Il volume è piccolo per costruzione: F3 rende la domanda **verificabile**, non la crea.

### Target e capacità

| | |
|---|---|
| **Platea di riferimento** | **573** ragazze 15-24 inattive e non studenti nel 2024 (387 casalinghe, 183 in altra condizione, 3 in pensione) |
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
| Quota casalinghe F 15-24 | 13,4% | 11,3% (Palermo) | −2,1 pp | **biennio** (potenza 82%) |
| Tasso di occupazione F 15-24 | 8,2% | 9,6% (Palermo) | +1,4 pp | **triennio pooled**, come direzione (potenza 41%) |

Il primario del modulo è la **quota casalinghe**, non l'occupazione. Stesso obiettivo di
convergenza, ma è l'unico dei due che, contro la variabilità dei comuni di taglia simile
(sezione 6), supera l'80% di potenza su una finestra che non attraversa la rottura di
misura del 2021: il biennio. È quindi il primo a restituire un verdetto (con il ritardo di
circa due anni dei dati comunali). Due cautele lo accompagnano: dal 2021 la quota è una
stima di modello del censimento, che può muoversi anche per ragioni di metodo, e si legge
solo dentro la definizione 2021+; e si legge sempre accanto al tasso di occupazione, che è
un conteggio. L'occupazione resta l'outcome che dà senso al primo e si legge sul triennio,
come direzione. Ridurre la quota di chi risulta casalinga non è un giudizio sul lavoro di
cura: è il segnale che una scelta in più è diventata possibile.
→ `genere_mde.csv`, fig09b

**Processo (lettura annuale; oggi nessuno lo rileva)**: utenza F per età singola contro la
platea residente della stessa cella; quota di prese in carico avviate entro 30 giorni;
copertura della finestra 22-25 sul totale femminile preso in carico.

**F2**: quota di partecipanti F che accedono a un'opportunità **fuori comune** entro 6 mesi,
riferimento **33,0% → 41,2%** (la quota di chi esce per lavoro fra le donne e fra gli uomini
di Bagheria, tutte le età, 2019). L'obiettivo è lavorare a Palermo restando residenti a
Bagheria: è il contrario della fuga, non un suo incentivo. Accanto, la misura del filtro:
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
- Non propone interventi sul trasporto. L'ipotesi è stata testata sui 390 comuni e non ha trovato sostegno, e il treno di Bagheria è al 98° percentile siciliano: non è l'offerta di trasporto che manca.
- Non sostiene alcuna tesi di segregazione per indirizzo di studio. L'anagrafe MIUR dà le sedi, non gli iscritti per genere e indirizzo: il dato non esiste, e senza quello «gli indirizzi femminili non convertono» resta un'ipotesi, non un'evidenza.

---

## 5. Decision gate dei primi 90 giorni

Nei 90 giorni di preparazione il servizio raccoglie evidenza sul territorio e decide, riga per riga, quali moduli attivare.

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
(2034), −15,5%**, contando i residenti di oggi a migrazioni nulle; nei benchmark il calo è
simmetrico fra i generi, qui no. L'asimmetria viene da un rapporto fra i sessi anomalo fra i
5-14enni (117 maschi ogni 100 femmine, contro 104-106 nei benchmark), replicato su due tavole
ma senza un meccanismo identificato: il KPI in tasso serve comunque, perché la platea cala
anche fra i ragazzi (−5,8%). Al tasso
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
| Tasso di occupazione F 15-24 | 8,2% | 9,6% (Palermo) | +1,4 pp | **triennio pooled**, come direzione (potenza 41%) |
| Quota casalinghe F 15-24 | 13,4% | 11,3% (Palermo) | −2,1 pp | biennio (potenza 82%) |

**I KPI di popolazione dicono la direzione, non provano l'effetto.** La potenza si misura
contro quanto si muovono, senza interventi, i 33 comuni siciliani di taglia simile a
Bagheria: per +1,4 punti di occupazione è del 50% su un anno, del 59% sul biennio e del 41%
sul triennio; per −2,1 punti di casalinghe arriva all'82% sul biennio. Il modello binomiale
prometteva il 90% sul triennio, ma tratta come indipendenti annualità che contano le stesse
persone: accorpare anni riduce il rumore di conteggio, non le divergenze persistenti fra
comuni. Le finestre restano dichiarate prima dell'avvio, per non sceglierle dopo; la lettura
annuale non è ammessa; la prova dell'effetto sta sui partecipanti (sezione 7).
→ `genere_mde.csv`

Tre precisazioni che i KPI di popolazione si portano dietro:

- **Si leggono come scarto da Palermo, non come soglia.** Il tasso femminile di Bagheria
  sale già da solo (+0,65 punti l'anno dal 2018) e al ritmo attuale toccherebbe il 9,6% in
  un paio d'anni. Il successo è chiudere lo scarto da Palermo, che sale anch'essa: una
  differenza nelle differenze rispetto al controfattuale dichiarato (sezione 7).
- **Sono l'orizzonte, non la prova dell'effetto.** 40 occupate in più su una platea di
  2.882 non si ottengono con 100 prese in carico l'anno. L'effetto del servizio si misura
  sui partecipanti, contro chi comincia più tardi (sezione 7); i tassi comunali dicono se
  il territorio converge.
- **Arrivano tardi.** I dati comunali escono con circa due anni di ritardo: un triennio
  pooled si legge quattro o cinque anni dopo l'avvio. Nel frattempo contano i KPI di
  processo e gli esiti sui partecipanti.

Se serve un equivalente in teste per la comunicazione, si scrive così e non altrimenti:
**«+40 occupate sulla platea 2024; il target si riparametra ogni anno come
tasso-obiettivo × platea dell'anno»**, con la formula pubblicata.

### Outcome del servizio (sui presi in carico)
Quota di partecipanti occupati, in istruzione o in formazione qualificante **a sei mesi,
con esito ancora attivo al dodicesimo**. Il confronto con chi comincia più tardi esiste
solo sull'esito a sei mesi (sezione 7); la tenuta al dodicesimo mese si riporta come dato
descrittivo.

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
riferimento 33,0% → 41,2% (donne e uomini di Bagheria che escono per lavoro, tutte le età,
2019).
⚠️ **Non aggiornabile dalla fonte**: il pendolarismo **scomposto per genere** esiste solo
per 2018-2019 e su quella misura la destinazione è «fuori comune» aggregato. La matrice
origine-destinazione ISTAT *sì* identifica Palermo (91,1% di chi esce per studio nel 2011,
65,1% per lavoro nel 2021) ma è ferma ai censimenti, e il 2021 è senza sesso: nessuna delle
due serve a leggere un intervento anno per anno. Questo KPI si misura sul **dato di
servizio**, mai sulla statistica ufficiale.
→ `mob_flussi_bagheria.csv`, `mob_sintesi.csv`, mob_fig01

---

## 7. Valutazione dell'impatto

La valutazione ha due livelli, e il prima-dopo da solo non basta a nessuno dei due.

**Sui presi in carico: rollout scaglionato.** Fra persone con uguale priorità l'ordine di
avvio è assegnato casualmente quando eticamente possibile; chi inizia più tardi è il
confronto temporaneo. Protocollo, outcome primario, finestre temporali ed esclusioni
pubblicati **prima** dell'avvio. È questo livello che identifica l'effetto del servizio, a
quattro condizioni scritte nel protocollo:

- **due coorti da 100**, con ingresso al mese 0 e al mese 6: chi aspetta, aspetta almeno
  sei mesi, quindi sull'esito primario a sei mesi il gruppo di confronto esiste. Chi
  abbandona resta nel gruppo in cui è stato assegnato;
- **sull'esito a dodici mesi il confronto non c'è**: a quel punto anche la seconda coorte è
  in carico da sei mesi, e la tenuta al dodicesimo mese si riporta come dato descrittivo;
- **se le domande non superano i posti, non c'è sorteggio**: la valutazione diventa
  monitoraggio descrittivo e lo si dichiara. Le gemelle restano un riferimento per i KPI di
  popolazione e non identificano l'effetto del servizio;
- **il pilota vede solo effetti grandi**: con 100 persone per coorte il confronto a sei mesi
  distingue effetti di 18-20 punti o più (17,8 se l'esito senza servizio è del 20%, 19,7 se
  è del 40%); con adesioni dimezzate la soglia sale a 26-28 punti. Un effetto più piccolo
  resterebbe non dimostrato, non assente.
→ `genere_potenza_pilota.csv`

**Sui KPI di popolazione: il controfattuale è dichiarato in anticipo, Palermo.** Il
prerequisito è stato controllato: la pendenza del tasso femminile di Bagheria 2018-2024
(+0,65 pp/anno) non si distingue da quelle di Palermo e dell'Italia (p = 0,29 / 0,33;
Sicilia al margine, 0,054). Con sei annate il test ha poca potenza: non prova tendenze
parallele, dice che i dati non le smentiscono. Il test tratta inoltre ogni annata come un
campione indipendente; senza quel modello, la distanza fra la pendenza di Bagheria e quella
di Palermo (−0,09 punti l'anno) è più piccola di quella del 67% dei comuni siciliani di
taglia simile (`genere_pretrend_390.csv`). È un confronto indulgente, perché include le
divergenze reali fra comuni: dice che la distanza da Palermo è ordinaria, non che le
tendenze siano parallele. Le dieci gemelle strutturali (i comuni più
simili a Bagheria per dimensione, densità, età, stranieri, abitazioni e distanza da
Palermo) sono il secondo termine di confronto.
→ `genere_pretrend.csv`, `genere_gemelle.csv`

⚠️ Sul tasso di occupazione femminile 15+, Bagheria sta **sotto la mediana delle gemelle
in tutti gli anni 2018-2024** (di 2,1-3,1 punti, contro 1,7 nel 2011): lo stacco aperto nel
decennio 2001-2011 non si è chiuso. Il disegno deve poter distinguere l'effetto
dell'intervento dalla prosecuzione di quel divario.

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

## 9-bis. Chi lo gestisce, con chi, e che cosa serve per partire

- **Titolarità.** Il servizio è comunale e sta fra politiche giovanili e servizi sociali,
  che già vedono una parte della platea (sezione 4-bis, F1). Le politiche attive del lavoro
  sono invece di competenza regionale e passano dai Centri per l'impiego: Ponte 19 non le
  duplica, ci porta le persone. I primi accordi da firmare, nei 90 giorni di preparazione,
  sono con il Centro per l'impiego competente e con le scuole secondarie di Bagheria.
- **Rapporto con le misure esistenti.** Garanzia Giovani e il programma GOL si rivolgono a
  chi si registra e si presenta ai servizi per il lavoro. Il segmento che Ponte 19 va a
  cercare è quello che non si presenta (il 70,6% di chi è fuori da lavoro e studio non cerca):
  il servizio è l'aggancio a monte di quelle misure, non un'alternativa.
- **Risorse.** La dotazione minima è quella della sezione 3 (4 case manager e 1 data
  manager per 12 mesi). In ordine di grandezza costa fra **205.924 e 256.105 euro l'anno**:
  il primo valore se il servizio è affidato a una cooperativa sociale (livello D2 del
  contratto, 35.812,94 euro l'anno per persona nelle tabelle del Ministero del Lavoro), il
  secondo con personale comunale dell'area dei Funzionari (44.539,99 euro l'anno per
  persona), in entrambi i casi più il 15% forfettario di costi indiretti ammesso dai fondi
  europei. Per posto fa fra 1.030 e 1.281 euro; il percorso più intensivo del programma GOL
  paga orientamento specialistico e accompagnamento fino a 1.198 euro per partecipante.
  Restano fuori le esperienze retribuite della componente D, che si attivano solo su
  posizioni verificate (all'indennità minima siciliana di 300 euro al mese, 30 posizioni
  costano almeno 9.000 euro per ogni mese), l'IVA di un eventuale affidamento, il tempo del
  personale già in servizio di Comune, scuole e Centro per l'impiego, e la valutazione
  esterna. È una stima parametrica, non un piano economico: quello va costruito con gli
  uffici comunali. → `genere_costo_pilota.csv`, `genere_costo_parametri.csv`.
  Le linee candidate sono il Fondo sociale europeo Plus del programma regionale 2021-2027 e
  le risorse comunali per le politiche giovanili.
- **Dati personali.** Il dataset della sezione 8 riguarda giovani adulti e, nella finestra
  A, studenti dell'ultimo anno. Prima dell'avvio servono una base giuridica di interesse
  pubblico, una valutazione d'impatto sulla protezione dei dati e un accordo con le scuole
  sul flusso delle segnalazioni, che parte solo con il consenso della persona.

## 10. Cosa questa proposta non promette

- Non stima il rendimento occupazionale individuale di un titolo: il dato non esiste, il
  servizio lo creerà. I margini mettono solo un tetto: nel 2024 lavora al massimo il
  16,1% delle ragazze 15-24 con almeno il diploma, contro il 35,7% dei ragazzi
  (`genere_frechet.csv`).
- Non tratta la quota di casalinghe, né la platea degli inattivi non studenti, come un
  conteggio: dal 2021 sono stime di modello del censimento, di cui la tavola comunale non
  riporta l'errore. Solo occupati e residenti sono conteggi (`genere_interi_condizione.csv`).
- Non attribuisce il calo della popolazione 15-34 a emigrazione misurata: la ritenzione di
  coorte è un **saldo netto senza destinazione**. I trasferimenti di residenza per età e
  titolo ISTAT li pubblica solo fino alla provincia; per il comune i dati elementari, anonimi,
  si chiedono a ISTAT, ed è la prima richiesta utile per misurare le partenze.
- Non mette in serie il pendolarismo «verso Palermo»: la destinazione c'è (matrice
  origine-destinazione ISTAT, sezione 4-bis), ma è ferma ai censimenti, il 2021 non ha il
  sesso e la serie annuale per genere dà solo «fuori comune» aggregato.
- Non attribuisce l'inattività a una singola causa non osservata.
- Non tratta la finestra 22-25 come un dato annuale: è una lettura pooled su triennio,
  con oscillazioni fino a 8 pp sulla singola età.

## Linee guida per la presentazione

### Tesi di fondo

> **A Bagheria le ragazze di 15-24 anni arrivano al diploma più dei ragazzi e lavorano la metà. Sette su dieci di chi è fuori da lavoro e studio non cercano: nessuno sportello a domanda li vede. Proponiamo un servizio che li va a cercare, con una quota per le ragazze, e che misura se funziona.**

Cosa la tesi non promette, detto una volta sola e in chiusura: non abbiamo spiegato la fuga. Il pilota misura gli esiti, non pretende di aver trovato la causa. È una clausola, non il messaggio.

## Ordine
1. Introduzione (claims (Ale), come abbiamo svolto il lavoro (Saverio)). 
2. Parte studio-lavoro (Saverio)
3. Genere. (Ale)
4. Policy
5. Conclusioni

È plausibile che nella sezione studio-lavoro possano essere presentati dei dati di supporto ai claim del tema che siano stati rilevati in Genere, vale anche il contrario.

## Stile
Stile minimale, professionale, essenziale, da esposizione.

## Da dire in apertura, prima che lo chiedano (introduzione, Ale)

Il bando è scritto sul NEET 15-34. Va detto nei primi sessanta secondi, come scelta di metodo e non come ammissione:

- Il NEET 15-34 comunale **non esiste nei dati pubblici**: il censimento permanente dà a livello comunale solo la classe 15-24, e il NEET 15-29 c'è solo al 2011. Non lo ricostruiamo e non lo stimiamo. Lavoriamo sul 15-24, che è la fascia che esiste.
- L'incrocio titolo di studio per condizione professionale **non è pubblicato** nelle tavole comunali: i due gap si misurano separatamente e si confrontano i segni.
- Perimetro: fonti consultate, non inesistenza generale.

Detto per primi, a un festival sulla cultura del dato, è un merito. Estratto sotto domanda è una mancanza.

## Claim forti: su cosa si baserà la presentazione
Solo tre claim numerici sono considerati blindati, a patto di utilizzare la formulazione esatta per prevenire le rispettive domande-trappola. L'8,2 ha due trappole, non una.

| **Cifra** | **Forma sicura** | **Domanda-trappola** | **Da NON dire** |
| --- | --- | --- | --- |
| **8,2%** | Occupazione femminile 15-24 nel 2024, la più bassa dei quattro territori in tutte le sei annate: Palermo 9,6, Sicilia 10,4, Italia 17,3 | _«È distinta anche statisticamente, o solo numericamente?»_ | «Significativamente», «minimo storico», e mai «occupazione delle diplomate» |
| **8,2%** (la serie) | Il tasso sale ovunque dal 2018, a Bagheria come altrove; Bagheria resta ultima in ogni annata e lo scarto da Palermo resta sotto i due punti senza chiudersi | _«È quasi raddoppiato in sei anni: non si sta risolvendo da solo?»_ | «Minimo storico», «peggiora», «crolla» |
| **70,6%** | Quota dei 15-24enni fuori da lavoro e studio non classificata in ricerca | _«Non cercare vuol dire non voler lavorare?»_ | «Non vogliono», «scoraggiati» |
| **13,4%** | Casalinghe fra le 15-24enni nel 2024 secondo le stime del censimento, contro 11,3% a Palermo, 10,1% in Sicilia e 4,6% in Italia | _«Condizione dichiarata o ore di cura misurate?»_ (nessuna delle due: dal 2021 è una stima di modello ISTAT) | «Carico di cura», «responsabilità familiari», «si dichiarano» |

Serie di controllo per l'8,2 (tasso di occupazione F 15-24, `genere_forbice_serie.csv`; il 2020 manca alla fonte):

| anno | Bagheria | Palermo | Sicilia | Italia |
| --- | --- | --- | --- | --- |
| 2018 | 4,7 | 6,3 | 7,5 | 14,1 |
| 2019 | 5,2 | 6,9 | 8,0 | 14,5 |
| 2021 | 6,2 | 7,5 | 8,4 | 15,0 |
| 2022 | 7,7 | 8,6 | 9,3 | 16,4 |
| 2023 | 8,0 | 9,2 | 9,9 | 16,9 |
| 2024 | 8,2 | 9,6 | 10,4 | 17,3 |

L'8,2 è il valore **più alto** della serie di Bagheria. È un minimo solo nel confronto fra territori, mai nel tempo: chi ha la serie sotto gli occhi lo vede subito.

Nel power point i limiti tra i punti devono essere flebili. Il terzo punto è un "misto" tra i due, può fungere come punto di transizione tra il 1 e 2 punto.

### Cifre ammesse ad alta voce

Regola: si pronunciano i numeri stampati sulla figura a schermo, sempre con il confronto. Il bando chiede per nome il benchmark con Palermo, la Sicilia e l'Italia: una cifra di Bagheria detta da sola non è prudenza, è un requisito saltato. Fuori dalle figure, solo queste:

1. **70,6%**: quota di 15-24enni fuori da lavoro e studio non classificata in ricerca. L'accesso spontaneo ai servizi ordinari non li intercetta.
2. **8,2%** con **9,6** (Palermo), **10,4** (Sicilia), **17,3** (Italia): occupazione femminile 15-24 nel 2024, la più bassa dei quattro in tutte le sei annate.
3. **13,4%** contro **4,6%** in Italia (11,3 Palermo, 10,1 Sicilia): casalinghe nelle stime del censimento, sono le barre della fig02b.
4. **200**: capacità progettata del pilota nel primo anno, di cui **100** donne (quota del 50%). Non è stima della domanda né copertura della platea. Non si pronuncia senza il KPI del punto 5.
5. **+1,4 punti**: il KPI primario, tasso di occupazione F 15-24 da 8,2 al 9,6 di Palermo, letto su un triennio come direzione della convergenza, non come prova dell'effetto.

## Selezione delle figure

|**Stato**|**Identificativo**|**Ruolo e accortezze verbali**|
|---|---|---|
|**In presentazione**|`fig11_per_1000`|Mette le due misure sulla stessa base; chiarire subito a voce: _«Non osserviamo quante diplomate stiano effettivamente lavorando»_.|
|**In presentazione**|`fig02b_casalinghe_territori`|Rappresenta il bisogno attraverso il confronto territoriale di vicinato. I tre confronti (Palermo, Sicilia, Italia) si dicono a voce, sono sulla figura.|
|**In presentazione**|`fig07_ritenzione_eta`|Usata unicamente come indizio per il reclutamento; specificare tassativamente che **l'asse orizzontale riporta l'età rilevata nel 2021**.|
|**In riserva (backup)**|Carta spostamenti verso Palermo|Da mostrare solo se sollecitati specificamente sul tema del pendolarismo.|
|**Escluse (fuori)**|Mappa 2011-2024 e grafico potenza|Da non inserire nelle slide né mostrare nel tempo principale.|

## Policy: cosa dire (sezione 4)

Nella policy consegnata c'è più di quanto il piano faceva dire. In quest'ordine:

- **Chi.** 18-25 fuori da lavoro e studio, con outreach verso chi non cerca (il 70,6%). Quota del 50% per le ragazze: 100 su 200 nel primo anno. Non è un servizio «per ragazze»: è un servizio con una quota.
- **Come si misura.** KPI in tasso, non in teste. Primario: occupazione F 15-24 da 8,2% a 9,6% (il valore di Palermo), +1,4 punti, letto sul triennio come direzione: contro la variabilità dei comuni della stessa taglia nessuna finestra arriva all'80% di potenza (41% sul triennio). Secondario: casalinghe da 13,4% a 11,3%, sul biennio (82%). Esito del servizio sui presi in carico: occupati, in istruzione o in formazione a sei mesi, con esito ancora attivo al dodicesimo.
- **Come si sa se ha funzionato.** Rollout scaglionato con lista d'attesa: due coorti da 100 a sei mesi di distanza, a parità di priorità l'ordine di avvio è casuale, chi inizia dopo è il confronto sull'esito a sei mesi. Il confronto vede effetti di 18-20 punti o più. Protocollo, outcome e finestre pubblicati prima dell'avvio. Per un contest data-driven è l'asset più forte che abbiamo: **il pilota produce la propria evidenza**. Va detto come titolo della sezione, non come risposta di riserva alla domanda sul p-value.
- **Tempi.** Decision gate a 90 giorni di preparazione, 12 mesi di erogazione in due coorti, follow-up a 3, 6 e 12 mesi.
- **Costo.** Fra 206.000 e 256.000 euro l'anno per la dotazione minima (cooperativa sociale o personale comunale, più il 15% di costi indiretti), fra 1.030 e 1.281 euro per posto; esperienze retribuite escluse.
- **Mobilità.** Non è un capitolo di spesa: è un vincolo di progettazione (componente E) e un KPI (F3, quota di partecipanti che accedono a un'opportunità fuori comune entro sei mesi). Se chiedono «e il terzo thread?», la risposta è questa.

## Frasi vietate (da non pronunciare mai)

- ❌ _«Abbiamo dimostrato perché le ragazze partono.»_
- ❌ _«La famiglia d'origine è la barriera.»_
- ❌ _«Il trasporto non è un problema.»_
- ❌ _«Quaranta occupate prodotte dal servizio.»_
- ❌ _«Chi cerca si risolve da sé.»_
- ❌ _«La pipeline garantisce tutto.»_
- ❌ _«Minimo storico dell'occupazione femminile.»_ (è il massimo della serie di Bagheria)

### Claim negativi e perimetro di validità

- **Fonti consultate, non inesistenza generale.** Il NEET 15-34 comunale **non lo ricostruiamo**; l'incrocio titolo di studio per condizione professionale **non è pubblicato** nelle tavole usate. Entrambi si dicono in apertura (sezione sopra), non si aspetta la domanda.
- **Valore 200:** sicuro **solo come capacità progettata**, mai come domanda stimata o copertura effettiva della platea. Sempre accompagnato dal KPI.

## Prontuario per l'orale: claim da eliminare o ridurre

Elenco delle affermazioni critiche della policy, con la relativa obiezione metodologica e l'eventuale versione difendibile.

- **«Il diploma non si converte in lavoro» (come transizione individuale)**
    - _Trappola:_ «Quante diplomate risultano occupate?»
    - _Forma ridotta:_ Osserviamo insieme istruzione più alta e occupazione più bassa; non seguiamo le stesse persone.
- **Diploma femminile 33,4% e +4,2 punti**
    - _Trappola:_ «Su quale fascia? Un bambino di nove anni non può avere il diploma.»
    - _Forma ridotta:_ È la classe 9-24, la più giovane della tavola istruzione a livello comunale; il denominatore abbassa il livello per entrambi i generi allo stesso modo, e sul 18-24 il vantaggio femminile regge (fig11b). Se non si vuole aprire il tema, non si cita la cifra.
- **Famiglia d'origine come canale dedotta dall'89% di nubili**
    - _Trappola:_ «Quale variabile la osserva?»
    - _Indicazione:_ **Si toglie.** Lo stato civile non misura convivenza, figli a carico o causalità.
- **«Il trasporto non è la barriera»**
    - _Trappola:_ «In che modo un'associazione non significativa esclude un effetto causale?»
    - _Forma ridotta:_ Non troviamo associazione nei dati aggregati; il pilota verifica la raggiungibilità caso per caso, ed è per questo che la mobilità sta nella policy come vincolo di progettazione (componente E) e come KPI (F3), non come capitolo di spesa.
- **«La fuga, contata» (con i 313 residenti in meno)**
    - _Trappola:_ «Quanti sono emigrati e quanti sono semplicemente usciti dalla fascia anagrafica per invecchiamento?»
    - _Forma ridotta:_ Lo stock 15-34 cala, ma non sappiamo chi parte né con quale titolo di studio.
- **«Chi cerca lavoro si sta risolvendo da sé»**
    - _Trappola:_ «La serie storica si rompe fra il 2019 e il 2021; il calo non può essere una riclassificazione?»
    - _Indicazione:_ **Si toglie.**
- **«Tre tavole indipendenti ricostruiscono la stessa catena»**
    - _Trappola:_ «In quale punto dei microdati vedete che chi studiava è esattamente chi non lavora e poi emigra?»
    - _Indicazione:_ **Si toglie.**
- **Ritenzione femminile 96,3 legata alla finestra 22-25**
    - _Correzione:_ Il dato fa riferimento alla **coorte 25-29 nel 2021** (`genere_coorti.csv`). O si cita la coorte corretta, o si omette del tutto. La finestra 22-25 della fig07 è un'altra misura (ritenzione a tre anni per età singola) e non va agganciata al 96,3.
- **«L'istruzione è l'anello intatto» / «Formazione inutile»**
    - _Trappola:_ «Bagheria è ultima sui tassi di diploma e laurea in valori assoluti.»
    - _Indicazione:_ **Si toglie.**
- **«Si esce per studiare, non per lavorare»**
    - _Contraddizione:_ L'appendice della relazione riporta l'opposto.
    - _Indicazione:_ **Si toglie.**
- **«Bagheria è unica nell'inversione» / «Il segno cambia ovunque»**
    - _Correzione:_ Palermo non inverte il segno.
    - _Formulazione esatta:_ Parlare unicamente di «ampiezza diversa dello scarto».
- **Palermo come controfattuale testato (p = 0,29)**
    - _Trappola:_ «Il mancato rifiuto di una differenza statistica non dimostra l'equivalenza dei gruppi.»
    - _Forma ridotta:_ È un confronto descrittivo; l'identificazione causale dell'effetto è affidata alla lista d'attesa. Alla domanda «sta crescendo da solo?» si risponde senza il p-value: cresce allo stesso passo dei territori di confronto, e Bagheria resta ultima in ogni annata.
- **«+40 occupate» / «200 coprono il 18% della platea»**
    - _Incongruenza:_ La platea censuaria 15-24 e i requisiti di accesso 18-25 non si sovrappongono. Il 18% è 200 su 1.121 (tutti i 15-24 inattivi non studenti); il 17% è 100 su 573 (le ragazze).
    - _Formulazione esatta:_ Definirla sempre e solo **platea indicativa**. «+40» solo nella forma della policy: tasso-obiettivo per platea dell'anno, mai «prodotte dal servizio».

## Numeri disallineati nei documenti consegnati: valore giusto e fonte

I documenti sono consegnati dal 30 agosto e la presentazione è il 24 settembre: l'armonizzazione non può più avvenire. `pipeline.verifica` passava (755 su 755) perché queste cifre stavano fuori dalla sua copertura, quindi le discrepanze sono nei PDF che la commissione ha in mano. Non si pronunciano spontaneamente. Se un giurato le solleva, la risposta è il valore giusto con la fonte, in una frase, senza bloccarsi.

| Coppia | Dove | Valore giusto e risposta | Fonte |
| --- | --- | --- | --- |
| **Diploma 33,4% e +4,2** | Relazione dichiara 9-24, policy non dichiara la fascia | 33,4% è la quota di ragazze **9-24** con almeno il diploma nel 2024, contro 29,2% dei ragazzi: +4,2 punti. Attenzione: nella policy «+4,2 punti» compare anche con un altro significato (inattivi non studenti al 19,0%, 4,2 punti sopra la Sicilia). Non usare «+4,2» a voce senza dire di cosa. | `genere_forbice_serie.csv`, `genere_quadro_sintesi.csv` |
| **Uscita prima delle 7:15: 54,4 / 65,0 nel testo, 44,7 / 61,1 nelle schede** | Policy §4-bis, relazione §5.4 contro scheda 3 | Le sole cifre riproducibili sono **44,7% delle donne e 61,1% degli uomini**, su tutti gli spostamenti in uscita dal comune. I 54,4 / 65,0 sono un taglio (verso Palermo) non esportato in processed e non ritrovabile nel notebook: non si difendono, si cita la coppia riproducibile. | `mob_orario_genere.csv` |
| **Mezzo privato 63,6 contro 63,7** | Relazione 63,6, policy 63,7 | **63,6%** (63,64 nel dato). Il 63,7 della policy è un arrotondamento sbagliato. | `mob_mezzo_genere.csv` |
| **Santa Flavia 6,8 contro 7,3** | Relazione 6,8, schede 7,3 | Sono due anni, non un refuso: **6,8% nel 2011, 7,3% nel 2021** (quota di chi esce per lavoro). Se si cita, con l'anno. | `mob_flussi_bagheria.csv` |
| **Treno 98° contro 97° percentile** | La policy usa entrambi | **98°** su 390 comuni per quota di chi esce che usa il treno; **97°** a parità di distanza e taglia. Due misure, non un refuso: citare sempre il qualificatore. | `mob_sintesi.csv`, `mob_treno_390.csv` |
| **Platea 1.121 / 573 / 549 / 771** | Policy §1 e §4-bis | Non sono alternative, sono nidificati: **1.121** è il totale dei 15-24 inattivi non studenti nel 2024 (19,0%), **573** le ragazze, **549** i ragazzi (la somma fa 1.122 per arrotondamento di stime frazionarie); dentro le 573 stanno 387 casalinghe. **771 non compare in nessun documento.** «Quanti sono» è la domanda più probabile di tutte: la risposta è «1.121, di cui 573 ragazze, platea indicativa». | `edu_finding_summary.csv`, `schede_claim.csv` |

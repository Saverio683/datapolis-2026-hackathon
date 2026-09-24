# Revisione tecnica finale: notebook → evidenze → policy

Documento di lavoro, 2026-09-24. Questi riferimenti fondano un protocollo di revisione;
non attestano che il progetto abbia già superato una nuova revisione indipendente.
Le applicazioni proposte sotto sono adattamenti al progetto, distinti dalle
raccomandazioni delle fonti.

## Punto di partenza verificato sul progetto

Il 24 settembre 2026 è stato eseguito `.venv/bin/python -m pipeline.verifica`:
**934 PASS, 0 FAIL**. Il controllo ricalcola risultati dai raw con implementazioni
alternative e verifica anche la presenza delle cifre nei testi. Questo è un controllo
di implementazione e coerenza, non una certificazione delle assunzioni statistiche.

Per preparare questo protocollo sono stati consultati struttura dei quattro notebook,
celle selezionate di `genere.ipynb`, metodologia educazione, policy e parti del verificatore.
Non sono stati rieseguiti i notebook né effettuati tutti gli stress test sotto proposti.
Notebook, dati e deliverable ufficiali non sono stati modificati da questa attività.
I rischi indicati sotto sono domande di revisione, salvo i passaggi testuali e di codice
esplicitamente riscontrati.

## Unità di revisione: l'affermazione che sostiene una decisione

Partire dalle affermazioni centrali della policy e risalire ai notebook. Per ciascuna
costruire una scheda, anche come semplice tabella Markdown:

| Campo | Contenuto obbligatorio |
|---|---|
| Identità | ID del claim, frase esatta, documento e posizione |
| Natura | Dato descrittivo, stima, proxy, associazione, limite matematico, scenario condizionale, ipotesi causale oppure scelta progettuale |
| Perimetro | Territorio, anno, età, sesso, universo, unità, numeratore e denominatore |
| Evidenza | Raw e versione, trasformazione, notebook e ID stabile della cella, CSV e figura |
| Passaggio logico | Perché l'evidenza sostiene la frase; assunzioni necessarie e spiegazioni alternative |
| Uso | Quale target, componente o KPI dipende dalla frase |
| Prova critica | Quale risultato obbligherebbe a cambiare la frase o la decisione |
| Chiusura | Esito, limite residuo, autore, revisore diverso dall'autore e azione da completare |

La duplicazione indipendente del calcolo protegge dagli errori di implementazione;
due implementazioni della stessa assunzione sbagliata possono comunque concordare.
I target politici e le soglie operative possono essere scelte motivate: non serve
presentarle come quantità necessariamente dedotte dai dati.

## Sequenza della revisione finale

1. **Congelare il materiale.** Identificare sorgenti, raw, ambiente, notebook, PDF,
   slide e copione della versione da consegnare. Conservare anche le modifiche locali:
   il solo hash di Git non le identifica. Non aggiornare le fonti durante il collaudo.
2. **Riprodurre in una copia isolata.** Ricostruire gli output dai raw, con l'ambiente
   bloccato e kernel puliti, seguendo l'ordine del README. Eseguire tutti e quattro i
   notebook, i test della pipeline educazione e `pipeline.verifica`. Controllare che
   output preesistenti non nascondano dipendenze mancanti. Conservare log e differenze.
3. **Revisionare definizioni e inferenze.** Compilare le schede dei claim centrali;
   distinguere incertezza di campionamento, modello, classificazione, variazione
   temporale e scelte analitiche. Un intervallo non rappresenta automaticamente tutte
   queste componenti. Verificare anche sovrapposizione dei territori nei benchmark
   e dipendenza fra annualità prima di usare formule di indipendenza.
4. **Provare a smentire le conclusioni.** Dichiarare prima le alternative ragionevoli:
   finestre compatibili con le rotture di serie, gruppi di confronto, fasce e
   ponderazioni. Eseguire solo le prove che potrebbero cambiare una decisione.
   Riportare tutte le alternative provate, inclusi esiti sfavorevoli e risultati nulli.
   Una variante con un altro universo risponde a un'altra domanda: non è una replica.
5. **Revisionare la policy.** Per ogni componente esplicitare problema, barriera
   ipotizzata, azione, esito e condizione di fallimento. Verificare che capacità,
   accesso, costo e valutazione siano compatibili. Separare monitoraggio comunale,
   risultati sui partecipanti e stima causale dell'effetto.
6. **Collaudare la consegna.** Leggere i PDF e le slide effettivi, inclusi titoli e
   didascalie, confrontandoli con le schede dei claim. Una cautela nel notebook non
   corregge un titolo assertivo nella presentazione. Chiudere il registro delle
   criticità con decisioni motivate e ripetere i controlli interessati dalle correzioni.

La revisione delle inferenze non va ridotta alla ricerca di significatività:
un risultato non significativo non dimostra assenza, l'intervallo di due livelli
non è l'intervallo della loro variazione e la robustezza descrittiva non identifica
un meccanismo causale.

## Criticità prioritarie da mettere alla prova

Le priorità sotto sono proposte di lavoro, non probabilità di errore o verdetti complessivi.
Molti limiti sono già dichiarati nel progetto: si verifica che rimangano visibili
nel passaggio alla decisione e nella comunicazione finale.

| Priorità | Punto concreto | Verifica richiesta e criterio di chiusura |
|---|---|---|
| Alta | `genere.ipynb`, cella `5a653e46`: «le oscillazioni annue [...] sono rumore, non trend», motivato dalla collocazione negli intervalli | La sovrapposizione degli intervalli dei livelli non basta a concluderlo. Esaminare direttamente variazione/trend con dipendenze appropriate oppure limitare la frase all'assenza di evidenza sufficiente per quella lettura. |
| Alta | `genere.ipynb`, cella `393221c2`; policy §§4-bis e 6: potenza 82% della quota casalinghe | Il calcolo usa una formula normale e la dispersione delle variazioni di 33 comuni rispetto alla loro mediana; non comprende la variabilità propria di Palermo. Verificare sensibilità a pari, finestra e dispersione stimata. Non presentarlo come potenza già validata del futuro DiD Bagheria-Palermo o probabilità di successo della policy. |
| Alta | Policy §4-bis: la quota casalinghe diventa KPI primario del modulo anche per la sua rilevabilità | Verificare validità sostanziale: una diminuzione può derivare da riclassificazione, composizione o passaggio ad altra inattività. La riduzione da sola non prova un miglioramento; predefinire gli esiti sui partecipanti che rappresentano una transizione utile. |
| Alta | Policy §7: Palermo come confronto, test dei pretrend con sei annualità | Separare compatibilità descrittiva ed identificazione. Esaminare shock diversi, spillover e composizione; non trattare il mancato rifiuto dei pretrend come prova di parallelismo. Se le assunzioni non sono difendibili, il confronto comunale resta monitoraggio. |
| Alta | Policy §§3 e 7: 200 partecipanti, due coorti da 100, quota femminile del 50% | Definire assegnazione, misura a sei mesi prima dell'avvio della seconda coorte, abbandoni, esiti mancanti e contaminazione. La potenza totale non vale automaticamente per il sottogruppo femminile. A dodici mesi conservare il carattere descrittivo già dichiarato. |
| Alta | Dal vantaggio educativo alla «mancata conversione» e dalla ritenzione alla «fuga di talenti» | Verificare che margini separati non diventino transizioni individuali e che il saldo netto non diventi numero di partenze di diplomati. I limiti di Fréchet restano limiti, non stime; controllare l'assunzione di universo comune. |
| Media, alta se decisiva per l'accesso | `genere.ipynb`, celle `80c2a31d`–`bcdcb8ee`: finestra 22-25 esplorativa e pooled | Confrontare finestre adiacenti motivate e transizioni, dichiarando la selezione dopo l'esplorazione. Se la finestra precisa è instabile, mantenere una priorità di ingaggio verificabile nel pilota, senza attribuirle una soglia naturale dimostrata. |
| Media, alta se usata come promessa | Platea osservata 15-24, servizio 18-25; KPI mobilità riferito a lavoratori di tutte le età nel 2019 | Scrivere esplicitamente i diversi universi. Il rapporto con la platea disponibile è indicativo, non copertura esatta degli eleggibili. Costruire la baseline di servizio sul medesimo denominatore del suo futuro KPI. |
| Media | Policy §9-bis: costo parametrico e voci escluse | Presentare scenari di costo completo, capacità e costo per partecipante/esito con ipotesi dichiarate. Non trasformare una stima della dotazione minima in costo totale o in convenienza economica dimostrata. |

La scelta del KPI richiede particolare attenzione: «misurabile con più potenza» e
«più aderente all'obiettivo pubblico» sono proprietà diverse. Il protocollo di
valutazione deve dichiarare quale prevale e perché.

## Come organizzare il team e chiudere i rilievi

Tre responsabilità, distribuibili anche fra tre persone con revisione incrociata:

- **Dati e riproducibilità:** fonti, definizioni, trasformazioni, esecuzione e lineage.
- **Statistica e inferenza:** unità osservata, assunzioni, incertezza, robustezza e
  alternative alla spiegazione proposta.
- **Policy e comunicazione:** teoria del cambiamento, target, costi, KPI, valutazione
  e coerenza del messaggio nei deliverable.

Ogni autore prepara l'evidenza; una persona diversa formula e chiude il rilievo.
Una breve sessione di premortem può partire da: «La giuria ha respinto la tesi centrale:
quale passaggio è saltato?» e «Il pilota ha raggiunto il KPI senza aiutare i giovani:
come è potuto accadere?». Ogni risposta deve produrre un controllo, non solo un timore.

Usare tre classi di rilievi:

- **Bloccante:** errore di dati, calcolo o universo che cambia una conclusione centrale;
  claim causale non sostenuto presentato come risultato; evidenza centrale non
  ricostruibile. Correggere o ritirare il claim prima della consegna.
- **Da qualificare:** evidenza utilizzabile entro un perimetro più stretto. Limitare la
  frase e adeguare la decisione dipendente, poi far approvare la nuova formulazione.
- **Limite accettato:** informazione indisponibile che non invalida il claim residuo.
  Dichiarare conseguenza, proprietario e raccolta dati necessaria; non marcarlo risolto.

La consegna è pronta quando i claim centrali hanno tracciabilità completa, i controlli
necessari passano, non restano rilievi bloccanti e ogni limite residuo è coerente con
le promesse della policy e con la versione finale delle slide. La fattibilità di un
pilota da proporre alla giuria resta distinta dall'autorizzazione ad avviare un servizio:
le verifiche amministrative e operative richiedono i responsabili competenti.

## Riferimenti metodologici verificati

### 1. AQuA Book: verifica, validazione e revisione proporzionata al rischio

La guida distingue la **verifica** dell'implementazione rispetto alle specifiche dalla
**validazione** dell'idoneità dell'analisi all'uso previsto. Richiede anche una componente
di assurance indipendente dall'autore, con profondità commisurata alle conseguenze
di un errore e alla complessità dell'analisi. Copre analisi descrittive e decisionali,
non soltanto modelli predittivi. Fonte: Government Analysis Function,
[The AQuA Book, §§1.3, 3, 5–9, edizione 2025](https://www.gov.uk/guidance/the-aqua-book).

**Applicazione proposta:** due giudizi separati per ogni affermazione centrale:
«il calcolo è corretto e riproducibile?» e «quel calcolo autorizza questa conclusione?».
Concentrare la revisione indipendente sulle affermazioni che determinano target,
strumenti o KPI della policy. Una suite di regressione verde non risponde da sola
alla seconda domanda. Dichiarare chi produce, chi revisiona e chi accetta i limiti residui.

### 2. Magenta Book: teoria del cambiamento e valutazione dell'intervento

La teoria del cambiamento esplicita intervento, meccanismi, risultati attesi,
assunzioni, evidenza a loro sostegno e contesto. La guida raccomanda di considerare
anche perché i passaggi potrebbero fallire e le spiegazioni alternative dei risultati.
Distingue valutazione del processo, dell'impatto e del rapporto fra costi e risultati.
Fonte: HM Treasury,
[Magenta Book, §§1–2, aggiornamento 15 maggio 2026](https://www.gov.uk/government/publications/the-magenta-book/magenta-book-central-government-guidance-on-evaluation-html).

**Applicazione proposta:** per ogni componente di Ponte 19 scrivere
«problema osservato → barriera ipotizzata → azione → risultato misurabile», marcando
quali frecce sono documentate e quali restano ipotesi. Se i notebook mostrano uno
svantaggio, non dimostrano automaticamente che lo specifico intervento lo ridurrà.
La policy può proporre un pilota verificabile con condizioni di prosecuzione,
senza presentare l'efficacia futura come risultato dell'analisi descrittiva.

### 3. JRC: sensibilità delle conclusioni alle scelte analitiche

Il JRC distingue l'analisi dell'incertezza complessiva dall'analisi delle fonti
di variazione. Illustra come inclusioni, dati mancanti, normalizzazioni, pesi e
aggregazioni possano alterare punteggi, graduatorie e messaggi di policy. Fonte:
Commissione europea, JRC,
[Step 8: Sensitivity analysis](https://knowledge4policy.ec.europa.eu/composite-indicators/toolkit_en/navigation-page/10-step-guide_en/step-8-sensitivity-analysis_en).

**Applicazione proposta:** il riferimento nasce per indicatori compositi; qui se ne
adatta il principio, senza introdurre un indice nuovo. Variare scelte difendibili
che possono cambiare la tesi: gruppo dei pari, finestra temporale, età, ponderazione,
esclusione dei capoluoghi, trattamento delle rotture di serie. Registrare se cambia
il segno, l'ordine di grandezza o la decisione. Dichiarare prima le alternative,
riportandole tutte; evitare di scegliere soltanto quelle che conservano il racconto.
La stabilità fra specificazioni non identifica, da sola, un effetto causale.

### 4. Inferenza ecologica: rispettare il livello a cui i dati osservano

Le analisi territoriali possono rispondere a domande territoriali e generare ipotesi;
non consentono di trasferire automaticamente associazioni fra territori agli
individui che vi risiedono. Fonte: Zeoli, Paruk, Pizarro e Goldstick,
[Ecological Research for Studies of Violence: A Methodological Guide (2019), manoscritto in CDC Stacks](https://stacks.cdc.gov/view/cdc/125397).

**Applicazione proposta:** il principio metodologico si trasferisce al progetto,
pur provenendo da un altro dominio. Il coesistere di maggiore istruzione femminile
e minore occupazione non identifica quante diplomate lavorano né misura la loro
transizione individuale. Una ritenzione di coorte non identifica titolo di studio,
destinazione o motivo delle uscite. Il controllo editoriale deve cercare questi
salti in titoli, grafici, schede e policy, oltre che nelle cautele dei notebook.

### 5. FMEA/FMECA: anticipare modalità di errore e conseguenze

La FMECA organizza l'esame delle modalità di guasto, dei loro effetti e della loro
criticità, mantenendo la valutazione aggiornata quando aumenta la conoscenza del
sistema. Fonte: NASA Goddard,
[GSFC-HDBK-8004, Guideline for Failure Modes and Effects Analysis and Risk Assessment (2024)](https://standards.nasa.gov/node/12367).

**Applicazione proposta:** usare una versione leggera come registro delle criticità
analitiche, senza dichiarare conformità al manuale aerospaziale. Per ciascun rischio:
affermazione coinvolta, possibile errore, conseguenza sulla policy, controllo che
lo intercetta, responsabile e decisione finale. Esempio: «quote con denominatori
diversi confrontate come tassi comparabili → target sbagliato → ricostruzione
indipendente di numeratore, denominatore, universo e anno».

## Limite del “modello di previsione delle criticità”

La proposta è una **valutazione preventiva e tracciabile del rischio**, non una
previsione statistica della probabilità di errore. Questa distinzione è una scelta
operativa per il progetto: etichette come alto/medio/basso esprimono giudizi motivati,
non frequenze stimate. Evitare percentuali inventate o un punteggio complessivo
ottenuto moltiplicando scale ordinali come se fossero probabilità.

Per ogni criticità, separare:

- **Impatto:** se fosse vera, cambierebbe una cifra secondaria, una conclusione o la policy?
- **Evidenza disponibile:** è un errore dimostrato, una fragilità osservata o un'ipotesi da controllare?
- **Controllo:** quale verifica concreta può confermarla, ridimensionarla o escluderla?
- **Esito:** correggere; limitare la formulazione; raccogliere dati; accettare con motivazione.

Il registro serve a scegliere dove investire il tempo di revisione. Non sostituisce
la verifica dei dati, il confronto fra interpretazioni né una valutazione dell'impatto
della policy dopo la sua realizzazione.

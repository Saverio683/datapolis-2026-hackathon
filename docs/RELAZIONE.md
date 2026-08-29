# La relazione - spina dorsale e scelte dichiarate

Documento di progetto, scritto il 2026-08-28. Tiene le decisioni che la relazione di
accompagnamento non deve rimettere in discussione: la tesi, le tre figure, e i limiti
che si dichiarano invece di nasconderli. **La relazione completa che ne discende è
`docs/RELAZIONE_DATAPOLIS.md`** (scritta il 2026-08-28): se una decisione cambia qui,
va riportata anche lì.

Regola che vale ovunque qui dentro: **nessuna cifra si scrive a mano**. Ogni numero
citato punta alla cella o al file che lo produce, e si rigenera con
`uv run jupyter nbconvert --to notebook --execute --inplace notebooks/<nb>.ipynb`.

---

## 1. La tesi

> **Bagheria produce titoli e non li converte. La conversione fallisce soprattutto sulle
> ragazze (più istruite del panel, 8,2% di occupazione, il minimo dei quattro territori
> in 6 anni su 6), in una finestra d'età stretta (22-25, ritenzione 96,3 contro ~103 in
> Italia), e il vincolo di mobilità ha lo stesso segno. Chi resta fuori non è chi cerca
> lavoro: il 70,6% dei giovani fuori da lavoro e studio non cerca nemmeno.**

I tre thread non danno tre diagnosi diverse: danno **una diagnosi in tre punti della
stessa catena**, formazione → conversione → permanenza. Ogni anello viene da una tavola
diversa, quindi nessuno è la riformulazione di un altro.

| Anello | Evidenza | Origine |
|---|---|---|
| I titoli ci sono | +4,2 pp di vantaggio femminile sul diploma; `I8` 2011 al 96,7% | `genere_quadro_sintesi.csv`, `edu_historical_benchmarks_2011.csv` |
| La conversione fallisce | occupazione F 15-24 all'8,2%, minimo del panel in 6 anni su 6 | `genere_forbice_serie.csv` |
| …e fallisce anche in mobilità | fra chi già lavora, escono dal comune 41,2% M contro 33,0% F, doppio dello scarto regionale; **sullo studio il segno si inverte** | `genere_pendolarismo.csv` |
| Poi si perdono | ritenzione F 25-29 = 96,3 (Italia 103,0); finestra 22-25 | `genere_coorti.csv`, `genere_ritenzione_eta.csv` |
| Chi resta fuori non cerca | 19,0% inattivi non studenti su 26,9% fuori da lavoro e studio = 70,6% | `edu_finding_summary.csv` |

⚠️ La finestra 22-25 è una lettura **pooled**: le transizioni annuali oscillano fino a
8 pp sulla stessa età. Si titola sul triennio, mai sull'anno singolo.

## 2. Il vincolo che rende la proposta seria

> **La platea femminile 15-24 è già nata e cala del 15,5% al 2034. Le "+40 occupate"
> valgono +18 nel 2029 e −2 nel 2034 (fig09). Cioè il KPI va scritto in tasso, non in
> teste, un dettaglio che di solito nessuno vede prima di scriverlo male.**

Conto in `genere_kpi_netto.csv`: al tasso obiettivo di Palermo (9,59%) il KPI lordo di
+40,4 occupate incontra un attrito demografico di −22,2 al 2029 e −42,9 al 2034 → netto
**+18,2** e **−2,5**. La platea F passa da 2.882 a 2.651 a 2.435 (`genere_platea.csv`):
è un conteggio di chi è **già nato**, non una proiezione.

⚠️ Da non confondere: **−19/−37** è lo scenario «non si fa niente» (tasso 2024 fermo,
`genere_tetto_platea.csv`); **−22/−43** è lo stesso attrito al tasso obiettivo. Due
numeri, due domande.

---

## 3. Le tre figure - dichiarate

La locandina chiede **2-3 visualizzazioni avanzate**. Queste sono le tre candidate alla
consegna; le altre restano nei notebook come apparato.

> ✅ **Scelta chiusa (2026-08-29).** La terna consegnata è quella qui sotto:
> `fig05_forbice`, `fig07_ritenzione_eta`, `fig04_mappa_sicilia`. Il criterio, dichiarato
> perché sia contestabile: la locandina chiede il **profiling e benchmarking** come voce
> obbligatoria e l'**analisi esplorativa** come «focus a scelta, almeno una dimensione»
> fra titolo per condizione, genere e pendolarismo. La terna copre quindi l'obbligatorio
> (`fig04`, Bagheria come punto fra 390 e non come aneddoto), il focus scelto al suo
> punto più affilato (`fig05`, il paradosso che dà il titolo alla relazione) e
> l'obiettivo del brief, la fuga di talenti (`fig07`, l'unica figura che dice **a che
> età** si parte, ed è la ragione per cui «Ponte 19» prende di mira la finestra 18-25).
>
> **Prima riserva: `mob_fig01_verso_palermo`.** È la candidata che resta fuori di poco:
> carta a flussi, forte impatto comunicativo, e risponde alla lettera al terzo focus.
> Non entra per due ragioni. Coprire un secondo focus opzionale vale meno che tenere la
> catena evidenza-intervento intatta, perché senza `fig07` la finestra d'età della
> proposta resta senza figura che la giustifichi; e con `fig04` già in terna la carta
> sarebbe la seconda su tre, ridondante nella forma. Il pendolarismo resta comunque
> presente nel pacchetto, con `scheda3_pendolarismo` e le quattro figure del thread.
> Per riaprire la scelta basta scambiare `fig07` con `mob_fig01` qui e nel pacchetto
> d'invio: le due figure sono autonome e nessun'altra parte del testo dipende da quale
> delle due è in terna.

### ① `fig05_forbice` - il paradosso
**Perché**: è la tesi in un'immagine sola. A sinistra il quadrante sulla **stessa fascia
15-24** (vantaggio nel diploma F−M × tasso di occupazione femminile): Bagheria da sola
nell'angolo «più istruite, meno occupate». A destra la forbice nel tempo, con il distacco
dal vicinato che si apre dal 2021.
**Cautela in caption**: sulla fascia 15-24 il primato del vantaggio educativo è un
pareggio con la Sicilia (+4,8 contro +4,7). Il claim è **il distacco dal vicinato e la
mancata conversione**, non il primato assoluto.

### ② `fig07_ritenzione_eta` - il *quando* della fuga
**Perché**: risponde a «fuga di talenti» con qualcosa di più preciso di "i giovani se ne
vanno" - dice **chi** e **a che età**. Profilo per età singola (F | M, quattro territori
+ vicinato) con la finestra 22-25 evidenziata; sotto, lo slope chart dei due decenni che
risponde all'obiezione che tre anni non bastano a chiamarla fuga.
**Cautela in caption**: il decennio 2011-2021 unisce due rilevazioni; il verso della
distorsione è dichiarato.

### ③ `fig04_mappa_sicilia` - la scala
**Perché**: la locandina nomina esplicitamente le mappe, e questa evita il difetto tipico
del caso singolo - Bagheria diventa un punto in 390, non un aneddoto. Coropleta 2024 +
istogramma delle due distribuzioni + scatter percentile 2011 × 2024 con rho di Spearman.
**Titolo**: *nel 2024 Bagheria arriva dove stava la mediana siciliana nel 2011*.

### Nuova, fuori dalla terna: `fig12_pendolarismo`
Il terzo focus del brief, che prima non aveva figura. Dumbbell M→F su due pannelli
(lavoro | studio): il verso dello scarto cambia col motivo in tutti i territori, e
Bagheria ha **l'ampiezza maggiore del panel in entrambi**, 8,2 punti sul lavoro (doppio
della Sicilia) e 2,7 sullo studio, con segno opposto.
**Cautele in caption**: `OMPUR` è «fuori comune» aggregato, quindi **questa figura** non
misura il pendolarismo verso Palermo — lo fa `mob_fig01`, da un'altra fonte; Palermo ha
valori bassissimi perché è un comune grande e su questa misura non è un termine di
paragone; la serie esiste solo per 2018-2019. Il suo valore, dopo il thread mobilità, è di
essere la **replica indipendente** del ribaltamento: stessa conclusione, altra rilevazione.

### Nuove, fuori dalla terna: le quattro del thread mobilità (2026-08-29)
Il terzo focus del brief, misurato sulla matrice origine-destinazione ISTAT.
- **`mob_fig01_verso_palermo`** - carta a flussi, due pannelli (studio 2011 | lavoro 2021):
  91,1% e 65,1% di chi esce va a Palermo, col nome del comune di arrivo.
  **Cautele**: le due annate hanno definizioni diverse e non stanno in serie; si confronta
  la composizione. Linee rette fra i centroidi, non percorsi.
- **`mob_fig02_ribaltamento`** - il risultato del thread: slope chart a cinque territori
  (+2,6 sullo studio, −12,1 sul lavoro, salto 14,7 contro 6,0 siciliano) e distribuzione
  dei 390 comuni. **Cautele**: conteggio esaustivo, nessuna età nella fonte.
- **`mob_fig03_treno_genere`** - mezzo e orario per genere, più il pannello che impedisce
  la lettura sbagliata: il treno a Bagheria è al 98° percentile siciliano, non è
  sottoutilizzato. **Cautele**: mezzo/orario/durata sono stime campionarie, calibrate sui
  margini esatti; errore relativo mediano 0,9%.
- **`mob_fig04_taglia_distanza`** - la figura che **toglie di mezzo un claim**: il 25°
  percentile di `M2` era un effetto della taglia, a parità di distanza e dimensione il
  residuo è −1,9 punti. **Cautele**: distanza in linea d'aria, nessuna pretesa causale.

### Fuori dalle tre, ma dentro la proposal
`fig09_kpi_finestra` non è una delle tre: sta nella **policy proposal**, ed è la figura
che la rende credibile - dichiara in anticipo *quando* si potrà dire se l'intervento ha
funzionato, e porta la cascata del KPI netto.

---

## 3-bis. Le quattro schede tematiche (2026-08-29)

Le figure rispondono una domanda per volta; le **schede** rispondono una *richiesta del
bando* per volta, incrociando i tre thread. Sono la superficie che accompagna la proposta,
e stanno in `docs/schede/` (HTML autoportante, stampabile in PDF con `@page A4`).

| Scheda | Richiesta della locandina | Cosa incrocia | Blocchi |
|---|---|---|---|
| `scheda1_profilo` | Profiling statistico & benchmarking | educazione (stati 15-24, arco 1991-2011, NEET storico) + demografia | 6 |
| `scheda2_forbice` | Focus differenze di genere, e «titolo × condizione» per quanto i dati consentano | genere (forbice, mappa dei 390, ritenzione per età, casalinghe, stato civile) + educazione (pari a pari istruzione) | 6 |
| `scheda3_pendolarismo` | Focus pendolarismo verso Palermo | mobilità (destinazione, ribaltamento, mezzo, taglia e distanza) + genere (coorti 25-29) | 5 |
| `scheda4_ponte19` | Proposta di intervento | tutte e tre: ogni scelta di progetto ha accanto il numero che l'ha imposta | 5 |

Si rigenerano con `uv run python -m pipeline.schede`, che legge solo `data/processed/`.
**Nessuna cifra è scritta a mano**: ogni claim finisce in `data/processed/schede_claim.csv`
con accanto il file che lo produce e la sua cautela (42 claim al 2026-08-29). È il modo in
cui la regola «nessun numero hardcodato nelle slide» diventa verificabile invece che
dichiarata.

**I blocchi sono numerati e portano la didascalia a quattro blocchi** (2026-08-29). Ogni
sezione di scheda si chiama «Figura 2.3» o «Tavola 4.1» e chiude con *cosa mostra · base
statistica · come si legge · fonte*, la stessa anatomia di `didascalia_4b()` in
`viz/theme.R`. In `blocco()` i quattro sono argomenti obbligatori senza default, e `main()`
verifica che ogni sezione ne abbia quattro: prima N, intervalli e metodo finivano dove
capitava, ed erano assenti in metà dei blocchi. La numerazione serve perché la proposal
possa citare «figura 2.4» invece di «il terzo grafico della scheda 2»: prima le schede
citavano `data/processed/`, ma nulla poteva citare le schede.

**Le schede incorporano sei figure di `figures/`**, ed è la giuntura che prima mancava fra
le schede e lo zip. La regola, in `figura()` di `pipeline/schede.py`, è che il default sia
il **ritaglio al solo grafico**: la figura R porta già titolo, sottotitolo e didascalia, che
la scheda rifà in HTML alla propria tipografia, e un PNG a 300 dpi rimpicciolito a una
colonna renderebbe quel testo a circa cinque pixel, illeggibile. Il ritaglio trova le bande
di inchiostro e toglie la testa e le ultime quattro bande, che sono sempre i quattro blocchi
della didascalia (`--bande` stampa la struttura di ogni PNG). L'**immagine intera** si usa
solo nelle appendici, a piena larghezza, dove il punto non è il dato ma mostrare che la
tavola dello zip viaggia da sola con la propria didascalia.

| Figura R | Dove | Come |
|---|---|---|
| `edu_fig01_storia_posizione` | figura 1.4 | ritagliata: restituisce al thread educazione l'asse del tempo |
| `fig04_mappa_sicilia` | figura 2.3 | ritagliata: una delle tre viz dichiarate, prima assente dalle schede |
| `fig07_ritenzione_eta` | figura 2.4 | ritagliata: la seconda viz dichiarata, e l'evidenza che impone le due finestre |
| `mob_fig04_taglia_distanza` | figura 3.4 | ritagliata: i due risultati negativi, prima solo testo |
| `fig05_forbice` | tavola 2.6 | **intera**, in appendice |
| `fig09_kpi_finestra` | tavola 4.5 | **intera**, in appendice |

⚠️ **Una discrepanza da sanare**: il percentile del divario di pendolarismo sul lavoro è
**13° sui 381 comuni non capoluogo** (notebook, cella 18) ma **15° sui 390** della tavola
condivisa `mob_ribaltamento_390.csv`. `docs/CONTEXT-fabio.md` scrive «13° percentile dei
390 comuni», che è la combinazione sbagliata delle due. La scheda 3 dichiara entrambi i
denominatori; il testo di CONTEXT-fabio va corretto.

## 4. Mappa brief → evidenza

| Richiesta locandina | Risposta | Dove |
|---|---|---|
| Profiling & benchmarking vs Sicilia / Italia / Palermo | ✅ con IC, percentili sui 390 comuni e **due** gruppi di pari dichiarati | `notebooks/genere.ipynb`, `notebooks/educazione.ipynb` |
| Focus **genere** | ✅ focus principale | thread genere |
| Focus **titolo × condizione** | 🟡 risolto come due misure parallele sulla stessa fascia | `fig11_per_1000` |
| Focus **pendolarismo** | ✅ destinazione identificata (91,1% studio e 65,1% lavoro verso Palermo) e ribaltamento di genere, replicato su due fonti | `mob_fig01`-`04`, `fig12_pendolarismo`, `notebooks/mobilita.ipynb` |
| Technical notebook riproducibile | ✅ sensore nbconvert verde sui quattro notebook (2026-08-29) | - |
| 2-3 data viz | ✅ le tre dichiarate sopra | `figures/` |
| Policy proposal | ✅ | `docs/POLICY_PONTE_19.md` |

## 5. I limiti che si dichiarano per primi

1. **Il NEET 15-34 della locandina non è calcolabile** a livello comunale. Si portano due
   misure etichettate e mai unite: NEET 15-29 al **2011** (40,1%; Sicilia 34,7, Italia
   22,5) e «fuori da lavoro e istruzione» **15-24** al 2024 (26,9%). Fasce e definizioni
   diverse: affiancate, mai in serie.
2. **L'incrocio titolo × condizione non esiste** nelle tavole comunali (verificato: nella
   tavola lavoro il titolo è solo `ALL`, in quella istruzione la condizione è solo `99`).
   "Quanti diplomati lavorano a Bagheria" non è una domanda a cui si può rispondere.
3. **«Verso Palermo» si misura, l'età no.** Il limite scritto qui fino al 2026-08-28 —
   «non è misurabile con le fonti in repo» — era una proprietà delle fonti consultate, non
   dei dati pubblici: la matrice del pendolarismo ISTAT dà il comune di destinazione
   (`docs/sources.md` §12). Quello che resta vero: **nessuna fonte incrocia il pendolarismo
   con l'età**, quindi il target 15-34 non è isolabile su questa dimensione, e la ritenzione
   di coorte resta un saldo netto senza destinazione. Le due misure non si sommano.
4. **Nessuna stima causale.** Il disegno di valutazione ha il pre-periodo testato, ma
   l'intervento non è avvenuto: tutto ciò che si mostra è descrittivo o ecologico.
5. **Il 2020 manca** sulla classe 15-24 e le età singole partono dal 2021. Buchi alla
   fonte, mai interpolati.
6. **Rottura di misura 2019→2021** sulla componente "in cerca": i gap fra territori
   reggono, i livelli delle componenti no.

## 6. Prima di congelare

- [x] sensore `nbconvert` sui quattro notebook, verde il 2026-08-29
- [x] `Rscript viz/build_all.R` dopo l'ultima modifica ai `data/processed/` — 37 figure, il 2026-08-29 (il glob ora prende anche il prefisso `mob_`)
- [x] `uv run python -m pipeline.verifica` — 701/701 PASS il 2026-08-29 (pin di regressione dei thread genere e mobilità: i 51 controlli `mob_` sono nuovi, e coprono il KPI «+279 donne» della proposal)
- [ ] rigenerare `docs/RELAZIONE_DATAPOLIS.docx`: è fermo alla versione del 2026-08-28, prima della correzione della sezione 5

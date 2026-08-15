# Le gemelle di Bagheria — trovare il benchmark giusto invece di quello comodo

> Confrontare Bagheria con l'Italia dice poco: quasi tutto il Mezzogiorno perde quel confronto.
> La domanda utile è se Bagheria stia peggio dei comuni che le somigliano davvero.

## L'idea

Il brief impone il confronto con Palermo, Sicilia e Italia, ed è giusto tenerlo. Ma tre
benchmark scelti per convenzione non dicono se un valore sia **anomalo** o semplicemente
**meridionale**. Questa idea costruisce un quarto benchmark, costruito dai dati: un gruppo di
comuni siciliani **statisticamente comparabili** a Bagheria per dimensione, struttura
demografica, condizioni abitative e posizione rispetto al capoluogo — e ci misura dentro la
posizione di Bagheria, in particolare sugli indicatori femminili.

Se Bagheria sta come le sue gemelle, il problema è strutturale e la policy deve essere
regionale. Se sta peggio delle sue gemelle, c'è qualcosa di locale su cui un comune può agire
— ed è esattamente il tipo di conclusione che rende una proposal difendibile.

## Perché è rilevante

È la risposta alla prima obiezione che una giuria fa a qualunque analisi comparativa:
*"ma non è così dappertutto in Sicilia?"*. Avere il gruppo di controllo pronto trasforma
l'obiezione in un punto a favore. Serve inoltre come **gruppo di controllo** per il disegno di
valutazione (`misurare_il_dopo.md`) e come base realistica per fissare i target dei KPI.

## Cosa dicono già i dati

- `ottomilacensus_long.csv` copre **390 comuni siciliani × 99 indicatori × 3 censimenti**
  (1991/2001/2011): è già scaricato, già in formato lungo, già con i codici territoriali
  normalizzati.
- Bagheria è al **12° percentile** per occupazione femminile 15+ (2011) e al **25°** per
  mobilità fuori comune: due posizionamenti bassi, ma calcolati su *tutti* i comuni, inclusi
  quelli montani da 500 abitanti che non sono un termine di paragone sensato.
- La cartografia dei 390 comuni è già pronta e non richiede `sf`
  (`comuni_sicilia_poligoni.csv`, EPSG:32633; esempio completo in `viz/fig04_mappa_sicilia.R`).

## Cosa bisogna sviluppare

1. **Definire la somiglianza su variabili non-outcome**: popolazione, struttura per età,
   patrimonio abitativo, distanza/posizione rispetto al capoluogo, vulnerabilità. ⚠️ Vanno
   **escluse** dal criterio di somiglianza le variabili che poi si vogliono confrontare
   (occupazione, istruzione, genere): altrimenti si selezionano comuni simili proprio in ciò
   che si voleva testare, e il confronto si annulla da solo.
2. **Costruire il gruppo**: distanza di Mahalanobis su componenti principali, oppure
   k-means, oppure semplicemente i *k* comuni più vicini. La scelta va motivata in una cella,
   e il risultato va mostrato robusto al variare di *k* — un gruppo che cambia
   completamente da *k*=10 a *k*=15 non è un gruppo.
3. **Misurare dentro il gruppo**: percentile di Bagheria sugli indicatori femminili (`L11`
   occupazione femminile, `L7` disoccupazione femminile, `I1` differenziale di istruzione)
   rispetto alle gemelle, non rispetto ai 390.
4. **Verifica di sanità**: le gemelle trovate devono essere riconoscibili a un occhio locale
   (comuni costieri della cintura palermitana di taglia media). Se il metodo restituisce
   comuni dell'entroterra ennese, il criterio è sbagliato, non la realtà.

## Fattibilità

🟢 Dati già presenti, nessun fetch. Solo pandas + scipy/scikit-learn (già in stack).
🟡 Il vincolo vero è che il matching si fa sul **2011**: le variabili strutturali cambiano
lentamente, quindi il gruppo resta valido, ma va dichiarato che è definito su dati 2011 e
usato per confronti 2018-2024.
🔴 Gli indicatori di genere di 8milaCensus sono su **15+, non giovanili**: il gruppo di
gemelle si costruisce e si confronta lì, e il risultato giovanile 2018-2024 resta limitato ai
quattro territori del brief. Non si può avere il peer group *e* la fascia 15-24 insieme: è un
limite della fonte, va detto.

## Viz candidata

Mappa della Sicilia con le gemelle evidenziate e Bagheria in risalto, affiancata a un
**dot plot** dove Bagheria è un punto colorato dentro la nuvola delle gemelle su tre o quattro
indicatori. È la figura che rende immediata la frase "peggio anche di chi le somiglia".

## Verso la proposal

- **Evidenza** → posizione di Bagheria dentro il proprio gruppo di comparabili, non contro
  medie che includono territori incomparabili.
- **Intervento** → se lo scarto è locale, l'intervento è comunale ed è giustificato; se non
  lo è, la proposta diventa un modello replicabile sulla cintura metropolitana, che è una
  conclusione più forte, non più debole.
- **Target/KPI** → il target numerico dei KPI smette di essere arbitrario: "raggiungere la
  mediana delle gemelle" è difendibile in un modo in cui "raggiungere l'Italia" non è.

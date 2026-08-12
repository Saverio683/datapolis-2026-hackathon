# CONTEXT — Saverio (focus educazione)

Contesto per il thread educazione. Le regole condivise (territori, anno base 2021, fasce,
trappole sui totali) stanno in `CLAUDE.md`; qui i fatti già verificati che riguardano
questo focus, per non ripetere ricognizioni già fatte.

## Verificato sui dati (2026-08-12)
- **L'incrocio condizione professionale × titolo di studio NON esiste a livello comunale**
  nel censimento permanente: nella tavola lavoro il titolo è solo `ALL`, in quella
  istruzione la condizione è solo `99`. Dimostrato nella cella "Verifica di fattibilità"
  di `notebooks/genere.ipynb`. "Tra i diplomati, quanti lavorano" non è una domanda a cui
  i dati comunali rispondono: non perderci tempo.
- La strada è **regionale/nazionale**: a livello `ITG1`/`IT` l'SDMX ISTAT pubblica incroci
  più ricchi. Un risultato sui ritorni del titolo di studio **per genere** in Sicilia
  farebbe da ponte col thread genere: a Bagheria le ragazze studiano più dei coetanei
  (dato comunale), ma il vantaggio si converte in lavoro? Etichettare sempre il livello
  territoriale quando si combinano i due.
- Tavola istruzione comunale: unica fascia giovanile `Y9-24` (dal 2018); titoli
  disponibili: `NED`, `PSE`, `LSE`, `USE_IF`, `BL`, `ML_RDD` (+ aggregati). Attenzione al
  denominatore: la fascia include bambini, e a Bagheria la struttura per età dentro la
  fascia differisce fra i generi (cella "Verifica di composizione per età" in
  `genere.ipynb` — parte del gap M-F è composizione).
- 8milaCensus: indicatori `I1`-`I9` (istruzione) su **tre censimenti 1991/2001/2011** per
  tutti i **390 comuni siciliani** → serie storiche lunghe e confronti cross-comunali
  (percentili, scatter). Correlazioni fra comuni = ecologiche: orientano, non dimostrano.
- Il 2020 manca sulla classe 15-24 della tavola lavoro; le età singole esistono solo dal
  2021. Non interpolare: sono buchi alla fonte.

## Celle riusabili da `notebooks/genere.ipynb` (pandas puro, copia-incolla)
CI di Wilson/Newcombe sui tassi, LPM per confrontare gap fra territori, cella di verifica
di fattibilità di un incrocio, controllo di composizione per età, "gap in persone"
(il template della proposal già istanziato: evidenza → target → KPI).

## Interfaccia
Python scrive in `data/processed/`, R legge, mai logica in R. Già disponibili dal thread
genere: `genere_istruzione.csv` (titoli per genere, 9-24, quattro territori) e
`genere_quadro_sintesi.csv` — se servono, non ricalcolarli.

# Il paradosso di Bagheria — la Talent Trap ha un genere

> Le ragazze di Bagheria sono le più istruite del panel rispetto ai coetanei, e le meno
> occupate del panel in assoluto. Il capitale umano che il territorio spreca di più è femminile.

## L'idea

`talent_trap.md` chiede se Bagheria riesca a convertire istruzione in lavoro. Questa idea
risponde che **la conversione fallisce in modo asimmetrico fra i generi**, e che questa
asimmetria non è un dettaglio del quadro ma il quadro stesso: se si scompone il divario
occupazionale di Bagheria rispetto ai territori di confronto, la parte femminile ne spiega
la quota maggiore.

Il quadrante di `talent_trap.md` viene disegnato **due volte**, una per genere. L'ipotesi è
che i due punti finiscano in quadranti diversi: i ragazzi verso "fragilità generale", le
ragazze in pieno **Talent Trap** — istruzione alta, occupazione bassissima.

## Perché è rilevante

Il brief chiede esplicitamente, fra i focus possibili, *"impatto delle differenze di genere"*
e *"relazione fra titolo di studio e condizione lavorativa"*. Questa idea li tiene insieme in
una sola domanda invece di trattarli come due capitoli separati, ed è il punto in cui il
thread genere smette di essere un approfondimento laterale e diventa la diagnosi principale.

## Cosa dicono già i dati (verificato, `notebooks/genere.ipynb`)

- **Istruzione**: a Bagheria il vantaggio femminile su "almeno il diploma" (9-24) è di
  **4.2 punti**, il più ampio dei quattro territori (Palermo 1.8, Sicilia 2.7, Italia 2.2).
  Le ragazze non solo studiano più dei coetanei: lo fanno *più che altrove*.
- **Occupazione**: il tasso femminile 15-24 è **8.2%**, il minimo del panel; il maschile 16.5%.
  Il rapporto M/F = **2.0** contro 1.55 nazionale è il peggiore dei quattro territori.
- In **punti percentuali** il gap (8.3) non è un'anomalia: è in linea con Sicilia e Italia,
  addirittura più basso. L'anomalia sta nel **livello femminile** e quindi nel **rapporto**.
  Questa è la distinzione che regge tutta l'idea e va spiegata bene, non nascosta.
- Al 2011 l'occupazione femminile 15+ colloca Bagheria al **12° percentile** dei 390 comuni
  siciliani (`fig04_mappa_sicilia`): non è un fenomeno nuovo del censimento permanente.

Il gap istruzione ha segno **opposto** al gap occupazione. È il fatto più comunicabile
dell'intera analisi ed è già pronto in `genere_quadro_sintesi.csv`.

## Cosa bisogna sviluppare

1. **La forbice**: una sola figura che mostri, sui quattro territori, il vantaggio femminile
   in istruzione e lo svantaggio femminile in occupazione. Bagheria è il territorio dove le
   due barre sono più lunghe e più opposte.
2. **Il quadrante per genere**: posizionare M e F di Bagheria e dei benchmark nel piano
   istruzione × occupazione. Serve a dire *dove* si rompe la catena, separatamente.
3. **Estensione ai 390 comuni (2011)**: con `ottomilacensus_long` si può costruire lo stesso
   piano per tutta la Sicilia usando `I1` (differenziale di istruzione superiore per genere)
   e `L10`/`L11` (occupazione M/F). Bagheria diventa un punto in una nuvola di 390, non un
   caso isolato senza scala. ⚠️ Sono indicatori **15+, non giovanili**: la nuvola serve come
   contesto strutturale, la parte giovanile resta il dato 2018-2024. Le due cose vanno
   etichettate, mai unite in un unico grafico.
4. **Test di robustezza**: parte del gap di istruzione 9-24 è composizione per età (già
   verificato nel notebook, cella "Verifica di composizione per età"). Va ripetuto e
   dichiarato prima di usare il numero come titolo di una figura.

## Fattibilità

🟢 Tutto con i dati già in `data/processed/`. Nessun fetch nuovo, nessuna dipendenza.
🔴 **Vicolo cieco già dimostrato**: l'incrocio titolo di studio × condizione professionale
non esiste a livello comunale. "Fra le diplomate, quante lavorano" **non è una domanda a cui
si può rispondere per Bagheria** — i due gap si misurano separatamente e si confrontano i
segni. Chi scrive la proposal deve saperlo per non promettere quel numero.

## Verso la proposal

- **Evidenza** → il territorio con il maggior vantaggio educativo femminile del panel ha
  anche la peggiore conversione in occupazione: la perdita di capitale umano a Bagheria è
  concentrata sulle ragazze.
- **Intervento** → tutto ciò che riguarda la transizione scuola-lavoro va progettato con una
  quota o un target di genere esplicito, non "neutro" (un intervento neutro su una
  popolazione asimmetrica conserva l'asimmetria).
- **Target** → le ragazze 15-24 fuori dal lavoro e dall'istruzione a Bagheria.
- **KPI** → rapporto M/F sul tasso di occupazione 15-24: da 2.0 verso 1.7 (il livello di
  Palermo). Si misura ogni anno sulla stessa fonte, senza costi di rilevazione.

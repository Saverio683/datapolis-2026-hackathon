# Doppia fuga — i ragazzi partono presto, le ragazze partono dopo

> La fuga dei talenti a Bagheria non ha un solo tempo. Ha due tempi, uno per genere, e
> succedono in due momenti diversi della vita.

## L'idea

Il tema dell'hackathon è la fuga di talenti. Il thread genere ha trovato che il fenomeno,
osservato sulle coorti, **non è un unico flusso**: i ragazzi si assottigliano già nella
transizione 15-19 → 18-22, le ragazze restano e poi si perdono **dopo i 25 anni** — cioè
esattamente quando il loro vantaggio educativo dovrebbe convertirsi in occupazione e non lo fa.

Questa idea prende quella misura e la rende il racconto centrale: **un solo grafico, due
curve, due momenti**. E ne trae la conseguenza di policy più diretta: interventi calibrati su
un'età sola ne mancano metà.

## Perché è rilevante

Risponde alla domanda del brief ("fuga di talenti") con qualcosa di più preciso di
"i giovani se ne vanno": dice **quando** se ne vanno e **chi**. È anche il punto di
giunzione naturale con il thread mobilità: le coorti misurano il saldo netto, i flussi
origine-destinazione dicono dove vanno.

## Cosa dicono già i dati

- Ritenzione di coorte 2021-2024 (`genere_coorti.csv`): coorte maschile 15-19 a **98.5**
  contro 104.8 in Italia; coorte femminile 25-29 a **96.3** contro 103.0. Valori sopra 100
  altrove significa che quelle coorti *crescono* (ingressi, migrazione): a Bagheria calano.
- La popolazione 15-34 passa da **12.174 (2021) a 11.861 (2024)**: −313 persone, −2.6% in
  tre anni. La fuga non è un aneddoto, è nel denominatore.
- Bagheria è al **25° percentile** siciliano per mobilità fuori comune (2011, `M2`): si esce
  poco per lavorare. Chi non pendola e non trova lavoro qui ha una sola opzione, andarsene.

## Cosa bisogna sviluppare

1. **La figura del doppio tempo**: ritenzione per coorte ed età, M e F, con la linea del 100%
   e i benchmark. `fig03_coorti` esiste già come dumbbell — qui si tratta di decidere se sia
   la forma migliore o se serva un profilo per età che renda visibile *quando* si rompe.
2. **Il gruppo invisibile**: incrociando composizione degli stati e ritenzione si isola chi
   **resta ma non è né occupato né studente né in cerca**. È il gruppo che nessuna statistica
   standard nomina e che a Bagheria è largamente femminile (vedi `casalinghe_a_venti_anni.md`).
3. **Aggancio al pendolarismo** (thread Fabio): se la matrice del pendolarismo conserva la
   dimensione sesso, si può distinguere fra *restare senza lavorare* e *restare pendolando*.
   Senza quella dimensione l'analisi regge lo stesso, ma resta senza destinazioni.
4. **Attenzione metodologica**: la ritenzione di coorte confonde migrazione, mortalità e
   variazioni anagrafiche. Ai 15-34 la mortalità è trascurabile, ma la cancellazione/iscrizione
   anagrafica no. Va detto che la misura è un **saldo netto**, non un conteggio di partenze.

## Fattibilità

🟢 Punti 1, 2, 4: dati già in `data/processed/`, calcolo già fatto nel notebook genere.
🟡 Punto 3: dipende da un dato di un altro thread — richiesta già scritta in
`docs/CONTEXT-fabio.md`. Da concordare, non da assumere.

## Viz candidata

Un **flusso** (alluvial/Sankey) della popolazione femminile 15-24 fra stati, affiancato al
profilo di ritenzione per età. Alternativa più sobria e probabilmente più leggibile: due
pannelli patchwork, ritenzione per età a sinistra, composizione degli stati a destra, con la
stessa scala di colore per genere del resto delle figure.

## Verso la proposal

- **Evidenza** → due uscite distinte: maschile precoce (attorno ai 18-19), femminile tardiva
  (dopo i 25), quest'ultima nel momento della mancata conversione istruzione → lavoro.
- **Intervento** → un intervento che agisce sui 18-19enni non tocca le ragazze che se ne
  andranno a 26; servono due leve, o una leva con due finestre di ingaggio.
- **Target** → coorte femminile 22-27 residente a Bagheria (la finestra prima dell'uscita).
- **KPI** → tasso di ritenzione della coorte femminile 25-29 a tre anni: da 96.3 verso 100
  (fermare il calo netto è già un risultato, superarlo è ambizione).

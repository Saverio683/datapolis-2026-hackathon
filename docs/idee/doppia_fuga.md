# Doppia fuga — i ragazzi partono presto, le ragazze partono dopo

> La fuga dei talenti a Bagheria non ha un solo tempo. Ha due tempi, uno per genere, e
> succedono in due momenti diversi della vita.

## L'idea

Il tema dell'hackathon è la fuga di talenti. Il thread genere ha trovato che il fenomeno,
osservato sulle coorti, **non è un unico flusso**: i ragazzi si assottigliano presto e **a
ondate** (età 17-19 e 23-24, con rientri netti dopo i 26), le ragazze restano e si perdono
**dalle età 24-25 in poi, senza rientri** — cioè esattamente quando il loro vantaggio
educativo dovrebbe convertirsi in occupazione e non lo fa. La finestra utile per
intervenire sulle ragazze è **22-25 anni**: prima la curva è sopra la pari, dopo la
perdita è già avvenuta (profilo per età in `fig07_ritenzione_eta`).

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

1. **La figura del doppio tempo** — ✅ fatta due volte: `fig03_coorti` (coorti quinquennali,
   dumbbell) e `fig07_ritenzione_eta` (profilo per età singola, con la finestra 22-25
   evidenziata e i rientri maschili dopo i 26).
2. **Il gruppo invisibile** — ⚠️ **corretto dal notebook** (sezione «La ritenzione per età»):
   chi resta fuori da lavoro, studio e ricerca è di **entrambi i generi** — 573 ragazze e
   549 ragazzi nel 2024, 51% F. Femminile è l'**etichetta** (387 casalinghe contro 50),
   maschile il residuo senza nome ("altra condizione": 485 contro 183). Un intervento "per
   le invisibili" che ignorasse i ragazzi sbaglierebbe platea di metà; uno neutro che
   ignorasse l'etichetta mancherebbe il meccanismo (`casalinghe_a_venti_anni.md`).
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
- **Target** → coorte femminile 22-25 residente a Bagheria (la finestra prima dell'uscita,
  dal profilo per età del notebook).
- **KPI** → tasso di ritenzione della coorte femminile 25-29 a tre anni: da 96.3 verso 100
  (fermare il calo netto è già un risultato, superarlo è ambizione).

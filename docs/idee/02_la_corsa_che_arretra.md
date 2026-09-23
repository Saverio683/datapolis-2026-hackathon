# La corsa che arretra

> Bagheria studia più di prima, ma gli altri territori corrono più velocemente. Si può
> migliorare nei numeri e, nello stesso tempo, perdere terreno.

## L'idea

Tra 1991 e 2011 Bagheria compie un progresso educativo evidente: la quota adulta con almeno
diploma o laurea passa dal **20,2% al 42,5%**; i laureati tra i 30–34 anni dal **6,4% al
14,4%**; l'uscita precoce 15–24 scende dal **40,8% al 28,6%**.

Ma la posizione relativa ai 390 comuni siciliani racconta la storia opposta. Sulla quota
adulta con diploma/laurea Bagheria passa circa dal **64° al 39° pervcentile**; sui laureati
30–34 dal **56° al 32°**. Per l'uscita precoce, dove salire è negativo, passa circa dal
**56° all'83° percentile**. Intanto l'occupazione giovanile resta quasi ferma: **19,6% nel
1991, 20,0% nel 2011**.

Il concept separa due cose che di solito vengono confuse: **progresso assoluto** e
**convergenza territoriale**. Bagheria non è immobile. Sta migliorando, ma non abbastanza
da agganciare la trasformazione educativa e lavorativa della Sicilia.

## Il fatto più sorprendente

Anche il dato NEET storico mostra questo effetto. Il valore di Bagheria scende leggermente,
dal **42,9% del 1991 al 40,1% del 2011**; ma la posizione passa circa dal **17° all'88°
percentile** dei comuni siciliani. Non significa che i singoli giovani stiano peggio di
vent'anni prima. Significa che **molti altri comuni hanno ridotto il problema molto più in
fretta**.

| Indicatore | 1991 | 2011 | Traiettoria di Bagheria |
|---|---:|---:|---|
| Adulti con diploma/laurea (`I6`) | 20,2% | 42,5% | forte crescita, perdita di posizione relativa |
| Laureati 30–34 (`I7`) | 6,4% | 14,4% | più che raddoppia, ma scende nel confronto siciliano |
| Uscita precoce 15–24 (`I5`) | 40,8% | 28,6% | diminuisce, ma più lentamente del contesto |
| Occupazione giovanile (`L14`) | 19,6% | 20,0% | sostanzialmente ferma |
| NEET 15–29 (`L4`) | 42,9% | 40,1% | lieve calo, forte arretramento relativo |

Questa è una storia molto più utile di “Bagheria ha valori bassi”: permette di chiedere
**quando** il territorio ha perso passo e **su quale anello** della catena titolo–lavoro.

## La domanda di ricerca

**Bagheria perde terreno perché forma troppo lentamente, perché il lavoro giovanile non
assorbe il miglioramento dei titoli o perché i due processi si bloccano in periodi diversi?**

L'analisi ha tre pannelli, senza costruire una falsa serie unica:

1. 1991–2001–2011: traiettoria storica degli indicatori 8milaCensus;
2. 2018–2024: andamento recente di istruzione e condizione dei 15–24enni, con il 2020
   lasciato mancante;
3. benchmark: variazione di Bagheria rispetto alla mediana siciliana e a comuni simili.

Per ogni indicatore si mostrano insieme il valore e il percentile. Se il valore migliora ma
il percentile peggiora, il messaggio è immediato: la città avanza, ma troppo lentamente.

## La visualizzazione

### 1. Il doppio tachimetro

Per ogni anno, due lancette:

- **quanto è migliorata Bagheria** rispetto a sé stessa;
- **quanto si è spostata** rispetto agli altri comuni siciliani.

L'uso simultaneo evita sia il racconto catastrofista (“non cambia nulla”) sia quello
autoassolutorio (“il dato è migliorato, quindi la politica funziona”).

### 2. La gara a corsie

Quattro linee indicizzate a 100 nel 1991 — diploma/laurea, laurea 30–34, occupazione
giovanile e uscita precoce invertita — mostrano quali dimensioni accelerano e quale resta
ferma. Una seconda vista presenta il percentile siciliano.

### 3. Il momento della separazione

Una vista selezionabile confronta Bagheria con un piccolo insieme di comuni che nel 1991
avevano condizioni simili. Non serve a proclamare vincitori: serve a individuare il decennio
in cui le traiettorie divergono e poi studiare le scelte o le strutture associate.

## La policy dipende dalla diagnosi

- Se Bagheria perde passo soprattutto sull'**istruzione**, occorre accelerare completamento
  e titoli professionalizzanti, fissando un obiettivo di convergenza e non solo di crescita.
- Se i titoli crescono ma il lavoro giovanile resta fermo, il collo di bottiglia è la
  **conversione**: prima esperienza retribuita, apprendistato, accesso a datori locali e
  metropolitani.
- Se l'arretramento avviene in un decennio preciso, la proposta deve cercare lo shock
  territoriale corrispondente — trasformazione produttiva, accessibilità, crisi settoriale —
  prima di scegliere lo strumento.
- Se i dati recenti mostrano un recupero, la policy non riparte da zero: identifica cosa
  sta funzionando e concentra risorse sui gruppi ancora esclusi.

## Verso la proposta

### Nome operativo: **Patto +10**

Un patto comunale con un obiettivo misurabile: recuperare dieci posizioni percentili, in un
periodo dichiarato, su un indicatore di completamento educativo e uno di transizione al
lavoro. Non è una graduatoria reputazionale: il percentile serve a impedire che un piccolo
miglioramento venga scambiato per convergenza.

Il patto pubblica ogni anno un cruscotto breve, associa a ogni indicatore un responsabile e
attiva una misura solo se coerente con il collo di bottiglia osservato.

**Target:** coorti 15–24 residenti a Bagheria, con approfondimento per titolo e genere nel
pilota.

**KPI:** variazione assoluta, variazione del percentile siciliano, quota fuori da lavoro e
studio, quota occupata, tempo al primo ingresso, esiti a 6 e 12 mesi per titolo.

## Fattibilità e limiti

🟢 La base 1991–2011 è già completa e normalizzata per 390 comuni siciliani.

🟢 La lettura valore + percentile è semplice da prototipare e molto forte in presentazione.

🟡 Le definizioni dei singoli indicatori vanno controllate anno per anno nel codebook.

🔴 Il salto 2011–2018 attraversa un cambio di fonte. Le due finestre temporali vanno
mostrate in pannelli separati, senza collegarle con una linea continua.

## Fonti

- Istat, [8milaCensus — Bagheria](https://ottomilacensus.istat.it/comune/082/082006/)
- Istat, [Data Browser](https://esploradati.istat.it/)
- File elaborati nella repository: `ottomilacensus_long.csv`,
  `censpop_istr_lav_long.csv`


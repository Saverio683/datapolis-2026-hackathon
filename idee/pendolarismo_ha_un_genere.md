---
related:
  - "[[gender_talent_trap]]"
  - "[[doppia_fuga]]"
  - "[[geografia_delle_opportunita]]"
  - "[[00_the_talent_trap]]"
tags:
  - genere
  - mobilita
  - pendolarismo
  - hackathon
last modified: 2026-08-28
AI: true
type: Note
---

# Il pendolarismo ha un genere - le ragazze si muovono per studiare, non per lavorare

> A Bagheria le ragazze che già lavorano escono dal comune molto meno dei coetanei,
> ma per studiare escono **più** di loro. Il vincolo non è la mobilità in sé: è la
> mobilità *per lavoro*.

## Il risultato (nuovo, 2026-08-28)

Fonte: `data/processed/edu_census_commuting_long.csv` (censimento permanente 2018-2019,
tavola pendolarismo con dimensione `genere` × `motivo` (STD/WK) × `destinazione`
(SMPUR = stesso comune / OMPUR = fuori comune)). La tavola era già stata scaricata dal
thread educazione ma usata **solo come appendice di contesto** (`edu_commuting_appendix.csv`,
solo totali T). La scomposizione per genere non era mai stata calcolata.

Quota di chi si sposta fuori comune, sul totale di chi si sposta giornalmente per
quel motivo:

| Territorio | anno | LAVORO M | LAVORO F | gap M−F | STUDIO M | STUDIO F | gap F−M |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Bagheria** | 2019 | **41,2%** | **33,0%** | **8,2** | 13,6% | **16,3%** | **+2,7** |
| Bagheria | 2018 | 40,6% | 32,3% | 8,3 | 14,0% | 17,0% | +3,0 |
| Palermo | 2019 | 5,5% | 4,0% | 1,5 | 0,6% | 0,7% | +0,1 |
| Sicilia | 2019 | 32,5% | 28,4% | 4,1 | 19,7% | 21,5% | +1,8 |
| Italia | 2019 | 50,7% | 46,0% | 4,7 | 28,6% | 30,0% | +1,4 |

Due fatti, entrambi stabili sui due anni disponibili:

1. **Sul lavoro il gap di genere di Bagheria è circa il doppio** di quello siciliano
   (8,2 contro 4,1) e nazionale (contro 4,7).
2. **Sullo studio il segno si inverte** e Bagheria ha lo scarto pro-femminile **più
   ampio del panel** (+2,7 contro +1,8 Sicilia e +1,4 Italia).

Il denominatore è già condizionato all'occupazione (chi si sposta *per lavoro* un
lavoro ce l'ha): il gap non è un riflesso meccanico del divario occupazionale
di [[gender_talent_trap]], è una misura indipendente sullo stesso punto di rottura.

## Perché conta

È il terzo focus del brief («dinamiche e ruolo del pendolarismo») e il pezzo che
[[CONTEXT-fabio]] chiedeva esplicitamente al thread mobilità («se la matrice ha la
dimensione sesso, tienila»). Era già nei dati.

Regge lo stesso racconto degli altri due thread da una fonte diversa: il territorio
accompagna le ragazze fino allo studio - anche fuori comune, anche più dei coetanei -
e le perde nel passaggio al lavoro. Stessa rottura di [[doppia_fuga]] e della forbice
di fig05, misurata su una variabile che non condivide né denominatore né tavola.

Contesto 2011 (8milaCensus, 390 comuni): `M2` mobilità fuori comune 14,3 → **25°
percentile**; `M4` mobilità studentesca 19,6 contro mediana 54,0 → **18° percentile**;
`M6` mezzo pubblico 8,4 → 36°. Serie M2: 28° (1991) → 31° (2001) → 25° (2011).

## Vincoli da dichiarare (non aggirabili)

1. **La destinazione non è Palermo.** `OMPUR` è «fuori comune», aggregato. La tavola
   2018-2019 non identifica il comune di destinazione: *non si può scrivere «pendolano
   verso Palermo»*, solo «escono dal comune». La nota è già in `edu_commuting_appendix.csv`.
2. Solo **2018 e 2019**. Nessuna serie recente, nessun aggancio al 2021-2024 degli
   altri thread.
3. `M4` è un rapporto fuori/dentro comune: un comune con scuole proprie ha `M4` basso
   per costruzione. Bagheria ha 3 sedi tecniche (anagrafe MIUR, cella del notebook
   genere). Il 18° percentile **non** è di per sé un dato negativo.
4. Correlazione ecologica nota da [[CONTEXT-fabio]]: sui 390 comuni `M2` × `L11`
   (occupazione femminile) dà Spearman +0,32, orienta l'ipotesi, non la dimostra.

## Verso la proposal

- **Evidenza** → fra chi già lavora, le donne di Bagheria escono dal comune 8,2 punti
  meno degli uomini, il doppio dello scarto regionale; sullo studio escono di più.
- **Intervento** → la componente di mobilità di [[Ponte 19]] non è un contorno: è una
  leva sullo stesso KPI occupazionale. Abbonamento/servizio calibrato sulla finestra
  22-25 e sul motivo *lavoro*, non sul motivo studio, che già funziona.
- **Target** → ragazze 22-25 di Bagheria che accettano un'occupazione fuori comune.
- **KPI** → quota F fuori comune per lavoro: da 33,0% verso il 41,2% dei coetanei
  (⚠️ la fonte è 2018-2019: senza una rilevazione nuova questo KPI **non è
  aggiornabile**, o si trova la serie recente, o lo si misura sul dato di servizio).

## Cosa serve per portarlo in relazione

Una cella nel notebook (pandas puro, ~15 righe: pivot su motivo × destinazione, quota
OMPUR/ALL per genere e territorio, i due anni) e la riga in `docs/sources.md`. La
tavola è già in `data/processed/`, nessun fetch nuovo.

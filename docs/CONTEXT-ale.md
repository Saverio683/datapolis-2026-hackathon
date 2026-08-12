# CONTEXT — Ale (focus genere)

Stato del thread genere al 2026-08-12. Le regole condivise stanno in `CLAUDE.md`; qui solo
ciò che riguarda questo thread. Ogni numero citato si rigenera da una cella di
`notebooks/genere.ipynb` — mai copiarlo a mano nella proposal.

## Stato
`notebooks/genere.ipynb` gira top-to-bottom (sensore nbconvert ok) e contiene, in ordine:
verifica di fattibilità degli incroci, serie e gap occupazionale 15-24 con CI
(Wilson/Newcombe), doppia scala (punti e rapporto M/F), LPM (GLM binomiale link identità)
sull'eccesso di gap vs benchmark, trend OLS 2018-2024, decomposizione della popolazione
per stato, scissione delle casalinghe, gap istruzione 9-24, verifica di composizione per
età, quadro di sintesi, gap in persone, ritenzione di coorte per genere 2021-2024,
contesto storico 2011, sintesi finale.
Ogni sezione si apre con una riga `📌 Risultato chiave`; la sezione «Sintesi finale» le
ricompone e le traduce nel template della proposal (evidenza → target → KPI).

## Risultati chiave
- Gap occupazionale 2024: 8.3 punti [CI 6.6-10.0]. In punti **non è un'anomalia locale**
  (pooled 2022-24: +1.1 vs Palermo p=0.03, -1.8/-1.9 vs Sicilia/Italia p<0.001); in
  **rapporto** Bagheria è la peggiore del panel (M/F = 2.0 contro 1.55 nazionale).
  Il tratto locale è il livello: tasso femminile 8.2%, il minimo dei quattro territori.
- Il 13.4% delle ragazze 15-24 si dichiara **casalinga** (387 persone) contro il 4.6%
  nazionale; l'inattività maschile è invece "altra condizione". Serie 2018-2024 stabile.
- Ritenzione di coorte 2021-2024: i ragazzi si perdono presto (15-19: 98.5 vs 104.8
  Italia), le ragazze **dopo i 25** (coorte 25-29: 96.3 vs 103.0) — proprio quando il
  vantaggio educativo dovrebbe convertirsi in lavoro.
- Gap in persone: **+40 occupate** allineandosi al tasso femminile di Palermo (KPI
  realistico), +239/+262 per parità coi coetanei o media nazionale (misura del problema).
- Il tasso di disoccupazione femminile poggia su 430-680 persone: declassato a misura
  non conclusiva, si usano occupazione e composizione.

## Export per R (`data/processed/`)
`genere_gap_occupazione.csv`, `genere_gap_occupazione_ci.csv` (bande di confidenza),
`genere_istruzione.csv`, `genere_quadro_sintesi.csv`, `genere_composizione_stato.csv`
(barre composte), `genere_casalinghe.csv`, `genere_coorti.csv`, `genere_gap_persone.csv`.

## Figure (R)
`Rscript viz/build_all.R` rigenera tutto in `figures/` (PNG 300dpi + SVG). Tema e palette
condivisi in `viz/theme.R`: Bagheria in vermiglio contro territori di contesto, genere in
arancio/verde (mai rosa-azzurro), Okabe-Ito ovunque.
- `fig01_gap_due_scale` — gap 15-24 nelle due scale (punti con bande IC 95% | rapporto M/F),
  composizione patchwork. Il 2020 è un buco alla fonte: linea interrotta, non interpolata.
- `fig02_composizione_stato` — popolazione 15-24 per sei stati, femmine e maschi a confronto:
  la figura del meccanismo (casalinghe 13,4% contro 1,7%).
- `fig03_coorti` — dumbbell F/M della ritenzione di coorte, riferimento al 100%.

## Aperture
- `pipeline/stats.py` condiviso (Wilson/Newcombe/LPM): decisione di team, per ora le
  funzioni vivono nelle celle del notebook e si copiano da lì.
- Fetch possibili ma non pianificati: stato civile e cittadinanza × condizione via SDMX
  (nel fetch attuale esistono solo come totali `ALL`/`TOTAL`).
- Richieste agli altri thread: in `CONTEXT-fabio.md` (dimensione sesso nel pendolarismo)
  e `CONTEXT-saverio.md` (incrocio titolo × condizione per genere a livello regionale).

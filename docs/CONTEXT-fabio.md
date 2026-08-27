# CONTEXT — Fabio (focus mobilità)

Contesto per il thread pendolarismo/mobilità. Le regole condivise stanno in `CLAUDE.md`;
qui i fatti già verificati e gli agganci con gli altri thread.

## Verificato sui dati (2026-08-12)
- 8milaCensus ha 9 indicatori di mobilità **`M1`-`M9`** (giornaliera, fuori comune,
  occupazionale, studentesca, mezzo pubblico/privato, distanza) per tutti i **390 comuni
  siciliani**, su tre censimenti **1991/2001/2011**. Non sono scomponibili per genere.
- Posizionamento di Bagheria al 2011: `M2` (mobilità fuori comune) al **25° percentile**
  regionale — ci si muove poco. Sui 390 comuni la mobilità fuori comune correla con
  l'occupazione femminile `L11` (Spearman +0.32): dove ci si muove di più, le donne
  lavorano di più. È una correlazione ecologica: orienta l'ipotesi, non la dimostra.
- Fonti (dettagli in `docs/sources.md`, da leggere prima di ogni fetch):
  `dati.regione.sicilia.it` è CKAN (API `package_search`/`datastore_search`);
  `opendata.comune.palermo.it` NON è CKAN → catalogo DCAT in Turtle su `/dcat/dcat.php`.
  Ogni download va in `data/raw/` (append-only) con una riga in `sources.md`.

## Richiesta dal thread genere
Se la matrice del pendolarismo che userai (ISTAT 2011 o altra fonte) ha la **dimensione
sesso, tienila** anche se a te non serve: una sola tabella origine-destinazione per
genere (chi pendola verso Palermo, ragazzi o ragazze?) cambia la portata del focus gender
e trasforma lo scenario di policy qui sotto in un intervento concreto.

## Cartografia già pronta (per le tue mappe)
`pipeline/fetch` scarica i confini ISTAT e `pipeline/build` li trasforma in
`comuni_sicilia_poligoni.csv` (vertici già proiettati, EPSG:32633) e
`comuni_sicilia_centroidi.csv` (punto-etichetta per comune). **Non serve `sf`**, che su queste
macchine non si installa: in R si disegna con `geom_polygon(group = interaction(territorio,
parte), subgroup = anello, rule = "evenodd")`. `viz/fig04_mappa_sicilia.R` è l'esempio completo,
copiabile cambiando solo la variabile colorata. Dettagli e trappole in `docs/sources.md` §5.

## Cosa offre il thread genere (`data/processed/`)
- `genere_composizione_stato.csv` — chi è disponibile a muoversi: popolazione 15-24 per
  stato (occupati / in cerca / studenti / altri inattivi) e genere, quattro territori.
- `genere_gap_persone.csv` — lo scenario "+40 occupate se Bagheria raggiungesse il tasso
  femminile di Palermo": l'aggancio naturale fra accesso alla mobilità e occupazione
  femminile per la proposal.
- `genere_coorti.csv` — ritenzione di coorte 2021-2024 per genere (le ragazze si perdono
  dopo i 25 anni, i ragazzi prima). La misura è netta e senza destinazioni: i flussi
  origine-destinazione sono il pezzo che manca, ed è roba tua.
- `genere_platea.csv` (nuovo, 2026-08-26) — la platea 15-24 del 2024 e quella già nata
  del 2029/2034, per genere e territorio: il denominatore futuro di qualunque scenario.
- `genere_stranieri.csv` (nuovo, 2026-08-26) — il 15-34 per cittadinanza e genere,
  2021-2024: a Bagheria il ricambio migratorio è l'1.6% (195 persone), quindi i flussi
  rilevanti sono quasi solo in uscita. (L'occupazione degli stranieri a livello comunale
  resta non misurabile: nelle tavole lavoro la cittadinanza è solo TOTAL.)

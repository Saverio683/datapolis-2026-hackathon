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

## Cosa offre il thread genere (`data/processed/`)
- `genere_composizione_stato.csv` — chi è disponibile a muoversi: popolazione 15-24 per
  stato (occupati / in cerca / studenti / altri inattivi) e genere, quattro territori.
- `genere_gap_persone.csv` — lo scenario "+40 occupate se Bagheria raggiungesse il tasso
  femminile di Palermo": l'aggancio naturale fra accesso alla mobilità e occupazione
  femminile per la proposal.
- `genere_coorti.csv` — ritenzione di coorte 2021-2024 per genere (le ragazze si perdono
  dopo i 25 anni, i ragazzi prima). La misura è netta e senza destinazioni: i flussi
  origine-destinazione sono il pezzo che manca, ed è roba tua.

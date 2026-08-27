# Disponibilità e ruolo delle fonti

Data dell'acquisizione inclusa: 25 agosto 2026.

## Fonti core acquisite

- **Istat 8milaCensus:** indicatori comunali 1991, 2001 e 2011, benchmark e codebook.
- **IstatData — condizione professionale:** 2018-2019 e 2021-2024; il 2020 non è presente.
- **IstatData — titolo di studio:** 2018-2024.
- **IstatData — popolazione per età:** 2021-2024 nel perimetro 15-34 usato.

## Fonti di contesto acquisite

- **IstatData — pendolarismo:** 2018-2019; usato solo in appendice perché non identifica
  Palermo come destinazione.
- **Ministero dell'Istruzione:** anagrafe 2025/26 delle sedi tecniche; usata per i canali
  operativi della policy, non per stimare esiti.
- **Comune di Palermo / AMAT:** GTFS corrente al run; usato solo come inventario della rete
  urbana palermitana, che non descrive il collegamento Bagheria-Palermo.

## Fonte non disponibile ed esclusa

Gli endpoint Open Data Regione Siciliana relativi a offerte di lavoro e operatori accreditati
hanno restituito ripetutamente HTTP 502. Erano fonti opzionali e sono esclusi da valori,
grafici, conclusioni e target quantitativi. Il fallimento resta registrato nel manifest.

## Tracciabilità

Il dettaglio macchina-legibile è in `data/raw/manifest.csv` e
`data/raw/download_status.json`. `outputs/tables/source_inventory.csv` offre una vista
editoriale con periodo, grana, ruolo e limite di ogni dataset. Gli SHA-256 dei raw acquisiti
sono ricalcolati da `src/datapolis_bagheria/validation.py`.

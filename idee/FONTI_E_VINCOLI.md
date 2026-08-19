# Fonti e vincoli di lettura

## Fonti usate

### Istat — 8milaCensus

- Profilo ufficiale di Bagheria: <https://ottomilacensus.istat.it/comune/082/082006/>
- Dataset storico già normalizzato nella repository: `data/processed/ottomilacensus_long.csv`
- Indicatori principali: istruzione (`I5`, `I6`, `I7`, `I8`), lavoro (`L4`, `L9`, `L13`,
  `L14`, `L19`, `L21`), mobilità (`M1`–`M6`) e vulnerabilità (`V8`).

Le posizioni percentili citate sono state ricalcolate sui **390 comuni siciliani** presenti
nel dataset 2011. Un percentile alto su un indicatore negativo, come uscita precoce o NEET,
indica una situazione peggiore rispetto a molti comuni.

### Istat — Censimento permanente 2018–2024

- Data Browser: <https://esploradati.istat.it/>
- Dati comunali già elaborati nella repository:
  `data/processed/censpop_istr_lav_long.csv`,
  `data/processed/analisi_condizione_15_24.csv` e
  `data/processed/genere_istruzione.csv`.

Questa fonte permette di descrivere separatamente titolo di studio e condizione prevalente
dei 15–24enni. Il 2020 manca nella tavola sul lavoro giovanile e non va interpolato.

### Istat — ritorni occupazionali dell'istruzione

- Comunicato e tavole 2024:
  <https://www.istat.it/comunicato-stampa/livelli-di-istruzione-e-ritorni-occupazionali-anno-2024/>

La fonte chiarisce a livello nazionale e regionale il legame tra titolo e lavoro, ma non
sostituisce un incrocio comunale per Bagheria.

### Open Data Sicilia

- Operatori accreditati ai servizi per il lavoro:
  <https://dati.regione.sicilia.it/dataset/operatori-accreditati-ai-servizi-al-lavoro>
- Offerte di lavoro pubblicate nel portale:
  <https://dati.regione.sicilia.it/dataset/offerte-lavoro/resource/bbe65028-4a65-49d8-b576-c74db2dbbbb0>
- Istituti Tecnici Superiori:
  <https://dati.regione.sicilia.it/catalogo/67f2c5e4-75d3-4fd1-aec0-c87796fcaa49/>

Queste basi servono soprattutto per mappare **offerta osservata e infrastruttura di
politica attiva**. Non sono una misura completa della domanda di lavoro: coprono solo il
canale pubblico osservato e vanno controllate data di aggiornamento, schema e duplicati.

### Comune di Palermo

- GTFS AMAT: <https://opendata.comune.palermo.it/opendata-dataset.php?dataset=1779>
- Catalogo DCAT: <https://opendata.comune.palermo.it/dcat/dcat.php>

Il GTFS pubblicato a febbraio 2026 contiene fermate, linee e orari di bus e tram nel
territorio di Palermo. È utile per l'ultimo tratto del viaggio, ma **non descrive da solo il
collegamento interurbano Bagheria–Palermo**: per quello occorre integrare orari ferroviari
e/o altri servizi extraurbani.

## Vincoli che non vanno nascosti

1. **Non esiste nei file comunali disponibili una tabella titolo × condizione lavorativa.**
   Non si può scrivere “il X% dei laureati di Bagheria lavora” senza acquisire un'altra
   fonte o raccogliere dati primari.
2. L'indicatore storico `L4` misura i NEET **15–29 anni**; la misura 2018–2024 riguarda i
   **15–24 anni fuori sia dal lavoro sia dallo studio**. Vanno affiancati, non uniti in una
   linea continua.
3. `I8` indica la quota di 15–19enni con almeno la licenza media: non misura la permanenza
   a scuola né il conseguimento del diploma.
4. `L19` descrive le professioni degli **occupati residenti**, non i posti di lavoro
   localizzati nelle imprese di Bagheria e non soltanto i giovani.
5. Correlazioni e confronti comunali sono **ecologici**: servono a formulare un meccanismo,
   non dimostrano che il titolo di un singolo causi la sua condizione lavorativa.
6. I valori 8milaCensus sono storici (ultimo censimento decennale 2011). I dati permanenti
   2018–2024 servono a controllare se la criticità è ancora presente, mantenendo separate
   definizioni e serie.

## Regola per il pilota

Ogni intervento dovrebbe raccogliere almeno: età, sesso, titolo e indirizzo di studio,
anno di uscita, condizione iniziale, durata dell'inattività, disponibilità alla mobilità,
accesso a un mezzo, candidatura, colloquio, ingresso in lavoro/formazione, coerenza percepita
e condizione a 3, 6 e 12 mesi. È il minimo necessario per trasformare l'ipotesi territoriale
in evidenza sul rapporto tra titolo e lavoro a Bagheria.


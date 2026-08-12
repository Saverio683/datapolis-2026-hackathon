# Fonti dati

Registro append-only. Questo documento descrive **gli endpoint**: come sono fatti, cosa contengono,
dove sono le trappole.

Il registro dei **singoli download** è `data/raw/manifest.csv`, scritto in automatico da
`pipeline/fetch.py` a ogni scarico: data UTC, nome file, URL esatto, byte, sha256.
È lì e non qui perché una riga per download scritta a mano si dimentica, e lo sha256 serve a
distinguere "stesso file" da "stesso nome".

---

## 1. ISTAT — 8milaCensus (ottomilacensus.istat.it)

**Ricognizione: 2026-08-12** (ispezione rete su https://ottomilacensus.istat.it/comune/082/082006/)

### Esito: nessuna API JSON, ma non serve scraping

Le pagine comunali sono TYPO3 server-rendered: durante il caricamento **zero richieste XHR/fetch**,
zero endpoint JSON. Gli accordion per tema sono collapse Bootstrap su HTML già presente.

**Però** ogni pagina espone link diretti a CSV/XLSX già puliti, e il portale ha una sezione Download
con file aggregati. Si scarica con `requests`, si legge con `pandas`. **Niente scraping HTML, niente Selenium.**

### ⚠️ Vincolo che cambia il piano: i dati sono al 2011, non 2021

8milaCensus copre i **Censimenti della popolazione 1951–2011**. La pagina di Bagheria è etichettata
"DATI 2011". **Non contiene il Censimento permanente 2021.**
Conseguenza: 8milaCensus serve come fonte per la **serie storica 1991/2001/2011**; per l'anno base
2021 fissato in CLAUDE.md serve un'altra fonte (`esploradati.censimentopopolazione.istat.it`, SDMX)
— da istruire separatamente.

### Endpoint utili

#### A. Serie ai confini 2011, tutti i comuni di una regione — **fonte primaria consigliata**
```
https://ottomilacensus.istat.it/fileadmin/download/{cod_regione}/confini/confini_{cod_regione}.csv
```
Sicilia = `19` → https://ottomilacensus.istat.it/fileadmin/download/19/confini/confini_19.csv
(verificato 2026-08-12: 200, `text/csv`, 1170 righe dati = 390 comuni × 3 anni)

Un solo file copre Bagheria **e** Comune di Palermo. Variante `.xlsx` allo stesso path.

#### B. Province, Regioni, Italia — benchmark territoriali
```
https://ottomilacensus.istat.it/fileadmin/download/Province_Regioni_Italia_confini_2011.csv
```
Contiene Provincia di Palermo, Regione Sicilia, Italia. Stesse 99 colonne indicatore del file A.

#### C. Codebook dei 99 indicatori — **scaricare per primo**
```
https://ottomilacensus.istat.it/fileadmin/download/Descrizione_degli_indicatori_serie_confini_2011.csv
```
99 righe: `Descrizione tema;Codice Indicatore;Nome indicatore;Descrizione`.
Le definizioni operative (fasce d'età, denominatori) stanno qui — è la mappa codice→significato.

#### D. Legenda simboli
```
https://ottomilacensus.istat.it/fileadmin/download/Legenda_codici_e_simboli_indicatori_ai_confini_2011.csv
```

#### E. Serie storica 1951–2011 ai confini dell'epoca (solo per trend lunghi)
```
https://ottomilacensus.istat.it/fileadmin/download/19/confini-epoca/confini-epoca_19.csv
```
Sottoinsieme di indicatori, molte celle mancanti nei censimenti vecchi (simbolo di dato non disponibile).
Colonna extra `Flag comuni con variazioni`. Da usare solo se serve andare oltre il 1991.

#### F. Singolo comune, formato long (comodo ma parziale)
```
https://ottomilacensus.istat.it/fileadmin/dati/csv/{prov}/dati_{prov}_{com3}_{NNN}.csv
```
Bagheria: `prov=082`, `com3=006`, `NNN` = `001`…`015` (016 → 404). Variante `/xlsx/` + `.xlsx`.
Formato: `Descrizione tema;Descrizione sottotema;Nome indicatore;Denominazione11;AnnoCP;Value`.
Territori inclusi: **Bagheria (1991, 2001, 2011) + Sicilia 2011 + Italia 2011** — manca il Comune di Palermo.

Mappa NNN → sottotema (somma indicatori = 99):

| NNN | Tema | Sottotema | n. ind. |
|-----|------|-----------|---------|
| 001 | Popolazione | Dinamica demografica e territorio | 7 |
| 002 | Popolazione | Struttura della popolazione | 7 |
| 003 | Integrazione degli stranieri | Indici di presenza ed integrazione | 10 |
| 004 | Famiglie | Struttura familiare | 3 |
| 005 | Famiglie | Struttura delle famiglie giovani | 4 |
| 006 | Famiglie | Struttura delle famiglie anziane | 4 |
| 007 | Condizioni abitative | Patrimonio abitativo | 11 |
| 008 | Condizioni abitative | Condizioni abitative | 4 |
| 009 | Istruzione | Livello generale di istruzione | 5 |
| 010 | Istruzione | Istruzione per classi di età | 4 |
| 011 | Mercato del lavoro | Attività della popolazione | 5 |
| 012 | Mercato del lavoro | Disoccupazione | 4 |
| 013 | Mercato del lavoro | Occupazione | 13 |
| 014 | Mobilità | Spostamenti quotidiani | 9 |
| 015 | Vulnerabilità materiale e sociale | Potenziali difficoltà materiali e sociali | 9 |

#### G. Report PDF di sintesi per comune
```
https://ottomilacensus.istat.it/fileadmin/report/{prov}/report_{prov}{com3}.pdf
```
Bagheria: https://ottomilacensus.istat.it/fileadmin/report/082/report_082006.pdf
Solo per lettura umana — non è una fonte dati.

### Struttura dei file A/B (formato wide)

Header: `AnnoCP;Livello territoriale;Codice Regione 2011;Codice Provincia 2011;Codice comune 2011;Denominazione del territorio;` + 99 codici indicatore.

Codici indicatore per tema: `P1–P14` popolazione, `S1–S10` stranieri, `F1–F11` famiglie,
`A1–A15` abitazioni, `I1–I9` istruzione, `L1–L22` lavoro, `M1–M9` mobilità, `V1–V9` vulnerabilità.

`Livello territoriale`: `1` comune, `2` provincia, `3` regione, `4` Italia.

**Trappole di parsing** (tutte verificate sui file reali):
- Encoding **windows-1252**, non UTF-8 → `encoding="cp1252"`, altrimenti "età" diventa "et�".
- Separatore campo `;`, **decimale `,`**, **separatore migliaia `.`** (`5.002.904`) → `decimal=","`, `thousands="."`.
- Codici comune **senza zero iniziale**: Bagheria = `82006`, Comune di Palermo = `82053`, provincia = `82`.
  Il codice ISTAT canonico a 6 cifre (`082006`) va ricostruito con zero-padding in pipeline.
- I file A/B hanno **righe vuote in coda** (artefatto export Excel: `;;;;…`). Filtrare su `AnnoCP` non nullo:
  in `confini_19.csv` → 3646 linee totali, 1170 righe dati.
- Nel file E il dato mancante è un simbolo, non una stringa vuota → vedi legenda (D).

### Codici territoriali verificati (2026-08-12)

| Territorio | Livello | Cod. nel file | Cod. ISTAT 6 cifre |
|---|---|---|---|
| Bagheria | 1 | `82006` | `082006` ✔ |
| Comune di Palermo | 1 | `82053` | `082053` ✔ (confermato: pop. 2011 = 657.561) |
| Provincia di Palermo | 2 | reg `19`, prov `82` | — |
| Sicilia | 3 | reg `19` | — |
| Italia | 4 | — | — |

Nota: nel file B la riga `Livello 2 / Palermo` è la **provincia**, non il comune. Il Comune di Palermo
sta solo nel file A a livello 1.

### Indicatori rilevanti per il target 15-34

Presenti (⚠️ tutti al **2011**):

| Cod. | Indicatore | Fascia d'età |
|---|---|---|
| `L4` | Giovani che non studiano e non lavorano (NEET) | **15-29** |
| `V8` | Giovani fuori dal mercato del lavoro e dalla formazione | 15-29 |
| `L14` | Tasso di occupazione giovanile | 15-29 |
| `L9` | Tasso di disoccupazione giovanile | 15-24 |
| `L5` | Rapporto giovani attivi/non attivi | 15-24 |
| `L13` | Indice di ricambio occupazionale (>45 su 15-29) | 15-29 |
| `I7` | Giovani con istruzione universitaria | **30-34** |
| `I5` | Uscita precoce da istruzione e formazione | 15-24 |
| `I8` | Livello di istruzione dei giovani | 15-19 |
| `F4` | Giovani che vivono da soli | **15-34** (denominatore) |
| `F5`–`F7` | Famiglie monogenitoriali / coppie giovani con e senza figli | <35 |

Indicatori di genere (`I1` differenziale istruzione superiore, `L1`/`L2` partecipazione,
`L6`/`L7` disoccupazione, `L10`/`L11` occupazione): **calcolati su 15 anni e più, non incrociati con l'età.**

→ Per il thread **Genere** questo significa: 8milaCensus dà il gap di genere *complessivo* e il dato
giovanile *senza genere*, ma **non il gap di genere dentro i 15-34**. Quell'incrocio va cercato altrove
(esploradati 2021 / dati.istat.it), oppure il thread lavora sul gap complessivo dichiarando il limite.
Nessuna fascia 15-34 diretta su lavoro/istruzione: solo 15-29, 15-24, 30-34 → l'aggregazione al target
15-34 non è ricostruibile da qui e va documentata come scelta nel notebook.

### Valori spot di controllo (Bagheria 2011, da `confini_19.csv`)

Da usare come assert di regressione nella pipeline, non come numeri da citare:
`L4 = 40,1` · `V8 = 23,4` · `L14 = 20,0` · `I7 = 14,4` · popolazione residente `54.257`.

### Note operative
- `HEAD` risponde **403** su `/fileadmin/`; usare sempre `GET`. Non è un blocco: il `GET` va a 200.
- Nessuna autenticazione, nessun rate limit incontrato.
- I file sono statici: scaricare una volta in `data/raw/` con la data nel nome.

---

## 2. ISTAT — Censimento permanente popolazione e abitazioni (IstatData, SDMX)

**Ricognizione: 2026-08-12**

### Il vecchio host è morto — usare IstatData

`esploradati.censimentopopolazione.istat.it` **non è più raggiungibile**: il certificato servito è
`CN=*.istat.it` con SAN `*.istat.it, istat.it`, e il wildcard copre un solo livello → non matcha un
sottodominio a tre etichette. Chrome dà "Privacy error", `curl` dà errore 60. Non è un problema nostro
e non va aggirato disabilitando la verifica TLS.

Il portale è stato **migrato**: `01a-filtro.istat.it` risponde `301` verso
`https://esploradati.istat.it/databrowser/#/it/censpop`.

→ Host corretto: **`esploradati.istat.it`**. Il censimento permanente è un nodo tematico (`censpop`)
dentro IstatData, stessa API SDMX del resto di ISTAT.

### API SDMX REST — funziona, nessuna autenticazione

Base: `https://esploradati.istat.it/SDMXWS/rest/`

| Risorsa | Path | Header `Accept` |
|---|---|---|
| Elenco dataflow | `dataflow/IT1` | `application/vnd.sdmx.structure+json;version=1.0` |
| DSD + codelist di un dataflow | `dataflow/IT1/{DF}/1.0?references=all&detail=full` | idem |
| Codelist singola | `codelist/IT1/{CL}/1.0` | idem |
| Mappa dataflow→categoria | `categorisation/IT1` | idem |
| **Dati** | `data/IT1,{DF},1.0/{key}/ALL/?detail=full` | `application/vnd.sdmx.data+csv;version=1.0.0` |

Verificato 2026-08-12: `dataflow/IT1` → 200, 4896 dataflow totali; `categorisation/IT1` → 5098 righe.
I dataflow del censimento sono i **114** categorizzati sotto il category scheme `IT1:Z1200CPA(1.0)`.

SDMX-CSV è il formato più comodo: una riga per osservazione, colonne = dimensioni + `OBS_VALUE`,
si legge con `pd.read_csv` senza parser SDMX. **Non serve `pandasdmx`.**

**Costruzione della `key`**: valori separati da `.`, nell'ordine esatto delle dimensioni della DSD,
posizione vuota = tutti i valori. Numero di posizioni sbagliato → **HTTP 422**.
Le dimensioni si leggono da `dataStructureComponents.dimensionList.dimensions`.

Esempio (Bagheria, tutte le altre dimensioni libere), DSD a 10 dimensioni:
```
data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_3,1.0/A.082006......../ALL/?detail=full
```

### Dataflow rilevanti (tutti a livello **comunale**)

| Dataflow | Contenuto | Dimensioni chiave | Anni |
|---|---|---|---|
| `DF_DCSS_ISTR_LAV_PEN_2_TV_3` | Pop. 15+ per **condizione professionale** ed età | GENDER, AGE_NOCLASS, CUR_ACT_STAT, EDU_ATTAIN, CITIZENSHIP | 2018–2024 |
| `DF_DCSS_ISTR_LAV_PEN_2_TV_1` | Pop. 9+ per **titolo di studio** ed età | GENDER, AGE_NOCLASS, EDU_ATTAIN | 2018–2024 |
| `DF_DCSS_POP_DEMCITMIG_SETA_1` | Pop. residente per **età singola**, genere, cittadinanza | GENDER, AGE_NOCLASS (Y0…Y_GE100) | 2018–2024 |
| `DF_DCSS_POP_DEMCITMIG_TV_1` | Pop. per classi quinquennali e genere | GENDER, AGE_CLASS | 2001, 2011, 2018–2024 |
| `DF_DCSS_EMPLP_1_COM` | Occupati per genere e posizione professionale | GENDER, EMPLOYMENT_STATUS | **solo 2021** |
| `DF_DCSS_ISTR_LAV_PEN_2_TV_5` | Pendolarismo giornaliero studio/lavoro | LOC_DEST, REAS_COMMUTING | 2018–2024 |
| `DF_DCSS_POP_DEMCITMIG_TV_5` | Indicatori demografici sintetici | — | — |
| `DCSS_BULK_ISTR_LAV_PEN_2` | Bulk download "Education, work, commuting and citizenship" | — | — |

Categoria `BULKDOWNLOAD` (8 dataflow) = scarico massivo, alternativa alle query puntuali.
Categoria `DCSS_BEST_PPC` (BesT) = benessere soggettivo, ma **solo province e grandi città** — non Bagheria.

### Codici territoriali (codelist `CL_ITTER107`, 12471 codici)

| Territorio | Codice |
|---|---|
| Bagheria | `082006` (**con** zero iniziale) |
| Comune di Palermo | `082053` |
| Sicilia | `ITG1` |
| Italia | `IT` |

⚠️ **Differenza da 8milaCensus**: là il codice comune è senza zero iniziale (`82006`), qui con (`082006`).
Normalizzare in pipeline a 6 cifre zero-padded.

Attenzione: `CL_ITTER107` contiene anche `SLL_2021_1906 = Bagheria` (Sistema Locale del Lavoro) e
`T19039 = Distretto di Bagheria`. Sono territori **diversi** dal comune — non confonderli.

### Codelist utili

- `CL_SEXISTAT1` → `M` maschi, `F` femmine, `T` totale (esistono anche `1`/`2`/`9` legacy: usare M/F/T).
- `CL_FORZE_LAV` (condizione professionale): `1` occupato · `12` disoccupato · `22` forze di lavoro ·
  `23` non forze di lavoro · `24` pensionato/percettore di rendita · `5` studente · `4` casalinga ·
  `7` altra condizione · `99` totale.
- `CL_TITOLO_STUDIO`: `ALL` totale · `NED` nessun titolo · `IL` analfabeta · `LSE` licenza media ·
  `USE_IF` diploma · `PSE` terziario · `BL` laurea · `ML` magistrale · `RDD`/`ML_RDD` dottorato.
- `CL_CITTADINANZA`: `TOTAL` · `ITL` italiani · `FRGAPO` stranieri.

### ⚠️ Vincolo che decide il taglio dell'analisi: le classi d'età

Nelle tabelle **condizione professionale** e **titolo di studio** a livello comunale le uniche classi
disponibili sono:

- `DF_..._TV_3` (lavoro): `Y15-24`, `Y25-49`, `Y50-64`, `Y_GE65`, `Y_GE15`
- `DF_..._TV_1` (istruzione): `Y9-24`, `Y25-49`, `Y50-64`, `Y_GE65`, `Y_GE9`

**La fascia 15-34 non è costruibile** su lavoro e istruzione: `Y25-49` sfora largamente il target e non
è scomponibile. Non esistono 15-29, 25-34, 30-34 a livello comunale.
Conseguenze operative:
- Il **NEET 15-29** definito in CLAUDE.md **non è calcolabile al 2021** per Bagheria. Al massimo si
  costruisce un proxy su `Y15-24` (non forze di lavoro `23` meno studenti `5`, oppure `23` netto degli
  studenti a seconda della convenzione) — è una misura diversa, va etichettata come tale, non spacciata per NEET.
- La serie 8milaCensus dà il NEET 15-29 **al 2011**; il 2021 dà `Y15-24`. **Non sono confrontabili**:
  qualunque grafico che li metta sulla stessa linea è sbagliato.

**Dove invece il 15-34 funziona**: `DF_DCSS_POP_DEMCITMIG_SETA_1` ha le **età singole** per genere,
quindi popolazione 15-34 M/F esatta e per ogni anno. Serve come denominatore e per misurare lo
spopolamento giovanile, non per gli indicatori di lavoro/istruzione.

### ✔ Buona notizia per il thread Genere

`GENDER` è dimensione piena, incrociata con età e condizione professionale a livello comunale.
Il gap di genere dentro i giovani — che 8milaCensus non dava — **al 2021 c'è**, sulla fascia `Y15-24`.
Incrociabile anche con `EDU_ATTAIN` per la decomposizione del gap per titolo di studio.

### ✔ Seconda buona notizia: è una serie annuale, non un singolo anno

Il censimento permanente pubblica **2018–2024**, non solo 2021. Si può mostrare la traiettoria recente
invece di una fotografia, e il 2024 è molto più attuale del 2021 previsto in CLAUDE.md.
(Su `SETA_1` il 2018 è risultato vuoto per Bagheria con `CITIZENSHIP=TOTAL`: verificare in pipeline,
non darlo per scontato.)

### Trappole di parsing

- **Doppio conteggio su `CITIZENSHIP`**: il CSV contiene `TOTAL`, `ITL` e `FRGAPO` come righe sorelle.
  Sommare senza filtrare `CITIZENSHIP == "TOTAL"` gonfia i totali di ~2×. Stesso rischio su `GENDER`
  (`T` convive con `M`/`F`) e su ogni dimensione con codice totale.
- `OBS_VALUE` è numerico puro, decimale `.` — a differenza dei CSV di 8milaCensus.
- Colonne `NOTE_*` quasi sempre vuote; `detail=full` le include comunque.
- Il segmento provider nella URL è `ALL`.

### Valori spot di controllo (Bagheria, verificati 2026-08-12)

Da usare come assert di regressione:
- Pop. 15-34 (somma età singole, `CITIZENSHIP=TOTAL`): **2021 → 12.174** (M 6.120 / F 6.054);
  **2024 → 11.861** (M 6.015 / F 5.846). Calo di 313 unità in 3 anni (−2,6%).
- Condizione professionale `Y15-24` 2021: occupati M **419** / F **176**; totale M **3.039** / F **2.852**.
  → tasso di occupazione 15-24: M 13,8% · F 6,2%.

---

## 3. Portali open data locali — esito negativo per il focus genere

**Ricognizione: 2026-08-12.** Domanda: aggiungono qualcosa all'analisi di genere sui 15-34 a Bagheria?
**Risposta: no.** Documentato qui perché il risultato negativo vale quanto quello positivo — evita che
qualcun altro rifaccia la stessa ricerca.

### dati.regione.sicilia.it (CKAN, 192 dataset)

API REST standard: `https://dati.regione.sicilia.it/api/3/action/package_search?q=...`

Ricerche su `genere`, `donne`, `femminile`, `sesso`, `occupazione`, `disoccupazione`, `giovani`,
`neet`, `istruzione`, `laureati`: **13 dataset distinti**, nessuno utile all'analisi.
Gli unici con disaggregazione per sesso (`Personale - Consistenza, categoria e sesso`,
`Personale - Fasce di età per sesso`) riguardano i **dipendenti della Regione**, non la popolazione.

**Utile invece per la parte propositiva** (dove sono i servizi, non come stanno i giovani):

| Dataset | Formati | Righe Bagheria |
|---|---|---|
| Percorsi di formazione superiore (ITS) — anagrafe scuole, a.s. 2025/26 | CSV, JSON | **3** |
| Operatori accreditati ai servizi al lavoro | CSV | **4** |
| Offerte di Lavoro (Agenzia Regionale per l'Impiego) | CSV, JSON, TTL | da verificare |
| FSE - Elenco beneficiari | — | da verificare |

Le tre scuole tecniche a Bagheria (a.s. 2025/26) e le quattro sedi accreditate ai servizi al lavoro
sono la base fattuale per un intervento: dicono cosa esiste già sul territorio.
Da scaricare quando si scrive la proposal, non ora.

### opendata.comune.palermo.it — non è CKAN

`/api/3/action/*` risponde **404**: è un portale PHP custom, non CKAN.
Il catalogo machine-readable è **DCAT in Turtle** su `https://opendata.comune.palermo.it/dcat/dcat.php`
(~4,3 MB, `text/n3`). Nel Turtle il predicato è `dc:title`, non `dct:title`, e ogni dataset compare
due volte (la seconda come `Distribuzione CSV del dataset ...`): 3451 titoli → **1691 dataset reali**.

Contiene dati per sesso e istruzione — `STUDENTI UNIVERSITARI ISCRITTI PER SESSO, FACOLTA' E TIPO DI
CORSO`, `XIV CENSIMENTO ... OCCUPATI PER POSIZIONE NELLA PROFESSIONE E SESSO` — ma:

1. sono **anni accademici 2008-2010** e censimento 2001, cioè più vecchi di tutto ciò che abbiamo già;
2. coprono **il solo Comune di Palermo**, mai Bagheria.

Come benchmark Palermo è già coperto meglio da ISTAT (stesse definizioni, stessi anni, stesse fonti).
**Non c'è motivo di usare questo portale per il thread Genere.**

---

## 4. Interfaccia `data/processed/` — schema delle tabelle

Prodotte da `pipeline/build.py`, rigenerabili con `uv run python -m pipeline.build`.
Tabelle lunghe + lookup: nessuna scelta di analisi è cotta dentro, ogni thread filtra ciò che gli serve.

| File | Righe | Colonne |
|---|---|---|
| `territori.csv` | 521 | `territorio`, `nome_territorio`, `livello`, `fonti` |
| `indicatori.csv` | 99 | `indicatore`, `nome_indicatore`, `tema`, `descrizione` |
| `codici.csv` | 136 | `dimensione`, `codice`, `etichetta` |
| `ottomilacensus_long.csv` | 154.737 | `territorio`, `nome_territorio`, `livello`, `anno`, `indicatore`, `valore` |
| `censpop_istr_lav_long.csv` | 6.552 | `territorio`, `anno`, `tavola`, `genere`, `eta`, `eta_anni`, `cittadinanza`, `titolo_studio`, `condizione`, `valore` |
| `censpop_popolazione_long.csv` | 14.462 | `territorio`, `anno`, `genere`, `eta`, `eta_anni`, `stato_civile`, `cittadinanza`, `valore` |

- **`territorio` è la chiave comune alle due fonti.** Comuni con codice ISTAT a 6 cifre (`082006`),
  Sicilia `ITG1`, Italia `IT` — gli stessi codici di SDMX, così le tabelle si uniscono senza mappature.
  Province e regioni diverse dalla Sicilia, che in SDMX non esistono, hanno prefisso `PROV`/`REG`.
- **`eta_anni`** è l'età come numero, valorizzata solo per le età singole (`Y23` → 23). Per le classi
  (`Y15-24`) e i totali resta vuota: si filtra su `eta`, non su `eta_anni`.
- **`tavola`** in `censpop_istr_lav_long` vale `lavoro` o `istruzione`: le due tabelle SDMX condividono
  la stessa DSD, quindi stanno in un file solo.
- Le descrizioni lunghe stanno nei lookup e non nelle tabelle: ripetute riga per riga portavano
  `ottomilacensus_long` da 5 a 40 MB.

**Leggendo in R, forzare le colonne codice a carattere.** `condizione` contiene `1`, `12`, `99`:
`readr` le indovina come intero e i filtri su stringa falliscono in silenzio.

```r
library(tidyverse)
long    <- read_csv("data/processed/censpop_istr_lav_long.csv", col_types = cols(.default = "c", valore = "d", anno = "i"))
codici  <- read_csv("data/processed/codici.csv", col_types = cols(.default = "c"))

occupazione_giovanile <- long |>
  filter(tavola == "lavoro", eta == "Y15-24", cittadinanza == "TOTAL",
         titolo_studio == "ALL", genere %in% c("M", "F")) |>
  select(territorio, anno, genere, condizione, valore) |>
  pivot_wider(names_from = condizione, values_from = valore) |>
  mutate(tasso_occupazione = 100 * `1` / `99`)
```

Attenzione a `PSE` = *licenza di scuola elementare*, non "post-secondary": i codici titolo di studio
non si indovinano dall'acronimo, si leggono da `codici.csv`.

---

## 5. ISTAT — Confini amministrativi (cartografia)

Aggiunto il 2026-08-12 per la mappa comunale del thread Genere (`viz/fig04_mappa_sicilia.R`).

### Endpoint

```
https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/2026/Limiti01012026_g.zip
```

Scaricato il **2026-08-12** (10.450.609 byte) in `data/raw/istat_confini_comuni_2026-08-12.zip`,
riga corrispondente in `data/raw/manifest.csv`. Nessun parametro, nessuna autenticazione.

### ⚠️ Esiste solo il vintage corrente

Le annate storiche **non sono più su questo storage** (verificato 2026-08-12: `2011`, `2012` e i
percorsi `archivio*` rispondono 404). Le uniche annate servite sono 2024, 2025 e 2026. Di
conseguenza la mappa di un dato 2011 usa confini 2026: lo scarto non si assume, si verifica sul
join (la cella "Bagheria nella distribuzione siciliana" di `notebooks/genere.ipynb` lo fa).

Esito del join per la Sicilia: **391 comuni nei confini 2026, 390 nel dato 2011**. Tutti i comuni
con dato hanno un confine; l'unico scoperto è **Misiliscemi** (`081025`), istituito nel 2021
staccandosi da Trapani. Nel 2011 non esisteva: resta in bianco sulla mappa, attribuirgli il valore
di Trapani sarebbe un'imputazione.

### Struttura dello zip

Quattro cartelle, una per livello: `Com01012026_g/` (comuni, 7.896 righe), `ProvCM01012026_g/`,
`Reg01012026_g/`, `RipGeo01012026_g/`. Ogni cartella è uno shapefile completo (`.shp/.dbf/.shx/.prj`).
Si legge senza scompattare: `gpd.read_file("zip://<zip>!Com01012026_g/Com01012026_g_WGS84.shp")`.

Colonne utili: `PRO_COM_T` (codice comune a 6 cifre, **già zero-padded**, combacia con `territorio`),
`COMUNE`, `COD_REG` (Sicilia = `19`).

**Il CRS del file è EPSG:32632** (UTM 32N) nonostante il suffisso `_WGS84` nel nome: la zona giusta
per la Sicilia è la 33N, `pipeline/build.py` riproietta a **EPSG:32633**.

### Perché in `data/processed/` ci sono vertici e non un GeoJSON

`sf` non è installabile su queste macchine (servono GDAL/GEOS/PROJ di sistema e i permessi di root).
`pipeline/build.py` esporta quindi `comuni_sicilia_poligoni.csv` — una riga per vertice, con
`territorio, nome_comune, parte, anello, ordine, x, y` — più `comuni_sicilia_centroidi.csv` con un
punto-etichetta interno al poligono per comune. In R si disegnano con `geom_polygon(group = comune ×
parte, subgroup = anello, rule = "evenodd")`: `parte` separa le isole dello stesso comune, `anello`
distingue il contorno esterno dai buchi. Sono 15.702 vertici dopo `simplify(100 m)`, 0,6 MB.

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

---

## 6. ISTAT — Censimento permanente, i cinque comuni vicini a Bagheria (SDMX)

Scaricato il **2026-08-25** per portare nelle figure 1 e 7 del thread Genere anche il vicinato
di Bagheria. Stesso host, stessi dataflow della sezione 2: cambia solo la `key`, che elenca i
cinque comuni **geograficamente più vicini** per distanza fra centroidi ISTAT (la selezione la
calcola `notebooks/genere.ipynb`, cella della mappa, e la scrive in
`data/processed/genere_mappa_etichette.csv`).

| Codice | Comune | Distanza dal centroide di Bagheria |
|---|---|---|
| `082067` | Santa Flavia | 2,9 km |
| `082035` | Ficarazzi | 3,2 km |
| `082079` | Villabate | 4,7 km |
| `082023` | Casteldaccia | 7,9 km |
| `082048` | Misilmeri | 8,1 km |

URL esatti (header `Accept: application/vnd.sdmx.data+csv;version=1.0.0`, `Accept-Language: it`):

```
data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_3,1.0/A.082067+082035+082079+082023+082048......../ALL/?detail=full
data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_1,1.0/A.082067+082035+082079+082023+082048......../ALL/?detail=full
data/IT1,DF_DCSS_POP_DEMCITMIG_SETA_1,1.0/A.082067+082035+082079+082023+082048......./ALL/?detail=full
```

→ `data/raw/censpop_lavoro_vicini_2026-08-25.csv`, `censpop_istruzione_vicini_2026-08-25.csv` e
`censpop_popolazione_vicini_2026-08-25.csv`, struttura identica ai fratelli a quattro territori
(sezione 2). Comando: `uv run python -m pipeline.fetch --solo=vicini`.

**Perché file separati e non `TERRITORI` allargato.** `pipeline/build.py` prende sempre il raw più
recente per prefisso (`ultimo()`): riscaricare i censpop con nove territori li avrebbe serviti in
automatico a tutti i thread, cambiando i numeri di chi aggrega senza filtrare per territorio.
Con prefissi distinti i `censpop_*_long.csv` condivisi restano a quattro territori e il vicinato
vive in `censpop_istr_lav_vicini_long.csv` (lavoro + istruzione, stesso schema del condiviso) e
`censpop_popolazione_vicini_long.csv`.

**Uscite del thread Genere** (tutte con i cinque comuni separati e, dove serve alle figure, la riga
aggregata `territorio = "VICINI5"` — chi somma quei file per territorio deve escluderla):
`genere_gap_occupazione_ci_vicini.csv` (fig01), `genere_composizione_stato_dettaglio_vicini.csv`
(fig02), `genere_coorti_vicini.csv` (fig03), `genere_forbice_vicini.csv` (fig05),
`genere_ritenzione_eta_vicini.csv` (fig07).

**Copertura verificata sul raw**: 5 territori, anni 2018-2024 con il **2020 assente sulla classe
15-24** (stesso buco alla fonte dei territori di confronto), età singole presenti dal 2021.

**Taglia campionaria**: comuni fra 10.000 e 28.000 abitanti, 580-800 donne 15-24 per anno e
conteggi di occupate nell'ordine delle decine. Gli intervalli di confidenza sul gap sono molto più
larghi di quelli dei quattro territori di confronto: le serie sono contesto locale, non stime da
confrontare anno su anno.

**Timeout**: la query per età singola impiega più di 180 secondi a produrre il corpo della risposta
(verificato 2026-08-25, tre tentativi falliti). Il timeout di `pipeline/fetch.py` è stato portato a
600 secondi.

---

## 7. ISTAT — Censimento permanente oltre il 2011: gemelle, 390 comuni, classi quinquennali

Ricognizione e scarico del **2026-08-25**. Domanda di partenza: `viz/fig10_muro_recente.R`
si ferma al 2011 perché 8milaCensus è l'ultimo censimento decennale — c'è modo di arrivare
più vicino a oggi restando dentro le fonti già censite? **Sì**, e senza cambiare fonte:
la stessa tavola lavoro della sezione 2 espone la classe **15 anni e più**.

### La chiave del ponte: `AGE_NOCLASS = Y_GE15`

In `DF_DCSS_ISTR_LAV_PEN_2_TV_3` la classe `Y_GE15` esiste a livello comunale, incrociata
con `GENDER` e `CUR_ACT_STAT`. È **la stessa base dei quattro indicatori di lavoro di
8milaCensus**, non un'approssimazione: le definizioni del codebook (`indicatori.csv`)
combaciano codice per codice.

| 8milaCensus (1991-2011) | Ricostruzione dal permanente (2018-2024) |
|---|---|
| `L11` tasso di occupazione femminile | `CUR_ACT_STAT=1` / `99`, `GENDER=F`, `Y_GE15` |
| `L10` tasso di occupazione maschile | `1` / `99`, `GENDER=M`, `Y_GE15` |
| `L2` partecipazione al lavoro femminile | `22` / `99`, `GENDER=F`, `Y_GE15` |
| `L7` tasso di disoccupazione femminile | `12` / `22`, `GENDER=F`, `Y_GE15` |

`I1` (differenziale educativo M/F) **non è ricostruibile**: 8milaCensus lo calcola sulla
popolazione **6+**, la tavola istruzione del permanente parte da `Y_GE9` e non ha una classe
15+. Sarebbe un altro indicatore, non un seguito: resta fermo al 2011.

### ✔ Le due rilevazioni concordano sull'occupazione — e non sulla disoccupazione

Il salto 2011 → 2018 mette a confronto **due disegni di rilevazione diversi**: censimento
decennale universale a questionario contro censimento permanente campionario appoggiato ai
registri. Non è una validazione esterna (i numeri restano ISTAT da entrambe le parti), ma
dice se il livello dipende dal disegno. Bagheria:

| | 2011 (decennale) | 2018 (permanente) | scarto |
|---|---|---|---|
| L11 occupazione F | 18,1 | 18,8 | +0,7 |
| L10 occupazione M | 43,1 | 40,4 | −2,7 |
| L2 partecipazione F | 28,7 | 30,4 | +1,7 |
| L7 disoccupazione F | 36,9 | 38,1 | +1,2 |

⚠️ **La rottura vera non è al giunto fra le fonti: è dentro il censimento permanente, fra
2019 e 2021**, e c'è su tutti i territori (Bagheria L7 38,1 → 22,6; Italia 15,1 → 10,6;
Sicilia 30,1 → 17,3). Cambia la misura di "in cerca di occupazione", quindi tocca **L7 e L2**
e lascia intatti L10 e L11, che attraversano il 2019-2021 senza scalini. Conseguenza
operativa: **si estendono L11 e L10; L2 e L7 solo con la rottura marcata a vista**.
La tabella completa per i quattro territori è in `data/processed/genere_coerenza_fonti.csv`,
prodotta da `notebooks/genere.ipynb` (sezione "Il ponte fra i due censimenti").

### ⚠️ Il limite che decide come si scarica: IIS taglia il segmento di path

Il server SDMX sta dietro IIS, che rifiuta un **segmento di path** oltre ~260 caratteri con
`400 Bad Request - Invalid URL` (non `414`, e il corpo è HTML: senza il controllo di
`pipeline/fetch.py` finirebbe in `data/raw/` una pagina di errore travestita da CSV).
Verificato il 2026-08-25 sulla chiave dei comuni: **33 codici → 200, 35 → 400**.
Quindi i 390 comuni siciliani si scaricano in **12 blocchi** da 33.

### Le tre query aggiunte

Header come nella sezione 2 (`Accept: application/vnd.sdmx.data+csv;version=1.0.0`,
`Accept-Language: it`). Comandi: `uv run python -m pipeline.fetch --solo=gemelle`,
`--solo=demografia_classi`, `--solo=15piu`.

**A. Le dieci gemelle strutturali** — `censpop_lavoro_gemelle_2026-08-25.csv`
```
data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_3,1.0/A.082070+082067+082020+082073+082048+082005+082071+081008+084028+084041......../ALL/?detail=full
```
Termini Imerese, Santa Flavia, Capaci, Trabia, Misilmeri, Altofonte, Terrasini, Erice,
Porto Empedocle, Sciacca — il gruppo di controllo del matching Mahalanobis, che finora
esisteva solo al 2011. Tavola intera (tutte le classi d'età), 1,0 MB.
Attenzione: **Santa Flavia e Misilmeri sono anche fra i cinque vicini** della sezione 6.
I due raw restano separati, chi li unisse deve deduplicare per territorio.

**B. I 390 comuni siciliani sulla sola classe 15+** — `censpop_lavoro_15piu_sicilia_01..12_2026-08-25.csv`
```
data/IT1,DF_DCSS_ISTR_LAV_PEN_2_TV_3,1.0/A.{33 codici separati da +}...Y_GE15.TOTAL.ALL.../ALL/?detail=full
```
Chiave ristretta a `Y_GE15` / `CITIZENSHIP=TOTAL` / `EDU_ATTAIN=ALL`: 162 righe per comune
invece di 819. Senza il vincolo sarebbero ~320.000 righe per usarne un quinto.
È il **denominatore dei percentili regionali**, che finora esistevano solo al 2011.

⚠️ **390 e non 391.** La lista è quella dei comuni **ai confini 2011**, la stessa su cui il
notebook calcola i percentili di 8milaCensus. **Misiliscemi** (`081025`), istituito nel 2021
staccandosi da Trapani, è escluso di proposito: includerlo cambierebbe il denominatore fra le
due epoche e renderebbe i percentili non confrontabili. Corollario da dichiarare: i valori
2021-2024 di **Trapani** (`081021`) sono su un territorio più piccolo di quello del 2011.

**C. Popolazione per classi quinquennali** — `censpop_demografia_classi_2026-08-25.csv`
```
data/IT1,DF_DCSS_POP_DEMCITMIG_TV_1,1.0/A.082006+082053+ITG1+IT......./ALL/?detail=full
```
DSD a **9 dimensioni**: `FREQ, REF_AREA, INDICATOR, GENDER, AGE_CLASS, MARITAL_STATUS,
CITIZENSHIP, AREA_CONTRY_CITIZEN, USUAL_RESID_1Y`. Nota che la dimensione dell'età qui si
chiama `AGE_CLASS`, non `AGE_NOCLASS` come nelle tavole della sezione 2.

È **l'unica tavola comunale che copre 2001 e 2011 oltre al 2018-2024**: `SETA_1` parte dal
2018 e le età singole solo dal 2021. Le classi `Y15-19`, `Y20-24`, `Y25-29`, `Y30-34`
ricompongono il target **15-34 esatto**, quindi la serie demografica del target si allunga di
vent'anni. A livello comunale `MARITAL_STATUS`, `AREA_CONTRY_CITIZEN` e `USUAL_RESID_1Y`
valgono solo `ALL` e `CITIZENSHIP` solo `TOTAL`: niente incroci, solo la struttura per età.

### Tempi e copertura

- Blocchi da 33 comuni: ~50-60 s ciascuno, ~12 minuti per i 390. `DF_DCSS_POP_DEMCITMIG_TV_1`
  a quattro territori: 70 s. Il timeout di `pipeline/fetch.py` (600 s) basta.
- Anni serviti su `Y_GE15`: **2018, 2019, 2021, 2022, 2023, 2024**. Il **2020 manca**, come su
  ogni classe che contenga i 15-24 (stesso buco alla fonte già noto dalla sezione 2).
- `DF_DCSS_POP_DEMCITMIG_TV_1`: **2001, 2011, 2018-2024**, qui il 2020 c'è.

### Uscite in `data/processed/`

| File | Contenuto |
|---|---|
| `censpop_lavoro_gemelle_long.csv` | tavola lavoro delle 10 gemelle, schema dei `censpop_istr_lav_*_long` |
| `censpop_lavoro_15piu_sicilia_long.csv` | 390 comuni × `Y_GE15`, 2018-2024 |
| `censpop_demografia_classi_long.csv` | popolazione per classi quinquennali, 2001-2024 |
| `genere_coerenza_fonti.csv` | decennale 2011 vs permanente 2018 + salto 2019-2021, per i 4 territori |
| `genere_madri_recente.csv` | L2/L11/L10/L7 e percentile sui 390, 2018-2024 (gemello recente di `genere_gap_madri.csv`) |
| `genere_pretrend_gemelle_recente.csv` | L11 di Bagheria contro la banda interquartile delle gemelle, 2018-2024 |

`pipeline/build.py` salta queste uscite senza rompersi se i raw non ci sono, così chi non
ha ancora rifatto il fetch continua a rigenerare tutto il resto.

### Regola per le figure

Le due fonti restano due. **Mai una linea continua fra il 2011 e il 2018**: stacco visibile,
fonte dichiarata per blocco. I **percentili** attraversano il giunto meglio dei livelli perché
sono ranghi calcolati dentro l'anno, e lo scarto di definizione sposta tutti i 390 comuni
nello stesso verso; i livelli assoluti no, e vanno letti come due serie affiancate.

---

## 8. Verifica di attualità dei claim: la graduatoria del 2011 regge nel 2024?

*Ricognizione del 2026-08-25, senza nuovi download.* Tutto quello che segue si ricava dai
raw già in `data/raw/` (sezioni 1, 2, 6 e 7): serve a rispondere alla domanda «i claim
poggiano su dati legacy o su previsioni verificabili?» prima di portarli nella proposal.

### Persistenza della graduatoria dei 390 comuni

Stesso indicatore (`L11`, tasso di occupazione femminile 15+), stessa platea (390 comuni ai
confini 2011), due epoche e due disegni di rilevazione. Il confronto è fra **ranghi**, non
fra livelli, per la ragione già scritta in fondo alla sezione 7.

| coppia di annate | rho di Spearman | quintile basso ancora tale nel 2024 |
|---|---|---|
| 2011 → 2024 (8milaCensus → permanente) | **0,848** | 74% |
| 2011 → 2018 | 0,883 | 83% |
| 2018 → 2024 (solo permanente) | **0,919** | 83% |
| 2021 → 2024 (solo permanente) | 0,942 | 87% |

Letto così: la graduatoria comunale è una struttura stabile, non un rumore annuale. Un
claim di posizionamento costruito sul censimento 2011 **si è avverato**, e il rho lo misura.
Il livello invece va aggiornato: Bagheria passa da 18,1% (12° percentile) a 23,7% (17°),
mentre la mediana regionale sale da 23,6% a 28,3% — cioè **nel 2024 Bagheria arriva dove
stava la mediana siciliana nel 2011**.

Cautela d'obbligo: rho alto significa che l'*ordine* si conserva, non che i livelli siano
confrontabili. Le due rilevazioni non misurano la stessa cosa allo stesso modo, e sulla
mappa le due annate restano due scale distinte.

### Ritenzione di coorte a passo quinquennale

`DF_DCSS_POP_DEMCITMIG_TV_1` (sezione 7) serve 2001, 2011 e 2018-2024 per classi
quinquennali: una coorte si segue spostandosi di **una classe ogni cinque anni**. Chi ha
15-19 anni in *t* ne ha 25-29 in *t+10*.

| coorte 15-19, femmine | Bagheria | Palermo | Sicilia | Italia |
|---|---|---|---|---|
| 2001 → 2011 | **102,9%** | 87,6% | 97,8% | 113,1% |
| 2011 → 2021 | **88,6%** | 90,2% | 92,1% | 104,4% |

Sui maschi il ribaltamento è di 98,4% → 83,9%. In entrambi i casi **circa quattordici punti
in un decennio**, e nel secondo decennio Bagheria sta sotto Palermo sui maschi.

**Il decennio 2011-2021 ha una gamba per rilevazione** (2011 decennale, 2021 permanente) e
va marcato. La distorsione nota però va nel verso prudente: il censimento 2011 contò meno
dell'anagrafe, quindi sta al *denominatore* del decennio che crolla e al *numeratore* di
quello che tiene — il divario fra i due decenni è una **stima per difetto in entrambe le
gambe**. In più i controlli interamente interni al permanente (2018→2023 e 2019→2024)
ritrovano la perdita sulla transizione 20-24 → 25-29: femmine 92,8% e 93,3% a Bagheria
contro ~102% in Italia. La perdita è databile ed è attuale.

### Stabilità della «forbice» (fig05)

Le due misure della forbice ripetute su tutte le annate disponibili (2018-2024, il 2020
manca), Bagheria contro i quattro benchmark e il vicinato aggregato:

| misura | Bagheria all'estremo in |
|---|---|
| tasso di occupazione femminile 15-24 (il più basso) | **6 anni su 6** |
| vantaggio educativo femminile 9-24 (il più ampio) | 4 anni su 6 (nel 2018-2019 era la Sicilia) |
| rapporto M/F sull'occupazione (il più alto) | 4 anni su 6 (nel 2022-2023 era il vicinato) |

Qui il problema non è l'età del dato — la fotografia è già al 2024 — ma il fatto che poggi
su **un anno solo**. Il rapporto M/F di Bagheria oscilla (2,47 nel 2018 → 1,89 nel 2023 →
2,01 nel 2024) e nel 2023 era il migliore del gruppo locale. Il claim difendibile è il
**livello femminile**, minimo del panel ogni anno, insieme all'allargamento della forbice
(vantaggio educativo da +3,1 a +4,2 mentre il vicinato crolla da +2,9 a +0,5).

### Uscite in `data/processed/`

| File | Contenuto |
|---|---|
| `genere_distribuzione_390.csv` | per anno: Bagheria, percentile, mediana, quartili, rho vs 2011 e vs 2024, persistenza del quintile |
| `genere_mappa_2011_2024.csv` | 390 comuni: valore e percentile alle due annate, centroide, ruolo per l'etichettatura |
| `genere_ritenzione_decennale.csv` | ritenzione di coorte per tutte le classi e i quattro periodi (2001-2011, 2011-2021, 2018-2023, 2019-2024) |
| `genere_forbice_serie.csv` | le tre misure della forbice per 5 territori × 6 anni (fotografia e serie nella stessa tabella) |

### Regola per le figure

Un claim di posizionamento va scritto **con il suo rho**: dire «12° percentile nel 2011»
senza dire che quella graduatoria predice il 2024 con rho 0,848 lascia al revisore
l'obiezione più facile. E viceversa: una fotografia recente costruita su un anno solo va
accompagnata dalla serie, altrimenti si scambia un'oscillazione per una struttura.

---

## 9. ISTAT — Popolazione per stato civile ed età singola (DCIS_POPRES1, SDMX)

**Ricognizione: 2026-08-26** — serve al thread genere per la domanda «le casalinghe
ventenni sono coniugate?» (`notebooks/genere.ipynb`, sezione «Le casalinghe sono
coniugate?»).

### Perché non dal censimento permanente

Il censimento permanente **non incrocia lo stato civile a livello comunale**: su tutta la
famiglia `DF_DCSS_POP_DEMCITMIG_*` la dimensione `MARITAL_STATUS` è servita solo come
`ALL`, e una chiave esplicita (es. `A.082006....2...` su `TV_1` o `SETA_1`) risponde
**404 NoRecordsFound** (verificato 2026-08-26). `DF_DCSS_HCUE_COM_1_COM` («Popolazione
per stato civile - comuni») ha lo stato civile ma **non l'età**. La tavola giusta è fuori
dal censimento:

- **Dataflow**: `22_289_DF_DCIS_POPRES1_26` — «Tutti i comuni per singola età e stato
  civile», famiglia DCIS_POPRES1 (popolazione residente al **1° gennaio**, su base
  censuaria dal 2019).
- **DSD a 6 dimensioni**: `FREQ, REF_AREA, DATA_TYPE, SEX, AGE, MARITAL_STATUS`.
- **Query usata** (fetch `popres_stato_civile_eta`, raw del 2026-08-26):
  `data/IT1,22_289_DF_DCIS_POPRES1_26,1.0/A.082006+082053+ITG1+IT..../ALL/?detail=full`
- Comando: `uv run python -m pipeline.fetch --solo=stato_civile`. Uscita processed:
  `popres_stato_civile_long.csv` (sessi normalizzati a M/F/T).

### ⚠️ È una fonte diversa dal censimento permanente

Stock al **1° gennaio** contro **media annua** (`SETA_1`, `INDICATOR=RESPOP_AV`): mai in
serie sullo stesso grafico. Il 1.1.2025 è la fotografia di fine 2024, l'anno di
riferimento della tavola lavoro. Controllo di coerenza (in notebook e in
`pipeline/verifica.py`): ragazze 15-24 di Bagheria al 1.1.2025 = **2.882**, identico alla
media annua 2024 di `SETA_1`.

### Trappole verificate

- `SEX` usa i **codici legacy** di `CL_SEXISTAT1`: `1` maschi, `2` femmine, `9` totale.
  La pipeline li normalizza a M/F/T in `pipeline/build.py`.
- `DATA_TYPE` = `JAN` (unico valore): popolazione al 1° gennaio.
- `MARITAL_STATUS` (codelist `CL_STATCIV2`): `1` nubile/celibe · `2` coniugata/o ·
  `3` divorziata/o · `4` vedova/o · `15` unito/a civilmente · `16`/`17` già in unione
  civile · `99` totale.
- **Anni 2019-2026, ma il dettaglio coniugale arriva al 1.1.2025**: il 1.1.2026 pubblica
  solo il totale `99`. L'anno di riferimento va scelto sugli anni con dettaglio.
- **Zeri strutturali, non buchi**: il dettaglio coniugale non è pubblicato sotto i 16
  anni (sotto i 18 per le unioni civili). Dove il dettaglio manca, nubile = totale
  esattamente; con `fillna(0)` la partizione ricostruisce `99` al centesimo (verificato
  su tutte le righe 2019-2025).
- Lo stato civile osserva il **matrimonio formale**: niente convivenze, niente maternità.
  Il check successivo sul canale famiglia (nati per età della madre, demo.istat) è un
  fetch nuovo, da decidere in team.

---

## 10. Interfaccia col thread educazione (`titolo_condizione/`)

Aggiunta il 2026-08-27. Il thread educazione (Saverio) vive in `titolo_condizione/` come
progetto autonomo con pipeline, raw e provenance propri: URL esatti, timestamp UTC,
licenze e SHA-256 in `titolo_condizione/data/raw/manifest.csv`, endpoint dichiarati in
`titolo_condizione/config/sources.yml`. Due fonti nuove rispetto al resto del repo:

- **Anagrafe sedi scolastiche MIUR** — SPARQL su
  `https://dati.istruzione.it/opendata/SCUANAGRAFESTAT/query` (query in
  `titolo_condizione/config/technical_schools.sparql`), a.s. 2025/26, sedi tecniche
  siciliane. Anagrafica di sedi, non di esiti.
- **GTFS AMAT Palermo** —
  `https://opendata.comune.palermo.it/js/server/uploads/dataset/gtfs/amat_gtfs.zip`
  (feed 20260727-20260831). Rete urbana: non copre il collegamento Bagheria-Palermo.
- Esito negativo registrato: i due dataset regionali su offerte di lavoro e operatori
  accreditati (`dati.regione.sicilia.it`) hanno risposto **HTTP 502** al run del
  2026-08-25 e sono esclusi da ogni risultato quantitativo (fallimento nel manifest).

Le tavole condivise passano da `data/processed/` col prefisso `edu_`, copiate con:

```bash
uv run python -m pipeline.edu
```

| file | contenuto |
|---|---|
| `edu_youth_states_2018_2024.csv` | stati 15-24 (totale di genere) per i quattro territori |
| `edu_change_decomposition_2018_2024.csv` | shift-share 2018→2024 dei conteggi (Bagheria, T) |
| `edu_gaps_vs_sicily.csv` | gap Bagheria−Sicilia per metrica e anno |
| `edu_matched_peers_2011.csv` | i 10 peer (caliper 0,5-2×, feature con profilo educativo) |
| `edu_model_robustness_2011.csv` | regressioni comunali 2011: residui di Bagheria con CI bootstrap |
| `edu_historical_bagheria.csv` | indicatori 8milaCensus 1991-2011 con percentile siciliano |
| `edu_historical_benchmarks_2011.csv` | benchmark 2011 (I5/I6/I7/I8/L4/L14) |
| `edu_technical_schools.csv` | anagrafe MIUR delle sedi tecniche (Sicilia) |

⚠️ Le quote della tavola lavoro hanno una **rottura di misura fra 2019 e 2021** (la
componente "in cerca" si dimezza in tutti i territori e i conteggi diventano frazionari:
cambio del metodo di stima del permanente, sezione 8): i *gap* fra territori restano
confrontabili, i *livelli* delle componenti no. Da dichiarare ogni volta che si cita la
serie di `edu_youth_states_2018_2024.csv` o la scomposizione 2018→2024.

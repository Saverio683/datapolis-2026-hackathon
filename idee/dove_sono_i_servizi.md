# Dove sono i servizi — il lato dell'offerta, e chi riesce ad arrivarci

> Tre percorsi di formazione tecnica superiore e quattro sedi accreditate ai servizi al lavoro
> esistono già a Bagheria. La domanda non è se servano servizi nuovi: è perché quelli che ci
> sono non intercettano le ragazze.

## L'idea

Tutta l'analisi finora guarda la **domanda**: chi sono i giovani, cosa fanno, chi manca.
Manca il lato dell'**offerta**: quali strumenti esistono già sul territorio, dove stanno
fisicamente, e chi può realisticamente raggiungerli.

La ricognizione delle fonti ha già trovato che `dati.regione.sicilia.it` non serve
all'analisi di genere sulla popolazione, ma **serve alla parte propositiva**: contiene
l'anagrafe dei percorsi ITS (3 righe per Bagheria, a.s. 2025/26), gli operatori accreditati ai
servizi al lavoro (4 sedi), le offerte di lavoro dell'Agenzia Regionale per l'Impiego e i
beneficiari FSE. Sono la base fattuale di qualunque intervento: dicono **cosa non va
inventato da capo**.

L'angolo di genere è l'accessibilità: in un comune al 25° percentile siciliano per mobilità
fuori comune, e con un'inattività femminile che si dichiara "casalinga", la distanza fisica e
gli orari non sono un dettaglio logistico — sono il filtro che decide chi usa un servizio.

## Perché è rilevante

Una proposal che ignora ciò che esiste già viene smontata da chiunque conosca il territorio.
Una che parte da lì ("questi 4 presidi esistono, ecco cosa manca per renderli efficaci per le
ragazze 15-24") è immediatamente più credibile e molto più economica da attuare.
È anche l'unico pezzo dell'analisi che usa una fonte **locale e attuale (2025/26)** invece del
censimento: dà attualità a un lavoro che altrimenti si ferma al 2024.

## Cosa dicono già i dati

- 3 percorsi di formazione superiore e 4 sedi accreditate a Bagheria (verificato 2026-08-12,
  `docs/sources.md` §3). Non ancora scaricati: la ricognizione dice che ci sono, il download è
  da fare quando si scrive la proposal.
- `opendata.comune.palermo.it` è stato **verificato come inutile** per questo scopo (dati
  2001-2010, solo Comune di Palermo): non rifare quella ricerca.
- Cartografia comunale già pronta in `data/processed/` per posizionare i presidi su mappa.

## Cosa bisogna sviluppare

1. **Scaricare e censire** i quattro dataset regionali, con la riga corrispondente in
   `docs/sources.md` e il file in `data/raw/` (append-only, come da regole).
2. **Mappare i presidi** su Bagheria, con la distribuzione della popolazione giovanile.
   La mappa comunale richiede un dettaglio sub-comunale (sezioni di censimento) che **non
   abbiamo**: se non lo si trova, la mappa resta al livello dei punti-servizio senza
   coropleta interna, ed è comunque leggibile. Non inventare un dato di popolazione per zona.
3. **Leggere le offerte di lavoro ARI** per profilo richiesto: quale domanda di competenze
   esprime davvero il territorio? È l'unico modo per dire qualcosa sul *mismatch* citato dal
   brief, dato che l'incrocio titolo × condizione non esiste a livello comunale.
   ⚠️ Le offerte pubblicate su un portale pubblico sono una frazione non casuale del mercato:
   descrivono ciò che passa dal canale formale, non la domanda totale. Va detto.
4. **Incrociare con l'orientamento di genere dei percorsi**: se i 3 ITS locali sono in
   settori a fortissima prevalenza maschile, la formazione tecnica esistente non è una
   risposta per la platea femminile — e questa è una conclusione operativa immediata.

## Fattibilità

🟡 Fonte già individuata ma **non ancora scaricata**: è un fetch nuovo, però su un CKAN
standard (`package_search`/`datastore_search`), quindi tecnicamente semplice.
🔴 Nessuna di queste fonti ha la dimensione genere sulla popolazione servita: si può dire
cosa esiste e dove, non chi lo usa. Il collegamento con la platea femminile è **argomentativo**
(distanza, orari, settori dei percorsi), non misurato. Dichiararlo evita di prometterlo.

## Verso la proposal

- **Evidenza** → l'offerta esiste (3 + 4 presidi) ma la platea femminile 15-24 resta fuori
  dal mercato del lavoro: il problema non è la mancanza di infrastruttura, è l'ingaggio.
- **Intervento** → riorientare presidi esistenti (orari, sede, modalità di contatto attivo,
  settori dei percorsi) invece di crearne di nuovi: costo marginale, non nuovo capitolo.
- **Target** → le ragazze 15-24 fuori da lavoro e istruzione residenti a Bagheria.
- **KPI** → quota di utenza femminile 15-24 dei servizi accreditati locali. ⚠️ Richiede che
  il dato venga rilevato: è un KPI che l'intervento deve **creare**, e vale la pena dirlo
  esplicitamente come parte della proposta (oggi quel numero non esiste).

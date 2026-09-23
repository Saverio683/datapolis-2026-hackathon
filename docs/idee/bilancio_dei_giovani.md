# [PARENT] Il bilancio dei giovani — contare chi entra, chi resta, chi è già nato

> La popolazione 15-34 di Bagheria è un conto corrente: entrate, uscite, e un saldo che fa
> −313 persone in tre anni. Questo parent tratta la demografia come contabilità, non come sfondo.

## Il frame

Gli altri parent spiegano *perché* i giovani se ne vanno. Questo misura **il bilancio**
stesso, in tutte le sue voci: le coorti che si assottigliano (uscite nette), la componente
straniera (l'unica entrata possibile oltre le nascite di vent'anni fa), e la platea futura
che è **già nata e già contabile** — i bambini di oggi sono i 15-24enni del prossimo
decennio, e le età singole 2021-2024 permettono di contarli senza alcuna proiezione.

Il punto per l'hackathon: ogni intervento proposto agirà su una platea che si muove. Dire di
quanto e in che direzione — per genere — è la cornice quantitativa dentro cui tutte le altre
idee devono stare. Un intervento dimensionato sulla platea 2024 che parte nel 2027 su una
platea più piccola del 5% è già sbagliato in partenza.

## Perché è un parent

Perché è il **denominatore comune** di tutte le altre idee: tassi, gap in persone, KPI —
tutto poggia sulla popolazione per età e genere, ed è l'unico dominio dove il target 15-34
dell'hackathon si rispetta esattamente (età singole di `DF_DCSS_POP_DEMCITMIG_SETA_1`).

## Idee figlie derivabili

- **Doppia fuga** 🟢 — già scritta (`doppia_fuga.md`): è la voce "uscite" di questo bilancio,
  scomposta per genere e per età.
- **La platea del 2035** 🟢 — pura aritmetica sulle età singole: i residenti 5-14 di oggi
  sono il tetto massimo dei 15-24 fra dieci anni (al netto delle migrazioni, che finora
  sottraggono). Nessuna proiezione, nessun modello: un conteggio, con l'onestà di dire che
  è un tetto e non una previsione. Dimensiona la platea su cui qualunque policy agirà.
  ✔ Sviluppata il 2026-08-26 in `notebooks/genere.ipynb` («Il bilancio dei giovani»):
  ragazze -15.5% al 2034 contro -5.8% dei ragazzi, con l'**audit della sex ratio 5-14**
  (117 M per 100 F, anomalia post-2011, meccanismo aperto) come sezione gemella.
- **Chi arriva: la componente straniera** 🟢 — `SETA_1` ha `CITIZENSHIP` (`ITL`/`FRGAPO`)
  incrociata con età singola e genere: la popolazione straniera giovane compensa in parte
  le uscite? A Bagheria, quanto? (⚠️ nelle tavole lavoro la cittadinanza è solo `TOTAL` —
  vicolo cieco già verificato: la componente straniera si conta in demografia, non se ne
  misura l'occupazione comunale.) Contesto anche negli `S1`-`S10` del 2011.
  ✔ Sviluppata il 2026-08-26 («La componente straniera»): 1.6% del 15-34 (195 persone)
  contro 12.4% Italia; 2021-2024: -350 italiani, +37 stranieri. Il ricambio non c'è.
- **La piramide a confronto** 🟢 — struttura per età completa di Bagheria vs benchmark,
  2021-2024: dove la piramide di Bagheria si scava rispetto a Palermo, e per quale genere.

## Cosa dicono già i dati

- 15-34: 12.174 (2021) → 11.861 (2024), −2.6%; M 6.015 / F 5.846 al 2024.
- Coorti: già calcolate per genere (`genere_coorti.csv`).
- ⚠️ Su `SETA_1` il 2018 è risultato vuoto per Bagheria con `CITIZENSHIP=TOTAL` (nota in
  `sources.md`): la serie demografica utile parte dal 2019/2021 a seconda del taglio —
  verificare in pipeline, non assumere.

## Rischi e limiti

🔴 Niente proiezioni demografiche vere (fecondità, migrazioni future): sarebbe un modello
non richiesto e indifendibile in hackathon. La "platea del 2035" resta un conteggio di nati,
dichiarato come tetto.
🔴 I movimenti anagrafici (iscrizioni/cancellazioni) spiegherebbero il saldo per causa, ma
sono un'altra fonte ISTAT non censita in `sources.md`: se qualcuno la vuole, è un task
"nuova fonte" da proporre prima.

## Verso la proposal

Questo parent non genera un intervento proprio: genera **la sezione di dimensionamento**
della proposal — platea attuale, tendenza, platea futura già nata — e il vincolo temporale
("ogni anno di ritardo la platea si riduce di ~100 persone" *se il numero regge dalla
cella*, mai hardcodato).

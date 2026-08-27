# CONTEXT — Ale (focus genere)

Stato del thread genere al 2026-08-26. Le regole condivise stanno in `CLAUDE.md`; qui solo
ciò che riguarda questo thread. Ogni numero citato si rigenera da una cella di
`notebooks/genere.ipynb` — mai copiarlo a mano nella proposal.

## Stato
`notebooks/genere.ipynb` gira top-to-bottom (sensore nbconvert ok, 2026-08-25) e contiene,
in ordine: verifica di fattibilità degli incroci, serie e gap occupazionale 15-24 con CI
(Wilson/Newcombe), doppia scala (punti e rapporto M/F), LPM (GLM binomiale link identità)
sull'eccesso di gap **e sui livelli femminili** vs benchmark, trend OLS 2018-2024, decomposizione della popolazione
per stato, scissione delle casalinghe, **bounds per età sulle casalinghe**, **stato civile per
età (le casalinghe sono nubili, fonte DCIS_POPRES1)**, gap istruzione 9-24, verifica di composizione per età, quadro di sintesi, **quadrante per genere** (con
export per le figure 5 e 6), gap in persone, **potenza statistica e MDE dei KPI**,
ritenzione di coorte per genere 2021-2024, **profilo di ritenzione per età singola +
gruppo invisibile scisso per genere**, **transizioni annuali (robustezza della
finestra 22-25)**, **bilancio dei giovani (platea 2029/2034 per genere)**, **audit
della sex ratio 5-14**, **componente straniera nel 15-34**, contesto storico 2011,
mappa siciliana,
**su 1.000 ragazze** (istruzione e lavoro sulla stessa fascia: estrazione 15-24 dalla
tavola 9-24 con assert di coerenza sulle età singole, bound 18-24), **gap
delle madri** (tre censimenti, valori + percentili sui 390), **gemelle di Bagheria**
(matching strutturale con robustezza) e relativo **export del posizionamento** (quartili
del gruppo + percentile regionale + `verso` per indicatore, per fig08),
**nuvola dei 390** (I1 × L11), **formazione
familiare precoce** (F4-F7), **trend paralleli** (verifica pre-periodo del disegno DiD),
**il ponte fra i due censimenti** (indicatori 15+ ricostruiti dal permanente 2018-2024:
coerenza fra le due rilevazioni, percentili sui 390 fino al 2024, gemelle 2018-2024),
**i claim reggono al 2024?** (persistenza della graduatoria dei 390 comuni con rho di
Spearman, ritenzione di coorte a scala decennale dalle classi quinquennali, forbice
ripetuta su tutte le annate disponibili),
sintesi finale in 13 sezioni con finestre di lettura dei KPI.
Ogni sezione si apre con una riga `📌 Risultato chiave`; la «Sintesi finale» le ricompone
e le traduce nel template della proposal (evidenza → target → KPI → finestra di lettura).

**Verifica indipendente** (2026-08-26): `uv run python -m pipeline.verifica` — 521
controlli che ricalcolano ogni numero chiave direttamente da `data/raw/` con
implementazioni alternative (Wilson/Newcombe riscritte, LPM saturo in forma analitica,
IRLS per il GLM a link identità, arcoseno per MDE/potenza, matching Mahalanobis rifatto, tassi 15+ ricalcolati dai 12 blocchi dei 390 comuni,
Spearman come Pearson sui ranghi, ritenzione di coorte rifatta dal raw delle classi
quinquennali, platea/sex ratio/stranieri/transizioni dalle età singole e dalle classi,
stato civile dal raw POPRES coi codici sesso legacy):
**521/521 PASS**; output salvati identici alla riesecuzione (diff nullo), CSV rigenerati
byte-identici. È il pin di regressione del thread: se i raw cambiano deve fallire finché
notebook e attesi non vengono riallineati.

## Risultati chiave
- Gap occupazionale 2024: 8.3 punti [CI 6.6-10.0]. In punti **non è un'anomalia locale**
  (pooled 2022-24: +1.1 vs Palermo p=0.03, -1.8/-1.9 vs Sicilia/Italia p<0.001); in
  **rapporto** Bagheria è la peggiore del panel (M/F = 2.01 contro 1.56 nazionale).
  Il tratto locale è il livello: tasso femminile 8.2%, il minimo dei quattro territori.
  Il **livello è testato** (effetti principali dello stesso LPM): Bagheria sotto Palermo
  di 1.2 pp, sotto Sicilia di 1.9, sotto Italia di 8.9 (p ≤ 0.0001 pooled 2022-24;
  p ≤ 0.009 anche sul solo 2024); Wilson 2024 sul tasso F: [7.2-9.2]. Cautela sul
  rapporto: verso la Sicilia lo scarto (2.01 vs 1.95) è nel rumore e nel 2023 l'ordine
  si invertiva — robusto verso Palermo e Italia.
- Il 13.4% delle ragazze 15-24 si dichiara **casalinga** (387 persone) contro il 4.6%
  nazionale; serie 2018-2024 stabile. **Bounds per età**: fra il 18.8% delle 18-24enni
  (nessuna minorenne) e il 25.8% delle 20-24enni; eccesso sull'incidenza italiana: 254.
- **Misurabilità dei KPI (MDE)**: "+40 occupate" = +1.40 pp, sotto l'MDE della lettura
  annuale (2.14 pp; potenza 46%). Su **trienni pooled** potenza 90% (casalinghe: 99%).
  I KPI primari si valutano su trienni; la lettura annuale spetta a indicatori di
  processo (utenza per età e genere) che oggi nessuno rileva.
- Ritenzione: i ragazzi si perdono presto (due onde: età 17-19 e 23-24, con **rientri
  netti dopo i 26**), le ragazze **dalle età 24-25 in poi** (96.7-97.9 contro ~103
  Italia sulle età 25-29), senza rientri. Finestra utile per un intervento: 22-25 anni.
- Il **"19% invisibile"** (fuori da lavoro, studio e ricerca) è di entrambi i generi:
  573 F + 549 M (51% F). Di genere è l'etichetta: 387 casalinghe contro 50; 183 contro
  485 in "altra condizione". Corregge `idee/doppia_fuga.md` e `idee/04`.
- **Gemelle di Bagheria** (matching Mahalanobis 2011 su dimensione, densità, età,
  stranieri, abitazioni, distanza da Palermo — mai su esiti; robustezza 8/10 z-score,
  6/10 PCA, LOVO ≥7/10): Santa Flavia, Capaci, Misilmeri, Altofonte, Trabia, Terrasini,
  Termini Imerese, Erice, Porto Empedocle, Sciacca. Dentro il gruppo Bagheria è nella
  norma su NEET e occupazione F (lo svantaggio è di fascia territoriale) ma estrema su:
  differenziale educativo pro-F (1/10 sotto), disoccupazione F (8/10 sotto), autonomia
  giovanile F4 (nessuna sotto), mobilità M2 (2/10 sotto).
- **Gap delle madri** (1991→2011, 15+): partecipazione F dal 8° al 32° percentile
  (20.6→28.7) ma occupazione F scivolata al **12°** e disoccupazione F al **95°**;
  I1 sotto la parità (98.9) già nel 2011, unico territorio del panel. Su L11 Bagheria
  era identica alle gemelle nel 1991 e 2001, **si stacca nel decennio 2001-2011**
  (18.1 contro 19.8): il muro precede il censimento permanente ed è recente, non eterno.
- **Il ponte fra i due censimenti** (nuovo, 2026-08-25): la classe `Y_GE15` del censimento
  permanente ricostruisce L2/L11/L10/L7 con le definizioni esatte del codebook 8milaCensus,
  quindi il lungo periodo arriva al **2024** invece che al 2011. Tre risultati.
  *(a) Coerenza fra rilevazioni diverse*: sul tasso di occupazione femminile 15+ il decennale
  2011 e il permanente 2018 danno 18.1 e 18.8 a Bagheria, scarto entro ±1 pp anche su
  Palermo, Sicilia e Italia — il livello non è un artefatto del disegno di rilevazione. **Non
  vale per L7 e L2**: dentro il permanente, fra 2019 e 2021, la disoccupazione F crolla di
  15.5 pp a Bagheria e 4.5 in Italia (cambio di misura di "in cerca di occupazione"). In
  figura si estendono L11 e L10; L2 e L7 solo con la rottura marcata.
  *(b) Percentili sui 390*: occupazione F 12° (2011) → **8° (2018)** → **17° (2024)**;
  occupazione M 15° → **30°**; partecipazione F 32° → **17°**. La lettura del 2011 — "un
  mercato ristretto per tutti" — al 2024 non regge: gli uomini recuperano, le donne no.
  *(c) Gemelle*: Bagheria sotto la mediana del gruppo in **tutti** gli anni 2018-2024, di
  2.1-3.1 pp, contro -1.7 del 2011. Lo stacco aperto nel decennio 2001-2011 **non si è
  chiuso**, e il pre-periodo del DiD adesso è misurato e non assunto.
- **Nuvola dei 390** (2011): Spearman I1 × L11 = -0.24 (p<0.001) — dove le donne sono
  relativamente più istruite l'occupazione femminile di solito è più alta; Bagheria
  contraddice il pattern (correlazione ecologica: orienta, non dimostra).
- **Famiglia** (2011): giovani soli (F4 = 3.6%) al 3° percentile siciliano e ultimo
  anche fra le gemelle; coppie giovani con figli (F7 = 11.7%) all'81° dei 390 ma nella
  mediana delle gemelle — tratto di fascia costiera, non anomalia locale.
- **Trend paralleli** (pre-periodo del DiD): pendenza F 2018-2024 di Bagheria +0.65
  pp/anno, indistinguibile da Palermo e Italia (p=0.29/0.33; Sicilia al margine 0.054).
  Controfattuale dichiarato in anticipo: **Palermo**; gemelle come ancora dei target.
- Il tasso di disoccupazione femminile poggia su 430-680 persone: declassato a misura
  non conclusiva, si usano occupazione e composizione.

- **I claim reggono al 2024** (verifica del 2026-08-25, senza nuovi download). Tre esiti
  distinti. *Posizionamento*: la graduatoria dei 390 comuni del 2011 predice quella del
  2024 con **rho di Spearman 0.848** (0.919 dentro il solo permanente, 2018 vs 2024) e il
  **74%** del quintile più basso del 2011 è ancora lì, Bagheria compresa — il claim del
  2011 non era una fotografia scaduta ma una previsione verificata. Il livello va
  aggiornato: 18.1% → **23.7%**, dal 12° al **17° percentile**, mentre la mediana regionale
  sale da 23.6% a 28.3%: *nel 2024 Bagheria arriva dove stava la mediana siciliana nel
  2011*. *Fuga*: sulla coorte 15-19 seguita per dieci anni Bagheria passa da **102.9%
  (2001-2011) a 88.6% (2011-2021)** sulle femmine e da 98.4% a **83.9%** sui maschi, ~14
  punti di ribaltamento, e nel secondo decennio sta sotto Palermo sui maschi — la frattura
  demografica cade nello stesso decennio del muro sul lavoro di fig10, da un dato
  indipendente. I controlli interni al permanente (2018-2023, 2019-2024) la ritrovano sulla
  transizione 20-24 → 25-29, dove il profilo per età singola colloca la finestra 22-25.
  *Forbice*: il tasso di occupazione femminile 15-24 di Bagheria è il minimo del panel in
  **6 anni su 6**, il vantaggio educativo passa da +3.1 a +4.2 mentre il vicinato crolla da
  +2.9 a +0.5, ma il **rapporto M/F oscilla** (2.47 → 1.89 nel 2023 → 2.01) e mette
  Bagheria in testa solo in 4 anni su 6. Il claim da portare nella proposal è il **livello
  femminile**, non il rapporto. Dettaglio e cautele in `docs/sources.md` sezione 8.
- **Il bilancio dei giovani** (nuovo, 2026-08-26). *Platea*: chi avrà 15-24 anni nel
  2029/2034 è già nato — le ragazze passano da 2.882 a 2.651 (-8.0%) e **2.435
  (-15.5%)**, i ragazzi -2.5% e -5.8%; nei benchmark il calo è simmetrico fra i generi.
  I KPI in teste si riparametrano sulla platea corrente; il conteggio è un tetto.
  *Audit*: l'asimmetria viene dalla **sex ratio 5-14** — 117 M per 100 F al 2024 contro
  il 104-106 dei benchmark, nella norma fino al 2011 (z +0.4) e in salita da allora
  (z +3.5; identica su due tavole indipendenti; tutta nella popolazione italiana).
  Meccanismo aperto: si cita solo insieme all'audit; i check decisivi (nati per sesso,
  gemelle sulle classi) sono fetch 🟡. *Ricambio*: stranieri all'**1.6% del 15-34**
  (195 persone) contro 5.1% Palermo / 6.4% Sicilia / 12.4% Italia; 2021-2024: -350
  italiani (di cui **-219 F**), +37 stranieri. La fuga è al netto di niente.
- **Le casalinghe sono nubili** (nuovo, 2026-08-26, fonte DCIS_POPRES1 — sources.md §9):
  già coniugate 15-24 al 1.1.2025 = **41 (1.4%)** contro 387 casalinghe → **almeno
  l'89% è nubile**; quota coniugate 20-24 di Bagheria (2.7%) *sotto* Palermo (3.2%) e
  Sicilia (2.9%), matrimonio under-25 in caduta ovunque (6.1% → 2.7% dal 2019). I
  denominatori delle due fonti coincidono alla singola unità (2.882 = 2.882). Il canale
  non è il matrimonio precoce ma la famiglia d'origine: servizio di **attivazione**,
  non solo conciliazione. Limite: lo stato civile non osserva convivenze né maternità.
- **La finestra 22-25 è una lettura pooled**: le transizioni annuali oscillano fino a
  8 pp sulla stessa età (24enni F: 100.7 / 104.5 / 96.5; n≈290 per cella) contro
  ±0.8 pp di solo rumore di conteggio e un'Italia ferma in 100.7-101.3; 5 celle su 12
  sotto quota 100. Il claim si titola sul triennio, l'anno singolo è un controllo.

## Export per R (`data/processed/`)
`genere_gap_occupazione.csv`, `genere_gap_occupazione_ci.csv` (bande di confidenza),
`genere_istruzione.csv`, `genere_quadro_sintesi.csv`, `genere_composizione_stato.csv`,
`genere_composizione_stato_dettaglio.csv`, `genere_casalinghe.csv`,
`genere_casalinghe_bounds.csv`, `genere_coorti.csv`, `genere_ritenzione_eta.csv`
(profilo per età singola), `genere_gap_persone.csv`, `genere_mde.csv` (potenza/finestre),
`genere_quadrante.csv` + `genere_forbice.csv` (alimentano fig05/fig06),
`genere_gap_madri.csv`, `genere_gemelle.csv` (anagrafica del gruppo di controllo),
`genere_nuvola_390.csv` (con flag gemelle), `genere_famiglia_precoce.csv`,
`genere_pretrend.csv` + `genere_pretrend_gemelle.csv`, `genere_mappa_*.csv`,
`genere_base_persone.csv` (denominatore e occupate 2024, alimenta fig09),
`genere_per_1000.csv` (diploma e lavoro sulla stessa fascia 15-24 + bound 18-24, 2021-2024,
alimenta fig11),
`genere_coerenza_fonti.csv` (decennale 2011 vs permanente 2018 + salto 2019-2021),
`genere_madri_recente.csv` + `genere_pretrend_gemelle_recente.csv` (i gemelli 2018-2024 di
`genere_gap_madri.csv` e `genere_pretrend_gemelle.csv`, alimentano fig10),
`genere_distribuzione_390.csv` + `genere_mappa_2011_2024.csv` (fig04: distribuzione per
anno con rho e persistenza del quintile; i 390 comuni alle due annate con ruolo di
etichettatura), `genere_ritenzione_decennale.csv` (fig07: ritenzione di coorte per tutte le
classi e i quattro periodi), `genere_forbice_serie.csv` (fig05: le tre misure per 5
territori × 6 anni — fotografia e serie nella stessa tabella),
`genere_posizionamento.csv` (alimenta fig08: min/q1/mediana/q3/max delle gemelle,
`gemelle_sotto`, `percentile_390`, più la colonna `verso` — +1 alto è meglio, -1 alto è
peggio, 0 descrittivo — che è l'unica scelta interpretativa e sta nel notebook, non in R),
`genere_ritenzione_transizioni.csv` (le tre transizioni annuali per età 15-30, 4 territori),
`genere_platea.csv` (15-24 del 2024 e platea 2029/2034 per genere),
`genere_sex_ratio_5_14.csv` (M per 100 F, 2001-2024, dalle classi quinquennali),
`genere_stranieri.csv` (15-34 per cittadinanza e genere, 2021-2024),
`genere_stato_civile.csv` (già coniugate per fascia 15-24/18-24/20-24, 1.1.2019-1.1.2025).

## Figure (R)
`Rscript viz/build_all.R` rigenera tutto in `figures/` (PNG 300dpi + SVG). Tema e palette
condivisi in `viz/theme.R`: Bagheria in vermiglio, genere in arancio/verde, Okabe-Ito.
- `fig01_gap_due_scale` — gap 15-24 nelle due scale (punti con IC 95% | rapporto M/F).
- `fig02_composizione_stato` — popolazione 15-24 per sei stati (casalinghe 13.4% vs 1.7%).
- `fig03_coorti` — dumbbell F/M della ritenzione di coorte.
- `fig04_mappa_sicilia` — coropleta dei 390 comuni al **2024** (legenda dentro il pannello,
  a nord-ovest: fuori rubava altezza alla carta) + istogramma con le due distribuzioni
  sovrapposte (2024 pieno, 2011 a profilo) + scatter percentile 2011 × percentile 2024 con
  rho di Spearman e quadrato del quintile basso. Il titolo è «nel 2024 Bagheria arriva dove
  stava la mediana siciliana nel 2011».
- `fig05_forbice` — vantaggio educativo (pp, 9-24) | svantaggio occupazionale (rapporto
  M/F, 15-24) al 2024, più una **striscia con le sei annate** sulle stesse tre misure e il
  conteggio degli anni in cui Bagheria è all'estremo. L'occupazione è in rapporto, non in
  punti, per coerenza con la sezione LPM. Il claim del sottotitolo è stato spostato dal
  rapporto (che oscilla) al livello femminile (minimo del panel ogni anno): la fotografia
  di un anno solo non reggeva la formula «prima in entrambe le classifiche sbagliate».
- `fig06_quadrante` — quadrante per genere 2024 (frecce M→F) | nuvola dei 390 comuni
  2011 con gemelle evidenziate. Pannelli affiancati ed etichettati, mai uniti: fasce e
  fonti diverse.
- `fig07_ritenzione_eta` — profilo di ritenzione 2021-2024 per età singola (femmine |
  maschi, quattro territori + vicinato): finestra utile 22-25 evidenziata, onde maschili
  con rientri dopo i 26. Sotto, lo **slope chart dei due decenni** (2001-2011 vs 2011-2021,
  coorte 15-19 dalle classi quinquennali): risponde all'obiezione che tre anni di dati non
  bastano a chiamarla fuga. Il decennio 2011-2021 unisce due rilevazioni, dichiarato in
  caption con l'argomento sul verso prudente della distorsione.
- `fig08_posizionamento` — la **terza lente di confronto**: Bagheria dentro le 10 gemelle
  strutturali | dentro i 390 comuni. Serve a separare lo svantaggio di fascia territoriale
  (NEET e occupazione F: nella norma fra i pari ma all'87° e al 12° percentile regionale)
  da quello che è di Bagheria (giovani soli 0/10, differenziale educativo 1/10, mobilità
  2/10). Si colora **solo** dove Bagheria esce dalla metà centrale del riferimento —
  interquartile delle gemelle a sinistra, 25°-75° percentile a destra — così un 3/10 non
  diventa un'affermazione categorica; il giudizio è calcolato **per pannello**, sul dato
  che quel pannello mostra. Dal 2026-08-26 i tre colori hanno una **legenda in figura**
  (prima la chiave stava nel sottotitolo, che si legge una volta e poi non si ritrova più
  mentre si guarda il grafico). Tutto 2011/8milaCensus, mai in serie con il 2018-2024.
- `fig09_kpi_finestra` — il KPI della proposal e la sua misurabilità: waffle delle 2.882
  ragazze (un quadratino = 10) con i tre scenari in persone | MDE all'80% di potenza per
  ampiezza della finestra, con la soglia del delta da rilevare. È la figura che dichiara
  in anticipo **quando** si potrà dire se l'intervento ha funzionato.
- `fig10_muro_recente` — il lungo periodo **fino al 2024**: percentili di Bagheria sui 390 |
  L11 contro la banda interquartile delle gemelle, entrambi in due blocchi (censimenti
  1991-2011 e permanente 2018-2024) separati da una banda grigia che nessuna linea
  attraversa. Il differenziale educativo M/F non è in figura: esiste solo fino al 2011
  (8milaCensus lo calcola su 6+, il permanente non ha una classe 15+ sull'istruzione) e una
  linea che muore a metà pannello confonde — resta in caption. Il punto per la proposal: il
  divario è **databile e non si richiude da solo**.
  L'asse del tempo **non è in scala** (dal 2026-08-26): il tratto 1991-2011 è compresso
  ~3,3:1 e il 2018-2024 dilatato 1,2:1, perché venti anni con tre rilevazioni si prendevano
  due terzi della larghezza e i sei anni con sei rilevazioni si schiacciavano contro il
  bordo. Si può fare solo perché le due epoche non sono già una serie unica: nessuna linea
  attraversa lo stacco, quindi non c'è una pendenza continua da falsare. Le pendenze restano
  confrontabili **dentro** ciascuna epoca, non fra le due, e la caption lo dichiara.
- `fig11_per_1000` — istruzione e lavoro **sulla stessa fascia**: su 1.000 ragazze 15-24,
  510 diplomate e 82 al lavoro (coetanei: 462 e 165); barre parallele sulla stessa base,
  **mai** stadi di un funnel (l'incrocio titolo × condizione non esiste a livello comunale
  e gli insiemi non sono annidati) | attainment 18-24 come bound superiore. Attenzione ai
  claim: sul 18-24 il primato del vantaggio educativo **non regge** (Bagheria +5,7,
  Sicilia +7,1, Italia +6,2) — usare il distacco dal vicinato (+5,7 contro +2,5) e la
  mancata conversione, non il primato assoluto; la nota è in sintesi finale.

Tipografia: Lato dove installato (fallback al sans di sistema) e numeri all'italiana
via `virgola()` — entrambi in `viz/theme.R`, nessuno stile inline.

Palette (rivista 2026-08-26). **Il genere prende blu (M `#0072B2`) e rosa (F `#CC79A7`)**
su decisione del team: lettura immediata senza legenda. La coppia resta Okabe-Ito, quindi
distinguibile in protanopia e deuteranopia — cambia la convenzione, non il requisito.
Di conseguenza nessun territorio può più indossare quei due colori: **Palermo passa a
`#785EF0`** (viola) e **Sicilia a `#E69F00`** (ambra); il rosa e il viola escono da
`PALETTE_VICINI`, che diventa sky/ambra/verde/marrone/nero (tocca solo fig06, dove Sicilia
non compare). Il vicinato resta `#1B9E8F` (era `#44AA99`, sotto il chroma floor).

Il costo, misurato: **l'ambra di Sicilia sta a 2,25:1 di contrasto sul bianco**, sotto la
soglia di 3:1 — peggio del 2,98 che aveva il rosa. Non è aggirabile scurendola: a parità
di separazione serve un'ocra tipo `#B8860B`, che passa il contrasto (3,25) ma crolla a
ΔE 5,0 contro il vermiglio di Bagheria in visione dicromatica, cioè diventa la stessa
linea. Una griglia HSL completa (contrasto ≥ 3 e ΔE ≥ 15 contro le altre quattro serie)
non restituisce nessun colore fuori dal blu-viola: con blu e rosa impegnati dal genere, i
cinque territori non stanno tutti sopra soglia. Si tiene l'ambra, che almeno conserva la
separazione CVD (ΔE 17,6 contro Bagheria), e la si copre come già si faceva con il rosa:
etichette dirette o legenda in ogni figura che la usa. Le alternative scartate sono il
nero (passa tutto, ma pesa più di Bagheria in fig01 dove le linee hanno lo stesso spessore)
e la rinuncia al blu/rosa sul genere.
`DIVERGENTE` (vermiglio ↔ grigio ↔ blu) è la scala di polarità di fig08, ora con legenda
in figura invece della spiegazione nel sottotitolo.

Tipografia: tre livelli, una sola famiglia — titolo della figura (`tema_figura()`, corpo
1,45 e nero), sottotitolo (testo normale grigio), titolo di pannello (`tema_datapolis()`,
bold grigio scuro). Niente secondo font: solo Lato ha un fallback verificato e i device
cairo convertono comunque il testo in tracciati nell'SVG.

## Aperture
- `pipeline/stats.py` condiviso (Wilson/Newcombe/LPM): decisione di team, per ora le
  funzioni vivono nelle celle del notebook.
- Fetch possibili ma non pianificati (decisione di team, "nuova fonte"): stato civile ×
  età via SDMX (per legare bounds casalinghe e matrimoni precoci).
  ✔ Fatto il 2026-08-26 via `DCIS_POPRES1` (il permanente non lo incrocia nemmeno con
  chiave esplicita, NoRecordsFound: sources.md §9). Risposta netta: le casalinghe sono
  nubili (≥89%), il matrimonio precoce è escluso come canale. Restano 🟡 da decidere:
  nati per sesso del comune (demo.istat) e classi quinquennali delle gemelle — i due
  check che chiuderebbero l'anomalia della sex ratio 5-14.
  ✔ Fatto il 2026-08-25: censimento permanente per le dieci gemelle (il DiD 2018-2024 ha
  adesso il suo pre-periodo) e per i 390 comuni siciliani sulla classe 15+.
- `censpop_demografia_classi_long.csv` (classi quinquennali, **2001, 2011 e 2018-2024**,
  l'unica tavola comunale che attraversa i due censimenti) è **usata dal 2026-08-25** per la
  ritenzione di coorte decennale di fig07. Resta inesplorato il pezzo che interessa gli
  altri thread: le classi Y15-19...Y30-34 ricompongono il **15-34 esatto** e allungano al
  2001 la serie demografica del target — materia per il thread mobilità/demografia.
  Endpoint e trappole in `docs/sources.md` sezione 7, letture in sezione 8.
- Richieste agli altri thread: in `CONTEXT-fabio.md` (dimensione sesso nel pendolarismo)
  e `CONTEXT-saverio.md` (incrocio titolo × condizione per genere a livello regionale).
- `doppia_fuga.md` e `04_il_19_percento_invisibile.md` aggiornate (2026-08-25) al
  risultato sul gruppo invisibile e alla finestra 22-25; resta stale il grafo mermaid
  di `idee/README.md` (non contiene le idee 00-04).

# CONTEXT — thread Mobilità

> **Passaggio di consegne, 2026-08-29.** Il thread era di Fabio, che ha lasciato l'hackathon.
> È stato ripreso e chiuso: notebook `notebooks/mobilita.ipynb`, quattro figure `mob_fig01`-`04`,
> fonte nuova documentata in `docs/sources.md` §12. Il file resta con questo nome perché
> `CLAUDE.md` ci punta. Sotto: cosa è cambiato rispetto al piano originale, cosa il thread
> produce e cosa chiede agli altri due.

Le regole condivise stanno in `CLAUDE.md`.

## Il ribaltamento del vincolo: la destinazione esiste

La relazione dichiara due volte — §5 e §9 — che «nessuna fonte disponibile identifica Palermo
come destinazione». **Era vero per le fonti allora usate, non in generale.** ISTAT pubblica le
*matrici del pendolarismo*: origine-destinazione comune per comune, con sesso, motivo, mezzo,
fascia oraria e durata (censimenti 1991/2001/2011) e, per il solo lavoro, rifatta sul
censimento permanente 2021. Endpoint, tracciati e trappole in `docs/sources.md` §12.

**Corretti il 2026-08-29**: `RELAZIONE_DATAPOLIS.md` (sezione 5 riscritta in cinque
sottosezioni, §9 punto 3, tabella di copertura del brief, §7.0, §8, appendice) e
`docs/RELAZIONE.md` (terna delle figure, mappa brief, limite 3, checklist). Il terzo focus
del bando — «Dinamiche e ruolo del pendolarismo verso Palermo» — è misurabile e misurato.
Resta da rigenerare `docs/RELAZIONE_DATAPOLIS.docx`, fermo alla versione precedente.

## Verificato sui dati (2026-08-29)

- **Il pendolarismo di Bagheria è pendolarismo verso Palermo.** Fra chi esce dal comune:
  **91,1%** per studio (2011) e **67,5%** per lavoro (2011), **65,1%** nel 2021. Il secondo
  comune di destinazione è Santa Flavia al 6,8%: non esiste una seconda direzione. Su tutte
  e tre le misure Bagheria è oltre il **90° percentile** dei 381 comuni non capoluogo per
  quota diretta al proprio capoluogo.
- **«Bagheria si muove poco» è una lettura sbagliata di un numero giusto.** `M2` al 25°
  percentile è esatto, ma fuori comune si va per mancanza di lavoro dentro e Bagheria è il
  comune più grande della corona di Palermo (12.000 pendolari contro i 3.000 di Ficarazzi).
  A parità di distanza dal capoluogo e di dimensione il residuo è **−1,9 punti** (z = −0,13):
  dal 36° percentile grezzo al 48° del residuo. La particolarità non è **quanto** si muove.
- **Il ribaltamento è il risultato del thread.** Quota che esce dal comune, scarto F−M, 2011,
  conteggio esaustivo: **+2,6 punti** per studio (le ragazze escono più dei coetanei),
  **−12,1** per lavoro. Il salto vale **14,7 punti** contro 6,0 in Sicilia, 6,5 in Italia,
  1,9 nel Comune di Palermo. Sul lavoro Bagheria è al **13° percentile** dei 381 comuni non
  capoluogo (15° sui 390).
  **Replica** sul censimento permanente 2018-2019, fonte e metodo diversi: +11,3 e +10,9
  contro +5,6 siciliano. Regge al controllo per tasso di occupazione femminile (`L11`) e per
  divario occupazionale: il residuo passa da −8,7 a −7,0 punti.
- **Il treno è il canale femminile, e non è sottoutilizzato.** Fra chi esce da Bagheria il
  treno vale il **31,5%** degli spostamenti delle donne e il **16,4%** di quelli degli
  uomini (mezzo collettivo 34,7% contro 18,9%; mezzo privato 63,7% contro 79,0%). Il comune
  nel complesso è al **97°-98° percentile siciliano** per uso del treno. Una proposta del
  tipo «portare il treno a Bagheria» risolverebbe un problema che non c'è.
- **Le donne partono più tardi e viaggiano più a lungo.** Verso Palermo per lavoro esce
  prima delle 7:15 il **65,0% degli uomini** e il **54,4% delle donne**; il 43,8% delle donne
  impiega 31-60 minuti contro il 36,1% degli uomini, per 17 km. Sullo studio la differenza
  quasi scompare: **la divergenza oraria nasce col lavoro.**

## Risultato negativo, da non dimenticare

L'ipotesi «più mezzo collettivo, meno divario di genere» **è stata testata sui 390 comuni e
non regge**: Spearman −0,10 (p = 0,06), segno sbagliato, e il quartile con più mezzo
collettivo ha il divario più ampio. Sul treno l'associazione è nulla (p = 0,29).
**Conseguenza: il vincolo non è l'offerta di trasporto**, e nessuna proposta può appoggiarcisi.
Sta in `notebooks/mobilita.ipynb` §7 apposta.

Coerente: l'ultimo miglio a Palermo non è un collo di bottiglia. Dal GTFS AMAT del Comune di
Palermo, le fermate «Stazione Centrale» hanno 18 linee e ~125-130 passaggi l'ora dalle 7 alle
21 (feed di agosto, cioè servizio estivo ridotto: a settembre sarebbe di più).

## Cosa il thread NON può dire

1. **Nessuna età**: né la matrice né il censimento permanente hanno la dimensione. Il target
   15-34 non è isolabile sul pendolarismo. Il motivo è un'informazione d'età parziale — chi
   esce per studio è quasi solo secondaria superiore e università.
2. **Nessun livello in serie 2011→2021**: definizioni diverse (giornaliero contro almeno tre
   giorni a settimana), 2021 solo lavoro e senza sesso. Si confronta la composizione.
3. **Nessun dato sul rientro**: si conosce solo l'orario di uscita di casa. L'ipotesi del
   carico di cura resta un'ipotesi.
4. **Nessuna causalità**: i confronti fra comuni sono ecologici, e l'`R²` dei modelli sui
   divari di genere è vicino a zero.

## Interfaccia (`data/processed/`)

Dalla pipeline: `pendolarismo_od_long.csv`, `pendolarismo_mezzo_long.csv`,
`pendolarismo_benchmark_long.csv`, `pendolarismo_mezzi.csv`.
Dal notebook, per le figure: `mob_flussi_bagheria.csv`, `mob_ribaltamento.csv`,
`mob_ribaltamento_territori.csv`, `mob_ribaltamento_390.csv`, `mob_mezzo_genere.csv`,
`mob_orario_genere.csv`, `mob_treno_390.csv`, `mob_taglia_distanza.csv`,
`mob_curva_attesa.csv`, `mob_sintesi.csv`.

`mob_sintesi.csv` è la tavola che la proposal cita: otto misure con la nota di cautela accanto.

## Aggancio con gli altri due thread

Il ribaltamento cade esattamente dove cadono gli altri due risultati.

- **Genere**: `genere_coorti.csv` mostra che Bagheria perde le donne a 25-29 (ritenzione 96,3,
  unica cella femminile negativa dei quattro territori). È lo stesso passaggio in cui la
  mobilità femminile si spegne — da una terza fonte che non condivide né tavola né denominatore.
- **Educazione**: le ragazze arrivano al diploma +4,2 punti più dei coetanei e hanno il tasso
  di occupazione più basso dei quattro territori. Il thread mobilità aggiunge che **non è un
  problema di raggiungibilità**: Palermo è raggiunta, e da loro più che dagli uomini.
- **Bersaglio in persone**: portare le pendolari di Bagheria al divario *medio siciliano* — non
  alla parità — vale **+279 donne** che lavorano fuori comune; la parità piena 449. Stesso
  ordine di grandezza degli scenari occupazionali del thread genere (+239 e +262), su misure
  che non condividono denominatore.

## Conseguenza per «Ponte 19»

La proposta unificata (`docs/POLICY_PONTE_19.md`) regge e **si rafforza**: la sua finestra B
(22-25, mancata conversione) è esattamente il punto in cui la mobilità femminile si spegne.
Quello che il thread mobilità aggiunge è un vincolo di progettazione: **l'intervento
infrastrutturale è escluso dai dati**, quindi la leva è la transizione, non il collegamento.
E un aggancio operativo: per le donne di Bagheria il canale verso Palermo è il mezzo
collettivo, per gli uomini è l'auto — un servizio che dia per scontata l'auto è un servizio
che seleziona per genere.

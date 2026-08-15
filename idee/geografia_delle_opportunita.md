# [PARENT] La geografia delle opportunità — il problema di Bagheria è *dove* sta?

> Bagheria è a mezz'ora dal mercato del lavoro più grande della Sicilia occidentale.
> Se la vicinanza non si converte in opportunità, la distanza non è geografica: è di accesso.

## Il frame

`talent_trap.md` chiede se Bagheria converta istruzione in lavoro. Questo parent chiede la
cosa complementare: se Bagheria converta **prossimità** in lavoro. Un comune di cintura
metropolitana non deve necessariamente generare occupazione qualificata dentro i propri
confini — può funzionare da residenza connessa a un mercato più grande. La diagnosi cambia
tutto: se Bagheria fallisce *come mercato locale* la policy è sulle imprese; se fallisce
*come nodo di accesso* la policy è su mobilità, orari, connessione.

L'aggancio col genere è già nei dati: dove ci si muove di più, le donne lavorano di più
(Spearman +0.32 su 390 comuni fra mobilità fuori comune `M2` e occupazione femminile `L11`,
2011 — correlazione ecologica, orienta e non dimostra). E Bagheria è al **25° percentile**
regionale per mobilità fuori comune: si esce poco. L'ipotesi da scrutinare è che
l'immobilità sia essa stessa **di genere** — che il pendolarismo verso Palermo sia
un'opzione praticata dai ragazzi e negata di fatto alle ragazze.

## Perché è un parent

Genera figlie indipendenti tra loro, ognuna con dati propri; tiene insieme il thread
mobilità (Fabio) e il thread genere senza che uno sia appendice dell'altro; e apre una
famiglia di policy (trasporto, lavoro ibrido, connessione con le aziende palermitane) che il
solo frame "talent trap" non contiene.

## Idee figlie derivabili

- **Pendolarismo per genere** 🟡 — `DF_DCSS_ISTR_LAV_PEN_2_TV_5` (2018-2024, comunale) ha
  `LOC_DEST` e `REAS_COMMUTING`; **da verificare se `GENDER` è dimensione piena** come nelle
  altre tavole della stessa DSD. Se sì, è la figlia più forte dell'intero parent: chi pendola
  verso Palermo, ragazzi o ragazze? Richiesta già scritta in `docs/CONTEXT-fabio.md`.
- **Il gradiente della distanza** 🟢 — con `comuni_sicilia_centroidi.csv` la distanza di
  ogni comune dal capoluogo è aritmetica; incrociata con `L11` sui 390 comuni dà la curva
  occupazione femminile × distanza da Palermo, e la posizione di Bagheria **sopra o sotto**
  quella curva. Se Bagheria sta sotto la curva dei comuni alla sua stessa distanza, la
  prossimità non viene sfruttata — ed è un finding, non una mappa decorativa.
- **Accessibilità dei servizi** 🟡 — figlia condivisa con `dove_sono_i_servizi.md`: i
  presidi esistenti letti come nodi raggiungibili (o no) senza auto propria.
- **Restare pendolando vs restare senza lavorare** 🟡 — incrocio con `doppia_fuga.md`: il
  pendolarismo come terza via fra occupazione locale ed emigrazione, e chi vi ha accesso.

## Cosa dicono già i dati

- `M1`-`M9` per 390 comuni × 3 censimenti, già in `ottomilacensus_long.csv`. Non
  scomponibili per genere (limite noto della fonte 2011).
- Bagheria: `M2` al 25° percentile (2011). La correlazione ecologica +0.32 è già calcolata.
- Centroidi e poligoni già pronti, nessun fetch cartografico nuovo.

## Rischi e limiti

🔴 La correlazione mobilità × occupazione femminile è **ecologica e su dati 2011**: il salto
"quindi più autobus = più occupate" non è nei dati e non va scritto. Il parent regge se le
figlie 2018-2024 (pendolarismo per genere) confermano il pattern al presente.
🔴 Senza la dimensione sesso nel pendolarismo, il parent si regge solo su correlazioni
ecologiche: in quel caso va **declassato** a contesto e non può guidare la proposal.

## Verso la proposal

Famiglia di interventi: accesso al mercato metropolitano (trasporto dedicato su orari di
lavoro e formazione, convenzioni con datori palermitani, postazioni di lavoro ibrido a
Bagheria). Target e KPI ereditati dalle figlie — es. quota femminile dei pendolari in uscita,
se il dato di genere esiste.

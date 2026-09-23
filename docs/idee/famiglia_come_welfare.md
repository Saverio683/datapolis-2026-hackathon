# [PARENT] La famiglia come welfare — chi paga quando il mercato non c'è

> Dove il lavoro giovanile manca, qualcosa assorbe i giovani che restano. A Bagheria quel
> qualcosa è la famiglia — e il conto lo paga in larga parte la parte femminile.

## Il frame

I frame "talent trap" e "geografia" guardano il mercato. Questo parent guarda **l'istituzione
che compensa il mercato**: la famiglia come ammortizzatore sociale di fatto. L'ipotesi è che
a Bagheria la transizione all'età adulta non passi dal lavoro ma dalla famiglia — restare in
quella d'origine o formarne una propria presto — e che questo canale sia strutturalmente
asimmetrico per genere: per una ragazza "entrare in famiglia" ha un nome censuario
(casalinga, 13.4% delle 15-24enni), per un ragazzo no ("altra condizione").

Il frame produce una lettura diversa dello stesso divario: l'occupazione femminile non è
bassa *nonostante* un equilibrio sociale, è bassa *perché* un equilibrio sociale esiste già
e funziona — assorbe, sistema, rende invisibile. Le policy che ignorano l'equilibrio
(sportelli, bandi) non lo scalfiscono; quelle che lo riconoscono trattano i vincoli reali
(carichi di cura, autonomia abitativa, reddito familiare).

## Perché è un parent

Perché dà una **causa candidata comune** a risultati che altrimenti restano slegati:
casalinghe a vent'anni, uscita femminile dopo i 25 (l'età della formazione familiare
altrove), immobilità pendolare. E genera figlie su indicatori (famiglie `F`, abitazioni `A`)
che nessun'altra idea del repo tocca.

## Idee figlie derivabili

- **Casalinghe a vent'anni** 🟢 — già scritta (`casalinghe_a_venti_anni.md`): diventa la
  figlia-meccanismo di questo parent.
- **Formazione familiare precoce** 🟢 — `F5`-`F7` (coppie giovani con/senza figli, famiglie
  monogenitoriali, <35) e `F4` (giovani soli, 15-34) sui 390 comuni, 2011: Bagheria forma
  famiglie prima e vive da sola meno dei comuni comparabili? Percentili, come per la mappa.
- **Andarsene di casa senza andarsene dal comune** 🟡 — l'autonomia abitativa come anello
  mancante: i giovani che non possono formare un nucleo autonomo a Bagheria o restano in
  famiglia o lasciano il comune. Gli indicatori `A` (patrimonio e condizioni abitative,
  2011) sono già scaricati; il codebook va letto per scegliere quelli giusti (es. quota di
  abitazioni non occupate). Prezzi/affitti richiederebbero una **fonte nuova** (OMI Agenzia
  delle Entrate): task "nuova fonte", da pianificare prima.
- **Stato civile per età e genere 2018-2024** 🟡 — il fetch SDMX già identificato in
  `gender_notes.txt` (oggi solo `ALL`): risponderebbe a "le ventenni si sposano prima che
  altrove?" al presente, non solo al 2011.

## Cosa dicono già i dati

- 13.4% casalinghe (387 persone) vs 4.6% nazionale, serie stabile 2018-2024.
- Le ragazze escono dalle coorti **dopo i 25 anni** — compatibile con un'uscita legata alla
  formazione familiare altrove, ma la compatibilità non è una prova: i dati misurano il
  saldo, non il motivo.
- `F4`-`F7` e `A1`-`A15` sono già in `ottomilacensus_long.csv`, mai usati finora.

## Rischi e limiti

🔴 **Il rischio più serio del repo è qui ed è narrativo**: il confine fra descrivere un
equilibrio sociale e giudicare le scelte delle persone. La scrittura deve restare sui vincoli
(cosa è disponibile, cosa no) e mai sulle preferenze ("le ragazze scelgono di..."), che i
dati non osservano. Una proposal che suona come "liberare le ragazze dalla famiglia" è
sbagliata due volte: normativamente e analiticamente.
🔴 Il motivo dell'inattività non è nei dati (già dichiarato in `casalinghe_a_venti_anni.md`):
questo parent accumula **evidenza circostanziale coerente**, non una dimostrazione causale.
Va scritto così.

## Verso la proposal

Famiglia di interventi sui vincoli: servizi di cura (se il carico di cura è il vincolo),
autonomia abitativa giovanile, ingaggio attivo che passa dai luoghi che le ragazze già
frequentano invece di aspettarle a uno sportello. Target e KPI ereditati dalle figlie
(quota casalinghe 15-24, giovani in nucleo autonomo).

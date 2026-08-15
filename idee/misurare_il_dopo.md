# Misurare il dopo — la proposta include il modo di sapere se ha funzionato

> Il censimento permanente esce ogni anno, per comune, per genere, per fascia d'età.
> Significa che qualunque intervento proposto qui è **valutabile a costo zero** — e quasi
> nessuna proposta lo sfrutta.

## L'idea

Le policy proposal da hackathon finiscono con un elenco di KPI plausibili e nessun disegno per
misurarli. Questa idea propone di trattare la **valutazione come parte del deliverable**: non
"misureremo il tasso di occupazione femminile", ma *quale* dato, con *quale* cadenza, contro
*quale* controfattuale, e con quale scarto minimo rilevabile.

Il pezzo che lo rende possibile è già in casa: il censimento permanente è una **serie annuale
2018-2024** a livello comunale, non una fotografia. C'è quindi un pre-periodo di sette anni
già osservato, un aggiornamento annuale garantito, e — con `gemelle_di_bagheria.md` — un
insieme di comuni di controllo.

## Perché è rilevante

Distingue una proposta scritta da chi ha guardato i dati da una scritta da chi li ha solo
citati. E risponde in anticipo alla domanda finale di ogni giuria: *"come sapreste se sta
funzionando?"*.

## Cosa dicono già i dati

- Serie **2018-2024** annuale, comunale, con genere ed età: sette punti di pre-trattamento.
  Il trend OLS 2018-2024 sul gap è già stimato in `notebooks/genere.ipynb`.
- Il **2020 manca** sulla classe 15-24 e le età singole esistono **solo dal 2021**: il
  disegno deve convivere con due buchi noti, che sono alla fonte e non si interpolano.
- I CI di Wilson/Newcombe sui tassi sono già calcolati: il gap 2024 è 8.3 punti con banda
  6.6-10.0. **La banda è larga quanto un effetto plausibile**: è il vincolo che decide tutto
  il disegno e va affrontato, non aggirato.
- La platea femminile 15-24 a Bagheria è di poche migliaia di persone: l'errore campionario
  su un tasso dell'8% non è trascurabile.

## Cosa bisogna sviluppare

1. **Potenza statistica minima**: dato l'ordine di grandezza della platea, quale variazione
   del tasso femminile sarebbe **distinguibile dal rumore** a uno o tre anni? Se la risposta
   è "più di quanto l'intervento possa plausibilmente produrre", allora il KPI primario non
   può essere il tasso comunale e serve un indicatore di processo (utenza dei servizi,
   ingressi nei percorsi). Questa è una conclusione onesta e utile, non un fallimento.
2. **Controfattuale**: differenza-in-differenze fra Bagheria e le sue gemelle, con i sette
   anni pre-intervento a verificare il **parallel trend**. Il test si può già fare *oggi*
   sui dati esistenti — ed è un pezzo di analisi vero, non un'ipotesi per il futuro.
3. **Gerarchia di indicatori**: uno primario (occupazione femminile 15-24), uno di
   meccanismo (quota casalinghe), uno di processo (utenza dei servizi, da creare), uno di
   contesto (ritenzione di coorte). Ognuno con la sua cadenza e la sua fonte.
4. **Un piano di aggiornamento**: quali celle del notebook rigenerano i KPI quando esce il
   dato 2025. Se la pipeline è scritta bene, la risposta è "tutte, con un comando" — ed è
   dimostrabile in una riga di README.

## Fattibilità

🟢 Interamente sui dati già presenti. Il calcolo di potenza è aritmetica su proporzioni; il
DiD sul pre-periodo è statsmodels, già in stack.
🟡 Dipende da `gemelle_di_bagheria.md` per il gruppo di controllo. Senza, il controfattuale
si riduce a Palermo/Sicilia — più debole ma non inutilizzabile.
🔴 Nessun intervento esiste ancora: il DiD post non è calcolabile. Ciò che si consegna è il
**disegno** più la verifica dei trend paralleli sul passato. Presentarlo come una valutazione
già fatta sarebbe falso.

## Verso la proposal

- **Evidenza** → esiste una fonte annuale, comunale, disaggregata per genere che copre
  esattamente gli indicatori dell'intervento: la valutazione non richiede nuove rilevazioni.
- **Intervento** → la proposta include il proprio protocollo di monitoraggio, con i comuni di
  controllo dichiarati in anticipo e i target fissati prima di partire.
- **Target** → il protocollo stesso: pubblicazione annuale dei quattro indicatori.
- **KPI** → la soglia di rilevabilità dichiarata onestamente insieme al target, invece di un
  numero tondo scelto perché suona bene.

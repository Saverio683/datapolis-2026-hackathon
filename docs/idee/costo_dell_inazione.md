# Il costo dell'inazione — mettere un numero sul talento che non si usa

> "+40 occupate" è un obiettivo. "Quanto ci costa ogni anno non averle" è un argomento.
> Sono lo stesso dato letto dai due lati.

## L'idea

Il thread genere ha già la misura in persone: allineando il tasso di occupazione femminile
15-24 a quello di Palermo si otterrebbero **+40 occupate**; per la parità con i coetanei
servirebbero **+239**, per la media nazionale **+262**. Sono numeri onesti e già calcolati
(`genere_gap_persone.csv`), ma parlano la lingua dell'analista.

Questa idea li traduce nella lingua di chi decide: **quanto capitale umano il territorio
lascia inutilizzato ogni anno**, e cosa costerebbe l'intervento a confronto. Non per fare
econometria da hackathon, ma perché una proposal che dice "questo intervento costa X e il
problema che affronta ne vale Y" è di un'altra categoria rispetto a una che dice solo
"il gap è di 8.3 punti".

## Perché è rilevante

La terza richiesta del brief è una *proposta concreta*. Concreto significa anche
dimensionato: quante persone, per quanto tempo, con quale ordine di grandezza di risorse. Ed è
il ponte fra il thread genere e una policy che un'amministrazione possa effettivamente
deliberare.

## Cosa dicono già i dati

- **+40 / +239 / +262** occupate secondo tre scenari di convergenza, già nel notebook.
  Il primo è un KPI realistico, gli altri due sono la **misura del problema**, non obiettivi:
  la distinzione è già scritta in `docs/CONTEXT-ale.md` e va conservata.
- La popolazione 15-34 cala di **313 persone in tre anni**: il costo dell'inazione non è
  statico, la base su cui si interviene si assottiglia mentre si discute.
- Sul territorio esistono già **3 percorsi di formazione tecnica superiore** e **4 sedi
  accreditate ai servizi al lavoro** (fonte regionale, cfr. `dove_sono_i_servizi.md`):
  l'intervento non parte da zero, e questo abbassa il costo dello scenario.

## Cosa bisogna sviluppare

1. **Scenari in persone, per fasce**: dalla convergenza minima (Palermo) a quella massima
   (parità con i coetanei), con bande di incertezza coerenti con i CI già calcolati sui tassi.
   Nessuno scenario va presentato come previsione: sono contabilità, non forecast.
2. **Traduzione economica** — 🟡 **richiede una fonte nuova**: i redditi comunali da
   dichiarazioni fiscali (open data MEF) darebbero un reddito medio locale con cui convertire
   le persone in ordine di grandezza economico. Non è nelle fonti già censite in
   `docs/sources.md`: se si fa, va aggiunta una riga lì e va scaricata in `data/raw/`.
   ⚠️ Il reddito medio dei dichiaranti **non è** il salario d'ingresso di una ventenne
   neo-occupata: usarlo tale e quale gonfia il numero. O si usa una soglia esplicita e
   dichiarata, o si rinuncia alla conversione in euro e si resta sulle persone.
3. **Il costo dal lato dell'intervento**: dimensionare l'intervento proposto (quante persone
   raggiunte, con quale intensità) e confrontarlo con la platea. È la parte che rende
   verificabile la promessa, e non richiede dati nuovi.
4. **Un contatore onesto**: se la conversione in euro non regge, l'alternativa forte è il
   **conteggio cumulato di persone-anno di inattività femminile giovanile** — stessa forza
   comunicativa, zero assunzioni discutibili.

## Fattibilità

🟢 Punti 1, 3, 4: dati già presenti.
🟡 Punto 2: fonte nuova + assunzioni. Va deciso in team **prima** di scriverlo nella proposal,
perché è il punto su cui una giuria attenta affonda per primo.
🔴 Nessuna stima di impatto causale è possibile qui: "se si occupassero 40 ragazze in più" è
un esercizio contabile, non l'effetto atteso di un intervento. Chiamarlo effetto sarebbe un
errore, e la distinzione va scritta nella cella, non solo intesa.

## Verso la proposal

- **Evidenza** → il divario femminile in persone, con tre scenari e la loro incertezza.
- **Intervento** → dimensionato sul primo scenario, non sul terzo: proporre +239 occupate è
  perdere credibilità in una riga.
- **Target** → +40 occupate 15-24 femmine nell'orizzonte dichiarato.
- **KPI** → numero assoluto di occupate 15-24 a Bagheria, letto dal censimento permanente
  ogni anno. È un KPI che nessuno deve rilevare apposta: esiste già e continuerà a esistere.

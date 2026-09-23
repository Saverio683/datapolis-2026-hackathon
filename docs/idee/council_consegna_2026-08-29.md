---
AI: true
last modified: 2026-08-29
type: Note
---

Council a quattro voci (Architect in contesto + Skeptic/Pragmatist/Critic indipendenti) sul pacchetto di consegna, deadline invio 30 agosto, festival 24 settembre. Verifica 743/743 PASS al momento della review.

## Verdetto
GO all'invio dopo un passaggio chirurgico (~2-3 ore). Causa radice unica (diagnosi Skeptic): i difetti sono residui pre-merge del thread mobilità, concentrati nelle frasi SENZA cifre, che i pin letterali di `pipeline/verifica.py` non coprono. L'apparato non riduce gli errori: li sposta dove non guarda.

## Stasera, prima dell'invio (ordine)
1. `POLICY_PONTE_19.md` §10 (riga ~446) + «Cosa il modulo non promette» (~316): i bullet «Non afferma un pendolarismo verso Palermo» contraddicono §6 e la relazione (matrice OD: 91,1% studio / 65,1% lavoro). Riallineare al fraseggio corretto già in §6.
2. Percentile ribaltamento lavoro: 13° vale sui 381 non capoluogo, 15° sui 390. Correggere `POLICY:184` («13° dei 390»), `RELAZIONE_DATAPOLIS:506` («13° dei comuni siciliani», ambiguo), `CONTEXT-fabio:40`.
3. Intro relazione: aggiungere `mobilita.ipynb` all'elenco (3 su 4; Appendice A ne ha 4).
4. `pipeline/relazione_docx.py:42` AUTORI = 2 nomi su team di 3 (manca Fabio/mobilità) — verificare col team, poi correggere.
5. F3 (policy §4-bis): «clausola di assunzione nelle gare riferita a residenti donne 22-25» = tripla discriminazione senza ancoraggio normativo. Riformulare come criteri premiali sul modello art. 47 DL 77/2021; i vincoli di residenza nelle gare sono giuridicamente fragili. Solo prosa, nessun pin toccato.
6. §1 relazione: aggiungere `dump_didascalie.R` e `relazione_docx` al blocco pipeline (README li ha già).
7. `RELAZIONE.md`: spuntare la checkbox docx (rigenerato 17:17); data «2026-08-28» → 29 nell'header.
8. Coda ricetta in ordine: `pipeline.schede` → `dump_didascalie.R` → `relazione_docx` → `verifica` (schede 15:28 < processed 15:54; leggono `genere_forbice_serie` e `genere_distribuzione_390`).
9. Invio (Pragmatist): PDF di cortesia (docx 12,6MB rimbalza sui cap 10MB), zip + README di lettura una pagina, decidere chi invia, spedire in mattinata con conferma ricezione.

## Prima del 24/9 (difesa orale)
- KPI «9,6% (Palermo)»: pre-trend +0,65pp/anno ⇒ +1,4pp arriva per inerzia in ~2 anni; esplicitare benchmark mobile / lettura in differenza (il §2 dice già «convergenza», la tabella lo congela).
- Potenza pooled: le annate non sono repliche indipendenti (stesse ragazze attraversano la finestra); una frase «limite superiore» in 7.4. La difesa censuario-vs-MDE esiste già in §1.5 (superpopolazione): prepararla, il Critic l'aveva mancata.
- «70,6% non cerca nemmeno»: etichetta censuaria residuale, non comportamento ILO. Tesi pinnata: non toccarla, preparare la risposta (§2.1 dice già «non classificato come»).
- `docs/analisi/educazione/README.md`: deliverable con path inesistenti (`outputs/…`, `make process`). Se rigenerato da pipeline.edu correggere il template, non il file; o escluderlo dal pacchetto.
- 4 cifre dichiarate scoperte dal sensore (orario/durata verso Palermo, POLICY §4-bis e RELAZIONE §5.4): esportare il taglio o lasciarle dichiarate.

## Cosa NON toccare
Tesi e numeri (pinnati), terna figure (scelta chiusa con criterio dichiarato), sezione limiti, mappa brief→evidenza. Congelare i numeri: correzioni solo di prosa; se verifica FAILa, la riga di FAIL stampa la frase da riscrivere.
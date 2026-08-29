---
related:
  - "[[gender_talent_trap]]"
  - "[[pendolarismo_ha_un_genere]]"
  - "[[doppia_fuga]]"
  - "[[bilancio_dei_giovani]]"
  - "[[00_the_talent_trap]]"
  - "[[04_il_19_percento_invisibile]]"
tags:
  - relazione
  - proposal
  - tesi
  - kpi
  - hackathon
last modified: 2026-08-28
AI: true
type: Note
---

# La tesi della relazione, e perché il KPI va scritto in tasso

Deciso il 2026-08-28. Sono i due paragrafi che reggono la relazione di accompagnamento:
il primo è la **tesi**, il secondo è il **vincolo di misura** che rende la proposta seria
invece che generica. Vanno citati così, non riformulati a ogni sessione.

## 1. La tesi (una sola frase, tre punti della stessa catena)

> **Bagheria produce titoli e non li converte. La conversione fallisce soprattutto sulle
> ragazze (più istruite del panel, 8,2% di occupazione, il minimo dei quattro territori
> in 6 anni su 6), in una finestra d'età stretta (22-25, ritenzione 96,3 contro ~103 in
> Italia), e il vincolo di mobilità ha lo stesso segno. Chi resta fuori non è chi cerca
> lavoro: il 70,6% dei giovani fuori da lavoro e studio non cerca nemmeno.**

Perché tiene: i tre thread non danno tre diagnosi diverse, danno **una diagnosi in tre
punti della stessa catena**, formazione → conversione → permanenza. Ogni pezzo viene da
una tavola diversa, quindi nessuno dei tre è una riformulazione degli altri.

Provenienza di ogni numero (tutti rigenerabili, mai a mano):

| Numero | Cella / file |
|---|---|
| 8,2% occupazione F 15-24; +4,2 vantaggio diploma F | `genere_quadro_sintesi.csv` |
| minimo del panel in 6 anni su 6 | «I claim reggono al 2024?», `genere_forbice_serie.csv` |
| ritenzione F 25-29 = 96,3 (Italia 103,0) | `genere_coorti.csv`; finestra 22-25 da `genere_ritenzione_eta.csv` |
| vincolo di mobilità con lo stesso segno | [[pendolarismo_ha_un_genere]], `genere_pendolarismo.csv` |
| 70,6% non cerca | thread educazione, `edu_finding_summary.csv` (19,0% inattivi su 26,9% fuori) |

⚠️ La finestra 22-25 è una lettura **pooled**: le transizioni annuali oscillano fino a
8 pp sulla stessa età. Si titola sul triennio, mai sull'anno singolo.

## 2. Il KPI va scritto in tasso, non in teste

> **La platea femminile 15-24 è già nata e cala del 15,5% al 2034. Le "+40 occupate"
> valgono +18 nel 2029 e −2 nel 2034 (fig09). Cioè il KPI va scritto in tasso, non in
> teste, un dettaglio che di solito nessuno vede prima di scriverlo male.**

Il conto sta in `genere_kpi_netto.csv`: allo stesso tasso obiettivo di Palermo (9,59%),
il KPI lordo di +40,4 occupate incontra un attrito demografico di −22,2 al 2029 e −42,9
al 2034, quindi netto **+18,2** e **−2,5**. La platea F passa da 2.882 (2024) a 2.651
(2029) e 2.435 (2034), `genere_platea.csv`, conteggio di chi è **già nato**, non una
proiezione.

⚠️ Da non confondere: **−19/−37** è lo scenario «non si fa niente» (tasso 2024 fermo,
`genere_tetto_platea.csv`); **−22/−43** è lo stesso attrito al tasso obiettivo di Palermo.
Due numeri diversi, due domande diverse.

Conseguenza operativa, da scrivere nella proposal e non solo nell'analisi:

1. Il KPI primario è un **tasso** (punti di occupazione femminile 15-24 chiusi verso il
   benchmark), mai un numero di teste.
2. Se un target in teste serve lo stesso per ragioni di comunicazione, va
   **riparametrato ogni anno** sulla platea corrente, dichiarando la formula.
3. La lettura è su **trienni pooled**: sulla lettura annuale il delta da rilevare (1,4 pp)
   sta sotto l'MDE (2,14 pp, potenza 46%); su tre anni la potenza è 90%
   (`genere_mde.csv`). L'anno singolo spetta agli indicatori di **processo**, che oggi
   nessuno rileva, e che il servizio deve produrre.

## Dove vivono

`docs/RELAZIONE_DATAPOLIS.md` (la relazione completa, scritta il 2026-08-28: i due
paragrafi vi compaiono verbatim nella sezione «In una pagina»), `docs/RELAZIONE.md`
(spina dorsale e decisioni) e `docs/POLICY_PONTE_19.md` (la proposta unificata). Le figure che le illustrano sono le tre dichiarate: `fig05_forbice`,
`fig07_ritenzione_eta`, `fig04_mappa_sicilia`, più `fig09_kpi_finestra` dentro la proposal.

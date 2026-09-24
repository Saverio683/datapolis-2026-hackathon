# Mappa della documentazione

Per riprodurre il progetto, partire dal [README generale](../README.md).
Per leggere i risultati, partire dalla [guida per la giuria](../LEGGIMI_GIURIA.md).
I percorsi scritti tra backtick nei documenti sono relativi alla radice del repository.
Questa mappa descrive il repository completo: lo ZIP per la giuria esclude idee,
archivio, i sorgenti della presentazione (del deck entra solo il PDF della v5,
`dist/PRESENTAZIONE_PONTE_19.pdf`), il generatore del deck e i materiali interni del team (contesti
personali, aggiornamenti datati, revisione tecnica). Dei documenti del team entra solo
`team/SCELTE_ANALITICHE.md`.

| Categoria | Contenuto e punto di ingresso |
|---|---|
| [Concorso](concorso/DataPolis_Concorso2026-UNI_OnePager-v02.md) | Brief degli organizzatori, con il PDF originale nella stessa cartella |
| [Fonti](sources.md) | Endpoint, acquisizioni e limiti dei dati; registro condiviso |
| [Relazione](relazione/RELAZIONE_DATAPOLIS.md) | Testo ufficiale per la giuria; il DOCX accanto è generato |
| [Policy](policy/POLICY_PONTE_19.md) | Proposta unificata Ponte 19; il DOCX accanto è generato |
| [Presentazione](presentazione/LINEE_GUIDA.md) | Linee guida, [copione](presentazione/COPIONE_PONTE_19.md), prompter, mappa delle cifre, [modifiche al pptx del 2026-09-24](presentazione/MODIFICHE_PPTX_2026-09-24.md) e materiali per l'orale |
| [Analisi: educazione](analisi/educazione/README.md) | Metodologia, dizionario e report del thread; la policy di thread è un contributo alla proposta unificata |
| [Team](team/SCELTE_ANALITICHE.md) | Scelte analitiche, contesti dei membri e aggiornamenti datati |
| [Idee](idee/README.md) | Ipotesi e piste esplorative, con il loro stato di fattibilità |
| [Archivio](archivio/UNISON.md) | Documentazione storica della migrazione; i percorsi citati descrivono la struttura dell'epoca |
| `schede/` | Quattro schede HTML generate da `pipeline.schede` |
| `silica/Inbox/` | Note locali di supporto, escluse da Git |

## Quale file modificare

- Relazione e policy: modificare i Markdown nelle rispettive cartelle, poi eseguire
  `python -m pipeline.relazione_docx` e `python -m pipeline.policy_docx` nell'ambiente del progetto.
- Schede: modificare `pipeline/schede.py` e rigenerare con `python -m pipeline.schede`.
- Report di educazione: i tre report e i JSON di esecuzione/validazione sono generati;
  le istruzioni e i documenti metodologici sono descritti nel README del thread.
- Presentazione: i deck sono in `presentazione/`, una versione per file (v1-v5), e non si
  sovrascrivono. La v4 è quella proiettata il 24 settembre; la v5 corregge quattro sue
  slide ed è quella consegnata ([le modifiche](presentazione/MODIFICHE_PPTX_2026-09-24.md)). Il generatore `pipeline/presentazione_pptx.py` non è allineato ai numeri
  correnti (l'[aggiornamento del team](team/AGGIORNAMENTO_SAVERIO_2026-09-23.md) lo
  documenta): non usarlo per rigenerare il deck.

## Esportazioni e consegne

`dist/` contiene PDF, notebook HTML e ZIP rigenerabili con `python -m pipeline.pdf`.
Il riordino documentale mantiene questo flusso e lascia DOCX, schede e report accanto
alle rispettive aree di lavoro. La separazione completa delle esportazioni in
sottocartelle di `dist/` è un passaggio successivo.

Un'esportazione corrente non certifica una consegna passata: conservare gli originali
effettivamente inviati con la loro data, senza ricostruirli dai sorgenti aggiornati.

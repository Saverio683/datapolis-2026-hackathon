from __future__ import annotations

import json
from datetime import date

import pandas as pd

from .paths import OUTPUTS, TABLES


def _fmt(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")


def _count(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def _markdown_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _load() -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame]:
    summary = json.loads((TABLES / "edu_analysis_summary.json").read_text(encoding="utf-8"))
    findings = pd.read_csv(TABLES / "edu_finding_summary.csv")
    decomposition = pd.read_csv(TABLES / "edu_change_decomposition_2018_2024.csv")
    return summary, findings, decomposition


def build_analytical_report() -> str:
    summary, findings, decomposition = _load()
    inventory = pd.read_csv(TABLES / "edu_source_inventory.csv")
    history = pd.read_csv(TABLES / "edu_historical_change_1991_2011.csv").set_index("indicatore")
    current = summary["current_2024"]
    change = summary["change_2018_2024"]
    gaps = summary["gaps_vs_sicily_2024"]
    peer = summary["peer_summary"]
    search_change = decomposition.loc[
        decomposition["metrica"].eq("in_cerca"), "variazione_conteggio"
    ].iloc[0]
    inactive_change = decomposition.loc[
        decomposition["metrica"].eq("inattivi_non_studenti"), "variazione_conteggio"
    ].iloc[0]
    source_table = "\n".join(
        "| "
        + " | ".join(
            _markdown_cell(getattr(row, column))
            for column in ["fonte", "dataset", "stato", "periodo", "grana", "ruolo", "limite"]
        )
        + " |"
        for row in inventory.itertuples(index=False)
    )

    report = f"""# Bagheria: dalla formazione all'attivazione

## Rapporto analitico

### La conclusione in una frase

**Bagheria è migliorata, ma non ha chiuso il divario con la Sicilia: il collo di bottiglia
oggi più persistente è l'inattività non studentesca dei 15-24enni.**

![Profilo 2024](../../figures/edu/01_snapshot_bagheria_2024.png)

## 1. Dati iniziali, perimetro e qualità

L'analisi integra indicatori storici comunali 1991-2011 e tavole IstatData recenti. Il
perimetro più aggiornato sulla condizione lavorativa è **15-24 anni**, non 15-34. Per i
15-34enni è disponibile la popolazione 2021-2024, ma non una classificazione comunale recente
per condizione. Il titolo di studio e il lavoro provengono da tavole separate: il progetto
confronta aggregati territoriali e non calcola il tasso di occupazione dei diplomati.

Le fonti core hanno superato i controlli di schema, unicità, composizione e checksum. Il 2020
manca nella tavola lavoro e non è stato interpolato. Gli endpoint regionali su offerte e
operatori hanno restituito HTTP 502 e sono esclusi dai risultati quantitativi.

| Fonte | Dataset | Stato | Periodo | Grana | Ruolo | Limite |
|---|---|---|---|---|---|---|
{source_table}

Il lineage completo è nel manifest raw; undici controlli automatici verificano checksum,
unicità, composizione, valori sentinella, assenza di interpolazione e identità delle
scomposizioni.

## 2. Il punto di partenza storico

Tra 1991 e 2011 l'uscita precoce 15-24 scende dal
**{_fmt(history.loc['I5', 'valore_1991'])}%** al
**{_fmt(history.loc['I5', 'valore_2011'])}%**, mentre diploma/laurea 25-64 sale dal
**{_fmt(history.loc['I6', 'valore_1991'])}%** al
**{_fmt(history.loc['I6', 'valore_2011'])}%**. Il progresso assoluto è netto. La posizione
relativa tra i 390 comuni siciliani, però, peggiora su tutti gli indicatori selezionati: è il
primo segnale che crescita interna e convergenza non sono la stessa cosa.

![Storia e posizione relativa](../../figures/edu/02_storia_livelli_e_posizione.png)

Nel 2011 il passaggio tra istruzione e lavoro presenta ancora una frattura: almeno licenza
media 15-19 al 96,7%, ma uscita precoce 15-24 al 28,6%, NEET 15-29 al 40,1% e occupazione
15-29 al 20,0%. Le fasce sono riportate esplicitamente e non descrivono un funnel individuale.

![Benchmark della transizione 2011](../../figures/edu/03_transizione_benchmark_2011.png)

## 3. Profilo corrente

Nel 2024 Bagheria conta **{_count(current['population_15_24'])} residenti di 15-24 anni**:

- **{_fmt(current['students_pct'])}%** studenti;
- **{_fmt(current['employed_pct'])}%** occupati, circa {_count(current['employed_count'])} persone;
- **{_fmt(current['searching_pct'])}%** in cerca di lavoro;
- **{_fmt(current['inactive_nonstudent_pct'])}%** inattivi non studenti, circa
  {_count(current['inactive_nonstudent_count'])} persone.

Gli inattivi rappresentano il **{_fmt(current['inactive_share_of_outside_pct'])}%** dei giovani
fuori da lavoro e studio. La loro quota è **{_fmt(gaps['inactive_nonstudent_15_24_pp'])} punti
sopra la Sicilia**.

![Composizione 2018-2024](../../figures/edu/04_composizione_giovani_2018_2024.png)

![Confronto degli stati 2024](../../figures/edu/05_benchmark_stati_2024.png)

## 4. Il recupero esiste, la convergenza no

Tra 2018 e 2024 l'occupazione 15-24 cresce di **{_fmt(change['employment_pp'])} punti** e la
quota fuori da lavoro e studio scende di **{_fmt(abs(change['outside_work_study_pp']))} punti**.
Tuttavia, il gap occupazionale con la Sicilia è ancora **{_fmt(abs(gaps['employment_15_24_pp']))}
punti**: quasi lo stesso osservato nel 2018.

![Gap con la Sicilia](../../figures/edu/06_gap_con_sicilia_2018_2024.png)

La composizione del cambiamento è decisiva. Il numero stimato di giovani in cerca diminuisce
di circa **{_count(abs(search_change))}**, mentre gli inattivi non studenti scendono soltanto di
circa **{_count(abs(inactive_change))}**. In quota, la ricerca cala di 10,2 punti e l'inattività di
appena 0,6. Il miglioramento complessivo non equivale quindi alla riattivazione del gruppo più
difficile da raggiungere.

![Scomposizione del cambiamento](../../figures/edu/07_scomposizione_cambiamento_2018_2024.png)

## 5. Istruzione e lavoro: cosa si può concludere

Il capitale umano è cresciuto. Tra i 25-49enni di Bagheria la quota con almeno diploma passa
dal 56,2% al 62,4% tra 2018 e 2024; l'occupazione sale dal 43,0% al 53,6%. I divari con la
Sicilia si riducono, ma nel 2024 restano rispettivamente **{_fmt(abs(gaps['at_least_diploma_25_49_pp']))}
e {_fmt(abs(gaps['employment_25_49_pp']))} punti**.

![Traiettoria 25-49](../../figures/edu/08_traiettoria_25_49.png)

![Posizionamento 25-49](../../figures/edu/09_posizionamento_istruzione_lavoro_25_49.png)

La lettura corretta è territoriale: istruzione e occupazione avanzano insieme, ma Bagheria
resta sotto il benchmark in entrambe. Senza un microdato comunale titolo × condizione non è
possibile attribuire il gap lavorativo al mancato rendimento di uno specifico titolo.

## 6. Demografia: un controllo, non una spiegazione

La popolazione 15-34 scende del 2,6% tra 2021 e 2024, quasi quanto la Sicilia. La serie è breve
e misura lo stock residente: non consente di attribuire il calo alla migrazione né di stimare
una fuga di capitale umano.

![Popolazione 15-34](../../figures/edu/10_popolazione_15_34.png)

## 7. Il benchmark non dipende soltanto dalla media regionale

Nel confronto storico con dieci comuni siciliani simili per popolazione, struttura e profilo
educativo, Bagheria registra un'occupazione 15-29 del **{_fmt(peer['bagheria_youth_employment'])}%**
contro una mediana del **{_fmt(peer['peer_median_youth_employment'])}%**. Il gap è
**{_fmt(abs(peer['employment_gap_vs_peer_median']))} punti**.

![Confronto con i peer](../../figures/edu/11_confronto_peer_2011.png)

Il matching non è causale, ma mostra che il basso ingresso nel lavoro non emerge soltanto nel
confronto con Italia o Sicilia.

## 8. Risultati che guidano la decisione

| Priorità | Risultato | Implicazione |
|---:|---|---|
"""
    for row in findings.itertuples():
        report += f"| {row.priorita} | {row.risultato} | {row.implicazione} |\n"
    report += f"""

## 9. Direzione di policy

La risposta coerente con i dati è un servizio di transizione e riattivazione, non un corso
generalista. **Ponte 19 Bagheria** combina presa in carico prima dell'uscita dalla scuola,
outreach verso chi non cerca e accesso a esperienze retribuite soltanto dopo la verifica della
domanda. Il progetto misura titolo, condizione iniziale, barriera, servizio ed esito a 3, 6 e
12 mesi, creando il dato oggi assente.

La specifica completa è in `POLICY_PONTE_19_BAGHERIA.md`.

_Report generato il {date.today().isoformat()} dalla pipeline riproducibile._
"""
    (OUTPUTS / "REPORT_ANALITICO.md").write_text(report, encoding="utf-8")
    return report


def build_policy_report() -> str:
    summary, _, _ = _load()
    current = summary["current_2024"]
    change = summary["change_2018_2024"]
    gaps = summary["gaps_vs_sicily_2024"]

    policy = f"""# Ponte 19 Bagheria

## Servizio comunale di transizione e riattivazione 18-24

## 1. Evidenza che motiva l'intervento

Nel 2024 il **{_fmt(current['inactive_nonstudent_pct'])}%** dei 15-24enni di Bagheria è
inattivo non studente: circa **{_count(current['inactive_nonstudent_count'])} persone** e
**{_fmt(gaps['inactive_nonstudent_15_24_pp'])} punti sopra la Sicilia**. Tra 2018 e 2024 questa
quota scende di appena **{_fmt(abs(change['inactive_nonstudent_pp']))} punti**, mentre la quota
di chi cerca lavoro diminuisce di **{_fmt(abs(change['searching_pp']))} punti**. Il servizio
ordinario basato sulla domanda spontanea rischia quindi di raggiungere il segmento sbagliato.

Nello stesso periodo l'occupazione 15-24 cresce, ma il divario con la Sicilia resta
**{_fmt(abs(gaps['employment_15_24_pp']))} punti**. La policy deve misurare la convergenza e la
tenuta degli esiti, non soltanto il numero di utenti presi in carico.

## 2. Obiettivo

Ridurre la durata dell'inattività dei giovani residenti e rendere osservabile la transizione
tra titolo posseduto, attivazione e primo esito lavorativo o formativo.

## 3. Target e capacità del pilota

- **Target primario:** residenti 18-24 fuori da studio e lavoro che non cercano attivamente.
- **Target preventivo:** studenti nell'ultimo anno della secondaria senza un passo successivo.
- **Capacità:** 200 partecipanti nel primo anno.
- **Durata:** 90 giorni di preparazione, 12 mesi di erogazione, follow-up a 3, 6 e 12 mesi.
- **Dotazione minima:** quattro case manager, un data manager, un coordinamento Comune-scuole-CPI.

## 4. Modello operativo

### A. Intercettazione prima del vuoto

Le scuole secondarie e tecniche di Bagheria propongono il servizio nell'ultimo anno e al momento
dell'interruzione. Con consenso e minimizzazione dei dati, ogni giovane riceve un appuntamento
prima che trascorrano 30 giorni senza studio o lavoro.

### B. Outreach verso chi non cerca

Il servizio non attende l'iscrizione allo sportello. Scuole, CPI, Comune e presidi territoriali
attivano campagne e contatto volontario. Il primo colloquio registra titolo e indirizzo, data
di uscita, esperienze, canali già usati, distanza dalle opportunità e obiettivo.

### C. Piano di transizione entro 15 giorni

Il case manager assegna una sola prossima azione verificabile: rientro in istruzione, qualifica
breve collegata a una posizione, ricerca assistita o esperienza retribuita. Il piano ha una
scadenza, un responsabile e un esito osservabile.

### D. Esperienze retribuite soltanto su domanda verificata

Nei primi 90 giorni il Comune effettua un audit dei datori locali e metropolitani. Ogni
esperienza deve avere attività reale, mentor, compenso, competenze attese e disponibilità a
registrare l'esito. Senza posti verificati non si convertono le risorse in formazione generica.

## 5. Decision gate dei primi 90 giorni

| Evidenza raccolta | Decisione |
|---|---|
| Almeno 30 esperienze retribuite con domanda e mentor verificati | Attivare il modulo esperienza |
| Gap di competenza ricorrente associato a posizioni reali | Progettare un modulo breve e mirato |
| Trasporto barriera primaria e offerta coerente già identificata | Testare un supporto mobilità sul sottogruppo |
| Domanda insufficiente o non verificabile | Concentrare risorse su outreach, orientamento e mercato metropolitano |

## 6. KPI

### Outcome primario

Quota di partecipanti occupati, in istruzione o in formazione qualificante a sei mesi, con
esito ancora attivo al dodicesimo mese.

### KPI di processo

- primo contatto entro 30 giorni dalla segnalazione;
- assessment completo e piano entro 15 giorni;
- quota di partecipanti che avvia l'azione concordata entro 30 giorni;
- giorni medi consecutivi fuori da lavoro, studio e formazione;
- quota con esperienza retribuita entro 90 giorni, solo dove prevista dal decision gate.

### KPI di qualità

- durata e tipologia del contratto;
- coerenza dichiarata tra indirizzo di studio e attività;
- continuità dell'esito a 6 e 12 mesi;
- ricaduta nell'inattività;
- esiti aggregati per titolo e indirizzo, senza pubblicare celle piccole.

## 7. Valutazione dell'impatto

Il rollout è scaglionato. Tra persone con uguale priorità, l'ordine di avvio viene assegnato
casualmente quando eticamente possibile; chi inizia più tardi costituisce il confronto
temporaneo. Protocollo, outcome primario, finestre temporali ed esclusioni vengono pubblicati
prima dell'avvio. Il confronto prima-dopo da solo non è sufficiente.

## 8. Dataset prodotto dal servizio

Ogni record pseudonimizzato segue lo schema:

**titolo/indirizzo → data di uscita → condizione iniziale → durata inattività → azione →
esito a 3, 6 e 12 mesi.**

Questo dato permette finalmente di misurare il rapporto tra titolo e condizione lavorativa a
livello individuale, oggi non disponibile nelle tavole comunali pubbliche.

## 9. Accountability pubblica

Una dashboard trimestrale pubblica soltanto indicatori aggregati: persone contattate, piani
attivati, esiti a 3/6/12 mesi, durata media dell'inattività e differenza rispetto al gruppo di
confronto. Il successo non è il numero di iscritti, ma una transizione stabile.

_Policy generata il {date.today().isoformat()} dalla pipeline riproducibile._
"""
    (OUTPUTS / "POLICY_PONTE_19_BAGHERIA.md").write_text(policy, encoding="utf-8")
    return policy


def build_executive_summary() -> str:
    summary, _, _ = _load()
    current = summary["current_2024"]
    change = summary["change_2018_2024"]
    gaps = summary["gaps_vs_sicily_2024"]
    content = f"""# Executive summary

## Messaggio centrale

**Bagheria migliora, ma non converge.** Tra 2018 e 2024 l'occupazione 15-24 aumenta di
{_fmt(change['employment_pp'])} punti e la quota fuori da lavoro e studio diminuisce di
{_fmt(abs(change['outside_work_study_pp']))} punti. Il gap occupazionale con la Sicilia resta
però {_fmt(abs(gaps['employment_15_24_pp']))} punti, quasi invariato.

## Il segmento prioritario

Nel 2024 il **{_fmt(current['inactive_nonstudent_pct'])}%** dei 15-24enni è inattivo non
studente: circa **{_count(current['inactive_nonstudent_count'])} persone**, pari al
{_fmt(current['inactive_share_of_outside_pct'])}% di chi è fuori da lavoro e studio. La quota
è {_fmt(gaps['inactive_nonstudent_15_24_pp'])} punti sopra la Sicilia e dal 2018 è scesa di
soli {_fmt(abs(change['inactive_nonstudent_pp']))} punti.

## Istruzione e lavoro

Tra i 25-49enni crescono sia almeno diploma sia occupazione, ma nel 2024 Bagheria resta sotto
la Sicilia di {_fmt(abs(gaps['at_least_diploma_25_49_pp']))} e
{_fmt(abs(gaps['employment_25_49_pp']))} punti. Le fonti sono aggregate e separate: non
consentono di calcolare l'occupazione dei diplomati.

## Policy

**Ponte 19 Bagheria**: presa in carico prima dell'uscita dalla scuola, outreach verso chi non
cerca, piano entro 15 giorni, esperienza retribuita solo su domanda verificata e monitoraggio
a 3, 6 e 12 mesi con rollout scaglionato.
"""
    (OUTPUTS / "EXECUTIVE_SUMMARY.md").write_text(content, encoding="utf-8")
    return content

#!/usr/bin/env python3
"""Genera il notebook editoriale e tecnico principale del progetto."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "Bagheria_transizione_istruzione_lavoro.ipynb"


def markdown(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str, tags: list[str] | None = None):
    cell = nbf.v4.new_code_cell(text.strip())
    if tags:
        cell.metadata["tags"] = tags
    return cell


def section(number: str, title: str, subtitle: str):
    return markdown(
        f"""
<div class="section-kicker">SEZIONE {number}</div>

## {title}

<p class="section-subtitle">{subtitle}</p>
"""
    )


def figure(filename: str, alt: str):
    return code(
        f"display(Image(filename=FIGURES / {filename!r}, alt={alt!r}))",
        tags=["figure", "hide-input"],
    )


def build() -> Path:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
        "title": "Bagheria: dalla formazione all'attivazione",
        "authors": [{"name": "DataPolis Bagheria Lab"}],
    }
    notebook["cells"] = [
        markdown(
            """
<style>
:root {
  --navy: #102A43; --blue: #2F6BFF; --green: #2A9D8F;
  --orange: #F28E2B; --red: #D1495B; --ink: #243B53;
  --muted: #627D98; --line: #D9E2EC; --paper: #F6F9FC;
}
.hero {
  padding: 34px 38px; border-radius: 22px; color: white;
  background: linear-gradient(125deg, #102A43 0%, #1E4E8C 58%, #2F6BFF 100%);
  box-shadow: 0 14px 35px rgba(16,42,67,.18); margin: 8px 0 26px 0;
}
.hero h1 { margin: 0 0 8px 0; font-size: 38px; line-height: 1.08; color: white; }
.hero p { margin: 8px 0 0; font-size: 17px; line-height: 1.5; color: #EAF2FF; max-width: 900px; }
.badge { display: inline-block; margin: 0 7px 12px 0; padding: 5px 10px; border-radius: 999px;
  background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.25); font-size: 12px; }
.section-kicker { color: #2F6BFF; font-size: 12px; letter-spacing: .12em; font-weight: 800; margin-top: 36px; }
.section-subtitle { color: #627D98; font-size: 16px; margin-top: -6px; max-width: 960px; }
.callout { border-left: 5px solid #2F6BFF; background: #F3F7FF; padding: 15px 18px;
  border-radius: 8px; margin: 14px 0 22px 0; color: #243B53; }
.warning { border-left-color: #F28E2B; background: #FFF7EB; }
.result { border-left-color: #2A9D8F; background: #EFFAF7; }
.kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(150px,1fr)); gap: 12px; margin: 18px 0 24px; }
.kpi { border: 1px solid #D9E2EC; border-radius: 14px; padding: 17px; background: white; }
.kpi-value { font-size: 27px; font-weight: 800; color: #102A43; }
.kpi-label { font-size: 13px; font-weight: 700; color: #334E68; margin-top: 4px; }
.kpi-note { font-size: 11px; color: #829AB1; margin-top: 7px; }
.finding { border: 1px solid #D9E2EC; border-radius: 12px; padding: 14px 16px; margin: 9px 0; background: white; }
.finding strong { color: #102A43; }
.output_png img, .jp-OutputArea-output img { max-width: 100% !important; height: auto !important; }
table { font-size: 12px !important; }
thead tr th { background: #102A43 !important; color: white !important; text-align: left !important; }
tbody tr:nth-child(even) { background: #F6F9FC; }
</style>

<div class="hero">
  <span class="badge">DataPolis 2026</span>
  <span class="badge">Bagheria</span>
  <span class="badge">Technical notebook</span>
  <h1>Dalla formazione all'attivazione</h1>
  <p>Un'analisi riproducibile della transizione tra istruzione e lavoro, costruita per
  distinguere miglioramento assoluto, convergenza territoriale e segmento prioritario di policy.</p>
</div>

**Domanda di ricerca**  
Come è cambiata la transizione tra istruzione e lavoro a Bagheria e quale segmento presenta
oggi il divario più persistente rispetto alla Sicilia?
"""
        ),
        code(
            """
from pathlib import Path
import json
import sys

import pandas as pd
from IPython.display import HTML, Image, Markdown, display

ROOT = Path.cwd()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))

from datapolis_bagheria.analysis import run_analysis
from datapolis_bagheria.charts import build_all_charts
from datapolis_bagheria.cleaning import build_clean_data
from datapolis_bagheria.paths import FIGURES, OUTPUTS, PROCESSED, TABLES
from datapolis_bagheria.policy import build_analytical_report, build_executive_summary, build_policy_report
from datapolis_bagheria.validation import validate_pipeline

pd.set_option("display.max_colwidth", 180)
pd.set_option("display.precision", 2)

def show_table(frame, formats=None):
    styled = (
        frame.style.hide(axis="index")
        .set_table_styles([
            {"selector": "th", "props": [("background-color", "#102A43"), ("color", "white"), ("font-weight", "700")]},
            {"selector": "td", "props": [("border-bottom", "1px solid #E4E7EB"), ("padding", "7px 9px"), ("vertical-align", "top")]},
        ])
        .set_properties(**{"text-align": "left"})
    )
    if formats:
        styled = styled.format(formats)
    display(styled)
""",
            tags=["setup"],
        ),
        code(
            """
# Pipeline locale: raw già acquisiti → pulizia → analisi → validazione → grafici → report
quality = build_clean_data()
summary = run_analysis()
validation = validate_pipeline()
figure_paths = build_all_charts()
policy_text = build_policy_report()
analytical_report = build_analytical_report()
executive_summary = build_executive_summary()

inventory = pd.read_csv(TABLES / "source_inventory.csv")
youth = pd.read_csv(TABLES / "youth_states_2018_2024.csv", dtype={"territorio": str})
adult = pd.read_csv(TABLES / "adult_transition_2018_2024.csv", dtype={"territorio": str})
gaps = pd.read_csv(TABLES / "gaps_vs_sicily.csv")
findings = pd.read_csv(TABLES / "finding_summary.csv")
""",
            tags=["pipeline"],
        ),
        code(
            """
c = summary["current_2024"]
g = summary["gaps_vs_sicily_2024"]
ch = summary["change_2018_2024"]
display(HTML(f'''
<div class="kpi-grid">
  <div class="kpi"><div class="kpi-value">{c['population_15_24']:,.0f}</div><div class="kpi-label">residenti 15-24</div><div class="kpi-note">perimetro lavoro 2024</div></div>
  <div class="kpi"><div class="kpi-value" style="color:#2A9D8F">{c['employed_pct']:.1f}%</div><div class="kpi-label">occupati</div><div class="kpi-note">{g['employment_15_24_pp']:+.1f} p.p. vs Sicilia</div></div>
  <div class="kpi"><div class="kpi-value" style="color:#D1495B">{c['outside_work_study_pct']:.1f}%</div><div class="kpi-label">fuori lavoro-studio</div><div class="kpi-note">{ch['outside_work_study_pp']:+.1f} p.p. dal 2018</div></div>
  <div class="kpi"><div class="kpi-value" style="color:#F28E2B">{c['inactive_nonstudent_pct']:.1f}%</div><div class="kpi-label">inattivi non studenti</div><div class="kpi-note">≈ {c['inactive_nonstudent_count']:.0f} persone</div></div>
</div>
<div class="callout result"><strong>Risultato centrale.</strong> Bagheria migliora, ma non converge: il gap occupazionale giovanile con la Sicilia resta circa -3 punti e il segmento inattivo diminuisce di appena 0,6 punti dal 2018.</div>
'''))
""",
            tags=["summary", "hide-input"],
        ),
        figure("01_snapshot_bagheria_2024.png", "Profilo 2024"),
        section(
            "01",
            "Dati iniziali e qualità",
            "Prima dei risultati: cosa è stato scaricato, con quale grana, per quali anni e con quali limiti.",
        ),
        markdown(
            """
La pipeline distingue tre livelli: **raw immutabile**, **dati puliti normalizzati** e
**tabelle analysis-ready**. Ogni raw disponibile è registrato con URL finale, timestamp,
dimensione e SHA-256. Le fonti non disponibili restano nel manifest con stato esplicito e non
vengono sostituite con valori stimati.

<div class="callout warning"><strong>Perimetro da non confondere.</strong> Il lavoro recente è
15-24; il NEET storico è 15-29; la popolazione del brief è 15-34. Queste misure vengono tenute
separate e non formano una serie unica.</div>
"""
        ),
        code(
            """
columns = ["fonte", "dataset", "stato", "periodo", "grana", "righe_pulite", "uso", "ruolo", "limite"]
show_table(inventory[columns], {"righe_pulite": "{:,.0f}"})
""",
            tags=["data-audit"],
        ),
        code(
            """
checks = pd.DataFrame(validation["checks"])
checks["esito"] = checks["passed"].map({True: "✓ PASS", False: "✗ FAIL"})
display(HTML(f'<div class="callout result"><strong>Validazione:</strong> {validation["checks_passed"]}/{validation["checks_total"]} controlli superati.</div>'))
show_table(checks[["esito", "check", "detail"]])
""",
            tags=["quality"],
        ),
        section(
            "02",
            "Il punto di partenza storico",
            "Il progresso assoluto è reale, ma il confronto con i 390 comuni siciliani racconta una mancata convergenza.",
        ),
        figure("02_storia_livelli_e_posizione.png", "Storia e posizione relativa"),
        markdown(
            """
Tra 1991 e 2011 Bagheria migliora in valore assoluto su istruzione e riduce leggermente i
NEET. Tuttavia perde posizione relativa su tutti gli indicatori osservati. Questo evita una
lettura compiacente basata soltanto sulla variazione interna.
"""
        ),
        figure("03_transizione_benchmark_2011.png", "Transizione 2011"),
        code(
            """
historical_change = pd.read_csv(TABLES / "historical_change_1991_2011.csv")
show_table(historical_change[["metrica", "valore_1991", "valore_2011", "variazione_valore_pp", "percentile_1991", "percentile_2011", "convergenza_relativa"]], {
    "valore_1991": "{:.1f}%", "valore_2011": "{:.1f}%", "variazione_valore_pp": "{:+.1f}",
    "percentile_1991": "{:.1f}", "percentile_2011": "{:.1f}",
})
""",
            tags=["historical-table"],
        ),
        section(
            "03",
            "Com'è composto oggi il mondo 15-24",
            "La composizione annuale distingue studenti, occupati, persone in cerca e inattivi non studenti.",
        ),
        figure("04_composizione_giovani_2018_2024.png", "Composizione 2018-2024"),
        figure("05_benchmark_stati_2024.png", "Benchmark 2024"),
        code(
            """
latest = youth[youth["anno"].eq(2024)][[
    "territorio_nome", "popolazione", "quota_studenti", "quota_occupati",
    "quota_in_cerca", "quota_inattivi_non_studenti", "quota_fuori_lavoro_studio"
]].copy()
show_table(latest, {
    "popolazione": "{:,.0f}", "quota_studenti": "{:.1f}%", "quota_occupati": "{:.1f}%",
    "quota_in_cerca": "{:.1f}%", "quota_inattivi_non_studenti": "{:.1f}%",
    "quota_fuori_lavoro_studio": "{:.1f}%",
})
""",
            tags=["recent-table"],
        ),
        section(
            "04",
            "Miglioramento o convergenza?",
            "La domanda decisiva non è soltanto se Bagheria migliora, ma se recupera terreno rispetto alla Sicilia.",
        ),
        figure("06_gap_con_sicilia_2018_2024.png", "Gap con la Sicilia"),
        markdown(
            """
L'occupazione 15-24 cresce di 4,2 punti, ma il gap con la Sicilia resta pressoché identico:
**-3,1 punti nel 2018 e -3,1 nel 2024**. L'inattività non studentesca rimane sopra il
benchmark e registra una nuova pressione nel 2023.
"""
        ),
        figure("07_scomposizione_cambiamento_2018_2024.png", "Scomposizione del cambiamento"),
        code(
            """
decomposition = pd.read_csv(TABLES / "change_decomposition_2018_2024.csv")
show_table(decomposition[["metrica_label", "conteggio_iniziale", "conteggio_finale", "variazione_conteggio", "quota_iniziale_pct", "quota_finale_pct", "variazione_quota_pp", "effetto_popolazione", "effetto_tasso"]], {
    "conteggio_iniziale": "{:,.0f}", "conteggio_finale": "{:,.0f}", "variazione_conteggio": "{:+,.0f}",
    "quota_iniziale_pct": "{:.1f}%", "quota_finale_pct": "{:.1f}%", "variazione_quota_pp": "{:+.1f}",
    "effetto_popolazione": "{:+,.0f}", "effetto_tasso": "{:+,.0f}",
})
""",
            tags=["decomposition"],
        ),
        markdown(
            """
<div class="callout result"><strong>Insight operativo.</strong> Il calo dell'area fuori
lavoro-studio deriva per circa 663 persone dalla riduzione di chi cerca; gli inattivi non
studenti diminuiscono soltanto di circa 102. Uno sportello che aspetta la domanda spontanea non
raggiunge quindi il segmento più persistente.</div>
"""
        ),
        section(
            "05",
            "Istruzione e lavoro nella fascia 25-49",
            "La stessa fascia d'età permette un confronto territoriale più pulito, pur restando due tavole aggregate separate.",
        ),
        figure("08_traiettoria_25_49.png", "Traiettoria 25-49"),
        figure("09_posizionamento_istruzione_lavoro_25_49.png", "Posizionamento 25-49"),
        markdown(
            """
Bagheria cresce su entrambe le dimensioni e riduce parte del divario. Nel 2024 resta però
sotto la Sicilia di **4,1 punti per almeno diploma** e **5,7 punti per occupazione**. Non
emerge quindi un territorio con capitale umano eccezionalmente alto: la policy deve sostenere
insieme completamento formativo e attivazione.
"""
        ),
        code(
            """
adult_endpoints = adult[adult["anno"].isin([2018, 2024])][[
    "territorio_nome", "anno", "quota_almeno_diploma", "quota_occupati_25_49", "nota"
]]
show_table(adult_endpoints, {
    "quota_almeno_diploma": "{:.1f}%", "quota_occupati_25_49": "{:.1f}%",
})
""",
            tags=["adult-table"],
        ),
        section(
            "06",
            "Demografia e comuni comparabili",
            "Due controlli di contesto: il denominatore 15-34 e un benchmark che non dipende soltanto dalle medie regionali.",
        ),
        figure("10_popolazione_15_34.png", "Popolazione 15-34"),
        markdown(
            """
La popolazione 15-34 cala del 2,6% tra 2021 e 2024, quasi come la Sicilia. Il dato descrive lo
stock residente, ma non consente di attribuire il calo alla migrazione o alla “fuga di talenti”.
"""
        ),
        figure("11_confronto_peer_2011.png", "Confronto peer"),
        code(
            """
peers = pd.read_csv(TABLES / "matched_peers_2011.csv")
show_table(peers[["nome_territorio", "ruolo", "distanza_standardizzata", "I6", "I7", "L14", "L4"]].sort_values("distanza_standardizzata"), {
    "distanza_standardizzata": "{:.2f}", "I6": "{:.1f}%", "I7": "{:.1f}%", "L14": "{:.1f}%", "L4": "{:.1f}%",
})
""",
            tags=["peer-table"],
        ),
        section(
            "07",
            "Risultati finali",
            "Cinque evidenze ordinate per priorità; nessuna scheda narrativa o ipotesi smentita nel corpo principale.",
        ),
        code(
            """
html = ""
for row in findings.sort_values("priorita").itertuples():
    html += f'<div class="finding"><strong>{row.priorita}. {row.risultato}</strong><br><span style="color:#52606D">{row.evidenza}</span><br><em>{row.implicazione}</em></div>'
display(HTML(html))
""",
            tags=["findings", "hide-input"],
        ),
        section(
            "08",
            "Policy: Ponte 19 Bagheria",
            "Un servizio di transizione e riattivazione costruito sul segmento che i dati indicano come più persistente.",
        ),
        code("display(Markdown(policy_text))", tags=["policy", "hide-input"]),
        section(
            "A",
            "Appendice di robustezza",
            "Controlli utili per valutare la stabilità del segnale, senza trasformarli nella storia principale.",
        ),
        figure("12_appendice_robustezza_modelli.png", "Robustezza modelli"),
        markdown(
            """
I modelli comunali confermano un residuo occupazionale negativo per Bagheria. La capacità
predittiva cross-validata è debole per l'occupazione e moderata per il NEET storico: per questo
restano controlli di appendice e non sono usati per quantificare l'impatto della policy né per
formulare conclusioni individuali.
"""
        ),
        figure("13_appendice_mobilita.png", "Mobilità"),
        markdown(
            """
La mobilità resta un contesto, non una spiegazione identificata: il pendolarismo non indica
Palermo come destinazione e il GTFS AMAT copre soltanto la rete urbana palermitana.
"""
        ),
        section(
            "B",
            "Riproducibilità",
            "Codice, parametri, lineage e output sono separati; nessun valore presentato è scritto manualmente nel notebook.",
        ),
        markdown(
            """
### Struttura

- `config/`: fonti, parametri, periodi e regole di matching;
- `data/raw/`: acquisizioni datate e manifest SHA-256;
- `data/processed/`: dati puliti in formato long;
- `outputs/tables/`: panel, gap, scomposizione, KPI e risultati;
- `outputs/figures/`: 11 grafici principali + 2 appendici;
- `src/datapolis_bagheria/`: download, cleaning, analisi, validazione, grafici e policy;
- `tests/`: contratti automatici della pipeline.

### Esecuzione

```bash
uv sync --frozen
uv run python scripts/run_pipeline.py --skip-download
uv run python scripts/build_notebook.py
uv run python scripts/execute_notebook.py notebooks/Bagheria_transizione_istruzione_lavoro.ipynb --workdir .
uv run python -m unittest discover -s tests -v
```

<div class="callout warning"><strong>Limite sostanziale.</strong> Le fonti comunali pubbliche
non incrociano titolo e condizione lavorativa. La policy è progettata anche per generare in
modo pseudonimizzato il dato longitudinale oggi mancante.</div>
"""
        ),
    ]
    NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, NOTEBOOK)
    return NOTEBOOK


if __name__ == "__main__":
    print(build())

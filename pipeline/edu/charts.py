from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

from .cleaning import BAGHERIA
from .paths import FIGURES, TABLES, ensure_directories


NAVY = "#102A43"
BLUE = "#2F6BFF"
LIGHT_BLUE = "#8CB4FF"
ORANGE = "#F28E2B"
YELLOW = "#F7B801"
RED = "#D1495B"
GREEN = "#2A9D8F"
PURPLE = "#725AC1"
GREY = "#AAB2BD"
DARK_GREY = "#52606D"
LIGHT = "#EEF3F8"
WHITE = "#FFFFFF"


def _style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.labelsize": 10,
        "axes.edgecolor": "#CBD5E1",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": "#E4EAF1",
        "grid.linewidth": 0.8,
        "figure.facecolor": WHITE,
        "axes.facecolor": WHITE,
    })


def _save(fig: plt.Figure, filename: str) -> Path:
    path = FIGURES / filename
    fig.savefig(path, dpi=190, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    return path


def _footer(fig: plt.Figure, text: str, x: float = 0.06) -> None:
    fig.text(x, 0.012, text, fontsize=8.5, color=DARK_GREY)


def _label_last(ax: plt.Axes, x: float, y: float, text: str, color: str) -> None:
    ax.annotate(
        text, (x, y), xytext=(7, 0), textcoords="offset points", va="center",
        color=color, fontweight="bold", fontsize=9,
    )


def snapshot_chart() -> Path:
    summary = json.loads((TABLES / "edu_analysis_summary.json").read_text(encoding="utf-8"))
    current = summary["current_2024"]
    gaps = summary["gaps_vs_sicily_2024"]
    change = summary["change_2018_2024"]
    population_label = f"{current['population_15_24']:,.0f}".replace(",", ".")
    cards = [
        (population_label, "residenti 15-24", "perimetro della tavola lavoro", NAVY),
        (f"{current['employed_pct']:.1f}%", "occupati 15-24", f"{gaps['employment_15_24_pp']:.1f} p.p. vs Sicilia", GREEN),
        (f"{current['outside_work_study_pct']:.1f}%", "fuori da lavoro e studio", f"{change['outside_work_study_pp']:.1f} p.p. dal 2018", RED),
        (f"{current['inactive_nonstudent_pct']:.1f}%", "inattivi non studenti", f"≈ {current['inactive_nonstudent_count']:.0f} persone · +{gaps['inactive_nonstudent_15_24_pp']:.1f} p.p. vs Sicilia", ORANGE),
    ]
    fig, ax = plt.subplots(figsize=(14, 4.8))
    ax.axis("off")
    fig.suptitle(
        "Bagheria 2024: il problema residuo non è la ricerca, è l'inattività",
        x=0.04, ha="left", fontsize=20, fontweight="bold", color=NAVY,
    )
    fig.text(
        0.04, 0.86,
        "Profilo sintetico della popolazione 15-24 nella tavola comunale IstatData",
        fontsize=11, color=DARK_GREY,
    )
    for i, (value, label, note, color) in enumerate(cards):
        x = 0.035 + i * 0.245
        patch = FancyBboxPatch(
            (x, 0.19), 0.215, 0.53,
            boxstyle="round,pad=0.012,rounding_size=0.025",
            transform=ax.transAxes, facecolor=WHITE, edgecolor="#D7E0EA", linewidth=1.2,
        )
        ax.add_patch(patch)
        ax.add_patch(FancyBboxPatch(
            (x, 0.19), 0.012, 0.53,
            boxstyle="round,pad=0,rounding_size=0.006",
            transform=ax.transAxes, facecolor=color, edgecolor=color,
        ))
        ax.text(x + 0.025, 0.57, value, transform=ax.transAxes, fontsize=25,
                fontweight="bold", color=color, va="center")
        ax.text(x + 0.025, 0.43, label, transform=ax.transAxes, fontsize=11,
                fontweight="bold", color=NAVY, va="center")
        ax.text(x + 0.025, 0.29, note, transform=ax.transAxes, fontsize=8.8,
                color=DARK_GREY, va="center", wrap=True)
    _footer(fig, "Fonte: elaborazione su IstatData. Quote arrotondate; conteggi non sempre interi nella fonte.", 0.04)
    return _save(fig, "01_snapshot_bagheria_2024.png")


def historical_change_chart() -> Path:
    data = pd.read_csv(TABLES / "edu_historical_change_1991_2011.csv")
    positive = {"I6", "I7", "L14"}
    data["cambiamento_favorevole_pp"] = np.where(
        data["indicatore"].isin(positive), data["variazione_valore_pp"], -data["variazione_valore_pp"]
    )
    data["cambiamento_posizione_favorevole"] = np.where(
        data["indicatore"].isin(positive), data["variazione_percentile"], -data["variazione_percentile"]
    )
    order = ["Diploma/laurea 25-64", "Titolo universitario 30-34", "Uscita precoce 15-24", "NEET 15-29", "Occupazione 15-29"]
    data = data.set_index("metrica").reindex(order).reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.4))
    for ax, column, title in [
        (axes[0], "cambiamento_favorevole_pp", "Variazione assoluta favorevole"),
        (axes[1], "cambiamento_posizione_favorevole", "Variazione della posizione relativa"),
    ]:
        values = data[column]
        colors = [GREEN if value > 0 else RED for value in values]
        bars = ax.barh(data["metrica"][::-1], values[::-1], color=colors[::-1], height=0.62)
        ax.axvline(0, color=NAVY, linewidth=1)
        for bar, value in zip(bars, values[::-1]):
            ax.text(
                value + (0.7 if value >= 0 else -0.7),
                bar.get_y() + bar.get_height() / 2,
                f"{value:+.1f}", va="center", ha="left" if value >= 0 else "right",
                fontsize=9, fontweight="bold", color=NAVY,
            )
        ax.set_title(title, loc="left")
        ax.set_xlabel("punti percentuali" if column.endswith("pp") else "punti percentile favorevoli")
        ax.grid(axis="x")
    fig.suptitle(
        "1991-2011: Bagheria migliora nei livelli, ma perde posizione su tutti gli indicatori",
        x=0.055, ha="left", fontsize=18, fontweight="bold", color=NAVY,
    )
    fig.text(0.055, 0.91, "Valori positivi = miglioramento; nel pannello destro tutti i valori negativi indicano mancata convergenza.", fontsize=10, color=DARK_GREY)
    _footer(fig, "Fonte: Istat 8milaCensus. Per uscita precoce e NEET una diminuzione è favorevole.")
    fig.tight_layout(rect=(0, 0.045, 1, 0.88))
    return _save(fig, "02_storia_livelli_e_posizione.png")


def transition_benchmark_chart() -> Path:
    data = pd.read_csv(TABLES / "edu_historical_benchmarks_2011.csv")
    order = ["Bagheria", "Palermo", "Sicilia", "Italia"]
    specs = [
        ("I8", "Almeno licenza media 15-19"),
        ("I5", "Uscita precoce 15-24"),
        ("L4", "NEET 15-29"),
        ("L14", "Occupazione 15-29"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(13, 8.2))
    for ax, (indicator, title) in zip(axes.flat, specs):
        subset = data[data["indicatore"].eq(indicator)].set_index("territorio_nome").reindex(order)
        display_order = order[::-1]
        colors = [BLUE if name == "Bagheria" else GREY for name in display_order]
        bars = ax.barh(display_order, subset.loc[display_order, "valore"], color=colors)
        for bar, value in zip(bars, subset.loc[display_order, "valore"]):
            ax.text(value + 0.6, bar.get_y() + bar.get_height() / 2, f"{value:.1f}%", va="center", fontsize=9)
        ax.set_title(title, loc="left")
        ax.set_xlim(0, max(subset["valore"].max() * 1.2, 25))
        ax.grid(axis="x")
        ax.set_xlabel("quota percentuale")
    fig.suptitle(
        "Nel 2011 la fragilità emergeva nel passaggio dalla scuola al lavoro",
        x=0.055, ha="left", fontsize=18, fontweight="bold", color=NAVY,
    )
    fig.text(0.055, 0.925, "Bagheria aveva una copertura quasi universale del titolo di base, ma uscita precoce e NEET sopra i benchmark.", fontsize=10, color=DARK_GREY)
    _footer(fig, "Le quattro misure hanno fasce d'età diverse: descrivono il territorio, non una coorte individuale.")
    fig.tight_layout(rect=(0, 0.045, 1, 0.89))
    return _save(fig, "03_transizione_benchmark_2011.png")


def youth_composition_trend_chart() -> Path:
    data = pd.read_csv(TABLES / "edu_youth_states_2018_2024.csv", dtype={"territorio": str})
    data = data[data["territorio"].eq(BAGHERIA)].sort_values("anno")
    categories = [
        ("quota_studenti", "Studenti", BLUE),
        ("quota_occupati", "Occupati", GREEN),
        ("quota_in_cerca", "In cerca", PURPLE),
        ("quota_inattivi_non_studenti", "Inattivi non studenti", ORANGE),
    ]
    fig, ax = plt.subplots(figsize=(13, 6.8))
    x = np.arange(len(data))
    bottom = np.zeros(len(data))
    for column, label, color in categories:
        values = data[column].to_numpy()
        bars = ax.bar(x, values, bottom=bottom, label=label, color=color, width=0.72)
        for bar, value, start in zip(bars, values, bottom):
            if value >= 7:
                ax.text(bar.get_x() + bar.get_width() / 2, start + value / 2, f"{value:.1f}%",
                        ha="center", va="center", color=WHITE, fontsize=9, fontweight="bold")
        bottom += values
    ax.set_ylim(0, 100)
    ax.set_xticks(x, data["anno"].astype(int))
    ax.set_ylabel("composizione dei 15-24enni (%)")
    ax.set_title("La composizione migliora, ma l'inattività resta intorno al 19%", loc="left", fontsize=18, color=NAVY, pad=34)
    ax.text(0, 1.01, "Il calo dell'area fuori lavoro-studio è trainato soprattutto dalla riduzione di chi cerca lavoro.", transform=ax.transAxes, fontsize=10, color=DARK_GREY)
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.10))
    ax.grid(axis="y")
    _footer(fig, "Fonte: IstatData. Il 2020 non è pubblicato nella tavola lavoro e non è interpolato.")
    fig.tight_layout(rect=(0, 0.08, 1, 0.94))
    return _save(fig, "04_composizione_giovani_2018_2024.png")


def youth_benchmark_chart() -> Path:
    data = pd.read_csv(TABLES / "edu_youth_states_2018_2024.csv")
    data = data[data["anno"].eq(2024)].set_index("territorio_nome").reindex(["Bagheria", "Palermo", "Sicilia", "Italia"])
    categories = [
        ("quota_studenti", "Studenti", BLUE),
        ("quota_occupati", "Occupati", GREEN),
        ("quota_in_cerca", "In cerca", PURPLE),
        ("quota_inattivi_non_studenti", "Inattivi non studenti", ORANGE),
    ]
    fig, ax = plt.subplots(figsize=(13, 6.4))
    left = np.zeros(len(data))
    for column, label, color in categories:
        values = data[column].to_numpy()
        bars = ax.barh(data.index, values, left=left, label=label, color=color, height=0.62)
        for bar, value, start in zip(bars, values, left):
            if value >= 6:
                ax.text(start + value / 2, bar.get_y() + bar.get_height() / 2, f"{value:.1f}%",
                        ha="center", va="center", color=WHITE, fontsize=9, fontweight="bold")
        left += values
    ax.set_xlim(0, 100)
    ax.set_xlabel("composizione dei 15-24enni (%)")
    ax.set_title("Nel 2024 Bagheria concentra più inattività dei benchmark", loc="left", fontsize=18, color=NAVY, pad=34)
    ax.text(0, 1.01, "Il 19,0% inattivo non studente supera Palermo, Sicilia e Italia.", transform=ax.transAxes, fontsize=10, color=DARK_GREY)
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    ax.grid(False)
    _footer(fig, "Inattivi non studenti = condizioni 4 + 7 + 24; non include chi cerca lavoro.")
    fig.tight_layout(rect=(0, 0.09, 1, 0.94))
    return _save(fig, "05_benchmark_stati_2024.png")


def convergence_gap_chart() -> Path:
    data = pd.read_csv(TABLES / "edu_gaps_vs_sicily.csv")
    specs = [
        ("quota_occupati", "Occupazione", GREEN),
        ("quota_inattivi_non_studenti", "Inattivi non studenti", ORANGE),
        ("quota_fuori_lavoro_studio", "Fuori da lavoro e studio", RED),
    ]
    fig, ax = plt.subplots(figsize=(12.5, 6.5))
    for metric, label, color in specs:
        subset = data[data["metrica"].eq(metric)].sort_values("anno")
        ax.plot(subset["anno"], subset["gap_bagheria_sicilia_pp"], marker="o", linewidth=2.6, color=color, label=label)
        last = subset.iloc[-1]
        _label_last(ax, last["anno"], last["gap_bagheria_sicilia_pp"], f"{last['gap_bagheria_sicilia_pp']:+.1f} p.p.", color)
    ax.axhline(0, color=NAVY, linewidth=1.2)
    ax.set_xticks(sorted(data[data["dominio"].eq("giovani")]["anno"].unique()))
    ax.set_ylabel("Bagheria - Sicilia (punti percentuali)")
    ax.set_xlabel("anno")
    ax.set_title("Il recupero non si è trasformato in convergenza con la Sicilia", loc="left", fontsize=18, color=NAVY, pad=34)
    ax.text(0, 1.01, "L'occupazione resta circa 3 punti sotto; l'inattività resta stabilmente sopra.", transform=ax.transAxes, fontsize=10, color=DARK_GREY)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    ax.grid(axis="y")
    _footer(fig, "Fonte: IstatData. Per occupazione un gap negativo è sfavorevole; per inattività un gap positivo è sfavorevole.")
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    return _save(fig, "06_gap_con_sicilia_2018_2024.png")


def decomposition_chart() -> Path:
    data = pd.read_csv(TABLES / "edu_change_decomposition_2018_2024.csv")
    data = data[data["metrica"].isin(["occupati", "in_cerca", "studenti", "inattivi_non_studenti"])].copy()
    order = ["Studenti", "Occupati", "In cerca di lavoro", "Inattivi non studenti"]
    data = data.set_index("metrica_label").reindex(order).reset_index()
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.2))
    for ax, column, title, unit in [
        (axes[0], "variazione_quota_pp", "Variazione della quota", "punti percentuali"),
        (axes[1], "variazione_conteggio", "Variazione del numero", "persone stimate"),
    ]:
        values = data[column]
        colors = [GREEN if value > 0 else RED for value in values]
        bars = ax.barh(data["metrica_label"][::-1], values[::-1], color=colors[::-1], height=0.62)
        ax.axvline(0, color=NAVY, linewidth=1)
        for bar, value in zip(bars, values[::-1]):
            unit_offset = 0.25 if column.endswith("pp") else 10
            if value >= 0:
                text_x, alignment, text_color = value + unit_offset, "left", NAVY
            elif abs(value) >= (2 if column.endswith("pp") else 150):
                text_x, alignment, text_color = value + unit_offset, "left", WHITE
            else:
                text_x, alignment, text_color = value - unit_offset, "right", NAVY
            ax.text(text_x, bar.get_y() + bar.get_height() / 2,
                    f"{value:+.1f}" if column.endswith("pp") else f"{value:+.0f}",
                    va="center", ha=alignment, fontsize=9, fontweight="bold", color=text_color)
        ax.set_title(title, loc="left")
        ax.set_xlabel(unit)
        ax.grid(axis="x")
    fig.suptitle("2018-2024: il cambiamento più grande è il calo di chi cerca lavoro", x=0.055, ha="left", fontsize=18, fontweight="bold", color=NAVY)
    fig.text(0.055, 0.91, "Gli inattivi non studenti diminuiscono di appena 0,6 punti, contro -10,2 punti di chi cerca.", fontsize=10, color=DARK_GREY)
    _footer(fig, "La variazione dei conteggi combina effetto popolazione ed effetto quota; la scomposizione completa è nella tabella CSV.")
    fig.tight_layout(rect=(0, 0.045, 1, 0.88))
    return _save(fig, "07_scomposizione_cambiamento_2018_2024.png")


def adult_trend_chart() -> Path:
    data = pd.read_csv(TABLES / "edu_adult_transition_2018_2024.csv")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.9), sharex=True)
    colors = {"Bagheria": BLUE, "Sicilia": ORANGE}
    for ax, column, title in [
        (axes[0], "quota_almeno_diploma", "Almeno diploma 25-49"),
        (axes[1], "quota_occupati_25_49", "Occupazione 25-49"),
    ]:
        for territory in ["Bagheria", "Sicilia"]:
            subset = data[data["territorio_nome"].eq(territory)].dropna(subset=[column]).sort_values("anno")
            ax.plot(subset["anno"], subset[column], marker="o", linewidth=2.6, color=colors[territory], label=territory)
            last = subset.iloc[-1]
            _label_last(ax, last["anno"], last[column], f"{last[column]:.1f}%", colors[territory])
        ax.set_title(title, loc="left")
        ax.set_ylabel("quota percentuale")
        ax.set_xticks([2018, 2019, 2020, 2021, 2022, 2023, 2024])
        ax.grid(axis="y")
    axes[0].legend(frameon=False, loc="upper left")
    fig.suptitle("Tra i 25-49enni Bagheria cresce e riduce parte del divario", x=0.055, ha="left", fontsize=18, fontweight="bold", color=NAVY)
    fig.text(0.055, 0.90, "Nel 2024 resta sotto la Sicilia sia per almeno diploma (-4,1 p.p.) sia per occupazione (-5,7 p.p.).", fontsize=10, color=DARK_GREY)
    _footer(fig, "Le due misure provengono da tavole aggregate separate: non rappresentano il tasso di occupazione dei diplomati.")
    fig.tight_layout(rect=(0, 0.045, 1, 0.87))
    return _save(fig, "08_traiettoria_25_49.png")


def adult_position_chart() -> Path:
    data = pd.read_csv(TABLES / "edu_adult_transition_2018_2024.csv").dropna(subset=["quota_occupati_25_49"])
    colors = {"Bagheria": BLUE, "Palermo": PURPLE, "Sicilia": ORANGE, "Italia": GREEN}
    label_offsets = {"Bagheria": (6, 4), "Palermo": (-58, -14), "Sicilia": (8, 8), "Italia": (7, 5)}
    fig, ax = plt.subplots(figsize=(10.5, 7.2))
    for territory, color in colors.items():
        subset = data[data["territorio_nome"].eq(territory)].set_index("anno")
        start, end = subset.loc[2018], subset.loc[2024]
        ax.annotate("", xy=(end["quota_almeno_diploma"], end["quota_occupati_25_49"]),
                    xytext=(start["quota_almeno_diploma"], start["quota_occupati_25_49"]),
                    arrowprops={"arrowstyle": "->", "color": color, "lw": 2.2})
        ax.scatter([start["quota_almeno_diploma"]], [start["quota_occupati_25_49"]], s=55, color=color, alpha=0.45)
        ax.scatter([end["quota_almeno_diploma"]], [end["quota_occupati_25_49"]], s=105, color=color, edgecolor=WHITE, linewidth=1.3, label=territory)
        ax.annotate(
            territory,
            (end["quota_almeno_diploma"], end["quota_occupati_25_49"]),
            xytext=label_offsets[territory], textcoords="offset points",
            color=color, fontweight="bold",
        )
    ax.set_xlabel("almeno diploma 25-49 (%)")
    ax.set_ylabel("occupazione 25-49 (%)")
    ax.set_title("2018 → 2024: tutti avanzano, Bagheria resta nel quadrante inferiore", loc="left", fontsize=17, color=NAVY, pad=34)
    ax.text(0, 1.01, "Le frecce mostrano il cambiamento dei due aggregati territoriali, non traiettorie individuali.", transform=ax.transAxes, fontsize=10, color=DARK_GREY)
    ax.grid(True)
    ax.legend(frameon=False, loc="lower right")
    _footer(fig, "Fonte: IstatData; tavole istruzione e lavoro separate, fascia 25-49 comune.", 0.08)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    return _save(fig, "09_posizionamento_istruzione_lavoro_25_49.png")


def population_chart() -> Path:
    data = pd.read_csv(TABLES / "edu_youth_population_15_34.csv")
    colors = {"Bagheria": BLUE, "Palermo": PURPLE, "Sicilia": ORANGE, "Italia": GREEN}
    fig, ax = plt.subplots(figsize=(11.8, 6.1))
    for territory, color in colors.items():
        subset = data[data["territorio_nome"].eq(territory)].sort_values("anno")
        ax.plot(subset["anno"], subset["indice_primo_anno_100"], marker="o", linewidth=2.4, color=color, label=territory)
        last = subset.iloc[-1]
        _label_last(ax, last["anno"], last["indice_primo_anno_100"], f"{last['variazione_da_primo_anno_pct']:+.1f}%", color)
    ax.axhline(100, color=NAVY, linewidth=1)
    ax.set_xticks([2021, 2022, 2023, 2024])
    ax.set_ylabel("indice 2021 = 100")
    ax.set_xlabel("anno")
    ax.set_title("La popolazione 15-34 di Bagheria cala come quella siciliana", loc="left", fontsize=18, color=NAVY, pad=34)
    ax.text(0, 1.01, "-2,6% tra 2021 e 2024: è una variazione di stock, non una misura diretta della fuga di talenti.", transform=ax.transAxes, fontsize=10, color=DARK_GREY)
    ax.legend(frameon=False, ncol=4, loc="upper left")
    ax.grid(axis="y")
    _footer(fig, "Fonte: IstatData, popolazione per età singola 15-34.")
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    return _save(fig, "10_popolazione_15_34.png")


def peer_chart() -> Path:
    data = pd.read_csv(TABLES / "edu_matched_peers_2011.csv")
    data = data.sort_values("L14")
    median = data[data["ruolo"].eq("Peer")]["L14"].median()
    colors = [BLUE if role == "Bagheria" else GREY for role in data["ruolo"]]
    fig, ax = plt.subplots(figsize=(11.5, 6.8))
    ax.hlines(data["nome_territorio"], 0, data["L14"], color="#D8E0E8", linewidth=1.2)
    ax.scatter(data["L14"], data["nome_territorio"], s=[115 if role == "Bagheria" else 65 for role in data["ruolo"]], color=colors, zorder=3)
    ax.axvline(median, color=ORANGE, linestyle="--", linewidth=1.8, label=f"Mediana peer: {median:.1f}%")
    for row in data.itertuples():
        ax.text(row.L14 + 0.25, row.nome_territorio, f"{row.L14:.1f}%", va="center", fontsize=8.8,
                fontweight="bold" if row.ruolo == "Bagheria" else "normal", color=BLUE if row.ruolo == "Bagheria" else NAVY)
    ax.set_xlim(0, max(data["L14"]) * 1.15)
    ax.set_xlabel("occupazione 15-29 L14 (%)")
    ax.set_title("Bagheria è 4,1 punti sotto la mediana dei comuni comparabili", loc="left", fontsize=18, color=NAVY, pad=34)
    ax.text(0, 1.01, "Peer selezionati senza usare occupazione o NEET e con popolazione compresa tra 0,5 e 2 volte Bagheria.", transform=ax.transAxes, fontsize=10, color=DARK_GREY)
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x")
    _footer(fig, "Confronto ecologico 2011: migliora il benchmark, ma non identifica un effetto causale.", 0.07)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    return _save(fig, "11_confronto_peer_2011.png")


def model_robustness_chart() -> Path:
    data = pd.read_csv(TABLES / "edu_model_robustness_2011.csv")
    labels = {
        "A_istruzione": "Istruzione",
        "B_istruzione_mobilita": "+ mobilità",
        "C_contesto_territoriale": "+ contesto",
    }
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.7))
    for ax, outcome, title, color in [
        (axes[0], "L14", "Occupazione 15-29: osservato - previsto", GREEN),
        (axes[1], "L4", "NEET 15-29: osservato - previsto", RED),
    ]:
        subset = data[data["outcome"].eq(outcome)].copy()
        x = np.arange(len(subset))
        y = subset["residuo_bagheria"].to_numpy()
        low = y - subset["residuo_ci95_basso"].to_numpy()
        high = subset["residuo_ci95_alto"].to_numpy() - y
        ax.errorbar(x, y, yerr=[low, high], fmt="o", color=color, ecolor=color, capsize=5, markersize=8)
        ax.axhline(0, color=NAVY, linewidth=1)
        ax.set_xticks(x, subset["modello"].map(labels))
        ax.set_ylabel("residuo (punti percentuali)")
        ax.set_title(title, loc="left")
        ax.grid(axis="y")
        for i, row in enumerate(subset.itertuples()):
            ax.annotate(f"{row.residuo_bagheria:+.1f}\nCV R² {row.r2_cv_10fold:.2f}", (i, row.residuo_bagheria),
                        xytext=(0, 10 if row.residuo_bagheria >= 0 else -32), textcoords="offset points", ha="center", fontsize=8)
    fig.suptitle("Appendice di robustezza: il deficit occupazionale resta, ma i modelli spiegano poco", x=0.055, ha="left", fontsize=18, fontweight="bold", color=NAVY)
    _footer(fig, "Bagheria esclusa dal training; intervalli bootstrap 95%. Analisi ecologica, non causale.")
    fig.tight_layout(rect=(0, 0.05, 1, 0.91))
    return _save(fig, "12_appendice_robustezza_modelli.png")


def mobility_appendix_chart() -> Path:
    data = pd.read_csv(TABLES / "edu_commuting_appendix.csv").set_index("territorio_nome").reindex(["Bagheria", "Palermo", "Sicilia", "Italia"])
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6))
    colors = [BLUE, GREY, GREY, GREY]
    bars = axes[0].bar(data.index, data["quota_lavoratori_fuori_comune_sui_pendolari"], color=colors)
    for bar, value in zip(bars, data["quota_lavoratori_fuori_comune_sui_pendolari"]):
        axes[0].text(bar.get_x() + bar.get_width() / 2, value + 0.8, f"{value:.1f}%", ha="center", fontsize=9)
    axes[0].set_title("Pendolari per lavoro fuori comune (2019)", loc="left")
    axes[0].set_ylabel("% dei pendolari per lavoro")
    axes[0].grid(axis="y")
    x = np.arange(len(data))
    axes[1].bar(x - 0.18, data["M2"], width=0.36, label="Fuori comune M2", color=PURPLE)
    axes[1].bar(x + 0.18, data["M6"], width=0.36, label="Mezzo collettivo M6", color=ORANGE)
    axes[1].set_xticks(x, data.index)
    axes[1].set_ylabel("indicatore 2011 (%)")
    axes[1].set_title("Mobilità complessiva e collettiva (2011)", loc="left")
    axes[1].legend(frameon=False)
    axes[1].grid(axis="y")
    fig.suptitle("Appendice mobilità: il mercato esterno conta, l'accessibilità non è misurata", x=0.055, ha="left", fontsize=18, fontweight="bold", color=NAVY)
    _footer(fig, "Il 2019 non identifica Palermo come destinazione; M2 e M6 hanno denominatori diversi.")
    fig.tight_layout(rect=(0, 0.05, 1, 0.91))
    return _save(fig, "13_appendice_mobilita.png")


def build_all_charts() -> list[Path]:
    ensure_directories()
    _style()
    for path in FIGURES.glob("*.png"):
        path.unlink()
    builders = [
        snapshot_chart,
        historical_change_chart,
        transition_benchmark_chart,
        youth_composition_trend_chart,
        youth_benchmark_chart,
        convergence_gap_chart,
        decomposition_chart,
        adult_trend_chart,
        adult_position_chart,
        population_chart,
        peer_chart,
        model_robustness_chart,
        mobility_appendix_chart,
    ]
    paths = [builder() for builder in builders]
    catalogue = [
        {"order": index, "file": path.name, "path": str(path.relative_to(FIGURES.parent.parent))}
        for index, path in enumerate(paths, start=1)
    ]
    (FIGURES / "chart_catalogue.json").write_text(
        json.dumps(catalogue, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return paths

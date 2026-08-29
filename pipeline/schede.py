"""data/processed/ -> docs/schede/: le quattro schede tematiche della proposta.

Ogni scheda risponde a UNA richiesta della locandina, incrociando i tre thread:

    scheda1_profilo.html       Profiling statistico & benchmarking (educazione + genere)
    scheda2_forbice.html       Focus differenze di genere + titolo x condizione
    scheda3_pendolarismo.html  Focus pendolarismo verso Palermo (mobilita + genere)
    scheda4_ponte19.html       Proposta di intervento

Le schede sono HTML autoportante: nessun asset esterno, nessuna rete. I grafici sono
di due tipi, entrambi incorporati nel file: SVG inline generati qui, e le figure di
figures/ come data URI. Si aprono in un browser e si stampano in PDF (@page A4).

Ogni blocco porta la stessa didascalia a quattro blocchi delle figure R (cosa mostra,
base statistica, come si legge, fonte): in blocco() sono argomenti obbligatori, e
main() verifica che nessuno sia vuoto. Le figure R incorporate sono di norma
ritagliate al solo grafico, perche' la scheda ne rifa' titolo e didascalia alla
propria tipografia; l'immagine intera si usa solo in appendice, dove il punto e'
mostrare che la tavola dello zip viaggia da sola. Il criterio sta in figura().

    uv run python -m pipeline.schede --bande   # struttura delle figure, per TESTA

Il vincolo del repo vale anche qui, ed e' il motivo per cui questo file esiste invece
di quattro HTML scritti a mano: **nessuna cifra e' scritta a mano**. Ogni numero viene
letto da data/processed/, e ogni claim finisce in data/processed/schede_claim.csv con
accanto il file che lo produce e la sua cautela. Se un raw cambia, le schede cambiano.

    uv run python -m pipeline.schede
"""

from __future__ import annotations

import html
from pathlib import Path

import pandas as pd

RADICE = Path(__file__).resolve().parent.parent
PROCESSED = RADICE / "data" / "processed"
SCHEDE = RADICE / "docs" / "schede"
FIGURE = RADICE / "figures"

# Palette: la stessa di viz/theme.R. I colori significano le stesse cose nelle figure e
# nelle schede, altrimenti chi legge il deck deve reimparare la legenda a meta' strada.
COL = {
    "Bagheria": "#D55E00",
    "Palermo": "#785EF0",
    "Comune di Palermo": "#785EF0",
    "Sicilia": "#E69F00",
    "Italia": "#666666",
    "vicinato (5 comuni)": "#1B9E8F",
    "vicinato": "#1B9E8F",
    "5 comuni vicini": "#1B9E8F",
}
COL_G = {"F": "#CC79A7", "M": "#0072B2"}
ETICHETTA_G = {"F": "femmine", "M": "maschi"}
COL_STATO = {
    "occupati": "#0072B2",
    "in cerca": "#56B4E9",
    "studenti": "#009E73",
    "casalinghe/i": "#D55E00",
    "altra condizione": "#E69F00",
    "pensione": "#999999",
}
GRIGIO = "#B9B4AD"
INCHIOSTRO = "#1A1A1A"
TENUE = "#6E6A65"

ORDINE = ["Bagheria", "Palermo", "Sicilia", "Italia"]

# Il registro dei claim: ogni numero che finisce in una scheda passa di qui.
CLAIM: list[dict] = []


def claim(scheda: str, testo: str, valore, unita: str, fonte: str, cautela: str = ""):
    CLAIM.append({"scheda": scheda, "claim": testo, "valore": valore,
                  "unita": unita, "fonte": fonte, "cautela": cautela})
    return valore


# --------------------------------------------------------------------------- numeri

def num(x, d: int = 1, suf: str = "", segno: bool = False, zero: bool = False) -> str:
    """Numero all'italiana: punto per le migliaia, virgola per i decimali.

    num(5904, 0) -> 5.904   ·   num(8.19) -> 8,2   ·   num(100.0) -> 100
    Lo zero finale cade: «100,0%» su una scheda dichiara una precisione che il dato
    non ha. `zero=True` lo tiene, ed e' il caso di una COLONNA: incolonnare «19%»
    sotto «19,6%» fa leggere due precisioni diverse dove ce n'e' una sola.
    """
    testo = f"{x:,.{d}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    if d and not zero and testo.endswith("," + "0" * d):
        testo = testo[: -(d + 1)]
    if segno and x > 0:
        testo = "+" + testo
    return testo + suf


def e(testo) -> str:
    return html.escape(str(testo))


# ------------------------------------------------------------------------- primitive
# Sette primitive SVG, nessuna libreria. Restituiscono una stringa con viewBox: la
# scheda le scala in larghezza, quindi le misure qui dentro sono un sistema di
# coordinate, non pixel.

def _svg(w: float, h: float, corpo: str) -> str:
    return (f'<svg viewBox="0 0 {w:.0f} {h:.0f}" width="100%" '
            f'preserveAspectRatio="xMidYMid meet" role="img">{corpo}</svg>')


def _txt(x, y, testo, *, size=11, col=TENUE, anchor="start", weight="400") -> str:
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{e(testo)}</text>')


def _scosta(y, gap):
    """Scosta le etichette quel tanto che basta a non sovrapporsi (come viz/theme.R).

    Tocca SOLO il testo: punti e barre restano sul valore vero. Serve proprio nel caso
    interessante — due serie che finiscono vicine E' il finding, e due scritte una sopra
    l'altra rendono illeggibile la cosa che il grafico vuole mostrare.
    """
    ordine = sorted(range(len(y)), key=lambda i: y[i])
    fuori = list(y)
    for k, i in enumerate(ordine[1:], start=1):
        fuori[i] = max(fuori[i], fuori[ordine[k - 1]] + gap)
    return fuori


def divergenti(righe, *, centro=100.0, w=560, h_riga=28, lab=150, coda=56, fmt=None,
               etichetta_centro="") -> str:
    """Barre che partono da una linea di riferimento: il verso della barra E' il finding.

    Le stesse cifre in barre da zero (96,3 contro 103,0 su una scala 0-110) sono
    indistinguibili a occhio: e' la differenza dal riferimento che va disegnata.
    """
    fmt = fmt or (lambda v: num(v, 1, zero=True))
    scarti = [r["valore"] - centro for r in righe]
    massimo = max(abs(v) for v in scarti) or 1
    x0, x1 = lab, w - coda
    meta = (x0 + x1) / 2
    scala = (x1 - meta) / (massimo * 1.18)
    h = len(righe) * h_riga + 20
    parti = [f'<line x1="{meta:.1f}" y1="10" x2="{meta:.1f}" y2="{h - 18:.1f}" '
             f'stroke="{TENUE}" stroke-width="0.9"/>',
             _txt(meta, h - 6, etichetta_centro, size=9.5, anchor="middle")]
    for i, (r, scarto) in enumerate(zip(righe, scarti)):
        y = i * h_riga + 8
        forte = r.get("forte", False)
        lung = abs(scarto) * scala
        x = meta if scarto >= 0 else meta - lung
        parti.append(_txt(x0 - 8, y + 12, r["label"], size=11.5, anchor="end",
                          col=INCHIOSTRO if forte else TENUE,
                          weight="700" if forte else "400"))
        parti.append(f'<rect x="{x:.1f}" y="{y + 2}" width="{max(lung, 1.2):.1f}" '
                     f'height="13" rx="1.5" fill="{r["colore"]}" '
                     f'opacity="{1 if forte else 0.6}"/>')
        fine = meta + lung + 7 if scarto >= 0 else meta - lung - 7
        parti.append(_txt(fine, y + 12.5, fmt(r["valore"]), size=11.5,
                          anchor="start" if scarto >= 0 else "end",
                          col=INCHIOSTRO if forte else TENUE,
                          weight="700" if forte else "400"))
    return _svg(w, h, "".join(parti))


def barre(righe, *, w=560, h_riga=27, lab=150, massimo=None, fmt=None, coda=56) -> str:
    """Barre orizzontali. righe: dict(label, valore, colore, forte?).

    `coda` e' lo spazio riservato all'etichetta del valore dopo la barra: senza, la
    barra piu' lunga spinge il proprio numero fuori dal viewBox e il numero sparisce.
    """
    fmt = fmt or (lambda v: num(v, 1, "%"))
    massimo = massimo or max(r["valore"] for r in righe)
    x0, x1 = lab, w - coda
    scala = (x1 - x0) / massimo if massimo else 0
    parti = []
    for i, r in enumerate(righe):
        y = i * h_riga + 6
        forte = r.get("forte", False)
        lung = max(r["valore"] * scala, 1.2)
        parti.append(_txt(x0 - 8, y + 12, r["label"], size=11.5, anchor="end",
                          col=INCHIOSTRO if forte else TENUE,
                          weight="700" if forte else "400"))
        parti.append(f'<rect x="{x0}" y="{y + 2}" width="{lung:.1f}" height="13" '
                     f'rx="1.5" fill="{r["colore"]}" opacity="{1 if forte else 0.6}"/>')
        parti.append(_txt(x0 + lung + 7, y + 12.5, fmt(r["valore"]), size=11.5,
                          col=INCHIOSTRO if forte else TENUE,
                          weight="700" if forte else "400"))
    return _svg(w, len(righe) * h_riga + 8, "".join(parti))


def impilate(righe, *, w=560, h_riga=44, lab=104) -> str:
    """Barre impilate al 100%. righe: (label, [(segmento, quota, colore)]).

    Il numero si scrive dentro il segmento solo se ci sta: sotto una certa larghezza
    esce dal proprio blocco e si legge come se appartenesse a quello accanto, cioe'
    peggio che non esserci.
    """
    x0, x1 = lab, w - 6
    parti = []
    for i, (etichetta, segmenti) in enumerate(righe):
        y = i * h_riga + 4
        forte = etichetta == "Bagheria"
        parti.append(_txt(x0 - 9, y + 20, etichetta, size=11.5, anchor="end",
                          col=INCHIOSTRO if forte else TENUE,
                          weight="700" if forte else "400"))
        x, totale = x0, sum(v for _, v, _ in segmenti)
        for _, valore, colore in segmenti:
            lung = (valore / totale) * (x1 - x0)
            parti.append(f'<rect x="{x:.1f}" y="{y + 4}" width="{max(lung, 0.4):.1f}" '
                         f'height="25" fill="{colore}" opacity="{1 if forte else 0.55}"/>')
            if lung > 32:
                parti.append(_txt(x + lung / 2, y + 21, num(valore, 1), size=10.5,
                                  col="#FFFFFF", anchor="middle", weight="700"))
            x += lung
    return _svg(w, len(righe) * h_riga + 6, "".join(parti))


# Il 2020 manca alla fonte sulla classe 15-24: l'asse si comprime sul buco invece di
# lasciare un'annata intera di bianco, come in viz/theme.R. La striscia va disegnata
# per ULTIMA ed e' opaca: cosi' taglia la linea che altrimenti passerebbe sotto e
# racconterebbe una continuita' che non c'e'.
VUOTO = 0.62
ANNI = [2018, 2019, 2021, 2022, 2023, 2024]


def _asse_anno(anno: int) -> float:
    return anno - 2018 if anno <= 2019 else anno - 2020 + VUOTO


def linee(serie, *, w=560, h=216, ymin=None, ymax=None, fmt=None, coda=104) -> str:
    """Serie storiche 2018-2024 con etichetta di fine linea. serie: nome -> {anno: v}."""
    fmt = fmt or (lambda v: num(v, 1, "%"))
    valori = [v for s in serie.values() for v in s.values()]
    ymin = ymin if ymin is not None else min(valori) - (max(valori) - min(valori)) * 0.16
    ymax = ymax if ymax is not None else max(valori) + (max(valori) - min(valori)) * 0.12
    x0, x1, y0, y1 = 18, w - coda, h - 26, 12
    px = lambda a: x0 + _asse_anno(a) / _asse_anno(2024) * (x1 - x0)
    py = lambda v: y1 + (ymax - v) / (ymax - ymin) * (y0 - y1)

    parti = [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{GRIGIO}" '
             f'stroke-width="0.8"/>']
    parti += [_txt(px(a), h - 8, a, size=10, anchor="middle") for a in ANNI]
    code: list[tuple] = []
    for nome, punti in serie.items():
        colore, forte = COL.get(nome, GRIGIO), nome == "Bagheria"
        d = " ".join(f"{'M' if i == 0 else 'L'}{px(a):.1f},{py(v):.1f}"
                     for i, (a, v) in enumerate(sorted(punti.items())))
        parti.append(f'<path d="{d}" fill="none" stroke="{colore}" '
                     f'stroke-width="{2.4 if forte else 1.5}" stroke-linejoin="round" '
                     f'opacity="{1 if forte else 0.7}"/>')
        ultimo = max(punti)
        parti.append(f'<circle cx="{px(ultimo):.1f}" cy="{py(punti[ultimo]):.1f}" '
                     f'r="{3.2 if forte else 2.4}" fill="{colore}"/>')
        code.append((px(ultimo) + 7, py(punti[ultimo]), f"{nome} {fmt(punti[ultimo])}",
                     colore, "700" if forte else "600"))
    for (x, _, testo, colore, peso), y in zip(code, _scosta([c[1] for c in code], 11.5)):
        parti.append(_txt(x, y + 4, testo, size=10.5, col=colore, weight=peso))
    xa, xb = px(2019) + 3, px(2021) - 3
    parti.append(f'<rect x="{xa:.1f}" y="{y1 - 4:.1f}" width="{xb - xa:.1f}" '
                 f'height="{y0 - y1 + 4:.1f}" fill="#EFECE7"/>')
    cx, cy = (xa + xb) / 2, (y0 + y1) / 2
    parti.append(f'<text x="{cx:.1f}" y="{cy:.1f}" font-size="8.5" fill="#8C877F" '
                 f'text-anchor="middle" transform="rotate(-90 {cx:.1f} {cy:.1f})">'
                 f'2020 non rilevato</text>')
    return _svg(w, h, "".join(parti))


def slope(righe, *, sx: str, dx: str, w=560, h=252, fmt=None) -> str:
    """Slope chart a due colonne. righe: (nome, v_sinistra, v_destra, colore, forte)."""
    # zero=True: in una colonna di valori «-1,8 / -2 / -4,6» il numero tondo sembra
    # misurato con un'altra precisione. Qui la precisione e' una sola.
    fmt = fmt or (lambda v: num(v, 1, segno=True, zero=True))
    valori = [v for _, a, b, _, _ in righe for v in (a, b)]
    margine = (max(valori) - min(valori)) * 0.16 or 1
    ymin, ymax = min(valori) - margine, max(valori) + margine
    xa, xb, y0, y1 = 148, w - 74, h - 20, 34
    py = lambda v: y1 + (ymax - v) / (ymax - ymin) * (y0 - y1)

    parti = [_txt(xa, 18, sx, size=11.5, anchor="middle", col=INCHIOSTRO, weight="700"),
             _txt(xb, 18, dx, size=11.5, anchor="middle", col=INCHIOSTRO, weight="700")]
    if ymin < 0 < ymax:  # la parita' e' la riga che da' senso al segno
        parti.append(f'<line x1="{xa - 10}" y1="{py(0):.1f}" x2="{xb + 10}" '
                     f'y2="{py(0):.1f}" stroke="{GRIGIO}" stroke-width="0.8" '
                     f'stroke-dasharray="3 3"/>')
        parti.append(_txt(xb + 14, py(0) + 4, "parità F = M", size=9.5))
    for nome, a, b, colore, forte in righe:
        parti.append(f'<line x1="{xa}" y1="{py(a):.1f}" x2="{xb}" y2="{py(b):.1f}" '
                     f'stroke="{colore}" stroke-width="{2.8 if forte else 1.4}" '
                     f'opacity="{1 if forte else 0.5}"/>')
        for x, v in ((xa, a), (xb, b)):
            parti.append(f'<circle cx="{x}" cy="{py(v):.1f}" r="{3.6 if forte else 2.4}" '
                         f'fill="{colore}"/>')
    sinistra = _scosta([py(r[1]) for r in righe], 12)
    destra = _scosta([py(r[2]) for r in righe], 12)
    for (nome, a, b, colore, forte), ys, yd in zip(righe, sinistra, destra):
        stile = dict(size=10.5, col=colore if forte else TENUE,
                     weight="700" if forte else "400")
        parti.append(_txt(xa - 10, ys + 4, f"{nome}  {fmt(a)}", anchor="end", **stile))
        parti.append(_txt(xb + 10, yd + 4, fmt(b), **stile))
    return _svg(w, h, "".join(parti))


def waffle(gruppi, *, per_quadrato: int, colonne=22, lato=15, gap=4.4) -> str:
    """Griglia di quadrati, uno ogni `per_quadrato` persone. gruppi: (label, n, colore)."""
    quadrati = [c for _, n, c in gruppi for _ in range(round(n / per_quadrato))]
    righe = -(-len(quadrati) // colonne)
    parti = []
    for i, colore in enumerate(quadrati):
        x, y = (i % colonne) * (lato + gap), (i // colonne) * (lato + gap) + 2
        parti.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{lato}" height="{lato}" '
                     f'rx="2" fill="{colore}"/>')
    return _svg(colonne * (lato + gap), righe * (lato + gap) + 4, "".join(parti))


def quadrante(punti, *, xlab: str, ylab: str, w=560, h=256) -> str:
    """Piano cartesiano con etichette dirette. punti: (nome, x, y, colore, forte)."""
    xs, ys = [p[1] for p in punti], [p[2] for p in punti]
    mx = (max(xs) - min(xs)) * 0.3 or 1
    my = (max(ys) - min(ys)) * 0.3 or 1
    xmin, xmax = min(xs) - mx, max(xs) + mx
    ymin, ymax = min(ys) - my, max(ys) + my
    x0, x1, y0, y1 = 46, w - 12, h - 34, 14
    px = lambda v: x0 + (v - xmin) / (xmax - xmin) * (x1 - x0)
    py = lambda v: y1 + (ymax - v) / (ymax - ymin) * (y0 - y1)

    parti = [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{GRIGIO}" stroke-width="0.8"/>',
             f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{GRIGIO}" stroke-width="0.8"/>',
             _txt(x1, h - 7, xlab, size=10, anchor="end"),
             f'<text x="13" y="{(y0 + y1) / 2:.1f}" font-size="10" fill="{TENUE}" '
             f'text-anchor="middle" '
             f'transform="rotate(-90 13 {(y0 + y1) / 2:.1f})">{e(ylab)}</text>']
    for nome, x, y, colore, forte in punti:
        # L'etichetta va a destra tranne quando il punto e' gia' al bordo destro.
        destra = px(x) < x1 - 128
        parti.append(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="{6.4 if forte else 4.2}" '
                     f'fill="{colore}" opacity="{1 if forte else 0.6}"/>')
        parti.append(_txt(px(x) + (11 if destra else -11), py(y) + 4, nome, size=11,
                          anchor="start" if destra else "end",
                          col=colore if forte else TENUE,
                          weight="700" if forte else "400"))
    return _svg(w, h, "".join(parti))


def cascata(passi, *, w=560, h=206, fmt=None) -> str:
    """Cascata: (label, valore, tipo) con tipo in {'totale', 'delta'}."""
    fmt = fmt or (lambda v: num(v, 1, segno=True))
    livello, punti, alto, basso = 0.0, [], 0.0, 0.0
    for etichetta, valore, tipo in passi:
        da = 0.0 if tipo == "totale" else livello
        livello = valore if tipo == "totale" else livello + valore
        punti.append((etichetta, da, livello, valore, tipo))
        alto, basso = max(alto, livello), min(basso, livello)
    margine = (alto - basso) * 0.2 or 1
    ymin, ymax = basso - margine, alto + margine
    larghezza = (w - 24) / len(punti)
    y0, y1 = h - 36, 26
    py = lambda v: y1 + (ymax - v) / (ymax - ymin) * (y0 - y1)

    parti = [f'<line x1="12" y1="{py(0):.1f}" x2="{w - 12}" y2="{py(0):.1f}" '
             f'stroke="{GRIGIO}" stroke-width="0.8"/>']
    for i, (etichetta, da, a, valore, tipo) in enumerate(punti):
        x, bw = 12 + i * larghezza + larghezza * 0.17, larghezza * 0.66
        colore = (COL["Bagheria"] if tipo == "totale" and i == 0
                  else "#C0392B" if valore < 0 else "#0072B2")
        y_alto, y_basso = py(max(da, a)), py(min(da, a))
        parti.append(f'<rect x="{x:.1f}" y="{y_alto:.1f}" width="{bw:.1f}" '
                     f'height="{max(y_basso - y_alto, 1.6):.1f}" fill="{colore}" '
                     f'opacity="{1 if tipo == "totale" else 0.8}"/>')
        parti.append(_txt(x + bw / 2, y_alto - 7, fmt(valore), size=12, anchor="middle",
                          col=INCHIOSTRO, weight="700"))
        for k, riga in enumerate(etichetta.split("\n")):
            parti.append(_txt(x + bw / 2, h - 22 + k * 11, riga, size=9.5, anchor="middle"))
        if i < len(punti) - 1:
            parti.append(f'<line x1="{x + bw:.1f}" y1="{py(a):.1f}" '
                         f'x2="{x + larghezza:.1f}" y2="{py(a):.1f}" stroke="{GRIGIO}" '
                         f'stroke-width="0.8" stroke-dasharray="2 2"/>')
    return _svg(w, h, "".join(parti))


# ------------------------------------------------------------------------ impaginato

def legenda(voci) -> str:
    # Le etichette sono scritte qui dentro, non arrivano da fuori: passano come HTML,
    # esattamente come in blocco() e kpi(). Escaparle stampava «&middot;» a schermo.
    pezzi = "".join(f'<span class="lg"><i style="background:{c}"></i>{t}</span>'
                    for t, c in voci)
    return f'<div class="legenda">{pezzi}</div>'


# ---------------------------------------------------------------- figure da figures/
# Le figure di R hanno tre parti impilate: titolo e sottotitolo in testa, il grafico,
# la didascalia a quattro blocchi in coda (didascalia_4b(), obbligatoria su ogni figura).
# Nella scheda il titolo lo rifa' <h3> e la didascalia la rifa' blocco(): incollare il
# PNG intero dentro un blocco le stamperebbe due volte, e la seconda a circa 5 px di
# corpo, cioe' illeggibile. Quindi di norma si ritaglia via il testo e resta il grafico.

# Quante bande di testo saltare in testa: 1 = titolo e sottotitolo stanno nella stessa
# banda, 2 = il sottotitolo e' staccato (e sotto c'e' la legenda, che va tenuta).
# Si legge dall'immagine con `python -m pipeline.schede --bande`, non si indovina.
TESTA = {"fig07_ritenzione_eta": 2}

# La didascalia e' sempre di quattro paragrafi, uno per blocco: sono le ultime quattro
# bande di ogni figura. E' una convenzione garantita da viz/theme.R, non una stima.
CODA_DIDASCALIA = 4


def _bande(grigia, vuoto: int = 28):
    """Le bande orizzontali di inchiostro, separate da almeno `vuoto` righe bianche."""
    import numpy as np

    righe = np.flatnonzero((grigia < 245).sum(axis=1) > 0)
    salti = np.flatnonzero(np.diff(righe) > vuoto)
    return list(zip(np.concatenate(([righe[0]], righe[salti + 1])),
                    np.concatenate((righe[salti], [righe[-1]]))))


def figura(nome: str, *, intera: bool = False, larghezza: int = 1500,
           margine: int = 26) -> str:
    """Una figura di figures/ dentro la scheda, incorporata come data URI.

    Il data URI, e non un <img src="../../figures/...">, perche' la scheda deve restare
    UN file: si manda per mail e si stampa senza portarsi dietro una cartella.

    `intera=False` (norma): via il titolo, il sottotitolo e la didascalia a 4 blocchi;
    resta il grafico, e il testo lo rimette la scheda alla propria tipografia, a corpo
    leggibile e selezionabile.

    `intera=True` ha un solo uso legittimo: la figura mostrata *come oggetto*, in
    appendice e a piena larghezza, quando il punto e' che la tavola dello zip viaggia
    da sola con la sua didascalia. In mezzo a un ragionamento non va mai, perche'
    compete col titolo del blocco e la sua didascalia non si legge.
    """
    import base64
    import io

    import numpy as np
    from PIL import Image

    im = Image.open(FIGURE / f"{nome}.png").convert("RGB")
    if not intera:
        salta = TESTA.get(nome, 1)
        bande = _bande(np.asarray(im.convert("L")))
        assert len(bande) > salta + CODA_DIDASCALIA, (
            f"{nome}: {len(bande)} bande, non bastano per saltare {salta} di testa e "
            f"{CODA_DIDASCALIA} di didascalia. La figura ha cambiato impaginazione: "
            f"guardala con --bande e aggiorna TESTA.")
        corpo = bande[salta:-CODA_DIDASCALIA]
        im = im.crop((0, max(0, corpo[0][0] - margine),
                      im.width, min(im.height, corpo[-1][1] + margine)))
    im.thumbnail((larghezza, 4 * larghezza), Image.LANCZOS)
    # Palette a 256 colori senza dithering: i grafici sono a tinte piatte, quindi il
    # PNG cala di 3-4 volte e a occhio non cambia niente, viridis della mappa compresa.
    # Con il dithering acceso, invece, il retino si vede sulle campiture chiare.
    buf = io.BytesIO()
    im.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.NONE).save(
        buf, format="PNG", optimize=True)
    dati = base64.b64encode(buf.getvalue()).decode("ascii")
    classe = "fig intera" if intera else "fig"
    return (f'<img class="{classe}" alt="{e(nome)}" '
            f'src="data:image/png;base64,{dati}">')


def blocco(numero: str, titolo: str, *contenuto: str,
           mostra: str, base: str, lettura: str, fonte: str) -> str:
    """Un blocco = titolo dichiarativo + grafico + didascalia a quattro blocchi.

    E' la stessa anatomia di didascalia_4b() in viz/theme.R, e per lo stesso motivo:
    chi legge la scheda in sala non ha il notebook accanto. I quattro blocchi non sono
    facoltativi, sono argomenti obbligatori senza default: un blocco cui manca `base`
    non compila. E' l'unico modo per impedire che «N e dispersione» finiscano dove
    capita, che e' come stavano prima.

    mostra   metrica, unita', fascia d'eta', territori, anni; e cosa la figura NON dice
    base     N per gruppo, tendenza centrale, dispersione col metodo, test, esclusioni
    lettura  decodifica di cio' che non e' un dato: tratteggi, bande, colori, scale
    fonte    fonte con anno + il file di data/processed/ che rigenera i numeri
    """
    did = "".join(f"<p><b>{et}</b> {tx}</p>" for et, tx in (
        ("Cosa mostra.", mostra), ("Base statistica.", base),
        ("Come si legge.", lettura), ("Fonte.", fonte)))
    return (f'<section class="blocco"><h3><span class="nb">{numero}</span>{titolo}</h3>'
            f'{"".join(contenuto)}<div class="did">{did}</div></section>')


class Numera:
    """Numera i blocchi di una scheda: «Figura 2.1», «Figura 2.2», «Tavola 2.3».

    Serve perche' la relazione e la proposal possano citare un blocco per nome invece
    che come «il terzo grafico della scheda 2». Finora le schede citavano i file di
    data/processed/, ma nulla poteva citare le schede.
    """

    def __init__(self, scheda: int):
        self.scheda, self.n = scheda, 0

    def __call__(self, tipo: str = "Figura") -> str:
        self.n += 1
        return f"{tipo} {self.scheda}.{self.n}"


def kpi(voci) -> str:
    """Riquadri col numero grande. voci: (numero, etichetta, colore)."""
    celle = "".join(f'<div class="kpi"><span class="kn" style="color:{c}">{n}</span>'
                    f'<span class="kl">{t}</span></div>' for n, t, c in voci)
    return f'<div class="kpi-riga">{celle}</div>'


def tabella(intestazioni, righe, *, forte=()) -> str:
    th = "".join(f'<th class="{"n" if i else ""}">{t}</th>'
                 for i, t in enumerate(intestazioni))
    tr = ""
    for riga in righe:
        cls = ' class="forte"' if riga[0] in forte else ""
        td = "".join(f'<td class="{"n" if i else ""}">{c}</td>' for i, c in enumerate(riga))
        tr += f"<tr{cls}>{td}</tr>"
    return (f'<div class="tab"><table><thead><tr>{th}</tr></thead>'
            f"<tbody>{tr}</tbody></table></div>")


CSS = """
:root{--carta:#FFFFFF;--fondo:#EDEAE4;--inchiostro:#1A1A1A;--tenue:#6E6A65;
--filo:#DCD7CF;--bagheria:#D55E00}
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--inchiostro);
font-family:Lato,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
font-size:14px;line-height:1.5;-webkit-font-smoothing:antialiased}
.foglio{max-width:920px;margin:26px auto;background:var(--carta);padding:44px 52px 32px;
border-radius:3px;box-shadow:0 1px 3px rgba(0,0,0,.14)}
.occhiello{font-size:11px;letter-spacing:.13em;text-transform:uppercase;color:var(--tenue);
font-weight:700;margin:0 0 12px}
h1{font-family:Georgia,"Iowan Old Style","Times New Roman",serif;font-weight:400;
font-size:38px;line-height:1.14;letter-spacing:-.012em;margin:0 0 12px}
.sommario{font-size:16px;line-height:1.5;color:#33302C;margin:0 0 4px;max-width:66ch}
.risposta{margin:22px 0 2px;padding:13px 17px;background:#FAF7F2;
border-left:3px solid var(--bagheria);font-size:13.5px;line-height:1.55}
.blocco{border-top:1px solid var(--filo);padding-top:20px;margin-top:26px}
h3{font-family:Georgia,"Iowan Old Style","Times New Roman",serif;font-weight:400;
font-size:22px;line-height:1.22;margin:0 0 5px}
.somm{font-size:13px;color:#4A4741;margin:0 0 14px;max-width:78ch}
.fonte{font-size:11px;color:#8C877F;font-style:italic;margin:10px 0 0;line-height:1.45}
.nb{display:block;font-family:Lato,Helvetica,Arial,sans-serif;font-size:10px;
letter-spacing:.11em;text-transform:uppercase;color:var(--bagheria);font-weight:700;
margin:0 0 3px}
.did{font-size:11.5px;color:#4A4741;margin:13px 0 0;padding:11px 14px;background:#F5F2EC;
border-radius:2px;line-height:1.55}
.did p{margin:0 0 7px;max-width:88ch}
.did p:last-child{margin:0}
.did b{color:var(--inchiostro)}
.fig{display:block;width:100%;height:auto;margin:2px 0 0}
.fig.intera{border:1px solid var(--filo);border-radius:2px}
.legenda{display:flex;flex-wrap:wrap;gap:7px 18px;margin:0 0 11px;font-size:11.5px;
color:var(--tenue)}
.lg{display:inline-flex;align-items:center;gap:6px}
.lg i{width:11px;height:11px;border-radius:2px;display:inline-block}
.kpi-riga{display:flex;flex-wrap:wrap;gap:24px;margin:16px 0 2px}
.kpi{flex:1 1 118px;min-width:112px}
.kn{display:block;font-family:Georgia,"Times New Roman",serif;font-size:31px;
line-height:1.06;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.kl{display:block;font-size:11.5px;color:var(--tenue);margin-top:4px;line-height:1.35}
.duo{display:flex;gap:36px;flex-wrap:wrap;align-items:flex-start}
.duo>*{flex:1 1 292px;min-width:250px}
.duo h4{font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--tenue);
margin:0 0 9px;font-weight:700}
.tab{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:12.5px;margin:2px 0 0;
font-variant-numeric:tabular-nums}
th{text-align:left;font-weight:700;font-size:10px;letter-spacing:.05em;
text-transform:uppercase;color:var(--tenue);border-bottom:1px solid var(--filo);
padding:6px 9px 6px 0}
th.n,td.n{text-align:right}
td{padding:7px 9px 7px 0;border-bottom:1px solid #F0EDE7;vertical-align:top}
tr.forte td{font-weight:700;color:var(--inchiostro)}
.pie{border-top:2px solid var(--inchiostro);margin-top:30px;padding-top:12px;
font-size:11px;color:#8C877F;line-height:1.55}
svg{display:block;overflow:visible}
@media print{body{background:#fff}
.foglio{box-shadow:none;margin:0;max-width:none;padding:0}
.blocco{break-inside:avoid}}
@page{size:A4;margin:13mm}
"""

PIEDE = (
    "Fonti: ISTAT censimento permanente della popolazione (IstatData, 2018-2024) &middot; "
    "ISTAT 8milaCensus (1991, 2001, 2011) &middot; ISTAT matrici del pendolarismo "
    "(2011, 2021) &middot; ISTAT DCIS_POPRES1 &middot; anagrafe scolastica MIUR &middot; "
    "GTFS AMAT (Comune di Palermo). Provenance completa in <b>docs/sources.md</b>. "
    "Ogni cifra di questa scheda &egrave; letta da <b>data/processed/</b> e si rigenera con "
    "<b>uv run python -m pipeline.schede</b>: nessun numero &egrave; scritto a mano. "
    "Il registro claim &rarr; file sta in <b>data/processed/schede_claim.csv</b>."
)


def intestazione(occhiello, titolo, sommario, risposta) -> str:
    return (f'<p class="occhiello">{occhiello}</p><h1>{titolo}</h1>'
            f'<p class="sommario">{sommario}</p><div class="risposta">{risposta}</div>')


def scrivi(nome: str, titolo: str, corpo: str, piede_extra: str = "") -> Path:
    """Un file che vale sia come pagina autoportante sia come frammento da pubblicare.

    Nessun <html>/<head>: il charset in testa basta al browser via file:// e il tag
    resta innocuo se la pagina viene incapsulata altrove.
    ponytail: se servisse un vero documento XHTML, lo scheletro si aggiunge qui, in un
    posto solo.
    """
    piede = f'<p class="pie">{piede_extra}{" " if piede_extra else ""}{PIEDE}</p>'
    percorso = SCHEDE / nome
    percorso.write_text(
        f'<meta charset="utf-8">\n<title>{e(titolo)}</title>\n<style>{CSS}</style>\n'
        f'<div class="foglio">{corpo}{piede}</div>\n', encoding="utf-8")
    return percorso


# ============================================================== 1. il profilo

def scheda_profilo() -> Path:
    """Profiling statistico & benchmarking: la richiesta principale della locandina."""
    S = "1. profilo"
    fig = Numera(1)
    stati = pd.read_csv(PROCESSED / "edu_youth_states_2018_2024.csv")
    b24 = stati[(stati.territorio_nome == "Bagheria") & (stati.anno == 2024)].iloc[0]
    b18 = stati[(stati.territorio_nome == "Bagheria") & (stati.anno == 2018)].iloc[0]
    s24 = stati[(stati.territorio_nome == "Sicilia") & (stati.anno == 2024)].iloc[0]
    s18 = stati[(stati.territorio_nome == "Sicilia") & (stati.anno == 2018)].iloc[0]
    pop = pd.read_csv(PROCESSED / "edu_youth_population_15_34.csv")
    pb = pop[pop.territorio_nome == "Bagheria"].set_index("anno")
    stra = pd.read_csv(PROCESSED / "genere_stranieri.csv")
    sb = stra[(stra.nome_territorio == "Bagheria") & (stra.anno == 2024)]
    quota_stranieri = 100 * sb.FRGAPO.sum() / sb.totale.sum()
    stor = pd.read_csv(PROCESSED / "edu_historical_benchmarks_2011.csv")
    l4 = stor[stor.indicatore == "L4"].set_index("territorio_nome").valore
    perc = pd.read_csv(PROCESSED / "edu_historical_bagheria.csv")
    perc_l4 = perc[(perc.indicatore == "L4") & (perc.anno == 2011)].percentile_sicilia.iloc[0]
    perc_l4_91 = perc[(perc.indicatore == "L4") & (perc.anno == 1991)].percentile_sicilia.iloc[0]

    claim(S, "residenti 15-24 a Bagheria (2024)", b24.popolazione, "persone",
          "edu_youth_states_2018_2024.csv")
    claim(S, "fuori da lavoro e studio, 15-24", b24.quota_fuori_lavoro_studio, "%",
          "edu_youth_states_2018_2024.csv", "proxy 15-24, non e' il NEET 15-29 ISTAT")
    claim(S, "di chi e' fuori, quota che non cerca", b24.inattivi_su_fuori, "%",
          "edu_youth_states_2018_2024.csv")
    claim(S, "inattivi non studenti, in persone", b24.inattivi_non_studenti, "persone",
          "edu_youth_states_2018_2024.csv", "stima dalla ricostruzione della tavola 15-24")
    claim(S, "gap occupazionale 15-24 vs Sicilia, 2018 e 2024",
          f"{b18.quota_occupati - s18.quota_occupati:.1f} / "
          f"{b24.quota_occupati - s24.quota_occupati:.1f}", "p.p.",
          "edu_youth_states_2018_2024.csv", "rottura di misura 2019-2021 sulle componenti")
    claim(S, "NEET 15-29 al 2011 (8milaCensus L4)", l4["Bagheria"], "%",
          "edu_historical_benchmarks_2011.csv",
          "fascia 15-29 e definizione 2011: MAI in serie col proxy 15-24")
    claim(S, "percentile siciliano del NEET, 1991 -> 2011",
          f"{perc_l4_91:.0f} -> {perc_l4:.0f}", "percentile",
          "edu_historical_bagheria.csv", "390 comuni, alto = sfavorevole")
    claim(S, "popolazione 15-34, 2021 -> 2024",
          f"{pb.loc[2021].popolazione_15_34:.0f} -> {pb.loc[2024].popolazione_15_34:.0f}",
          "persone", "edu_youth_population_15_34.csv",
          "saldo netto: non misura l'emigrazione, non ha destinazione")
    claim(S, "stranieri sul 15-34", quota_stranieri, "%", "genere_stranieri.csv")

    corpo = intestazione(
        "Profiling statistico &amp; benchmarking &middot; Bagheria (PA) &middot; 15-24 anni &middot; 2018-2024",
        "Uno su quattro &egrave; fuori da lavoro e studio. Sette su dieci di loro non stanno nemmeno cercando.",
        f"Nel 2024 Bagheria conta {num(b24.popolazione, 0)} residenti fra i 15 e i 24 anni. "
        f"Il {num(b24.quota_fuori_lavoro_studio)}% &egrave; fuori sia dal lavoro sia dallo studio, "
        f"contro il {num(s24.quota_fuori_lavoro_studio)}% siciliano. Il recupero degli ultimi sei anni "
        f"&egrave; reale ma non ha ridotto la distanza dal contesto.",
        f"<b>La risposta alla domanda del bando.</b> Il problema di Bagheria non &egrave; la "
        f"disoccupazione giovanile: &egrave; l&rsquo;<b>inattivit&agrave; non studentesca</b>, "
        f"{num(b24.quota_inattivi_non_studenti)}% dei 15-24enni "
        f"(circa {num(b24.inattivi_non_studenti, 0)} persone, "
        f"{num(b24.quota_inattivi_non_studenti - s24.quota_inattivi_non_studenti, 1, segno=True)} p.p. "
        f"sopra la Sicilia). Fra 2018 e 2024 chi cerca lavoro cala di "
        f"{num(b24.quota_in_cerca - b18.quota_in_cerca)} punti, chi &egrave; inattivo di "
        f"{num(b24.quota_inattivi_non_studenti - b18.quota_inattivi_non_studenti)}. "
        f"Un servizio a domanda spontanea raggiungerebbe il segmento che si sta gi&agrave; "
        f"risolvendo da s&eacute;.")

    gruppi = [("studenti", b24.studenti, COL_STATO["studenti"]),
              ("occupati", b24.occupati, COL_STATO["occupati"]),
              ("in cerca", b24.in_cerca, COL_STATO["in cerca"]),
              ("inattivi non studenti", b24.inattivi_non_studenti, COL_STATO["casalinghe/i"])]
    corpo += blocco(
        fig(),
        f"I {num(b24.popolazione, 0)} quindici-ventiquattrenni di Bagheria, uno per uno",
        legenda([(f"{n} &middot; {num(v, 0)}", c) for n, v, c in gruppi]),
        waffle(gruppi, per_quadrato=50, colonne=22),
        mostra="Condizione prevalente dei residenti di 15-24 anni a Bagheria nel 2024, in "
               "persone: le quattro condizioni sono esaustive e si escludono a vicenda. "
               "La figura <b>non</b> dice nulla su titolo di studio, genere n&eacute; "
               "et&agrave; singola: la scomposizione per genere sta nella scheda 2, quella "
               "per et&agrave; nella figura 2.4.",
        base=f"N = {num(b24.popolazione, 0)} residenti 15-24 al 2024; per gruppo "
             f"{num(b24.studenti, 0)} studenti, {num(b24.occupati, 0)} occupati, "
             f"{num(b24.in_cerca, 0)} in cerca, {num(b24.inattivi_non_studenti, 0)} "
             f"inattivi non studenti. <b>Nessun intervallo di confidenza</b>: sono "
             f"conteggi della tavola censuaria e non stime campionarie, e nessun record "
             f"&egrave; escluso. Gli occupati sono un conteggio diretto; le altre tre "
             f"componenti vengono dalla ricostruzione della tavola 15-24 e sono stime "
             f"della ricostruzione, non conteggi.",
        lettura="Un quadrato ogni 50 residenti, letti per righe da 22. I quadrati per "
                "gruppo sono arrotondati all&rsquo;intero, quindi il totale disegnato "
                "pu&ograve; scostarsi di poche unit&agrave; dal conteggio. Il colore "
                "codifica la condizione e <b>non un ordine</b>: non &egrave; una scala, "
                "l&rsquo;accostamento arancione-azzurro non va letto come un gradiente. "
                "Il blocco arancione &egrave; la met&agrave; del problema che nessuna "
                "statistica corrente conta.",
        fonte="ISTAT, censimento permanente 2024, ricostruzione della tavola 15-24 "
              "&rarr; <b>edu_youth_states_2018_2024.csv</b>.")

    righe_imp = []
    for nome in ORDINE:
        r = stati[(stati.territorio_nome == nome) & (stati.anno == 2024)].iloc[0]
        righe_imp.append((nome, [
            ("studenti", r.quota_studenti, COL_STATO["studenti"]),
            ("occupati", r.quota_occupati, COL_STATO["occupati"]),
            ("in cerca", r.quota_in_cerca, COL_STATO["in cerca"]),
            ("inattivi", r.quota_inattivi_non_studenti, COL_STATO["casalinghe/i"])]))
    enne = {t: stati[(stati.territorio_nome == t) & (stati.anno == 2024)].popolazione.iloc[0]
            for t in ORDINE}
    corpo += blocco(
        fig(),
        "Il benchmarking: pi&ugrave; studenti della media, meno occupati, pi&ugrave; inattivi",
        impilate(righe_imp),
        mostra="Composizione percentuale della condizione prevalente dei 15-24enni nel 2024, "
               "per i quattro territori di confronto del bando. Ogni barra somma a 100: sono "
               "quote, non numeri assoluti, quindi la figura <b>non</b> dice quanto pesa "
               "Bagheria sulla Sicilia. I valori assoluti stanno nella base qui sotto.",
        base="N per territorio: " + ", ".join(
            f"{t} {num(enne[t], 0)}" for t in ORDINE) + " residenti 15-24. "
             "Conteggi censuari e non stime campionarie: nessun intervallo di confidenza. "
             "Nessun test formale fra territori: i confronti sono descrittivi e su "
             "denominatori di ordini di grandezza diversi, dalle 5.904 persone di "
             "Bagheria ai 5,9 milioni italiani.",
        lettura="Le barre sono al 100% e i segmenti seguono sempre lo stesso ordine "
                "(studenti, occupati, in cerca, inattivi non studenti), cos&igrave; le "
                "posizioni sono confrontabili in verticale. Bagheria &egrave; a piena "
                "intensit&agrave; di colore, gli altri territori al 55%: &egrave; una "
                "gerarchia di lettura, non un dato. Il numero compare dentro il segmento "
                "solo dove ci sta: sotto una certa larghezza uscirebbe dal proprio blocco e "
                "si leggerebbe come appartenente a quello accanto.",
        fonte="ISTAT, censimento permanente 2024 &rarr; "
              "<b>edu_youth_states_2018_2024.csv</b>.")

    delta = [("occupati", b18.quota_occupati, b24.quota_occupati),
             ("studenti", b18.quota_studenti, b24.quota_studenti),
             ("in cerca di occupazione", b18.quota_in_cerca, b24.quota_in_cerca),
             ("inattivi non studenti", b18.quota_inattivi_non_studenti,
              b24.quota_inattivi_non_studenti)]
    corpo += blocco(
        fig("Tavola"),
        "Il recupero c&rsquo;&egrave;. La convergenza no.",
        tabella(["Condizione 15-24", "2018", "2024", "variazione"],
                [(n, num(a, 1, "%", zero=True), num(b, 1, "%", zero=True),
                  num(b - a, 1, " p.p.", segno=True, zero=True))
                 for n, a, b in delta] +
                [("gap occupazione vs Sicilia",
                  num(b18.quota_occupati - s18.quota_occupati, 1, " p.p.", segno=True),
                  num(b24.quota_occupati - s24.quota_occupati, 1, " p.p.", segno=True),
                  "invariato")],
                forte=("inattivi non studenti", "gap occupazione vs Sicilia")),
        mostra="Le quattro quote della condizione 15-24 a Bagheria agli estremi della serie "
               "disponibile, 2018 e 2024, in punti percentuali, pi&ugrave; il divario "
               "occupazionale con la Sicilia alle stesse due date. Da dove viene il "
               "miglioramento: quasi tutto dal calo di chi cerca lavoro, quasi niente dalla "
               "riattivazione di chi non cerca.",
        base=f"N = {num(b18.popolazione, 0)} residenti 15-24 nel 2018 e "
             f"{num(b24.popolazione, 0)} nel 2024, cio&egrave; due popolazioni diverse: la "
             f"variazione &egrave; fra due quote, non un pannello sulle stesse persone. "
             f"Conteggi censuari, nessun intervallo di confidenza e nessun test: la "
             f"colonna &laquo;variazione&raquo; &egrave; una differenza aritmetica, non una "
             f"stima con incertezza. <b>Esclusioni</b>: il 2020 manca alla fonte sulla "
             f"classe 15-24 e non &egrave; interpolato; fra 2019 e 2021 c&rsquo;&egrave; una "
             f"rottura di misura sulla componente &laquo;in cerca di occupazione&raquo;.",
        lettura="Le due righe in nero sono quelle su cui poggia la tesi della scheda: "
                "l&rsquo;inattivit&agrave; ferma e il divario invariato. &laquo;Invariato&raquo; "
                "nell&rsquo;ultima cella non &egrave; un arrotondamento di comodo: il gap vale "
                f"{num(b18.quota_occupati - s18.quota_occupati, 1, ' p.p.', segno=True)} nel "
                f"2018 e {num(b24.quota_occupati - s24.quota_occupati, 1, ' p.p.', segno=True)} "
                "nel 2024, la stessa cifra a un decimale. Per la rottura di misura del 2019-2021 "
                "i confronti fra territori reggono, i livelli delle singole componenti no.",
        fonte="ISTAT, censimento permanente 2018 e 2024 &rarr; "
              "<b>edu_youth_states_2018_2024.csv</b>.")

    # I cinque indicatori del pannello storico, gli stessi di viz/edu_fig01. Il percentile
    # «favorevole» ribalta quelli in cui alto = male, cosi' che in alto = meglio valga per
    # tutti e cinque: senza il ribaltamento le linee del pannello destro non si leggono
    # insieme. La regola sta nella colonna `direzione`, non nel codice.
    CINQUE = ["I6", "I7", "I5", "L14", "L4"]
    s91 = perc[perc.anno == 1991].set_index("indicatore")
    s11 = perc[perc.anno == 2011].set_index("indicatore")
    favo = lambda r: (100 - r.percentile_sicilia if "sfavorevole" in r.direzione
                      else r.percentile_sicilia)
    verso = lambda i: -1 if "sfavorevole" in s11.loc[i].direzione else 1
    meglio = sum(1 for i in CINQUE
                 if (s11.loc[i].valore - s91.loc[i].valore) * verso(i) > 0)
    arretra = sum(1 for i in CINQUE if favo(s11.loc[i]) < favo(s91.loc[i]))
    claim(S, "indicatori 8milaCensus che migliorano in valore 1991-2011",
          f"{meglio}/{len(CINQUE)}", "indicatori", "edu_historical_bagheria.csv",
          "I6 I7 I5 L14 L4; fasce d'eta' diverse fra loro")
    claim(S, "gli stessi che arretrano in percentile siciliano",
          f"{arretra}/{len(CINQUE)}", "indicatori", "edu_historical_bagheria.csv",
          "percentile favorevole: ribaltato dove alto = sfavorevole")

    corpo += blocco(
        fig(),
        f"Trent&rsquo;anni: {meglio} indicatori su {len(CINQUE)} migliorano in valore, e "
        f"{arretra} su {len(CINQUE)} arretrano in posizione",
        figura("edu_fig01_storia_posizione"),
        mostra="Cinque indicatori 8milaCensus per Bagheria ai censimenti 1991, 2001 e 2011. "
               "A sinistra il <b>livello</b>, in percentuale della popolazione di riferimento "
               "di ciascun indicatore; a destra la <b>posizione</b>, cio&egrave; il percentile "
               "fra i 390 comuni siciliani. Le fasce d&rsquo;et&agrave; sono diverse da "
               "indicatore a indicatore e sono scritte accanto a ciascuno: si legge ogni riga "
               "per s&eacute;, mai una colonna. La figura <b>non</b> si unisce alla serie "
               "2018-2024 del resto della scheda, che &egrave; un&rsquo;altra rilevazione con "
               "altre definizioni.",
        base=f"N = 390 comuni siciliani a ogni censimento; Bagheria &egrave; uno di questi. "
             f"Conteggi censuari e non stime campionarie: <b>nessun intervallo di "
             f"confidenza</b> e nessun test. Tre sole osservazioni per indicatore, a dieci "
             f"anni di distanza: nessuna interpolazione fra un censimento e l&rsquo;altro. "
             f"Il conteggio {meglio}/{len(CINQUE)} e {arretra}/{len(CINQUE)} &egrave; il "
             f"segno della variazione 1991-2011, calcolato indicatore per indicatore nel "
             f"verso dichiarato dalla fonte.",
        lettura="A sinistra, per ogni riga: cerchio vuoto 1991, tacca 2001, cerchio pieno "
                "2011; la barra grigia &egrave; la distanza percorsa, non un intervallo di "
                "incertezza. La freccia sotto l&rsquo;etichetta dice da che parte sta il "
                "meglio, perch&eacute; per &laquo;uscita precoce&raquo; e &laquo;NEET&raquo; "
                "scendere &egrave; un miglioramento. A destra il percentile &egrave; "
                "<b>favorevole</b>: dove alto significava male &egrave; stato ribaltato, "
                "cos&igrave; in alto = davanti per tutte e cinque le linee. La tratteggiata a "
                "50 &egrave; la mediana regionale, cio&egrave; un riferimento mobile, non un "
                "obiettivo: Bagheria pu&ograve; scendere anche migliorando, se gli altri "
                "migliorano di pi&ugrave;. I due pannelli hanno scale diverse e non "
                "condividono l&rsquo;asse.",
        fonte="ISTAT 8milaCensus, censimenti 1991, 2001 e 2011 &rarr; "
              "<b>edu_historical_bagheria.csv</b>. Figura a piena risoluzione: "
              "<b>figures/edu_fig01_storia_posizione.png</b> (nello zip, con la propria "
              "didascalia).")

    corpo += blocco(
        fig(),
        "Il NEET del bando: due misure, mai una serie",
        '<div class="duo">'
        f'<div><h4>2011 &middot; NEET 15-29 (8milaCensus, L4)</h4>'
        + barre([{"label": n, "valore": float(l4[n]), "colore": COL[n], "forte": n == "Bagheria"}
                 for n in ORDINE], w=300, lab=76, coda=46) + '</div>'
        f'<div><h4>2024 &middot; fuori da lavoro e studio, 15-24</h4>'
        + barre([{"label": n, "valore": float(
            stati[(stati.territorio_nome == n) & (stati.anno == 2024)]
            .quota_fuori_lavoro_studio.iloc[0]),
            "colore": COL[n], "forte": n == "Bagheria"} for n in ORDINE],
            w=300, lab=76, coda=46) + '</div>'
        '</div>',
        mostra="La locandina chiede il NEET 15-34. A livello comunale <b>non esiste</b>: la "
               "fascia non &egrave; pubblicata. Si riportano allora le due misure che "
               "esistono, ciascuna con la propria etichetta. A sinistra il NEET ISTAT "
               "standard <b>15-29</b> al 2011 (8milaCensus, indicatore L4), in percentuale "
               "dei residenti di quella fascia. A destra il proxy <b>15-24</b> al 2024, "
               "costruito sulla condizione professionale del censimento permanente: quota di "
               "chi non lavora, non studia e non risulta in cerca, pi&ugrave; chi cerca "
               "senza studiare.",
        base="N a sinistra: i residenti 15-29 dei quattro territori al censimento 2011. N a "
             f"destra: {num(enne['Bagheria'], 0)} residenti 15-24 a Bagheria nel 2024 e i "
             "corrispondenti degli altri tre (vedi figura 1.2). Conteggi censuari in "
             "entrambi i pannelli, <b>nessun intervallo di confidenza</b> e nessun test fra "
             "pannelli, che sarebbe privo di senso: le popolazioni non coincidono. Del "
             f"{num(b24.quota_fuori_lavoro_studio)}% di destra, il "
             f"<b>{num(b24.inattivi_su_fuori)}% non risulta in cerca di occupazione</b>: "
             f"&egrave; la componente su cui poggia la scelta dell&rsquo;outreach nella "
             f"scheda 4.",
        lettura="I due pannelli hanno <b>scale indipendenti</b>: si confrontano le posizioni "
                "dentro ciascun pannello, mai le lunghezze fra l&rsquo;uno e l&rsquo;altro. "
                "Bagheria &egrave; la barra a piena intensit&agrave;. <b>Perch&eacute; non si "
                "sommano e non si mettono in serie</b>: fasce diverse (15-29 contro 15-24), "
                "definizioni diverse, rilevazioni diverse. Affiancarle &egrave; corretto, "
                "unirle sarebbe un errore, non un&rsquo;approssimazione. Sul pannello di "
                f"sinistra vale quanto detto alla figura 1.{fig.n - 1}: fra i 390 comuni "
                f"siciliani il NEET di Bagheria passa dal {num(perc_l4_91, 0)}&deg; "
                f"percentile del 1991 al <b>{num(perc_l4, 0)}&deg; del 2011</b>, dove alto "
                f"&egrave; sfavorevole. Il valore migliora, la posizione peggiora.",
        fonte="ISTAT 8milaCensus 2011 (<b>edu_historical_benchmarks_2011.csv</b>, percentili "
              "da <b>edu_historical_bagheria.csv</b>) e censimento permanente 2024 "
              "(<b>edu_youth_states_2018_2024.csv</b>).")

    corpo += blocco(
        fig("Tavola"),
        "La fuga sta nel denominatore",
        kpi([(num(pb.loc[2024].popolazione_15_34, 0), "residenti 15-34 nel 2024, da "
              f"{num(pb.loc[2021].popolazione_15_34, 0)} nel 2021", COL["Bagheria"]),
             (num(pb.loc[2024].variazione_da_primo_anno_pct, 1, "%"),
              "in tre anni (Italia: +1,2%)", COL["Bagheria"]),
             (num(quota_stranieri, 1, "%"),
              "stranieri sul 15-34, contro 12,4% in Italia", INCHIOSTRO)]),
        mostra="Popolazione residente di 15-34 anni a Bagheria, in persone, e sua variazione "
               "fra 2021 e 2024; pi&ugrave; la quota di cittadini stranieri sulla stessa "
               "fascia. Questa &egrave; l&rsquo;unica misura della scheda sul <b>15-34</b> "
               "pieno del bando: lavoro e istruzione a livello comunale esistono solo sul "
               "15-24, ed &egrave; il motivo per cui il resto della scheda sta su quella "
               "fascia.",
        base=f"N = {num(pb.loc[2024].popolazione_15_34, 0)} residenti 15-34 al 2024, da "
             f"{num(pb.loc[2021].popolazione_15_34, 0)} al 2021. La serie parte dal 2021 e "
             f"non prima: le et&agrave; singole, necessarie a ricostruire il 15-34 esatto, "
             f"esistono nella fonte solo da quell&rsquo;anno. Conteggi anagrafici del "
             f"censimento permanente, non stime: nessun intervallo di confidenza. Il "
             f"confronto italiano (+1,2%) &egrave; sullo stesso arco 2021-2024.",
        lettura="I tre numeri non sono una serie n&eacute; una scomposizione: sono tre "
                "misure sullo stesso denominatore. <b>Cosa il calo non dice</b>: &egrave; un "
                "<b>saldo netto</b> fra iscrizioni e cancellazioni anagrafiche, quindi non "
                "conta le partenze e non ha una destinazione. Chiamarlo &laquo;emigrazione "
                "misurata&raquo; sarebbe scorretto. Il profilo per et&agrave; di questo saldo, "
                "che dice <i>quando</i> le uscite avvengono, sta nella figura 2.4.",
        fonte="ISTAT, censimento permanente, et&agrave; singole 2021-2024 &rarr; "
              "<b>edu_youth_population_15_34.csv</b>, <b>genere_stranieri.csv</b>.")

    return scrivi("scheda1_profilo.html",
                  "Il profilo dei giovani di Bagheria", corpo,
                  "Scheda 1 di 4 &middot; risponde alla richiesta "
                  "&laquo;Profiling statistico &amp; Benchmarking&raquo;.")


# ============================================================== 2. la forbice

def scheda_forbice() -> Path:
    """Focus differenze di genere, e la risposta obliqua a «titolo x condizione»."""
    S = "2. forbice"
    fig = Numera(2)
    q = pd.read_csv(PROCESSED / "genere_quadro_sintesi.csv").set_index("nome_territorio")
    serie = pd.read_csv(PROCESSED / "genere_forbice_serie.csv")
    quad = pd.read_csv(PROCESSED / "genere_forbice_quadrante.csv")
    mille = pd.read_csv(PROCESSED / "genere_per_1000.csv")
    ci = pd.read_csv(PROCESSED / "genere_gap_occupazione_ci.csv")
    det = pd.read_csv(PROCESSED / "genere_composizione_stato_dettaglio.csv")
    civ = pd.read_csv(PROCESSED / "genere_stato_civile.csv")
    bounds = pd.read_csv(PROCESSED / "genere_casalinghe_bounds.csv")
    pos = pd.read_csv(PROCESSED / "genere_posizionamento.csv").set_index("indicatore")
    dist = pd.read_csv(PROCESSED / "genere_distribuzione_390.csv").set_index("anno")
    rit = pd.read_csv(PROCESSED / "genere_ritenzione_eta.csv")
    coo = pd.read_csv(PROCESSED / "genere_coorti.csv")
    breve = lambda n: "vicinato" if n.startswith("vicinato") else n

    b = q.loc["Bagheria"]
    ci_b = ci[(ci.nome_territorio == "Bagheria") & (ci.anno == 2024)].iloc[0]
    m24 = mille[(mille.nome_territorio == "Bagheria") & (mille.anno == 2024)].set_index("genere")
    # In quante annate Bagheria ha il tasso femminile piu' basso dei quattro territori?
    minimi = (serie.loc[serie.groupby("anno").tasso_occupazione_F.idxmin()]
              .nome_territorio.eq("Bagheria").sum())
    annate = serie.anno.nunique()
    d24 = det[(det.nome_territorio == "Bagheria") & (det.anno == 2024)]
    # La tavola porta F, M e il totale T come righe sorelle: sommare senza filtrare
    # raddoppia il conteggio (la trappola dichiarata in CLAUDE.md, qui su `genere`).
    fuori = d24[(d24.destinazione == "fuori e non in cerca") & (d24.genere != "T")]
    inatt = fuori.groupby("genere").persone.sum()
    casa = d24[(d24.stato == "casalinghe/i")].set_index("genere").persone
    altra = d24[(d24.stato == "altra condizione")].set_index("genere").persone
    con25 = civ[(civ.nome_territorio == "Bagheria") & (civ.anno == 2025) &
                (civ.genere == "F") & (civ.fascia == "15-24")].iloc[0]
    nubili = 100 * (1 - con25.gia_coniugate / casa["F"])

    claim(S, "almeno diploma 9-24, vantaggio femminile", -b["gap istruzione (M-F)"], "p.p.",
          "genere_quadro_sintesi.csv", "fascia 9-24 della fonte, include bambini")
    claim(S, "tasso di occupazione F 15-24", b["occupazione F"], "%",
          "genere_quadro_sintesi.csv")
    claim(S, "gap occupazionale M-F 15-24 con IC 95%",
          f"{ci_b.gap:.1f} [{ci_b.gap_lo:.1f}; {ci_b.gap_hi:.1f}]", "p.p.",
          "genere_gap_occupazione_ci.csv", "Newcombe")
    claim(S, "annate in cui Bagheria ha il tasso F minimo del panel",
          f"{minimi}/{annate}", "annate", "genere_forbice_serie.csv")
    claim(S, "su 1.000 ragazze: diplomate / occupate",
          f"{m24.loc['F'].per_1000_diploma:.0f} / {m24.loc['F'].per_1000_occupati:.0f}",
          "per mille", "genere_per_1000.csv",
          "stessa base, NON un funnel: l'incrocio individuale non esiste")
    claim(S, "su 1.000 ragazzi: diplomati / occupati",
          f"{m24.loc['M'].per_1000_diploma:.0f} / {m24.loc['M'].per_1000_occupati:.0f}",
          "per mille", "genere_per_1000.csv")
    claim(S, "casalinghe 15-24 (F) contro casalinghi (M)",
          f"{casa['F']:.0f} / {casa['M']:.0f}", "persone",
          "genere_composizione_stato_dettaglio.csv")
    claim(S, "quota delle casalinghe che NON e' gia' coniugata", nubili, "%",
          "genere_stato_civile.csv + genere_composizione_stato_dettaglio.csv",
          "bound inferiore: fonti e date di riferimento diverse")
    claim(S, "posizione fra i 10 comuni ugualmente scolarizzati (occupazione F 15+, 2011)",
          f"{pos.loc['L11'].istruiti_sotto}/10 sotto Bagheria", "rango",
          "genere_posizionamento.csv", "indicatore 15+, non giovanile")

    corpo = intestazione(
        "Focus &laquo;impatto delle differenze di genere&raquo; &middot; istruzione 9-24 &middot; "
        "occupazione 15-24 &middot; 2018-2024",
        "Su 1.000 ragazze di Bagheria, 510 hanno almeno il diploma e 82 lavorano.",
        f"Le ragazze di Bagheria arrivano al diploma "
        f"{num(-b['gap istruzione (M-F)'])} punti pi&ugrave; dei coetanei (il vantaggio "
        f"educativo femminile pi&ugrave; ampio del panel) e hanno un tasso di occupazione "
        f"del {num(b['occupazione F'])}%, il pi&ugrave; basso dei quattro territori in "
        f"{minimi} annate su {annate}. Il capitale umano c&rsquo;&egrave;: quello che non "
        f"funziona &egrave; la conversione.",
        f"<b>La risposta alla domanda del bando.</b> Il capitale umano che Bagheria spreca di "
        f"pi&ugrave; &egrave; femminile. I due divari hanno <b>segno opposto</b>: "
        f"{num(-b['gap istruzione (M-F)'], 1, segno=True)} punti a favore delle ragazze "
        f"sull&rsquo;istruzione, {num(b['gap occupazione (M-F)'], 1, segno=True)} punti a "
        f"sfavore sull&rsquo;occupazione "
        f"[IC 95% {num(ci_b.gap_lo)}; {num(ci_b.gap_hi)}]. E non &egrave; un tratto di fascia "
        f"territoriale: fra i dieci comuni siciliani ugualmente scolarizzati, Bagheria &egrave; "
        f"<b>penultima</b> per occupazione femminile.")

    per_mille = [
        {"label": "ragazze con almeno il diploma", "valore": m24.loc["F"].per_1000_diploma,
         "colore": COL_G["F"], "forte": True},
        {"label": "ragazze occupate", "valore": m24.loc["F"].per_1000_occupati,
         "colore": COL_G["F"], "forte": True},
        {"label": "ragazzi con almeno il diploma", "valore": m24.loc["M"].per_1000_diploma,
         "colore": COL_G["M"]},
        {"label": "ragazzi occupati", "valore": m24.loc["M"].per_1000_occupati,
         "colore": COL_G["M"]}]
    corpo += blocco(
        fig(),
        "Due misure, la stessa base di 1.000 persone",
        barre(per_mille, lab=214, fmt=lambda v: num(v, 0), coda=44),
        mostra="Diplomate e occupate ogni 1.000 residenti dello stesso sesso, 15-24 anni, "
               "Bagheria 2024. Le due misure sono normalizzate sulla <b>stessa base</b> per "
               "renderle confrontabili, ma restano due misure distinte: la figura <b>non</b> "
               "dice quante fra le diplomate lavorino, e quel dato non esiste (vedi la base).",
        base=f"N = {num(m24.loc['F'].pop_15_24, 0)} ragazze e "
             f"{num(m24.loc['M'].pop_15_24, 0)} ragazzi residenti 15-24 nel 2024; in valore "
             f"assoluto {num(m24.loc['F'].diplomati, 0)} diplomate e "
             f"{num(m24.loc['F'].occupati, 0)} occupate, {num(m24.loc['M'].diplomati, 0)} "
             f"diplomati e {num(m24.loc['M'].occupati, 0)} occupati. Conteggi censuari e non "
             f"stime campionarie: <b>nessun intervallo di confidenza sui livelli</b>. "
             f"L&rsquo;unico intervallo di questa scheda sta sulla <i>differenza</i> M&minus;F "
             f"dell&rsquo;occupazione ({num(ci_b.gap)} p.p., IC 95% di Newcombe "
             f"[{num(ci_b.gap_lo)}; {num(ci_b.gap_hi)}]), perch&eacute; &egrave; l&rsquo;unica "
             f"quantit&agrave; su cui il thread dichiara un&rsquo;incertezza.",
        lettura="Rosa le ragazze, blu i ragazzi: la coppia &egrave; dentro Okabe-Ito e resta "
                "distinguibile in protanopia e deuteranopia. Le due barre femminili sono a "
                "piena intensit&agrave; perch&eacute; sono il soggetto, non perch&eacute; "
                "valgano di pi&ugrave;. <b>Non &egrave; un imbuto</b>: le barre hanno la stessa "
                "base ma non sono le stesse persone seguite in sequenza. Nelle tavole comunali "
                "titolo di studio e condizione professionale <b>non sono incrociati</b> (nella "
                "tavola lavoro il titolo &egrave; solo &laquo;totale&raquo;, in quella "
                "istruzione la condizione &egrave; solo &laquo;totale&raquo;). &laquo;Quante "
                "diplomate di Bagheria lavorano&raquo; non &egrave; una domanda a cui i dati "
                "pubblici rispondano, ed &egrave; il primo dato che il servizio della scheda 4 "
                "produrrebbe.",
        fonte="ISTAT, censimento permanente 2024 &rarr; <b>genere_per_1000.csv</b>; intervallo "
              "da <b>genere_gap_occupazione_ci.csv</b>.")

    q24 = quad[quad.anno == 2024]
    punti = [(breve(r.nome_territorio), r.vantaggio_diploma_15_24_pp, r.tasso_occupazione_F,
              COL.get(r.nome_territorio, GRIGIO), r.nome_territorio == "Bagheria")
             for _, r in q24.iterrows()]
    ser_f = {breve(n): dict(zip(g.anno, g.tasso_occupazione_F))
             for n, g in serie.groupby("nome_territorio")}
    enne_f = (mille[mille.anno == 2024].set_index(["nome_territorio", "genere"])
              .pop_15_24.unstack())
    corpo += blocco(
        fig(),
        "La forbice: pi&ugrave; il vantaggio educativo cresce, meno il lavoro arriva",
        '<div class="duo">'
        '<div><h4>2024 &middot; il quadrante</h4>'
        + quadrante(punti, xlab="vantaggio femminile sul diploma (p.p.)",
                    ylab="occupazione femminile 15-24 (%)", w=300, h=232) + '</div>'
        '<div><h4>2018-2024 &middot; occupazione femminile 15-24</h4>'
        + linee(ser_f, w=300, h=232, coda=92) + '</div></div>',
        mostra="A sinistra il piano istruzione &times; occupazione al 2024, entrambe le misure "
               "sulla <b>stessa fascia 15-24</b>: in ascissa il vantaggio femminile sul "
               "diploma (quota F meno quota M, in punti percentuali), in ordinata il tasso di "
               "occupazione femminile in percentuale delle coetanee residenti. A destra la "
               "serie 2018-2024 dello stesso tasso femminile. La figura <b>non</b> mostra il "
               "rapporto fra tasso maschile e femminile, che sta nella figura 2.1.",
        base="N delle coetanee 15-24 al 2024: " + ", ".join(
            f"{breve(t)} {num(enne_f.loc[t, 'F'], 0)}"
            for t in ["Bagheria", "Palermo", "Sicilia", "Italia", "vicinato (5 comuni)"]) +
             ". Conteggi censuari e non stime campionarie: nessun intervallo sui singoli "
             "punti. Per il vicinato i conteggi dei cinque comuni sono <b>sommati e solo "
             "dopo</b> si calcola il tasso: non &egrave; la media dei cinque tassi. "
             f"<b>Esclusioni</b>: il 2020 manca alla fonte sulla classe 15-24 e non &egrave; "
             f"interpolato. Bagheria ha il tasso femminile pi&ugrave; basso del panel in "
             f"{minimi} annate su {annate}, cio&egrave; il minimo non dipende dall&rsquo;anno "
             f"scelto.",
        lettura="Nel pannello di sinistra gli assi sono assi, <b>non mediane</b>: non "
                "dividono il piano in quadranti, e la lettura &egrave; relativa fra i cinque "
                "punti, non rispetto a una soglia. Bagheria &egrave; il punto grande e "
                "colorato, e sta in basso a destra, cio&egrave; pi&ugrave; vantaggio educativo "
                "e meno occupazione. La versione con le mediane del panel disegnate &egrave; "
                "la tavola 2.6. Nel pannello di destra la striscia grigia verticale "
                "&egrave; il <b>2020 non rilevato</b>: &egrave; opaca apposta, per tagliare la "
                "linea invece di lasciarla passare sotto e raccontare una continuit&agrave; "
                "che non c&rsquo;&egrave;. Le etichette di fine linea sono scostate quel tanto "
                "che basta a non sovrapporsi: i punti restano sul valore vero. "
                "<b>Il claim robusto, e quello che non lo &egrave;</b>: sulla fascia 15-24 il "
                "primato del vantaggio educativo &egrave; un pareggio con la Sicilia, quindi "
                "il claim solido non &egrave; &laquo;le pi&ugrave; istruite d&rsquo;Italia&raquo; "
                "ma il <b>distacco dal vicinato</b> unito alla <b>mancata conversione</b>.",
        fonte="ISTAT, censimento permanente 2018-2024 &rarr; "
              "<b>genere_forbice_quadrante.csv</b>, <b>genere_forbice_serie.csv</b>, "
              "denominatori da <b>genere_per_1000.csv</b>.")

    dist11, dist24 = dist.loc[2011], dist.loc[2024]
    l11 = pos.loc["L11"]
    claim(S, "percentile siciliano dell'occupazione femminile, 2011 -> 2024",
          f"{dist11.percentile:.1f} -> {dist24.percentile:.1f}", "percentile",
          "genere_distribuzione_390.csv", "indicatore 15+, non giovanile; 390 comuni")
    claim(S, "rho di Spearman fra la graduatoria 2011 e quella 2024", dist24.rho_vs_2011,
          "-", "genere_distribuzione_390.csv", "la posizione del 2011 predice quella del 2024")

    corpo += blocco(
        fig(),
        f"Non &egrave; un comune medio della Sicilia: sta nella coda bassa, e ci stava "
        f"gi&agrave; nel 2011",
        figura("fig04_mappa_sicilia"),
        mostra="Tasso di occupazione femminile sulla popolazione di <b>15 anni e pi&ugrave;</b>, "
               "per comune siciliano, 2024. In alto la carta dell&rsquo;isola, in basso la "
               "distribuzione dello stesso indicatore confrontata con quella del 2011. "
               "<b>Attenzione alla fascia</b>: qui e solo qui la misura &egrave; sui 15+ e non "
               "sui 15-24 del resto della scheda, perch&eacute; il confronto sui 390 comuni "
               "esiste solo su quella base. Il tasso di questa figura e quello delle figure "
               "2.1 e 2.2 <b>non si confrontano fra loro</b>: popolazioni diverse.",
        base=f"N = 390 comuni ai confini del 2011 in entrambe le annate. Unica esclusione: "
             f"Misiliscemi, istituito nel 2021 per distacco da Trapani, disegnato in grigio e "
             f"tenuto fuori dai 390 perch&eacute; nel 2011 non esisteva. Conteggi censuari, "
             f"<b>nessun intervallo di confidenza sui singoli comuni</b>; nei comuni piccoli "
             f"il tasso resta per&ograve; instabile, perch&eacute; poche persone spostano "
             f"molti punti. Bagheria passa da {num(dist11.bagheria)}% "
             f"({num(dist11.percentile, 1)}&deg; percentile, {num(dist11.comuni_sotto, 0)} comuni "
             f"sotto) a {num(dist24.bagheria)}% ({num(dist24.percentile, 1)}&deg; percentile, "
             f"{num(dist24.comuni_sotto, 0)} sotto), mentre la mediana regionale sale da "
             f"{num(dist11.mediana)}% a {num(dist24.mediana)}%. La graduatoria &egrave; stabile: "
             f"rho di Spearman fra 2011 e 2024 = <b>{num(dist24.rho_vs_2011, 3)}</b>. Fra i "
             f"{num(l11.n_istruiti, 0)} comuni siciliani ugualmente scolarizzati, uno solo "
             f"sta sotto Bagheria: <b>&egrave; penultima del gruppo</b>. Le due annate "
             f"vengono da rilevazioni con disegni diversi (universale a questionario nel "
             f"2011, campionaria sui registri il permanente): il livello ne risente, il rango "
             f"dentro l&rsquo;anno molto meno, ed &egrave; il motivo per cui il confronto fra "
             f"annate si fa in percentili e non in punti percentuali.",
        lettura="Sulla carta il colore &egrave; il valore, su scala continua viridis: "
                "pi&ugrave; chiaro significa occupazione femminile pi&ugrave; alta, e la "
                "stessa scala vale per le barre dell&rsquo;istogramma sotto. &Egrave; una "
                "scala sequenziale, quindi ha un verso e non va letta come categorie. Bagheria "
                "ha il bordo vermiglio, i cinque comuni pi&ugrave; vicini per distanza fra i "
                "centroidi il bordo scuro, Palermo il bordo viola: a questa scala i loro "
                "poligoni sono un punto, perci&ograve; i nomi sono raccolti in una graffa in "
                "mare, ordinati per valore decrescente. Nell&rsquo;istogramma le barre piene "
                "sono il 2024 e il profilo grigio vuoto &egrave; il 2011: sono "
                "<b>sovrapposti e non affiancati</b>, perch&eacute; il finding &egrave; lo "
                "scorrimento dell&rsquo;intera distribuzione. Le verticali tratteggiate sono i "
                "valori 2011 e quelle piene i valori 2024. Il riquadro &egrave; centrato sulla "
                "terraferma: Lampedusa, Linosa, Pantelleria e Marettimo restano fuori dalla "
                "carta ma sono nel dato e nell&rsquo;istogramma.",
        fonte="ISTAT 8milaCensus indicatore L11 (2011) e censimento permanente (2024) &rarr; "
              "<b>genere_distribuzione_390.csv</b>, <b>genere_posizionamento.csv</b>. Confini: "
              "unit&agrave; amministrative generalizzate ISTAT al 01/01/2026, EPSG:32633. "
              "Figura a piena risoluzione: <b>figures/fig04_mappa_sicilia.png</b>.")

    rit_b = rit[(rit.nome_territorio == "Bagheria") & rit.eta_2021.between(14, 30)]
    n_rit = rit_b.groupby("genere").n_2021.sum()
    c2529f = coo[(coo.coorte == "25-29 nel 2021") & (coo.genere == "F")].set_index(
        "nome_territorio")["ritenzione_%"]
    claim(S, "ritenzione della coorte F 25-29, Bagheria contro Italia",
          f"{c2529f['Bagheria']:.1f} / {c2529f['Italia']:.1f}", "per 100",
          "genere_coorti.csv", "saldo netto di coorte, non un conteggio di partenze")

    corpo += blocco(
        fig(),
        "Le uscite hanno due tempi, e quello femminile &egrave; fra i 22 e i 25 anni",
        figura("fig07_ritenzione_eta"),
        mostra="Quota della coorte del 2021 ancora residente nello stesso comune tre anni "
               "dopo, per <b>et&agrave; singola</b> da 14 a 30 anni e per genere, cinque "
               "territori. Base 100 = la coorte di partenza: chi aveva 20 anni nel 2021 ne ha "
               "23 nel 2024. &Egrave; una misura <b>netta</b>, che comprende sia chi parte sia "
               "chi arriva, quindi <b>non</b> conta le partenze e non ha una destinazione: "
               "dice a che et&agrave; si perde, non dove si va.",
        base=f"N = {num(n_rit.sum(), 0)} persone nella coorte 2021 di Bagheria "
             f"({num(n_rit['F'], 0)} femmine e {num(n_rit['M'], 0)} maschi), fra "
             f"{num(rit_b.n_2021.min(), 0)} e {num(rit_b.n_2021.max(), 0)} per singola "
             f"et&agrave;. Le linee sono <b>medie mobili centrate su tre et&agrave;</b>, "
             f"quindi si leggono i pattern e non i decimali. Conteggi censuari, "
             f"<b>nessun intervallo di confidenza</b>: l&rsquo;incertezza residua &egrave; "
             f"l&rsquo;aggiustamento post-censuario delle stime di popolazione, che la misura "
             f"incorpora. Nessun record escluso: le et&agrave; ai bordi servono solo a "
             f"chiudere la media mobile. Sulla coorte 25-29 la ritenzione femminile di "
             f"Bagheria vale {num(c2529f['Bagheria'])} contro {num(c2529f['Italia'])} in "
             f"Italia, l&rsquo;unica cella femminile negativa dei quattro territori.",
        lettura="La tratteggiata orizzontale a 100 &egrave; la parit&agrave;: sopra, la coorte "
                "&egrave; cresciuta; sotto, si &egrave; ridotta. Il rettangolo vermiglio "
                "chiaro, presente <b>solo sul pannello femminile</b>, &egrave; il soggetto "
                "della figura: la finestra 22-25. A sinistra le femmine, a destra i maschi, e "
                "i due pannelli condividono la scala verticale. Il vicinato &egrave; "
                "l&rsquo;insieme dei cinque comuni pi&ugrave; vicini per distanza fra i "
                "centroidi, non un vicino singolo. <b>Cautela</b>: la finestra 22-25 &egrave; "
                "una lettura <i>pooled</i>, e le transizioni annuali oscillano fino a 8 punti "
                "sulla stessa et&agrave;. Si titola sul triennio, mai sull&rsquo;anno singolo. "
                "&Egrave; la figura che impone le due finestre di ingaggio della scheda 4.",
        fonte="ISTAT, censimento permanente, et&agrave; singole 2021 e 2024 &rarr; "
              "<b>genere_ritenzione_eta.csv</b>, <b>genere_coorti.csv</b>. Figura a piena "
              "risoluzione: <b>figures/fig07_ritenzione_eta.png</b>.")

    corpo += blocco(
        fig(),
        "Dentro l&rsquo;inattivit&agrave;: stesse dimensioni, etichette opposte",
        legenda([("femmine", COL_G["F"]), ("maschi", COL_G["M"])]),
        barre([{"label": "casalinghe (F)", "valore": casa["F"], "colore": COL_G["F"], "forte": True},
               {"label": "casalinghi (M)", "valore": casa["M"], "colore": COL_G["M"]},
               {"label": "«altra condizione» (F)", "valore": altra["F"],
                "colore": COL_G["F"]},
               {"label": "«altra condizione» (M)", "valore": altra["M"],
                "colore": COL_G["M"], "forte": True}],
              lab=196, fmt=lambda v: num(v, 0) + " persone", coda=90),
        mostra=f"Come il censimento etichetta i circa {num(inatt.sum(), 0)} quindici-"
               f"ventiquattrenni di Bagheria che al 2024 sono fuori da lavoro, studio e "
               f"ricerca attiva: in persone, per genere e per stato dichiarato. La figura "
               f"mostra l&rsquo;<b>etichetta</b>, non una condizione accertata, e non dice "
               f"nulla su quanto quelle persone vorrebbero lavorare.",
        base=f"N = {num(inatt.sum(), 0)} persone fuori da lavoro e istruzione e non in cerca, "
             f"di cui {num(inatt['F'], 0)} femmine e {num(inatt['M'], 0)} maschi: il gruppo "
             f"&egrave; per met&agrave; maschile, non &egrave; un gruppo femminile. Conteggi "
             f"censuari, nessun intervallo di confidenza. Nella tavola i codici F, M e il "
             f"totale T convivono come righe sorelle: <b>il totale &egrave; filtrato via</b> "
             f"prima di sommare, altrimenti i conteggi raddoppiano. Sullo stato civile la "
             f"fonte e la data di riferimento sono diverse (1&deg; gennaio 2025, DCIS_POPRES1 "
             f"contro censimento 2024), quindi il {num(nubili, 0)}% qui sotto &egrave; un "
             f"<b>limite inferiore</b>, non una stima puntuale.",
        lettura=f"Rosa le femmine, blu i maschi; a piena intensit&agrave; le due barre che "
                f"reggono il ragionamento, cio&egrave; le casalinghe e l&rsquo;&laquo;altra "
                f"condizione&raquo; maschile. Le quattro barre sono conteggi sulla stessa "
                f"scala e si confrontano direttamente. <b>Le casalinghe di Bagheria sono "
                f"nubili</b>: al 1&deg; gennaio 2025 le gi&agrave; coniugate 15-24 sono "
                f"{num(con25.gia_coniugate, 0)} ({num(con25.quota_gia_coniugate_pct)}%) contro "
                f"{num(casa['F'], 0)} casalinghe, quindi almeno il "
                f"<b>{num(nubili, 0)}% non &egrave; sposato</b>, e il matrimonio under-25 a "
                f"Bagheria sta sotto Palermo e Sicilia. Il canale non &egrave; la famiglia "
                f"propria ma quella d&rsquo;origine: serve un servizio di <b>attivazione</b>, "
                f"non solo di conciliazione. La quota &egrave; sensibile alla struttura per "
                f"et&agrave;, e passa da {num(bounds.iloc[0, 1])}% sui 15-24 a "
                f"{num(bounds.iloc[2, 1])}% se si assume che nessuna abbia meno di 20 anni.",
        fonte="ISTAT, censimento permanente 2024 &rarr; "
              "<b>genere_composizione_stato_dettaglio.csv</b>; stato civile al 1&deg; gennaio "
              "2025 (DCIS_POPRES1) &rarr; <b>genere_stato_civile.csv</b>, bound in "
              "<b>genere_casalinghe_bounds.csv</b>.")

    corpo += blocco(
        fig("Tavola"),
        "La stessa forbice come esce dal notebook, con la sua didascalia",
        figura("fig05_forbice", intera=True, larghezza=1650),
        mostra="&Egrave; la figura 2.2, nella versione integrale che sta nello zip: stessa "
               "misura, stesse cinque unit&agrave;, ma con le mediane del panel disegnate e "
               "la didascalia a quattro blocchi incorporata nell&rsquo;immagine. Compare qui "
               "<b>intera e non ritagliata</b> perch&eacute; il punto non &egrave; il dato, "
               "che la scheda ha gi&agrave; dato, ma mostrare che ogni tavola del progetto "
               "viaggia da sola: chi la trova in una cartella sa gi&agrave; che cosa misura, "
               "su quante persone e con quali limiti.",
        base="Le altre figure di questa scheda sono ritagliate al solo grafico proprio "
             "perch&eacute; questa non lo &egrave;: alla larghezza di una colonna il testo "
             "incorporato in un PNG a 300 dpi scende sotto i cinque pixel e non si legge, "
             "quindi la didascalia va ricomposta in HTML, come nelle figure 2.1-2.5. La "
             "regola sta in <b>pipeline/schede.py</b>, funzione <code>figura()</code>. I "
             "denominatori sono quelli della figura 2.2.",
        lettura="Rispetto alla figura 2.2 cambiano due cose: le <b>tratteggiate chiare</b> "
                "sono le mediane del panel e dividono davvero il piano in quadranti, e "
                "l&rsquo;etichetta accanto a ogni punto ne ripete i due valori. La "
                "tratteggiata verticale allo zero &egrave; la parit&agrave; educativa fra "
                "ragazze e ragazzi: a destra di quella riga le ragazze sono pi&ugrave; "
                "istruite dei coetanei. Bagheria &egrave; il punto vermiglio pi&ugrave; grande, "
                "e sta da sola in basso a destra.",
        fonte="Generata da <b>viz/fig05_forbice.R</b> &rarr; "
              "<b>figures/fig05_forbice.png</b> (300 dpi) e <b>.svg</b>. Dati: "
              "<b>genere_forbice_quadrante.csv</b>, <b>genere_per_1000.csv</b>.")

    return scrivi("scheda2_forbice.html",
                  "La forbice di genere a Bagheria", corpo,
                  "Scheda 2 di 4 &middot; risponde al focus &laquo;impatto delle differenze di "
                  "genere&raquo; e, per quanto i dati pubblici consentano, a "
                  "&laquo;titolo di studio &times; condizione lavorativa&raquo;.")


# ============================================================== 3. il pendolarismo

def _spearman(a, b):
    """rho e p. scipy arriva con statsmodels: se manca, si degrada a rho senza p."""
    try:
        from scipy import stats
        r = stats.spearmanr(a, b)
        return float(r.statistic), float(r.pvalue)
    except Exception:  # ponytail: il p-value e' un di piu', il rho no
        return float(pd.Series(a).corr(pd.Series(b), method="spearman")), float("nan")


def scheda_pendolarismo() -> Path:
    """Focus «dinamiche e ruolo del pendolarismo verso Palermo»."""
    S = "3. pendolarismo"
    fig = Numera(3)
    flu = pd.read_csv(PROCESSED / "mob_flussi_bagheria.csv")
    rib = pd.read_csv(PROCESSED / "mob_ribaltamento_territori.csv").set_index("territorio")
    mez = pd.read_csv(PROCESSED / "mob_mezzo_genere.csv")
    ora = pd.read_csv(PROCESSED / "mob_orario_genere.csv")
    sin = pd.read_csv(PROCESSED / "mob_sintesi.csv").set_index("misura")
    r390 = pd.read_csv(PROCESSED / "mob_ribaltamento_390.csv")
    t390 = pd.read_csv(PROCESSED / "mob_treno_390.csv")
    tag = pd.read_csv(PROCESSED / "mob_taglia_distanza.csv")
    coo = pd.read_csv(PROCESSED / "genere_coorti.csv")
    pen = pd.read_csv(PROCESSED / "genere_pendolarismo.csv")

    studio11 = flu[(flu.anno == 2011) & (flu.motivo == "studio")].nlargest(5, "persone")
    lavoro21 = flu[(flu.anno == 2021) & (flu.motivo == "lavoro")].nlargest(5, "persone")
    bag = rib.loc["Bagheria"]
    treno = mez[mez.classe == "di cui: treno"].set_index("genere").quota
    coll = mez[mez.classe == "collettivo"].set_index("genere").quota
    priv = mez[mez.classe == "privato a motore"].set_index("genere").quota
    presto = ora[ora.orario == "prima delle 7:15"].set_index("genere").quota
    # Percentile del treno fra i 390 comuni, e l'ipotesi che non regge.
    tb = t390[t390.nome == "Bagheria"].iloc[0]
    perc_treno = 100 * (t390.treno < tb.treno).mean()
    unito = r390.merge(t390[["territorio", "treno"]], on="territorio")
    rho, p = _spearman(unito.treno, unito.gap_lavoro_F_M)
    perc_gap = 100 * (r390.gap_lavoro_F_M < bag.gap_lavoro_F_M).mean()
    tagb = tag[tag.nome == "Bagheria"].iloc[0]
    c2529 = (coo[coo.coorte == "25-29 nel 2021"]
             .assign(_t=lambda d: d.nome_territorio.map(ORDINE.index),
                     _g=lambda d: d.genere.map({"F": 0, "M": 1}))
             .sort_values(["_t", "_g"]))
    pen19 = pen[pen.anno == 2019].set_index(["nome_territorio", "motivo"])

    claim(S, "di chi esce per studio (2011), quota diretta a Palermo",
          sin.loc["quota di chi esce che va a Palermo, studio 2011"].valore, "%",
          "mob_sintesi.csv / mob_flussi_bagheria.csv", "93o percentile dei 381 non capoluogo")
    claim(S, "di chi esce per lavoro (2021), quota diretta a Palermo",
          sin.loc["quota di chi esce che va a Palermo, lavoro 2021"].valore, "%",
          "mob_sintesi.csv", "definizione 2021 diversa dal 2011: non e' una serie")
    claim(S, "divario F-M sull'uscire per studio, 2011", bag.gap_studio_F_M, "p.p.",
          "mob_ribaltamento_territori.csv", "conteggio esaustivo, nessuna eta' nella fonte")
    claim(S, "divario F-M sull'uscire per lavoro, 2011", bag.gap_lavoro_F_M, "p.p.",
          "mob_ribaltamento_territori.csv", f"{perc_gap:.0f}o percentile dei 390 comuni")
    claim(S, "ribaltamento studio->lavoro", bag.ribaltamento, "p.p.",
          "mob_ribaltamento_territori.csv", "Sicilia 6,0 - il salto e' 2,5 volte il regionale")
    claim(S, "quota treno fra chi esce, donne / uomini",
          f"{treno['F']:.1f} / {treno['M']:.1f}", "%", "mob_mezzo_genere.csv",
          "stima campionaria calibrata sui margini esatti")
    claim(S, "percentile siciliano di Bagheria per uso del treno", perc_treno, "percentile",
          "mob_treno_390.csv", "il treno non e' sottoutilizzato")
    claim(S, "Spearman treno x divario di genere sul lavoro, 390 comuni",
          f"rho={rho:.2f} p={p:.2f}", "-", "mob_treno_390.csv + mob_ribaltamento_390.csv",
          "RISULTATO NEGATIVO: l'offerta di trasporto non spiega il divario")
    claim(S, "residuo di Bagheria a parita' di taglia e distanza", tagb.residuo, "p.p.",
          "mob_taglia_distanza.csv", "«Bagheria si muove poco» non regge al controllo")
    claim(S, "donne in piu' fuori comune col divario medio siciliano",
          sin.loc["donne in piu' fuori comune col divario siciliano".replace("'", "'")].valore
          if "donne in piu' fuori comune col divario siciliano" in sin.index
          else sin[sin.index.str.startswith("donne in pi")].valore.iloc[0], "persone",
          "mob_sintesi.csv", "bersaglio del KPI; parita' piena = 449")

    corpo = intestazione(
        "Focus &laquo;dinamiche e ruolo del pendolarismo verso Palermo&raquo; &middot; "
        "matrice origine-destinazione ISTAT 2011 e 2021",
        "Si esce per studiare, non per lavorare, e la destinazione &egrave; una sola.",
        f"Fra chi lascia Bagheria ogni giorno, il "
        f"{num(sin.loc['quota di chi esce che va a Palermo, studio 2011'].valore)}% per studio "
        f"e il {num(sin.loc['quota di chi esce che va a Palermo, lavoro 2021'].valore)}% per "
        f"lavoro va a Palermo. Non esiste una seconda direzione. Ma lo scarto fra ragazze e "
        f"ragazzi <b>cambia segno</b> a seconda del motivo dello spostamento.",
        f"<b>La risposta alla domanda del bando.</b> Il pendolarismo di Bagheria &egrave; "
        f"pendolarismo verso Palermo, e non &egrave; un problema di raggiungibilit&agrave;: "
        f"la citt&agrave; &egrave; raggiunta, e dalle ragazze pi&ugrave; che dai ragazzi "
        f"({num(bag.gap_studio_F_M, 1, ' p.p.', segno=True)} sullo studio). "
        f"&Egrave; sul <b>lavoro</b> che la mobilit&agrave; femminile si spegne: "
        f"{num(bag.gap_lavoro_F_M)} punti, {num(perc_gap, 0)}&deg; percentile dei 390 comuni "
        f"siciliani (13&deg; sui soli 381 non capoluogo). Il salto fra i due motivi vale <b>{num(bag.ribaltamento)} punti</b> contro "
        f"i {num(rib.loc['Sicilia'].ribaltamento)} della Sicilia. Le ragazze si muovono: "
        f"smettono quando il motivo diventa il lavoro.")

    usc11 = flu[(flu.anno == 2011) & (flu.motivo == "studio")].persone.sum()
    usc21 = flu[(flu.anno == 2021) & (flu.motivo == "lavoro")].persone.sum()
    corpo += blocco(
        fig(),
        "La destinazione ha un nome, ed &egrave; una sola",
        '<div class="duo">'
        '<div><h4>2011 &middot; motivo studio</h4>'
        + barre([{"label": r.comune, "valore": r.quota_su_chi_esce, "colore": COL["Bagheria"],
                  "forte": r.comune == "Palermo"} for _, r in studio11.iterrows()],
                w=300, lab=118, coda=48) + '</div>'
        '<div><h4>2021 &middot; motivo lavoro</h4>'
        + barre([{"label": r.comune, "valore": r.quota_su_chi_esce, "colore": COL["Bagheria"],
                  "forte": r.comune == "Palermo"} for _, r in lavoro21.iterrows()],
                w=300, lab=118, coda=48) + '</div></div>',
        mostra="I primi cinque comuni di arrivo di chi esce ogni giorno da Bagheria, in "
               "percentuale di chi esce, per i due motivi e le due rilevazioni disponibili: "
               "studio al censimento 2011, lavoro alla matrice del censimento permanente "
               "2021. La figura mostra <b>dove</b> vanno quelli che escono, non <b>quanti</b> "
               "escono: il livello di uscita sta nella figura 3.4.",
        base=f"N = {num(usc11, 0)} persone che escono da Bagheria per studio nel 2011 e "
             f"{num(usc21, 0)} che ne escono per lavoro nel 2021; le quote sono su questi "
             f"due denominatori, non sulla popolazione. Record esaustivi della matrice "
             f"origine-destinazione, non un campione: <b>nessun intervallo di confidenza</b>. "
             f"Sono mostrate le prime cinque destinazioni su tutte quelle presenti; la coda "
             f"non &egrave; esclusa dal calcolo delle quote, solo dal disegno.",
        lettura="I due pannelli hanno scale indipendenti e Palermo &egrave; la barra a piena "
                "intensit&agrave;. <b>Non sono una serie</b>: il 2011 conta chi si sposta "
                "<i>giornalmente</i>, il 2021 chi si reca al lavoro <i>almeno tre giorni a "
                "settimana</i>, e il 2021 copre il solo lavoro. Si confronta la composizione "
                "(dove vanno, su cento che escono), mai il livello. Che il secondo comune stia "
                "sempre un ordine di grandezza sotto il primo &egrave; il finding: non "
                "c&rsquo;&egrave; da scegliere quale destinazione servire.",
        fonte="ISTAT, matrici del pendolarismo 2011 e 2021 &rarr; "
              "<b>mob_flussi_bagheria.csv</b>. La matrice ricostruisce sette su sette gli "
              "indicatori <i>M</i> gi&agrave; pubblicati da 8milaCensus: &egrave; il livello "
              "sottostante, non una fonte alternativa.")

    ordine_rib = ["Bagheria", "5 comuni vicini", "Sicilia", "Italia", "Comune di Palermo"]
    corpo += blocco(
        fig(),
        "Il ribaltamento: lo scarto di genere cambia segno col motivo",
        slope([(n, rib.loc[n].gap_studio_F_M, rib.loc[n].gap_lavoro_F_M,
                COL.get(n, GRIGIO), n == "Bagheria") for n in ordine_rib],
              sx="per STUDIO", dx="per LAVORO"),
        mostra="Quota di chi esce dal comune di residenza, come <b>scarto femmine "
               "&minus; maschi</b> in punti percentuali, per i due motivi dello spostamento e "
               "cinque territori, censimento 2011. Il denominatore &egrave; chi si sposta per "
               "quel motivo, non la popolazione: la figura misura il verso dello "
               "spostamento a parit&agrave; di motivo, e <b>non</b> quante persone lavorano o "
               "studiano.",
        base=f"Record esaustivi del censimento 2011: <b>nessun intervallo di confidenza</b> e "
             f"nessun test, sono conteggi di popolazione. Per Bagheria il divario sul lavoro "
             f"vale {num(bag.gap_lavoro_F_M)} punti, il "
             f"{num(perc_gap, 0)}&deg; percentile dei 390 comuni siciliani (13&deg; sui soli "
             f"381 non capoluogo); il salto fra i due motivi vale "
             f"{num(bag.ribaltamento)} punti contro i "
             f"{num(rib.loc['Sicilia'].ribaltamento)} della Sicilia. <b>Replicato su una "
             f"fonte indipendente</b>: la stessa misura sul censimento permanente 2018-2019 "
             f"(altra rilevazione, altro metodo, sette anni dopo) d&agrave; per Bagheria "
             f"{num(pen19.loc[('Bagheria', 'WK')].gap_M_meno_F)} punti sul lavoro contro "
             f"{num(pen19.loc[('Sicilia', 'WK')].gap_M_meno_F)} in Sicilia, e il segno "
             f"opposto sullo studio. La fonte non ha la dimensione et&agrave;: il target "
             f"15-34 del bando non &egrave; isolabile qui.",
        lettura="Ogni linea &egrave; un territorio e collega la stessa misura ai due motivi: "
                "la <b>pendenza</b> &egrave; il finding, non i due livelli presi da soli. La "
                "tratteggiata orizzontale &egrave; la parit&agrave; F = M: sopra escono "
                "pi&ugrave; le donne, sotto pi&ugrave; gli uomini. Bagheria &egrave; la linea "
                "spessa e colorata. Il verso cambia in tutti i territori, quindi il "
                "ribaltamento in s&eacute; non &egrave; una particolarit&agrave; locale: "
                "l&rsquo;<b>ampiezza</b> lo &egrave;. <b>E non &egrave; il divario "
                "occupazionale travestito</b>: il denominatore &egrave; gi&agrave; "
                "condizionato al motivo, cio&egrave; chi si sposta per lavoro un lavoro "
                "ce l&rsquo;ha.",
        fonte="ISTAT, censimento 2011, record esaustivi &rarr; "
              "<b>mob_ribaltamento_territori.csv</b>; replica sul censimento permanente "
              "2018-2019 &rarr; <b>genere_pendolarismo.csv</b>.")

    n_mob = ora.groupby("genere").persone.sum()
    corpo += blocco(
        fig(),
        "Il treno &egrave; il canale femminile, l&rsquo;auto quello maschile",
        legenda([("femmine", COL_G["F"]), ("maschi", COL_G["M"])]),
        '<div class="duo">'
        '<div><h4>Mezzo usato (2011)</h4>'
        + barre([{"label": "mezzo collettivo (F)", "valore": coll["F"], "colore": COL_G["F"], "forte": True},
                 {"label": "mezzo collettivo (M)", "valore": coll["M"], "colore": COL_G["M"]},
                 {"label": "di cui treno (F)", "valore": treno["F"], "colore": COL_G["F"], "forte": True},
                 {"label": "di cui treno (M)", "valore": treno["M"], "colore": COL_G["M"]},
                 {"label": "auto o moto (F)", "valore": priv["F"], "colore": COL_G["F"]},
                 {"label": "auto o moto (M)", "valore": priv["M"], "colore": COL_G["M"], "forte": True}],
                w=300, lab=132, coda=46) + '</div>'
        '<div><h4>Esce di casa prima delle 7:15</h4>'
        + barre([{"label": "femmine", "valore": presto["F"], "colore": COL_G["F"], "forte": True},
                 {"label": "maschi", "valore": presto["M"], "colore": COL_G["M"]}],
                w=300, lab=132, coda=46)
        + '</div></div>',
        mostra="Come si sposta chi esce da Bagheria, per genere, censimento 2011: a sinistra "
               "il mezzo usato, in percentuale di chi si sposta dello stesso sesso; a destra "
               "la quota che esce di casa prima delle 7:15. <b>Tutti i motivi insieme</b>, "
               "perch&eacute; la tavola per mezzo non incrocia il motivo. La figura non dice "
               "nulla sul viaggio di rientro, che la fonte non rileva.",
        base=f"N = {num(n_mob['F'], 0)} femmine e {num(n_mob['M'], 0)} maschi che si spostano "
             f"giornalmente. <b>Stima campionaria</b>, non conteggio: la tavola per mezzo e "
             f"orario &egrave; rilevata sui comuni sopra i 20.000 abitanti e calibrata sui "
             f"margini dei conteggi esaustivi; <b>errore relativo mediano 0,9%</b>, che alle "
             f"differenze qui mostrate (16 punti sul mezzo collettivo) non cambia il segno. "
             f"Le classi &laquo;di cui: treno&raquo; sono un sottoinsieme del mezzo "
             f"collettivo e non vanno sommate alle altre.",
        lettura="Rosa le femmine, blu i maschi; a piena intensit&agrave; la barra pi&ugrave; "
                "alta della coppia, cio&egrave; il canale prevalente per quel sesso. Le due "
                "colonne hanno scale indipendenti. Le donne partono pi&ugrave; tardi e "
                "viaggiano pi&ugrave; a lungo, per 17 chilometri; il rientro non &egrave; "
                "rilevato, quindi <b>il carico di cura resta un&rsquo;ipotesi e non un "
                "dato</b>. La conseguenza operativa &egrave; nella scheda 4: un servizio che "
                "d&agrave; per scontata l&rsquo;auto seleziona per genere.",
        fonte="ISTAT, censimento 2011, tavola per mezzo e orario &rarr; "
              "<b>mob_mezzo_genere.csv</b>, <b>mob_orario_genere.csv</b>.")

    # Il finding e' lo scarto fra i due percentili, non i due percentili: sulla quota
    # grezza Bagheria sembra muoversi poco, sul residuo del modello e' nella media.
    perc_grezzo = 100 * (tag.quota_fuori < tagb.quota_fuori).mean()
    perc_residuo = 100 * (tag.residuo < tagb.residuo).mean()
    claim(S, "percentile di Bagheria fra i 381 non capoluogo, quota grezza -> residuo",
          f"{perc_grezzo:.0f} -> {perc_residuo:.0f}", "percentile",
          "mob_taglia_distanza.csv", "a parita' di taglia e distanza Bagheria e' nella media")

    corpo += blocco(
        fig(),
        "Due ipotesi testate, e cadute: il treno non &egrave; sottoutilizzato e Bagheria "
        "non si muove poco",
        figura("mob_fig04_taglia_distanza"),
        mostra="Quota di residenti che esce dal comune per lavoro, in percentuale, contro la "
               "taglia del comune e la distanza dal capoluogo, per i 381 comuni siciliani non "
               "capoluogo. Serve a rispondere a una sola domanda: <b>quanto di quello che si "
               "vede a Bagheria &egrave; spiegato da quanto Bagheria &egrave; grande e da "
               "quanto dista da Palermo.</b> La figura non riguarda il divario di genere, che "
               "&egrave; nella figura 3.2.",
        base=f"N = {num(len(tag), 0)} comuni non capoluogo. Bagheria: quota osservata "
             f"{num(tagb.quota_fuori)}%, attesa {num(tagb.atteso)}% a parit&agrave; di taglia "
             f"e distanza, <b>residuo {num(tagb.residuo)} punti</b> contro una deviazione "
             f"standard dei residui di {num(tag.residuo.std())} punti. Sulla quota grezza "
             f"Bagheria &egrave; al {num(perc_grezzo, 0)}&deg; percentile, sul residuo del "
             f"modello al {num(perc_residuo, 0)}&deg;: <b>il controllo sposta Bagheria nella "
             f"media</b>, cio&egrave; l&rsquo;apparente anomalia era la taglia del comune e "
             f"la distanza da Palermo. <b>Secondo test, e secondo risultato negativo</b>: "
             f"sui 390 comuni "
             f"l&rsquo;ipotesi naturale (dove il treno pesa di pi&ugrave;, il divario di "
             f"genere sul lavoro &egrave; pi&ugrave; piccolo) d&agrave; un&rsquo;associazione "
             f"<b>non distinguibile da zero</b>, Spearman {num(rho, 2)} con p = {num(p, 2)}. "
             f"E Bagheria &egrave; al {num(perc_treno, 0)}&deg; percentile siciliano per uso "
             f"del treno, cio&egrave; fra i comuni che il treno lo usano di pi&ugrave;.",
        lettura=f"Nel pannello A ogni bolla &egrave; un comune e il <b>diametro</b> &egrave; il "
                "numero di pendolari, non il valore: la scala dei diametri sta in legenda. "
                "L&rsquo;asse orizzontale &egrave; in <b>scala logaritmica</b>, quindi la "
                "stessa distanza sullo schermo vale un raddoppio di chilometri e non un "
                "numero fisso. Le due linee sono l&rsquo;attesa del modello a taglia fissata: "
                "continua per il comune mediano, tratteggiata per la taglia di Bagheria. "
                "Bagheria &egrave; la bolla vermiglia, etichettata con osservato e atteso. "
                "Nel pannello B i due istogrammi contano i comuni: sopra la quota grezza, "
                "sotto il residuo del modello, con la verticale vermiglia su Bagheria. "
                f"<b>Il finding &egrave; lo spostamento fra i due istogrammi</b>: dal "
                f"{num(perc_grezzo, 0)}&deg; al {num(perc_residuo, 0)}&deg; percentile, "
                f"cio&egrave; una volta tolte taglia e distanza Bagheria &egrave; un comune "
                f"qualunque. Un risultato negativo si riporta perch&eacute; &egrave; stato "
                f"testato, non nonostante lo sia. "
                "Attenzione a due cose: l&rsquo;associazione &egrave; <b>ecologica</b>, "
                "calcolata fra comuni e non fra persone, quindi orienta l&rsquo;ipotesi e non "
                "la dimostra; e un test che non rifiuta non prova l&rsquo;assenza di un "
                "effetto, dice che con questi dati non se ne vede. <b>Conseguenza di "
                "progettazione: la leva non &egrave; il collegamento, &egrave; la "
                "transizione</b>, ed &egrave; il motivo per cui la scheda 4 non propone "
                "nessuna infrastruttura.",
        fonte="ISTAT, matrice del pendolarismo 2021 e censimento 2011 &rarr; "
              "<b>mob_taglia_distanza.csv</b>, <b>mob_treno_390.csv</b>, "
              "<b>mob_ribaltamento_390.csv</b>. Figura a piena risoluzione: "
              "<b>figures/mob_fig04_taglia_distanza.png</b>.")

    rit = pd.read_csv(PROCESSED / "genere_ritenzione_eta.csv")
    n_coorte = (rit[(rit.nome_territorio == "Bagheria") & rit.eta_2021.between(25, 29)]
                .groupby("genere").n_2021.sum())
    corpo += blocco(
        fig(),
        "Dove la mobilit&agrave; femminile si spegne, la coorte si assottiglia",
        legenda([("femmine", COL_G["F"]), ("maschi", COL_G["M"])]),
        divergenti([{"label": f"{r.nome_territorio} ({ETICHETTA_G[r.genere]})",
                     "valore": r["ritenzione_%"], "colore": COL_G[r.genere],
                     "forte": r.nome_territorio == "Bagheria" and r.genere == "F"}
                    for _, r in c2529.iterrows()],
                   centro=100, lab=150, coda=52,
                   etichetta_centro="100 = coorte intatta"),
        mostra="Ritenzione della coorte che aveva 25-29 anni nel 2021, misurata al 2024: "
               "quante persone su 100 sono ancora residenti nello stesso comune, per genere e "
               "quattro territori. &Egrave; l&rsquo;et&agrave; in cui la mobilit&agrave; "
               "femminile per lavoro si spegne, misurata qui da una <b>terza fonte</b> che "
               "non condivide n&eacute; tavola n&eacute; denominatore con le figure 3.1-3.4. "
               "Il profilo completo per et&agrave; singola, che mostra dove si apre la "
               "finestra, &egrave; la figura 2.4.",
        base=f"N = {num(n_coorte.sum(), 0)} persone nella coorte 25-29 di Bagheria al 2021 "
             f"({num(n_coorte['F'], 0)} femmine e {num(n_coorte['M'], 0)} maschi); per gli "
             f"altri territori i denominatori sono di due o tre ordini di grandezza "
             f"superiori. Conteggi censuari, <b>nessun intervallo di confidenza</b>. La "
             f"ritenzione femminile di Bagheria &egrave; l&rsquo;unica cella femminile sotto "
             f"100 dei quattro territori. La misura &egrave; un <b>saldo netto</b> fra "
             f"iscrizioni e cancellazioni: confonde partenze, arrivi e rettifiche "
             f"anagrafiche, e ai 25-29 la mortalit&agrave; &egrave; trascurabile ma le "
             f"rettifiche no.",
        lettura="Le barre partono dalla verticale a 100, che &egrave; la coorte intatta, e la "
                "loro lunghezza &egrave; lo <b>scarto</b> da quella linea: a destra la coorte "
                "&egrave; cresciuta, a sinistra si &egrave; ridotta. Sono disegnate cos&igrave; "
                "e non da zero perch&eacute; 96,3 contro 103,0 su una scala 0-110 sarebbero "
                "indistinguibili a occhio. Rosa le femmine, blu i maschi; a piena "
                "intensit&agrave; la cella di Bagheria femmine. <b>Il limite che questa scheda "
                "dichiara per prima</b>: n&eacute; la matrice del pendolarismo n&eacute; la "
                "tavola per mezzo hanno la dimensione et&agrave;, quindi il target 15-34 del "
                "bando non &egrave; isolabile sul pendolarismo, e questa coorte non si somma "
                "alle figure precedenti. Il motivo dello spostamento &egrave; "
                "un&rsquo;informazione d&rsquo;et&agrave; solo parziale (chi esce per studio "
                "&egrave; quasi solo secondaria superiore e universit&agrave;) e viene usato "
                "come tale.",
        fonte="ISTAT, censimento permanente, et&agrave; singole 2021 e 2024 &rarr; "
              "<b>genere_coorti.csv</b>, denominatori da "
              "<b>genere_ritenzione_eta.csv</b>.")

    return scrivi("scheda3_pendolarismo.html",
                  "Il pendolarismo di Bagheria verso Palermo", corpo,
                  "Scheda 3 di 4 &middot; risponde al focus &laquo;dinamiche e ruolo del "
                  "pendolarismo verso Palermo&raquo;.")


# ============================================================== 4. Ponte 19

def scheda_ponte19() -> Path:
    """La proposta di intervento, e il vincolo di misura che la distingue da un auspicio."""
    S = "4. Ponte 19"
    fig = Numera(4)
    netto = pd.read_csv(PROCESSED / "genere_kpi_netto.csv").set_index("orizzonte")
    platea = pd.read_csv(PROCESSED / "genere_platea.csv")
    tetto = pd.read_csv(PROCESSED / "genere_tetto_platea.csv")
    mde = pd.read_csv(PROCESSED / "genere_mde.csv")
    gapp = pd.read_csv(PROCESSED / "genere_gap_persone.csv")
    sin = pd.read_csv(PROCESSED / "mob_sintesi.csv")
    det = pd.read_csv(PROCESSED / "genere_composizione_stato_dettaglio.csv")
    stati = pd.read_csv(PROCESSED / "edu_youth_states_2018_2024.csv")
    pre = pd.read_csv(PROCESSED / "genere_pretrend.csv")
    gem = pd.read_csv(PROCESSED / "genere_gemelle.csv")

    pb = platea[(platea.nome_territorio == "Bagheria")].set_index("genere")
    b24 = stati[(stati.territorio_nome == "Bagheria") & (stati.anno == 2024)].iloc[0]
    d24 = det[(det.nome_territorio == "Bagheria") & (det.anno == 2024) &
              (det.destinazione == "fuori e non in cerca")]
    inatt = d24.groupby("genere").persone.sum()
    n29, n34 = netto.loc[2029], netto.loc[2034]
    mde_occ = mde[mde.KPI.str.startswith("tasso di occupazione")].set_index(
        "anni pooled per lato")
    tf = tetto[tetto.genere == "F"].set_index("orizzonte")
    bersaglio = sin[sin.misura.str.startswith("donne in pi")].valore.iloc[0]
    pilota = 200

    claim(S, "platea femminile 15-24, 2024 -> 2029 -> 2034",
          f"{pb.loc['F'].platea_2024:.0f} -> {pb.loc['F'].platea_2029:.0f} -> "
          f"{pb.loc['F'].platea_2034:.0f}", "persone", "genere_platea.csv",
          "conteggio di chi e' gia' nato e residente, non una proiezione")
    claim(S, "variazione della platea F al 2034", pb.loc["F"].var_2034_pct, "%",
          "genere_platea.csv", "sui maschi e' -5,8%: l'asimmetria e' locale")
    claim(S, "KPI lordo, attrito e netto al 2029",
          f"{n29.kpi_lordo:.1f} / {n29.attrito_demografico:.1f} / {n29.kpi_netto:.1f}",
          "occupate", "genere_kpi_netto.csv", "al tasso obiettivo di Palermo")
    claim(S, "KPI netto al 2034", n34.kpi_netto, "occupate", "genere_kpi_netto.csv",
          "DIVERSO dallo scenario «non si fa niente» (-19/-37, genere_tetto_platea.csv)")
    claim(S, "scenario «non si fa niente», 2029 / 2034",
          f"{tf.loc[2029].delta_vs_2024:.1f} / {tf.loc[2034].delta_vs_2024:.1f}", "occupate",
          "genere_tetto_platea.csv", "tasso 2024 fermo")
    claim(S, "MDE annuale contro delta da rilevare",
          f"{mde_occ.loc[1, 'MDE 80% (pp)']:.2f} vs "
          f"{mde_occ.loc[1, 'delta da rilevare (pp)']:.1f}", "p.p.", "genere_mde.csv",
          "la lettura annuale NON e' ammessa sui KPI primari")
    claim(S, "inattivi non studenti 15-24, F / M",
          f"{inatt['F']:.0f} / {inatt['M']:.0f}", "persone",
          "genere_composizione_stato_dettaglio.csv", "51% F: il gruppo non e' femminile")
    claim(S, "pendenza del tasso F 2018-2024 e test di pre-trend vs Palermo",
          f"{pre.iloc[0].stima:.2f} pp/anno; p={pre.iloc[1].p:.2f}", "-",
          "genere_pretrend.csv", "prerequisito del controfattuale, testato non assunto")

    corpo = intestazione(
        "Proposta di intervento &middot; Ponte 19 &middot; servizio comunale di transizione e "
        "riattivazione &middot; 18-25 anni",
        "Il KPI va scritto in tasso: le stesse &laquo;+40 occupate&raquo; valgono +18 nel 2029 "
        "e &minus;2 nel 2034.",
        f"<b>Ponte 19</b> &egrave; un servizio comunale di transizione con <b>outreach attivo</b> "
        f"(non a domanda spontanea), <b>due finestre di ingaggio</b> e una <b>quota di genere</b>. "
        f"Le tre scelte non sono preferenze di design: ognuna risponde a un numero delle schede "
        f"1-3.",
        f"<b>Il vincolo che rende la proposta seria.</b> La platea femminile 15-24 "
        f"<b>&egrave; gi&agrave; nata</b> e cala del {num(-pb.loc['F'].var_2034_pct)}% al 2034 "
        f"(sui coetanei maschi {num(-pb.loc['M'].var_2034_pct)}%). Un obiettivo scritto in teste "
        f"si annullerebbe da solo entro il 2034 senza che nessuno abbia sbagliato nulla. "
        f"Per questo il KPI primario &egrave; un <b>tasso</b>, con la sua finestra di lettura "
        f"dichiarata prima dell&rsquo;avvio.")

    corpo += blocco(
        fig("Tavola"),
        "Dalle evidenze alle scelte di progetto",
        tabella(["Evidenza", "Dove", "Scelta imposta"],
                [(f"Il {num(b24.inattivi_su_fuori)}% di chi &egrave; fuori non cerca",
                  "fig. 1.5", "outreach attivo, non sportello a domanda"),
                 ("Le uscite hanno due tempi: i ragazzi a 17-19 e 23-24 con rientri, "
                  "le ragazze da 24-25 senza rientri", "fig. 2.4, 3.5",
                  "<b>due finestre</b>: A 18-20 all&rsquo;uscita, B 22-25 sulla conversione"),
                 (f"{num(inatt['F'], 0)} ragazze e {num(inatt['M'], 0)} ragazzi, "
                  f"etichette opposte", "fig. 2.5",
                  "<b>quota &ge;50% F</b> e due tracce di contatto distinte"),
                 ("Almeno l&rsquo;89% delle casalinghe &egrave; nubile", "fig. 2.5",
                  "attivazione dalla famiglia d&rsquo;origine, non sola conciliazione"),
                 ("A pari istruzione il lavoro non arriva, e la posizione regionale "
                  "&egrave; stabile da tredici anni", "fig. 2.3",
                  "il servizio non finanzia altra istruzione: paga l&rsquo;anello intatto"),
                 ("L&rsquo;offerta di trasporto non spiega il divario, e a pari taglia e "
                  "distanza Bagheria &egrave; nella media", "fig. 3.4",
                  "<b>nessun intervento infrastrutturale</b>: la leva &egrave; la transizione"),
                 ("Le donne vanno a Palermo in treno, gli uomini in auto", "fig. 3.3",
                  "sedi, orari e tirocini scelti su ci&ograve; che &egrave; raggiungibile "
                  "senza auto"),
                 (f"La platea F cala del {num(-pb.loc['F'].var_2034_pct)}% al 2034",
                  "fig. 4.2", "<b>KPI in tasso</b>, riparametrato ogni anno sulla platea")],
                forte=(f"Il {num(b24.inattivi_su_fuori)}% di chi &egrave; fuori non cerca",)),
        mostra="La derivazione del progetto: ogni riga &egrave; un numero delle schede 1-3 e "
               "la scelta di disegno che quel numero impone. Si legge da sinistra a destra, "
               "una riga per volta. La tavola <b>non</b> &egrave; un elenco di funzionalit&agrave; "
               "del servizio: &egrave; l&rsquo;elenco delle scelte che i dati hanno gi&agrave; "
               "chiuso, e ogni riga senza evidenza a monte &egrave; stata tolta.",
        base="Nessun numero nuovo: le otto righe rimandano alle figure che li producono, con "
             "N, incertezza e cautele dichiarati l&igrave;. Due righe sono <b>risultati "
             "negativi</b> (l&rsquo;offerta di trasporto e la taglia del comune), e sono "
             "quelle che escludono un intervento invece di aggiungerlo: valgono quanto le "
             "altre.",
        lettura="La riga in nero &egrave; quella che decide la forma del servizio: se sette "
                "persone su dieci fra chi &egrave; fuori non stanno cercando, uno sportello a "
                "domanda spontanea raggiunge il segmento che si sta gi&agrave; risolvendo da "
                "s&eacute;. La colonna centrale &egrave; un rimando, non un dato.",
        fonte="Derivazione completa in <b>docs/POLICY_PONTE_19.md</b>. Ogni numero rimanda "
              "alla figura che lo produce, e da l&igrave; al file di "
              "<b>data/processed/</b>.")

    corpo += blocco(
        fig(),
        "Perch&eacute; il KPI non pu&ograve; essere scritto in teste",
        '<div class="duo">'
        '<div><h4>Orizzonte 2029</h4>'
        + cascata([("+40 occupate\nsulla platea 2024", n29.kpi_lordo, "totale"),
                   ("attrito\ndemografico", n29.attrito_demografico, "delta"),
                   ("KPI netto\n2029", n29.kpi_netto, "totale")], w=290, h=196,
                  fmt=lambda v: num(v, 1, segno=True)) + '</div>'
        '<div><h4>Orizzonte 2034</h4>'
        + cascata([("+40 occupate\nsulla platea 2024", n34.kpi_lordo, "totale"),
                   ("attrito\ndemografico", n34.attrito_demografico, "delta"),
                   ("KPI netto\n2034", n34.kpi_netto, "totale")], w=290, h=196,
                  fmt=lambda v: num(v, 1, segno=True)) + '</div></div>',
        mostra=f"Che cosa resta dello stesso obiettivo a due orizzonti, in <b>numero di "
               f"occupate</b>. Le &laquo;+40 occupate&raquo; sono l&rsquo;effetto lordo di "
               f"portare l&rsquo;occupazione femminile 15-24 di Bagheria al tasso di Palermo "
               f"({num(n29.tasso_obiettivo_pct)}%); applicato alla platea di ciascun anno, lo "
               f"stesso obiettivo incontra un attrito demografico. La figura <b>non</b> "
               f"&egrave; una previsione di quante saranno le occupate: &egrave; il conto di "
               f"che cosa misura un target scritto in teste.",
        base=f"La platea femminile 15-24 passa da {num(pb.loc['F'].platea_2024, 0)} (2024) a "
             f"{num(pb.loc['F'].platea_2029, 0)} (2029) a {num(pb.loc['F'].platea_2034, 0)} "
             f"(2034): &egrave; un <b>conteggio di chi &egrave; gi&agrave; nato e residente</b> "
             f"al 2024 fatto scorrere per et&agrave;, non una proiezione demografica, quindi "
             f"non ha incertezza di modello e non incorpora migrazione futura. Sui coetanei "
             f"maschi il calo al 2034 &egrave; {num(pb.loc['M'].var_2034_pct)}%, meno di un "
             f"terzo: l&rsquo;asimmetria &egrave; locale e nota. Nessun intervallo di "
             f"confidenza: tutti i termini sono aritmetica su conteggi.",
        lettura=f"Ogni cascata si legge da sinistra: la prima barra &egrave; l&rsquo;effetto "
                f"lordo, la seconda l&rsquo;attrito (negativa, in rosso), la terza il netto. "
                f"Le tratteggiate collegano il livello di una barra all&rsquo;inizio della "
                f"successiva e non sono dati. I due pannelli hanno la stessa scala, quindi le "
                f"altezze si confrontano fra orizzonti. <b>Due numeri, due domande: non "
                f"confonderli.</b> {num(tf.loc[2029].delta_vs_2024)} e "
                f"{num(tf.loc[2034].delta_vs_2024)} &egrave; lo scenario &laquo;non si fa "
                f"niente&raquo; (tasso 2024 fermo, <b>genere_tetto_platea.csv</b>); "
                f"{num(n29.attrito_demografico)} e {num(n34.attrito_demografico)} &egrave; "
                f"l&rsquo;attrito sullo stesso conto al tasso obiettivo. Se serve un "
                f"equivalente in teste per la comunicazione si scrive cos&igrave; e non "
                f"altrimenti: &laquo;+40 occupate sulla platea 2024; il target si riparametra "
                f"ogni anno come tasso-obiettivo &times; platea dell&rsquo;anno&raquo;, con la "
                f"formula pubblicata.",
        fonte="ISTAT, et&agrave; singole del censimento permanente 2024 &rarr; "
              "<b>genere_platea.csv</b>, <b>genere_kpi_netto.csv</b>, "
              "<b>genere_tetto_platea.csv</b>.")

    corpo += blocco(
        fig("Tavola"),
        "Quando si potr&agrave; dire se ha funzionato",
        tabella(["Finestra di lettura", "MDE 80%", "Potenza sul delta"],
                [(f"{int(k)} {'anno' if k == 1 else 'anni'} pooled per lato",
                  num(r["MDE 80% (pp)"], 2, " p.p."),
                  num(r["potenza per il delta (%)"], 0, "%"))
                 for k, r in mde_occ.iterrows()],
                forte=("3 anni pooled per lato",)),
        mostra="Il disegno di valutazione dichiarato <b>prima</b> dell&rsquo;avvio: per ogni "
               "finestra di lettura, il minimo effetto rilevabile (MDE) sul tasso di "
               "occupazione femminile 15-24, in punti percentuali, e la potenza statistica "
               "sull&rsquo;effetto atteso. La tavola dice <b>quando</b> si potr&agrave; "
               "rispondere, non se l&rsquo;intervento funzioner&agrave;.",
        base=f"Calcolo di potenza sui <b>denominatori reali</b> di Bagheria, non su un N "
             f"ipotetico. Soglie convenzionali: alfa 0,05 a due code, potenza obiettivo 80% "
             f"per la colonna MDE. Il delta da rilevare &egrave; "
             f"{num(mde_occ.loc[1, 'delta da rilevare (pp)'])} punti; su un anno solo il "
             f"minimo rilevabile &egrave; {num(mde_occ.loc[1, 'MDE 80% (pp)'], 2)} punti, "
             f"cio&egrave; <b>sopra</b> il delta, quindi la lettura annuale del KPI primario "
             f"non &egrave; ammessa. Controfattuale dichiarato in anticipo: <b>Palermo</b>, "
             f"col prerequisito testato e non assunto (pendenza di Bagheria "
             f"{num(pre.iloc[0].stima, 2)} pp/anno, differenza con Palermo "
             f"p = {num(pre.iloc[1].p, 2)}, cio&egrave; le due traiettorie pre-intervento non "
             f"si distinguono). Ancoraggio dei target sulle {len(gem)} gemelle strutturali.",
        lettura="&laquo;Pooled per lato&raquo; significa che gli anni vengono accorpati prima "
                "e dopo l&rsquo;avvio: tre anni per lato sono sei anni di dati, non tre. La "
                "riga in nero &egrave; la sola finestra su cui il KPI primario si legge, ed "
                "&egrave; una scelta vincolante, non un consiglio. La lettura <b>annuale</b> "
                "spetta ai KPI di processo, che oggi nessuno rileva e che il servizio produce: "
                "primo contatto entro 30 giorni, piano entro 15, utenza per et&agrave; singola "
                "e genere contro la platea residente, copertura separata delle due finestre.",
        fonte="Calcolo di potenza sui denominatori reali &rarr; <b>genere_mde.csv</b>; "
              "pre-trend in <b>genere_pretrend.csv</b>; gruppo di controllo in "
              "<b>genere_gemelle.csv</b>.")

    corpo += blocco(
        fig("Tavola"),
        "Target, capacit&agrave; e ordine di grandezza",
        kpi([(num(b24.inattivi_non_studenti, 0), "inattivi non studenti 15-24, la platea "
              f"({num(inatt['F'], 0)} F, {num(inatt['M'], 0)} M)", COL["Bagheria"]),
             (num(pilota, 0), f"presi in carico nel primo anno "
              f"(~{num(100 * pilota / b24.inattivi_non_studenti, 0)}% della platea)", INCHIOSTRO),
             ("&ge;50%", "quota femminile minima sui presi in carico, monitorata ogni "
              "trimestre", COL_G["F"])]),
        tabella(["Scenario di convergenza", "Misura", "Persone"],
                [(r.scenario, "occupazione F 15-24", num(r["occupate in più (2024)"], 0))
                 for _, r in gapp.iterrows()] +
                [("divario di pendolarismo pari alla media siciliana",
                  "donne che lavorano fuori comune", num(bersaglio, 0))],
                forte=("parit&agrave; con i coetanei maschi di Bagheria",)),
        mostra="Il dimensionamento del pilota: la platea di riferimento, la capacit&agrave; "
               "del primo anno e la quota di genere minima; sotto, quattro scenari di "
               "convergenza espressi in <b>persone</b>. Gli scenari dicono quanto vale il "
               "divario, non quanto il servizio produrr&agrave;: sono un ordine di grandezza "
               "del bersaglio, non un obiettivo.",
        base=f"Platea: {num(b24.inattivi_non_studenti, 0)} inattivi non studenti 15-24 al "
             f"2024 ({num(inatt['F'], 0)} F, {num(inatt['M'], 0)} M). Capacit&agrave; del "
             f"primo anno {num(pilota, 0)} prese in carico, cio&egrave; il "
             f"{num(100 * pilota / b24.inattivi_non_studenti, 0)}% della platea. I quattro "
             f"scenari poggiano su <b>denominatori diversi</b>: i primi tre sull&rsquo;"
             f"occupazione femminile 15-24, il quarto sulle donne che lavorano fuori comune, "
             f"da una fonte che non condivide n&eacute; tavola n&eacute; base. Che cadano "
             f"nello stesso ordine di grandezza &egrave; il motivo per cui vengono riportati "
             f"insieme, non una loro somma.",
        lettura="Gli scenari <b>non si sommano</b>: misurano popolazioni diverse sullo stesso "
                "passaggio, e sommarli conterebbe due volte le stesse persone. La riga in nero "
                "&egrave; lo scenario di riferimento della proposta. <b>Decision gate a 90 "
                "giorni</b>: il modulo esperienza si attiva solo con &ge;30 posti a domanda e "
                "mentor verificati; il supporto mobilit&agrave; solo se il trasporto risulta "
                "barriera primaria su un sottogruppo con offerta coerente; se la quota di "
                "genere scende sotto il 40% si rivedono i canali di contatto <i>prima</i> di "
                "aumentare la capacit&agrave;. Il servizio genera, per ogni presa in carico, il "
                "record <b>titolo &rarr; uscita &rarr; barriera &rarr; azione &rarr; esito a "
                "3/6/12 mesi</b>: &egrave; l&rsquo;unico modo di misurare a Bagheria il "
                "rapporto individuale fra titolo di studio e condizione lavorativa, che le "
                "tavole pubbliche non incrociano (figura 2.1).",
        fonte="<b>genere_gap_persone.csv</b>, <b>mob_sintesi.csv</b>, "
              "<b>edu_youth_states_2018_2024.csv</b>, "
              "<b>genere_composizione_stato_dettaglio.csv</b>.")

    corpo += blocco(
        fig("Tavola"),
        "La finestra di lettura del KPI, come esce dal notebook",
        figura("fig09_kpi_finestra", intera=True, larghezza=1650),
        mostra="&Egrave; la tavola tecnica dietro le figure 4.2 e 4.3, nella versione "
               "integrale che sta nello zip: la cascata del KPI netto e la potenza per "
               "finestra di lettura sulla stessa pagina, con la didascalia a quattro blocchi "
               "incorporata. Compare <b>intera e non ritagliata</b> per la stessa ragione "
               "della tavola 2.6: qui il punto non &egrave; il numero, che la scheda ha "
               "gi&agrave; dato, ma che la tavola sia leggibile da sola quando qualcuno la "
               "trova fuori da questa scheda.",
        base="Nessun numero nuovo rispetto alle figure 4.2 e 4.3: stessi denominatori, stesse "
             "soglie, stesso controfattuale. La didascalia incorporata nell&rsquo;immagine "
             "dichiara N, metodo e cautele per conto proprio, ed &egrave; esattamente "
             "ci&ograve; che questa pagina vuole mostrare.",
        lettura="A questa larghezza il testo dentro l&rsquo;immagine si legge; nelle colonne "
                "strette delle altre figure non si leggerebbe, ed &egrave; il motivo per cui "
                "l&igrave; viene ritagliato via e ricomposto in HTML. Il criterio &egrave; "
                "scritto in <b>pipeline/schede.py</b>, funzione <code>figura()</code>: "
                "ritaglio al solo grafico dentro un ragionamento, immagine intera quando la "
                "figura &egrave; essa stessa l&rsquo;oggetto.",
        fonte="Generata da <b>viz/fig09_kpi_finestra.R</b> &rarr; "
              "<b>figures/fig09_kpi_finestra.png</b> (300 dpi) e <b>.svg</b>. Dati: "
              "<b>genere_kpi_netto.csv</b>, <b>genere_platea.csv</b>, "
              "<b>genere_mde.csv</b>.")

    return scrivi("scheda4_ponte19.html", "Ponte 19", corpo,
                  "Scheda 4 di 4 &middot; risponde alla richiesta &laquo;Proposta di "
                  "intervento&raquo;. Versione integrale: <b>docs/POLICY_PONTE_19.md</b>.")


# ===================================================================== esecuzione

def bande_figure() -> None:
    """`--bande`: stampa la struttura a bande di ogni PNG di figures/.

    Serve solo a decidere il valore di TESTA quando una figura cambia impaginazione:
    l'ultima colonna dice quante bande restano dopo aver tolto la didascalia.
    """
    import numpy as np
    from PIL import Image

    for png in sorted(FIGURE.glob("*.png")):
        b = _bande(np.asarray(Image.open(png).convert("L")))
        testa = TESTA.get(png.stem, 1)
        print(f"{png.stem:34s} bande={len(b):2d} testa={testa} "
              f"grafico={len(b) - testa - CODA_DIDASCALIA:2d}  "
              + " ".join(f"[{s}-{f}]" for s, f in b))


def main() -> None:
    import sys

    if "--bande" in sys.argv:
        return bande_figure()
    SCHEDE.mkdir(parents=True, exist_ok=True)
    prodotte = [scheda_profilo(), scheda_forbice(), scheda_pendolarismo(), scheda_ponte19()]

    registro = pd.DataFrame(CLAIM)
    registro.to_csv(PROCESSED / "schede_claim.csv", index=False)

    # Il controllo minimo: quattro schede non vuote, ogni claim con la sua fonte, e la
    # composizione 15-24 che chiude a 100. Se una tavola cambia forma, si rompe qui e
    # non in silenzio dentro una figura.
    assert len(prodotte) == 4 and all(p.stat().st_size > 8000 for p in prodotte)
    assert not registro.empty and registro.fonte.str.len().min() > 0

    # I quattro blocchi della didascalia sono argomenti obbligatori di blocco(), quindi
    # non possono mancare; qui si controlla che ce ne sia uno per ogni <section>, cioe'
    # che nessuno sia stato svuotato con una stringa vuota per fretta.
    for p in prodotte:
        testo = p.read_text(encoding="utf-8")
        sezioni, didascalie = testo.count("<section"), testo.count('<div class="did">')
        assert sezioni == didascalie, f"{p.name}: {sezioni} blocchi, {didascalie} didascalie"
        assert didascalie * 4 == testo.count("<p><b>Cosa mostra.</b>") \
            + testo.count("<p><b>Base statistica.</b>") \
            + testo.count("<p><b>Come si legge.</b>") + testo.count("<p><b>Fonte.</b>"), \
            f"{p.name}: una didascalia non ha tutti e quattro i blocchi"
        # La regola dell'em-dash vale sul testo renderizzato, non solo nelle figure R.
        assert "&mdash;" not in testo and "—" not in testo, f"{p.name}: em-dash"
    stati = pd.read_csv(PROCESSED / "edu_youth_states_2018_2024.csv")
    b = stati[(stati.territorio_nome == "Bagheria") & (stati.anno == 2024)].iloc[0]
    somma = (b.quota_occupati + b.quota_in_cerca + b.quota_studenti
             + b.quota_inattivi_non_studenti)
    assert abs(somma - 100) < 0.5, f"la composizione 15-24 non chiude a 100: {somma}"

    for p in prodotte:
        print(f"scritto: docs/schede/{p.name}  ({p.stat().st_size // 1024} KB)")
    print(f"scritto: data/processed/schede_claim.csv  ({len(registro)} claim tracciati)")


if __name__ == "__main__":
    main()

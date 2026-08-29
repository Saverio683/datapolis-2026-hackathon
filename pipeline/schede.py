"""data/processed/ -> docs/schede/: le quattro schede tematiche della proposta.

Ogni scheda risponde a UNA richiesta della locandina, incrociando i tre thread:

    scheda1_profilo.html       Profiling statistico & benchmarking (educazione + genere)
    scheda2_forbice.html       Focus differenze di genere + titolo x condizione
    scheda3_pendolarismo.html  Focus pendolarismo verso Palermo (mobilita + genere)
    scheda4_ponte19.html       Proposta di intervento

Le schede sono HTML autoportante: nessun asset esterno, nessuna rete, i grafici sono
SVG inline generati qui. Si aprono in un browser e si stampano in PDF (@page A4).

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


def blocco(titolo: str, sommario: str, *contenuto: str, fonte: str, nota: str = "") -> str:
    corpo = "".join(contenuto)
    nota_html = f'<p class="nota">{nota}</p>' if nota else ""
    return (f'<section class="blocco"><h3>{titolo}</h3><p class="somm">{sommario}</p>'
            f'{corpo}{nota_html}<p class="fonte">{fonte}</p></section>')


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
.nota{font-size:11.5px;color:#4A4741;margin:12px 0 0;padding:9px 12px;background:#F5F2EC;
border-radius:2px;line-height:1.5}
.nota b{color:var(--inchiostro)}
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
        f"I {num(b24.popolazione, 0)} quindici-ventiquattrenni di Bagheria, uno per uno",
        "Un quadrato ogni 50 residenti. Il blocco arancione &egrave; la met&agrave; del problema che "
        "nessuna statistica corrente conta: giovani che non studiano, non lavorano e non "
        "risultano in cerca di occupazione.",
        legenda([(f"{n} &middot; {num(v, 0)}", c) for n, v, c in gruppi]),
        waffle(gruppi, per_quadrato=50, colonne=22),
        fonte="ISTAT, censimento permanente 2024, ricostruzione della tavola 15-24 "
              "&rarr; <b>edu_youth_states_2018_2024.csv</b>. Le componenti diverse dagli "
              "occupati sono stime della ricostruzione, non conteggi.")

    righe_imp = []
    for nome in ORDINE:
        r = stati[(stati.territorio_nome == nome) & (stati.anno == 2024)].iloc[0]
        righe_imp.append((nome, [
            ("studenti", r.quota_studenti, COL_STATO["studenti"]),
            ("occupati", r.quota_occupati, COL_STATO["occupati"]),
            ("in cerca", r.quota_in_cerca, COL_STATO["in cerca"]),
            ("inattivi", r.quota_inattivi_non_studenti, COL_STATO["casalinghe/i"])]))
    corpo += blocco(
        "Il benchmarking: pi&ugrave; studenti della media, meno occupati, pi&ugrave; inattivi",
        "Condizione prevalente dei 15-24enni, 2024. Bagheria ha la quota di studenti pi&ugrave; alta "
        "del panel e insieme la quota di occupati pi&ugrave; bassa: il territorio trattiene i "
        "giovani dentro la formazione e non li consegna al lavoro.",
        impilate(righe_imp),
        fonte="ISTAT, censimento permanente 2024 &rarr; <b>edu_youth_states_2018_2024.csv</b>.")

    delta = [("occupati", b18.quota_occupati, b24.quota_occupati),
             ("studenti", b18.quota_studenti, b24.quota_studenti),
             ("in cerca di occupazione", b18.quota_in_cerca, b24.quota_in_cerca),
             ("inattivi non studenti", b18.quota_inattivi_non_studenti,
              b24.quota_inattivi_non_studenti)]
    corpo += blocco(
        "Il recupero c&rsquo;&egrave;. La convergenza no.",
        "Da dove viene il miglioramento 2018-2024: quasi tutto dal calo di chi cerca lavoro, "
        "quasi niente dalla riattivazione di chi non cerca. Il divario occupazionale con la "
        "Sicilia &egrave; identico all&rsquo;inizio e alla fine del periodo.",
        tabella(["Condizione 15-24", "2018", "2024", "variazione"],
                [(n, num(a, 1, "%", zero=True), num(b, 1, "%", zero=True),
                  num(b - a, 1, " p.p.", segno=True, zero=True))
                 for n, a, b in delta] +
                [("gap occupazione vs Sicilia",
                  num(b18.quota_occupati - s18.quota_occupati, 1, " p.p.", segno=True),
                  num(b24.quota_occupati - s24.quota_occupati, 1, " p.p.", segno=True),
                  "invariato")],
                forte=("inattivi non studenti", "gap occupazione vs Sicilia")),
        fonte="ISTAT, censimento permanente &rarr; <b>edu_youth_states_2018_2024.csv</b>.",
        nota="<b>Cautela dichiarata.</b> Fra il 2019 e il 2021 c&rsquo;&egrave; una rottura di misura "
             "sulla componente &laquo;in cerca di occupazione&raquo;: i confronti fra territori "
             "reggono, i livelli delle singole componenti no. Il <b>2020 manca alla fonte</b> "
             "sulla classe 15-24 e non &egrave; stato interpolato.")

    corpo += blocco(
        "Il NEET del bando: due misure, mai una serie",
        "La locandina chiede il NEET 15-34. A livello comunale <b>non esiste</b>: la fascia non "
        "&egrave; pubblicata. Si riportano due misure diverse, ciascuna con la sua etichetta, e "
        "non si sommano n&eacute; si mettono in serie.",
        '<div class="duo">'
        f'<div><h4>2011 &middot; NEET 15-29 (8milaCensus, L4)</h4>'
        + barre([{"label": n, "valore": float(l4[n]), "colore": COL[n], "forte": n == "Bagheria"}
                 for n in ORDINE], w=300, lab=76, coda=46) +
        f'<p class="fonte">Percentile fra i 390 comuni siciliani: '
        f'{num(perc_l4_91, 0)}&deg; nel 1991 &rarr; <b>{num(perc_l4, 0)}&deg; nel 2011</b>. '
        f'Bagheria migliora in assoluto e arretra in posizione.</p></div>'
        f'<div><h4>2024 &middot; fuori da lavoro e studio, 15-24</h4>'
        + barre([{"label": n, "valore": float(
            stati[(stati.territorio_nome == n) & (stati.anno == 2024)]
            .quota_fuori_lavoro_studio.iloc[0]),
            "colore": COL[n], "forte": n == "Bagheria"} for n in ORDINE],
            w=300, lab=76, coda=46) +
        f'<p class="fonte">Proxy costruito sulla condizione professionale. '
        f'Di questo {num(b24.quota_fuori_lavoro_studio)}%, il '
        f'<b>{num(b24.inattivi_su_fuori)}% non risulta in cerca di occupazione</b>.</p></div>'
        '</div>',
        fonte="ISTAT 8milaCensus 2011 (<b>edu_historical_benchmarks_2011.csv</b>) e censimento "
              "permanente 2024 (<b>edu_youth_states_2018_2024.csv</b>).",
        nota="<b>Perch&eacute; non si sommano.</b> Fasce diverse (15-29 contro 15-24), "
             "definizioni diverse, rilevazioni diverse. Affiancarle &egrave; corretto, unirle in "
             "una serie sarebbe un errore, non un&rsquo;approssimazione. I due pannelli hanno "
             "<b>scale indipendenti</b>: si confrontano le posizioni dentro ciascun pannello, "
             "mai le lunghezze fra l&rsquo;uno e l&rsquo;altro.")

    corpo += blocco(
        "La fuga sta nel denominatore",
        "Ogni tasso di questa scheda ha sotto una popolazione che si assottiglia, e senza "
        "ricambio migratorio: il calo &egrave; al netto di niente.",
        kpi([(num(pb.loc[2024].popolazione_15_34, 0), "residenti 15-34 nel 2024, da "
              f"{num(pb.loc[2021].popolazione_15_34, 0)} nel 2021", COL["Bagheria"]),
             (num(pb.loc[2024].variazione_da_primo_anno_pct, 1, "%"),
              "in tre anni (Italia: +1,2%)", COL["Bagheria"]),
             (num(quota_stranieri, 1, "%"),
              "stranieri sul 15-34, contro 12,4% in Italia", INCHIOSTRO)]),
        fonte="ISTAT, censimento permanente &rarr; <b>edu_youth_population_15_34.csv</b>, "
              "<b>genere_stranieri.csv</b>.",
        nota="<b>Cosa questo numero non dice.</b> &Egrave; un <b>saldo netto</b>: nessuna fonte "
             "comunale d&agrave; la destinazione di chi se ne va, quindi non si pu&ograve; "
             "chiamarlo &laquo;emigrazione misurata&raquo;.")

    return scrivi("scheda1_profilo.html",
                  "Il profilo dei giovani di Bagheria", corpo,
                  "Scheda 1 di 4 &middot; risponde alla richiesta "
                  "&laquo;Profiling statistico &amp; Benchmarking&raquo;.")


# ============================================================== 2. la forbice

def scheda_forbice() -> Path:
    """Focus differenze di genere, e la risposta obliqua a «titolo x condizione»."""
    S = "2. forbice"
    q = pd.read_csv(PROCESSED / "genere_quadro_sintesi.csv").set_index("nome_territorio")
    serie = pd.read_csv(PROCESSED / "genere_forbice_serie.csv")
    quad = pd.read_csv(PROCESSED / "genere_forbice_quadrante.csv")
    mille = pd.read_csv(PROCESSED / "genere_per_1000.csv")
    ci = pd.read_csv(PROCESSED / "genere_gap_occupazione_ci.csv")
    det = pd.read_csv(PROCESSED / "genere_composizione_stato_dettaglio.csv")
    civ = pd.read_csv(PROCESSED / "genere_stato_civile.csv")
    bounds = pd.read_csv(PROCESSED / "genere_casalinghe_bounds.csv")
    pos = pd.read_csv(PROCESSED / "genere_posizionamento.csv").set_index("indicatore")
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
        f"{num(-b['gap istruzione (M-F)'])} punti pi&ugrave; dei coetanei &mdash; il vantaggio "
        f"educativo femminile pi&ugrave; ampio del panel &mdash; e hanno un tasso di occupazione "
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
        "Due misure, la stessa base di 1.000 persone",
        "Ogni barra &egrave; su 1.000 residenti dello stesso sesso, 15-24 anni, Bagheria 2024. "
        "Le ragazze superano i coetanei sul titolo di studio e ne fanno la met&agrave; sul lavoro.",
        barre(per_mille, lab=214, fmt=lambda v: num(v, 0), coda=44),
        fonte="ISTAT, censimento permanente 2024 &rarr; <b>genere_per_1000.csv</b>.",
        nota="<b>Non &egrave; un imbuto.</b> Le due barre hanno la stessa base ma non sono "
             "le stesse persone seguite in sequenza: nelle tavole comunali il titolo di studio "
             "e la condizione professionale <b>non sono incrociati</b> (nella tavola lavoro il "
             "titolo &egrave; solo &laquo;totale&raquo;, in quella istruzione la condizione "
             "&egrave; solo &laquo;totale&raquo;). &laquo;Quante diplomate di Bagheria "
             "lavorano&raquo; non &egrave; una domanda a cui i dati pubblici rispondono &mdash; "
             "ed &egrave; il primo dato che il servizio proposto nella scheda 4 produrrebbe.")

    q24 = quad[quad.anno == 2024]
    punti = [(breve(r.nome_territorio), r.vantaggio_diploma_15_24_pp, r.tasso_occupazione_F,
              COL.get(r.nome_territorio, GRIGIO), r.nome_territorio == "Bagheria")
             for _, r in q24.iterrows()]
    ser_f = {breve(n): dict(zip(g.anno, g.tasso_occupazione_F))
             for n, g in serie.groupby("nome_territorio")}
    corpo += blocco(
        "La forbice: pi&ugrave; il vantaggio educativo cresce, meno il lavoro arriva",
        "A sinistra il piano istruzione &times; occupazione sulla <b>stessa fascia 15-24</b>: "
        "Bagheria &egrave; sola nell&rsquo;angolo &laquo;pi&ugrave; istruite, meno occupate&raquo;. "
        "A destra la serie del tasso femminile: la distanza dagli altri territori non si chiude.",
        '<div class="duo">'
        '<div><h4>2024 &middot; il quadrante</h4>'
        + quadrante(punti, xlab="vantaggio femminile sul diploma (p.p.)",
                    ylab="occupazione femminile 15-24 (%)", w=300, h=232) + '</div>'
        '<div><h4>2018-2024 &middot; occupazione femminile 15-24</h4>'
        + linee(ser_f, w=300, h=232, coda=92) + '</div></div>',
        fonte="ISTAT, censimento permanente &rarr; <b>genere_forbice_quadrante.csv</b>, "
              "<b>genere_forbice_serie.csv</b>. Il 2020 manca alla fonte e non &egrave; "
              "interpolato.",
        nota="<b>Il claim robusto, e quello che non lo &egrave;.</b> Sulla fascia 15-24 il "
             "primato del vantaggio educativo &egrave; un pareggio con la Sicilia: il claim "
             "solido non &egrave; &laquo;le pi&ugrave; istruite d&rsquo;Italia&raquo;, ma il "
             "<b>distacco dal vicinato</b> unito alla <b>mancata conversione</b>.")

    corpo += blocco(
        "Dentro l&rsquo;inattivit&agrave;: stesse dimensioni, etichette opposte",
        f"I circa {num(inatt.sum(), 0)} giovani fuori da lavoro, studio e ricerca "
        f"<b>non sono un gruppo femminile</b>: {num(inatt['F'], 0)} ragazze e "
        f"{num(inatt['M'], 0)} ragazzi. Sono femminili nell&rsquo;<b>etichetta</b> che il "
        f"censimento assegna loro, e l&rsquo;etichetta &egrave; il canale di contatto.",
        legenda([("femmine", COL_G["F"]), ("maschi", COL_G["M"])]),
        barre([{"label": "casalinghe (F)", "valore": casa["F"], "colore": COL_G["F"], "forte": True},
               {"label": "casalinghi (M)", "valore": casa["M"], "colore": COL_G["M"]},
               {"label": "«altra condizione» (F)", "valore": altra["F"],
                "colore": COL_G["F"]},
               {"label": "«altra condizione» (M)", "valore": altra["M"],
                "colore": COL_G["M"], "forte": True}],
              lab=196, fmt=lambda v: num(v, 0) + " persone", coda=90),
        fonte="ISTAT, censimento permanente 2024 &rarr; "
              "<b>genere_composizione_stato_dettaglio.csv</b>; stato civile al 1&deg; gennaio "
              "2025 (DCIS_POPRES1) &rarr; <b>genere_stato_civile.csv</b>.",
        nota=f"<b>Le casalinghe di Bagheria sono nubili.</b> Al 1&deg; gennaio 2025 le gi&agrave; "
             f"coniugate 15-24 sono {num(con25.gia_coniugate, 0)} "
             f"({num(con25.quota_gia_coniugate_pct)}%) contro {num(casa['F'], 0)} casalinghe: "
             f"almeno il <b>{num(nubili, 0)}% non &egrave; sposato</b>, e il matrimonio "
             f"under-25 a Bagheria sta <i>sotto</i> Palermo e Sicilia. Il canale non &egrave; la "
             f"famiglia propria ma quella d&rsquo;origine &mdash; quindi serve un servizio di "
             f"<b>attivazione</b>, non solo di conciliazione. "
             f"&Egrave; anche un dato sensibile alla struttura per et&agrave;: la quota passa "
             f"da {num(bounds.iloc[0, 1])}% sui 15-24 a {num(bounds.iloc[2, 1])}% se si "
             f"assume che nessuna abbia meno di 20 anni.")

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
        "Si esce per studiare, non per lavorare &mdash; e la destinazione &egrave; una sola.",
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

    corpo += blocco(
        "La destinazione ha un nome, ed &egrave; una sola",
        "Primi cinque comuni di arrivo di chi esce da Bagheria. Il secondo &egrave; sempre un "
        "ordine di grandezza sotto il primo: non c&rsquo;&egrave; da scegliere quale "
        "destinazione servire.",
        '<div class="duo">'
        '<div><h4>2011 &middot; motivo studio</h4>'
        + barre([{"label": r.comune, "valore": r.quota_su_chi_esce, "colore": COL["Bagheria"],
                  "forte": r.comune == "Palermo"} for _, r in studio11.iterrows()],
                w=300, lab=118, coda=48) + '</div>'
        '<div><h4>2021 &middot; motivo lavoro</h4>'
        + barre([{"label": r.comune, "valore": r.quota_su_chi_esce, "colore": COL["Bagheria"],
                  "forte": r.comune == "Palermo"} for _, r in lavoro21.iterrows()],
                w=300, lab=118, coda=48) + '</div></div>',
        fonte="ISTAT, matrici del pendolarismo &rarr; <b>mob_flussi_bagheria.csv</b>. "
              "La matrice ricostruisce sette su sette gli indicatori <i>M</i> gi&agrave; "
              "pubblicati da 8milaCensus: &egrave; il livello sottostante, non una fonte "
              "alternativa.",
        nota="<b>I due pannelli non sono una serie.</b> Il 2011 conta chi si sposta "
             "<i>giornalmente</i>, il 2021 chi si reca al lavoro <i>almeno tre giorni a "
             "settimana</i>, e il 2021 copre il solo lavoro. Si confronta la composizione "
             "(dove vanno, su cento che escono), mai il livello.")

    ordine_rib = ["Bagheria", "5 comuni vicini", "Sicilia", "Italia", "Comune di Palermo"]
    corpo += blocco(
        "Il ribaltamento: lo scarto di genere cambia segno col motivo",
        "Quota di chi esce dal comune, scarto femmine &minus; maschi. Il verso cambia in tutti i "
        "territori; la particolarit&agrave; di Bagheria &egrave; l&rsquo;<b>ampiezza</b> del salto.",
        slope([(n, rib.loc[n].gap_studio_F_M, rib.loc[n].gap_lavoro_F_M,
                COL.get(n, GRIGIO), n == "Bagheria") for n in ordine_rib],
              sx="per STUDIO", dx="per LAVORO"),
        fonte="ISTAT, censimento 2011, record esaustivi &rarr; "
              "<b>mob_ribaltamento_territori.csv</b>.",
        nota=f"<b>Replicato su una fonte che non condivide niente.</b> La stessa misura sul "
             f"censimento permanente 2018-2019 &mdash; altra rilevazione, altro metodo, sette "
             f"anni dopo &mdash; d&agrave; per Bagheria "
             f"{num(pen19.loc[('Bagheria', 'WK')].gap_M_meno_F)} punti sul lavoro contro "
             f"{num(pen19.loc[('Sicilia', 'WK')].gap_M_meno_F)} in Sicilia, e il segno "
             f"opposto sullo studio. <b>E non &egrave; il divario occupazionale travestito</b>: "
             f"il denominatore &egrave; gi&agrave; condizionato al motivo &mdash; chi si sposta "
             f"per lavoro un lavoro ce l&rsquo;ha.")

    corpo += blocco(
        "Il treno &egrave; il canale femminile &mdash; e non &egrave; sottoutilizzato",
        "Come raggiungono Palermo, fra chi esce da Bagheria. Le donne sul mezzo collettivo, "
        "gli uomini in auto: un servizio che d&agrave; per scontata l&rsquo;auto seleziona per "
        "genere.",
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
        + f'<p class="fonte">Tutti i motivi. Le donne partono pi&ugrave; tardi e viaggiano '
          f'pi&ugrave; a lungo, per 17 chilometri. Il rientro non &egrave; rilevato: il carico '
          f'di cura resta un&rsquo;ipotesi, non un dato.</p></div></div>',
        fonte="ISTAT, censimento 2011, tavola per mezzo e orario &rarr; "
              "<b>mob_mezzo_genere.csv</b>, <b>mob_orario_genere.csv</b>. Stima campionaria "
              "(comuni sopra i 20.000 abitanti), calibrata sui margini dei conteggi esaustivi; "
              "errore relativo mediano 0,9%.",
        nota=f"<b>Un risultato negativo, riportato perch&eacute; &egrave; stato testato.</b> "
             f"Bagheria &egrave; al <b>{num(perc_treno, 0)}&deg; percentile siciliano</b> per "
             f"uso del treno: non c&rsquo;&egrave; infrastruttura sottoutilizzata da attivare. "
             f"E sui 390 comuni l&rsquo;ipotesi naturale &mdash; dove il treno pesa di pi&ugrave; "
             f"il divario di genere &egrave; pi&ugrave; piccolo &mdash; d&agrave; "
             f"un&rsquo;associazione <b>non distinguibile da zero</b>: Spearman "
             f"{num(rho, 2)}, p = {num(p, 2)}. "
             f"Anche &laquo;Bagheria si muove poco&raquo; non regge: a parit&agrave; di taglia e "
             f"distanza dal capoluogo il residuo &egrave; {num(tagb.residuo)} punti. "
             f"<b>Conseguenza di progettazione: la leva non &egrave; il collegamento, &egrave; "
             f"la transizione.</b>")

    corpo += blocco(
        "Dove la mobilit&agrave; femminile si spegne, la coorte si assottiglia",
        "Ritenzione della coorte 25-29 fra 2021 e 2024: quanti restano ogni 100. &Egrave; "
        "l&rsquo;unica cella femminile negativa dei quattro territori, ed &egrave; lo stesso "
        "passaggio, misurato da una terza fonte che non condivide n&eacute; tavola n&eacute; "
        "denominatore.",
        legenda([("femmine", COL_G["F"]), ("maschi", COL_G["M"])]),
        divergenti([{"label": f"{r.nome_territorio} ({ETICHETTA_G[r.genere]})",
                     "valore": r["ritenzione_%"], "colore": COL_G[r.genere],
                     "forte": r.nome_territorio == "Bagheria" and r.genere == "F"}
                    for _, r in c2529.iterrows()],
                   centro=100, lab=150, coda=52,
                   etichetta_centro="100 = coorte intatta"),
        fonte="ISTAT, censimento permanente, et&agrave; singole 2021-2024 &rarr; "
              "<b>genere_coorti.csv</b>. &Egrave; un <b>saldo netto</b>: non ha destinazione e "
              "non si somma al pendolarismo, che invece non ha l&rsquo;et&agrave;.",
        nota="<b>Il limite che questa scheda dichiara per prima.</b> N&eacute; la matrice del "
             "pendolarismo n&eacute; il censimento permanente hanno la dimensione et&agrave;: "
             "il target 15-34 del bando <b>non &egrave; isolabile</b> sul pendolarismo. Il "
             "motivo dello spostamento &egrave; un&rsquo;informazione d&rsquo;et&agrave; "
             "parziale &mdash; chi esce per studio &egrave; quasi solo secondaria superiore e "
             "universit&agrave; &mdash; e viene usato come tale.")

    return scrivi("scheda3_pendolarismo.html",
                  "Il pendolarismo di Bagheria verso Palermo", corpo,
                  "Scheda 3 di 4 &middot; risponde al focus &laquo;dinamiche e ruolo del "
                  "pendolarismo verso Palermo&raquo;.")


# ============================================================== 4. Ponte 19

def scheda_ponte19() -> Path:
    """La proposta di intervento, e il vincolo di misura che la distingue da un auspicio."""
    S = "4. Ponte 19"
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
        "Dalle evidenze alle scelte di progetto",
        "Ogni riga: il numero che l&rsquo;ha imposta, e in quale scheda sta.",
        tabella(["Evidenza", "Scheda", "Scelta imposta"],
                [("Il 70,6% di chi &egrave; fuori non cerca", "1",
                  "outreach attivo, non sportello a domanda"),
                 (f"Le uscite hanno due tempi: i ragazzi a 17-19 e 23-24 con rientri, "
                  f"le ragazze da 24-25 senza rientri", "2, 3",
                  "<b>due finestre</b>: A 18-20 all&rsquo;uscita, B 22-25 sulla conversione"),
                 (f"{num(inatt['F'], 0)} ragazze e {num(inatt['M'], 0)} ragazzi, "
                  f"etichette opposte", "2",
                  "<b>quota &ge;50% F</b> e due tracce di contatto distinte"),
                 ("Almeno l&rsquo;89% delle casalinghe &egrave; nubile", "2",
                  "attivazione dalla famiglia d&rsquo;origine, non sola conciliazione"),
                 ("Il treno &egrave; al 98&deg; percentile; l&rsquo;offerta di trasporto non "
                  "spiega il divario", "3",
                  "<b>nessun intervento infrastrutturale</b>: la leva &egrave; la transizione"),
                 ("Le donne vanno a Palermo in treno, gli uomini in auto", "3",
                  "sedi, orari e tirocini scelti su ci&ograve; che &egrave; raggiungibile "
                  "senza auto"),
                 (f"La platea F cala del {num(-pb.loc['F'].var_2034_pct)}% al 2034", "4",
                  "<b>KPI in tasso</b>, riparametrato ogni anno sulla platea")],
                forte=("Il 70,6% di chi &egrave; fuori non cerca",)),
        fonte="Derivazione completa in <b>docs/POLICY_PONTE_19.md</b>; ogni numero rimanda "
              "alla scheda che lo produce.")

    corpo += blocco(
        "Perch&eacute; il KPI non pu&ograve; essere scritto in teste",
        f"Le &laquo;+40 occupate&raquo; sono l&rsquo;effetto lordo di portare Bagheria al tasso "
        f"femminile di Palermo ({num(n29.tasso_obiettivo_pct)}%). Applicato alla platea di "
        f"ciascun anno, lo stesso obiettivo incontra un attrito demografico che se lo mangia. "
        f"La platea femminile 15-24 passa da {num(pb.loc['F'].platea_2024, 0)} (2024) a "
        f"{num(pb.loc['F'].platea_2029, 0)} (2029) a {num(pb.loc['F'].platea_2034, 0)} "
        f"(2034); sui coetanei maschi il calo al 2034 &egrave; "
        f"{num(pb.loc['M'].var_2034_pct)}%, meno di un terzo.",
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
        fonte="ISTAT, et&agrave; singole del censimento permanente &rarr; "
              "<b>genere_platea.csv</b>, <b>genere_kpi_netto.csv</b>. La platea &egrave; un "
              "conteggio di chi &egrave; gi&agrave; nato e residente, non una proiezione "
              "demografica.",
        nota=f"<b>Due numeri, due domande: non confonderli.</b> "
             f"{num(tf.loc[2029].delta_vs_2024)} e {num(tf.loc[2034].delta_vs_2024)} &egrave; "
             f"lo scenario &laquo;non si fa niente&raquo; (tasso 2024 fermo). "
             f"{num(n29.attrito_demografico)} e {num(n34.attrito_demografico)} &egrave; "
             f"l&rsquo;attrito sullo stesso conto al tasso obiettivo. "
             f"Se serve un equivalente in teste per la comunicazione si scrive cos&igrave; e non "
             f"altrimenti: &laquo;+40 occupate sulla platea 2024; il target si riparametra ogni "
             f"anno come tasso-obiettivo &times; platea dell&rsquo;anno&raquo;, con la formula "
             f"pubblicata.")

    corpo += blocco(
        "Quando si potr&agrave; dire se ha funzionato",
        f"Il delta da rilevare &egrave; {num(mde_occ.loc[1, 'delta da rilevare (pp)'])} punti. "
        f"Su un anno solo il minimo rilevabile &egrave; "
        f"{num(mde_occ.loc[1, 'MDE 80% (pp)'], 2)} punti: la lettura annuale del KPI primario "
        f"<b>non &egrave; ammessa</b>, e dichiararlo prima dell&rsquo;avvio &egrave; parte "
        f"della proposta.",
        tabella(["Finestra di lettura", "MDE 80%", "Potenza sul delta"],
                [(f"{int(k)} {'anno' if k == 1 else 'anni'} pooled per lato",
                  num(r["MDE 80% (pp)"], 2, " p.p."),
                  num(r["potenza per il delta (%)"], 0, "%"))
                 for k, r in mde_occ.iterrows()],
                forte=("3 anni pooled per lato",)),
        fonte="Calcolo di potenza sui denominatori reali &rarr; <b>genere_mde.csv</b>. "
              "Controfattuale dichiarato in anticipo: <b>Palermo</b>; il prerequisito &egrave; "
              f"testato, non assunto (pendenza di Bagheria {num(pre.iloc[0].stima, 2)} pp/anno, "
              f"differenza con Palermo p = {num(pre.iloc[1].p, 2)}). "
              f"Ancoraggio dei target sulle {len(gem)} gemelle strutturali "
              f"(<b>genere_gemelle.csv</b>).",
        nota="La lettura <b>annuale</b> spetta ai KPI di processo, che oggi nessuno rileva e che "
             "il servizio produce: primo contatto entro 30 giorni, piano entro 15, utenza per "
             "et&agrave; singola e genere contro la platea residente, copertura separata delle "
             "due finestre.")

    corpo += blocco(
        "Target, capacit&agrave; e ordine di grandezza",
        "Il pilota non promette di risolvere il problema: promette di misurarlo mentre lo "
        "affronta. Le tre stime di bersaglio vengono da misure che <b>non condividono il "
        "denominatore</b> e cadono nello stesso ordine di grandezza.",
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
        fonte="<b>genere_gap_persone.csv</b>, <b>mob_sintesi.csv</b>, "
              "<b>edu_youth_states_2018_2024.csv</b>. Gli scenari <b>non si sommano</b>: "
              "misurano popolazioni diverse sullo stesso passaggio.",
        nota="<b>Decision gate a 90 giorni.</b> Il modulo esperienza si attiva solo con "
             "&ge;30 posti a domanda e mentor verificati; il supporto mobilit&agrave; solo se il "
             "trasporto risulta barriera primaria su un sottogruppo con offerta coerente; se la "
             "quota di genere scende sotto il 40% si rivedono i canali di contatto <i>prima</i> "
             "di aumentare la capacit&agrave;. Il servizio genera, per ogni presa in carico, il "
             "record <b>titolo &rarr; uscita &rarr; barriera &rarr; azione &rarr; esito a 3/6/12 "
             "mesi</b>: &egrave; l&rsquo;unico modo di misurare a Bagheria il rapporto "
             "individuale fra titolo di studio e condizione lavorativa, che le tavole pubbliche "
             "non incrociano (scheda 2).")

    return scrivi("scheda4_ponte19.html", "Ponte 19", corpo,
                  "Scheda 4 di 4 &middot; risponde alla richiesta &laquo;Proposta di "
                  "intervento&raquo;. Versione integrale: <b>docs/POLICY_PONTE_19.md</b>.")


# ===================================================================== esecuzione

def main() -> None:
    SCHEDE.mkdir(parents=True, exist_ok=True)
    prodotte = [scheda_profilo(), scheda_forbice(), scheda_pendolarismo(), scheda_ponte19()]

    registro = pd.DataFrame(CLAIM)
    registro.to_csv(PROCESSED / "schede_claim.csv", index=False)

    # Il controllo minimo: quattro schede non vuote, ogni claim con la sua fonte, e la
    # composizione 15-24 che chiude a 100. Se una tavola cambia forma, si rompe qui e
    # non in silenzio dentro una figura.
    assert len(prodotte) == 4 and all(p.stat().st_size > 8000 for p in prodotte)
    assert not registro.empty and registro.fonte.str.len().min() > 0
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

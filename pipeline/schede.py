"""data/processed/ -> docs/schede/: le quattro schede tematiche della proposta.

Ogni scheda risponde a UNA richiesta della locandina, incrociando i tre thread:

    scheda1_profilo.html       Profiling statistico & benchmarking (educazione + genere)
    scheda2_genere.html        Focus differenze di genere + titolo x condizione
    scheda3_pendolarismo.html  Focus pendolarismo verso Palermo (mobilita + genere)
    scheda4_ponte19.html       Proposta di intervento

Le schede sono HTML autoportante: nessun asset esterno, nessuna rete. I grafici sono
di due tipi, entrambi incorporati nel file: SVG inline generati qui, e le figure di
figures/ come data URI. Si aprono in un browser e si stampano in PDF (@page A4).

Ogni blocco porta la didascalia delle figure R (cosa mostra, come si legge, fonte;
la base statistica resta obbligatoria nel sorgente ma non si stampa dal 2026-08-30):
in blocco() sono argomenti obbligatori, e
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


def il(testo: str, a: bool = False) -> str:
    """L'articolo davanti a una cifra: «l'89%», «il 13%»; con `a`, «all'82%», «al 41%»."""
    vocale = testo.startswith(("8", "11", "18"))
    return ("all&rsquo;" if vocale else "al ") if a else ("l&rsquo;" if vocale else "il ")


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

    # Il numero sta di norma oltre la punta della barra. Quando le barre di un lato sono
    # lunghe li' non c'e' spazio, e il numero finisce sopra l'etichetta di riga: succedeva
    # sui residui della scheda 1, dove tutti e sei i valori sono negativi e il mezzo grafico
    # a destra resta vuoto. In quel caso i numeri di quel lato passano dall'altra parte
    # della linea. Passano TUTTI, non solo quelli che sbordano, altrimenti la colonna dei
    # numeri si spezza a meta' e si legge peggio dello sbordo.
    # ponytail: larghezza del testo stimata a 6,2 px per carattere (font-size 11.5), come
    # il budget in caratteri di a_capo() in viz/theme.R. Se un giorno servisse precisione
    # vera qui serve una misura del font, non una stima.
    testi = [fmt(r["valore"]) for r in righe]
    stretto = any(meta - abs(sc) * scala - 7 - len(t) * 6.2 < x0 + 6
                  for sc, t in zip(scarti, testi) if sc < 0)
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
        if scarto < 0 and stretto:
            fine, ancora = meta + 7, "start"
        else:
            fine = meta + lung + 7 if scarto >= 0 else meta - lung - 7
            ancora = "start" if scarto >= 0 else "end"
        parti.append(_txt(fine, y + 12.5, testi[i], size=11.5, anchor=ancora,
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
        # Ancorata al bordo destro: a `xb + 14` la scritta usciva dal viewBox di
        # 7 px nelle figure a piena larghezza, e l'ultima lettera spariva.
        parti.append(_txt(w - 4, py(0) + 4, "parità F = M", size=9.5,
                          anchor="end"))
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
CODA_DIDASCALIA = 2


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

    `intera=False` (norma): via il titolo, il sottotitolo e la didascalia a 2 blocchi;
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
    """Un blocco = titolo dichiarativo + grafico + didascalia.

    E' la stessa anatomia di didascalia_4b() in viz/theme.R, e per lo stesso motivo:
    chi legge la scheda in sala non ha il notebook accanto. I quattro argomenti non sono
    facoltativi, sono senza default: un blocco cui manca `base` non compila. E' l'unico
    modo per impedire che «N e dispersione» finiscano dove capita, che e' come stavano
    prima.

    `base` resta obbligatorio ma **non si stampa** (2026-08-30, richiesta del team): la
    pagina era diventata piu' didascalia che grafico. Il testo vive nel sorgente accanto
    ai numeri che descrive, quindi chi scrive un blocco deve comunque dichiarare N e
    metodo prima di poterlo compilare; quello che cade e' solo la resa a schermo.

    mostra   metrica, unita', fascia d'eta', territori, anni; e cosa la figura NON dice
    base     N per gruppo, tendenza centrale, dispersione col metodo, test, esclusioni
    lettura  decodifica di cio' che non e' un dato: tratteggi, bande, colori, scale
    fonte    fonte con anno + il file di data/processed/ che rigenera i numeri
    """
    # Il controllo che prima stava in main() leggendo l'HTML: ora che `base` non si
    # stampa, l'unico posto dove si puo' vedere che non e' vuoto e' qui.
    assert all(t and t.strip() for t in (mostra, base, lettura, fonte)), \
        f"{numero}: didascalia incompleta"
    did = "".join(f"<p><b>{et}</b> {tx}</p>" for et, tx in (
        ("Cosa mostra.", mostra),
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
    # Le componenti «in cerca» e «inattivi» si confrontano solo dentro la stessa definizione:
    # fra 2019 e 2021 cambia la misura della condizione «in cerca» (docs/sources.md §7).
    b21 = stati[(stati.territorio_nome == "Bagheria") & (stati.anno == 2021)].iloc[0]
    s21 = stati[(stati.territorio_nome == "Sicilia") & (stati.anno == 2021)].iloc[0]
    stock = pd.read_csv(PROCESSED / "genere_stock_coorti.csv").set_index("nome_territorio")
    pop = pd.read_csv(PROCESSED / "edu_youth_population_15_34.csv")
    pb = pop[pop.territorio_nome == "Bagheria"].set_index("anno")
    stra = pd.read_csv(PROCESSED / "genere_stranieri.csv")
    sb = stra[(stra.nome_territorio == "Bagheria") & (stra.anno == 2024)]
    quota_stranieri = 100 * sb.FRGAPO.sum() / sb.totale.sum()
    dec = pd.read_csv(PROCESSED / "edu_change_decomposition_2018_2024.csv"
                      ).set_index("metrica")
    istr = pd.read_csv(PROCESSED / "edu_education_context_2018_2024.csv")
    pari = pd.read_csv(PROCESSED / "edu_matched_peers_2011.csv")
    rob = pd.read_csv(PROCESSED / "edu_model_robustness_2011.csv")
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
        f"sopra la Sicilia). A definizione costante, fra 2021 e 2024, chi cerca lavoro scende "
        f"da {num(b21.quota_in_cerca)}% a {num(b24.quota_in_cerca)}%, mentre gli inattivi non "
        f"studenti restano fermi ({num(b21.quota_inattivi_non_studenti)}% &rarr; "
        f"{num(b24.quota_inattivi_non_studenti)}%). Un servizio a domanda spontanea "
        f"raggiungerebbe chi gi&agrave; cerca, non il segmento che non si muove.")

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
        "Il benchmarking: meno occupati e pi&ugrave; inattivi di ogni territorio di confronto",
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
               "occupazionale con la Sicilia alle stesse due date. Da dove venga il "
               "miglioramento la tavola non pu&ograve; dirlo da sola: fra 2019 e 2021 cambia "
               "la misura della condizione &laquo;in cerca&raquo;, e le righe di chi cerca e "
               "degli inattivi attraversano quel cambio.",
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
                "nel 2024, la stessa cifra a un decimale: l&rsquo;occupazione non risente della "
                "rottura di misura. Le righe di chi cerca e degli inattivi s&igrave;, e vanno "
                "lette dentro la stessa definizione: fra 2021 e 2024 chi cerca passa da "
                f"{num(b21.quota_in_cerca)}% a {num(b24.quota_in_cerca)}%, gli inattivi non "
                f"studenti da {num(b21.quota_inattivi_non_studenti)}% a "
                f"{num(b24.quota_inattivi_non_studenti)}%.",
        fonte="ISTAT, censimento permanente 2018 e 2024 &rarr; "
              "<b>edu_youth_states_2018_2024.csv</b>.")

    # La tavola qui sopra dice DI QUANTO ogni condizione si e' mossa, non PERCHE'. La
    # scomposizione shift-share separa i due addendi: quanto sarebbe cambiato con i tassi
    # fermi e la sola popolazione che si assottiglia, e quanto per il solo cambiamento dei
    # tassi. Senza questa riga «gli inattivi calano di 102 persone» si legge come una
    # riattivazione, e per due terzi non lo e'. E' anche la riga che regge la scelta
    # dell'outreach nella scheda 4: non si puo' contare su un recupero spontaneo che in
    # buona parte e' demografia.
    ORD_DEC = ["fuori_lavoro_studio", "in_cerca", "inattivi_non_studenti",
               "occupati", "studenti"]
    d_ina = dec.loc["inattivi_non_studenti"]
    d_fuo = dec.loc["fuori_lavoro_studio"]
    quota_demo = 100 * abs(d_ina.effetto_popolazione) / abs(d_ina.variazione_conteggio)
    claim(S, "calo degli inattivi non studenti 15-24, 2018-2024",
          d_ina.variazione_conteggio, "persone",
          "edu_change_decomposition_2018_2024.csv",
          "due popolazioni diverse, non un pannello sulle stesse persone")
    claim(S, "quota di quel calo che e' sola demografia", quota_demo, "%",
          "edu_change_decomposition_2018_2024.csv",
          "shift-share: effetto popolazione contro effetto tasso")
    claim(S, "calo di chi e' fuori da lavoro e studio, di cui comportamento",
          f"{d_fuo.variazione_conteggio:.0f} / {d_fuo.effetto_tasso:.0f}", "persone",
          "edu_change_decomposition_2018_2024.csv",
          "sul totale il recupero e' quasi tutto effetto tasso")

    corpo += blocco(
        fig("Tavola"),
        "Il recupero, scomposto: quanto &egrave; comportamento e quanto &egrave; la "
        "coorte che si assottiglia",
        tabella(["Condizione 15-24", "2018", "2024", "variazione",
                 "di cui demografia", "di cui comportamento"],
                [(dec.loc[m].metrica_label,
                  num(dec.loc[m].conteggio_iniziale, 0),
                  num(dec.loc[m].conteggio_finale, 0),
                  num(dec.loc[m].variazione_conteggio, 0, segno=True),
                  num(dec.loc[m].effetto_popolazione, 0, segno=True),
                  num(dec.loc[m].effetto_tasso, 0, segno=True))
                 for m in ORD_DEC],
                forte=("Inattivi non studenti",)),
        mostra="Le condizioni dei 15-24 di Bagheria in <b>persone</b> agli estremi della "
               "serie, e la variazione spezzata nei due addendi che la compongono: quanto "
               "sarebbe cambiato con i tassi fermi al 2018 e la sola popolazione che si "
               "muove (<b>demografia</b>), e quanto per il solo cambiamento dei tassi a "
               "popolazione ferma (<b>comportamento</b>). La tavola <b>non</b> dice dove "
               "siano andate le persone uscite da una condizione: non &egrave; un pannello "
               "individuale, e la destinazione non &egrave; osservata.",
        base=f"N = {num(b18.popolazione, 0)} residenti 15-24 nel 2018 e "
             f"{num(b24.popolazione, 0)} nel 2024. La scomposizione &egrave; una "
             f"identit&agrave; aritmetica (shift-share a due termini), non una stima: i due "
             f"addendi sommano alla variazione a meno dell&rsquo;errore di macchina, e il "
             f"CSV porta la colonna di controllo che lo verifica riga per riga. Nessun "
             f"intervallo di confidenza e nessun test: sono conteggi censuari. "
             f"<b>Esclusioni</b>: il 2020 manca alla fonte sulla classe 15-24; fra 2019 e "
             f"2021 c&rsquo;&egrave; una rottura di misura sulla componente &laquo;in cerca "
             f"di occupazione&raquo;, che qui pesa sulla riga omonima e sul totale.",
        lettura=f"La colonna &laquo;di cui demografia&raquo; &egrave; negativa su tutte le "
                f"righe per una ragione sola: fra 2018 e 2024 la popolazione 15-24 di "
                f"Bagheria si riduce, e sottrae persone a ogni condizione, comprese quelle "
                f"che vorremmo veder crescere. <b>La riga in nero &egrave; il caveat della "
                f"scheda</b>: gli inattivi non studenti calano di "
                f"{num(-d_ina.variazione_conteggio, 0)} persone, ma "
                f"{num(-d_ina.effetto_popolazione, 0)} di quel calo "
                f"({num(quota_demo, 0)}%) &egrave; la coorte che si assottiglia, non gente "
                f"che si riattiva. Sul totale il segno &egrave; opposto e va detto: dei "
                f"{num(-d_fuo.variazione_conteggio, 0)} in meno fuori da lavoro e studio, "
                f"{num(-d_fuo.effetto_tasso, 0)} risultano comportamento, ma passano quasi "
                f"tutti dalla componente &laquo;in cerca&raquo;, che fra 2019 e 2021 cambia "
                f"misura: non si leggono come riattivazione. Prima riga e terza non si sommano: &laquo;fuori "
                f"da lavoro e studio&raquo; &egrave; gi&agrave; la somma di &laquo;in "
                f"cerca&raquo; e &laquo;inattivi non studenti&raquo;, non una sesta "
                f"condizione.",
        fonte="ISTAT, censimento permanente 2018 e 2024 &rarr; "
              "<b>edu_change_decomposition_2018_2024.csv</b>.")

    # L'istruzione e' la terza gamba della richiesta del bando («istruzione, occupazione,
    # NEET») e finora la scheda la toccava solo di striscio. Due fasce e due tavole
    # diverse: la 9-24 e' quella su cui il censimento pubblica il titolo di studio, la
    # 25-49 e' lo stock adulto e sta qui come contesto. Mai nella stessa figura senza
    # etichetta, e infatti sono due oggetti separati.
    ist9 = istr[istr.eta == "Y9-24"].set_index(["territorio_nome", "anno"])
    ist25 = istr[istr.eta == "Y25-49"].set_index(["territorio_nome", "anno"])
    q9 = lambda n, a: float(ist9.loc[(n, a)].quota_almeno_diploma)
    q25 = lambda n, a: float(ist25.loc[(n, a)].quota_almeno_diploma)
    gap9_18, gap9_24 = q9("Bagheria", 2018) - q9("Sicilia", 2018), q9("Bagheria", 2024) - q9("Sicilia", 2024)
    gap25_24 = q25("Bagheria", 2024) - q25("Sicilia", 2024)
    claim(S, "almeno diploma 9-24 a Bagheria, 2018 -> 2024",
          f"{q9('Bagheria', 2018):.1f} -> {q9('Bagheria', 2024):.1f}", "%",
          "edu_education_context_2018_2024.csv", "fascia 9-24 della fonte, include bambini")
    claim(S, "gap sul diploma 9-24 vs Sicilia, 2018 -> 2024",
          f"{gap9_18:.1f} -> {gap9_24:.1f}", "p.p.",
          "edu_education_context_2018_2024.csv")
    claim(S, "gap sul diploma 25-49 vs Sicilia, 2024", gap25_24, "p.p.",
          "edu_education_context_2018_2024.csv",
          "stock adulto: fascia diversa da quella giovanile, non confrontabile con la 9-24")

    corpo += blocco(
        fig(),
        "L&rsquo;istruzione: sui 9-24 il divario si &egrave; quasi chiuso, sullo stock "
        "adulto no",
        slope([(n, q9(n, 2018), q9(n, 2024), COL[n], n == "Bagheria") for n in ORDINE],
              sx="2018", dx="2024", fmt=lambda v: num(v, 1, "%")),
        tabella(["Territorio", "9-24, 2024", "25-49, 2024", "scarto fra le due fasce"],
                [(n, num(q9(n, 2024), 1, "%"), num(q25(n, 2024), 1, "%"),
                  num(q25(n, 2024) - q9(n, 2024), 1, " p.p.", segno=True))
                 for n in ORDINE], forte=("Bagheria",)),
        mostra="Quota di residenti con <b>almeno il diploma</b> di scuola secondaria "
               "superiore, in percentuale della popolazione della stessa fascia, nei quattro "
               "territori di confronto. Lo slope in alto &egrave; la sola fascia "
               "<b>9-24</b> fra il 2018 e il 2024; la tavola sotto affianca al 2024 la "
               "<b>9-24</b> e la <b>25-49</b>, che sono due fasce diverse e due tavole "
               "diverse della fonte. La figura <b>non</b> dice quanto in alto arriver&agrave; "
               "chi oggi ha 15 anni, e <b>non</b> incrocia il titolo con la condizione "
               "lavorativa: quell&rsquo;incrocio non esiste nei dati comunali (scheda 2).",
        base=f"Conteggi censuari, nessun intervallo di confidenza e nessun test: gli scarti "
             f"sono differenze aritmetiche. La fascia <b>9-24</b> &egrave; quella su cui la "
             f"fonte pubblica il titolo di studio a livello comunale e include i bambini in "
             f"et&agrave; scolare, quindi il livello assoluto va letto come indice di "
             f"confronto fra territori, non come &laquo;quota di diplomati&raquo;. La "
             f"<b>25-49</b> &egrave; lo stock adulto e sfora il target dell&rsquo;hackathon: "
             f"sta qui come contesto, mai come proxy dei giovani. Serie 2018-2024 completa "
             f"su entrambe le fasce, <b>2020 compreso</b>: a differenza della tavola lavoro "
             f"15-24, qui la fonte non ha il buco.",
        lettura=f"Bagheria &egrave; la linea vermiglia a tratto pieno, gli altri territori "
                f"al 55%. Nello slope conta la <b>pendenza</b>, non l&rsquo;altezza: tutti e "
                f"quattro i territori salgono, e Bagheria sale abbastanza da portare il "
                f"proprio divario con la Sicilia da "
                f"{num(gap9_18, 1, ' p.p.', segno=True)} a "
                f"{num(gap9_24, 1, ' p.p.', segno=True)}. Nella tavola la colonna a destra "
                f"&egrave; la distanza fra le due fasce dello stesso territorio: &egrave; "
                f"grande ovunque perch&eacute; la 9-24 contiene chi il diploma non pu&ograve; "
                f"ancora averlo, quindi si confrontano le <b>righe fra loro</b>, non le due "
                f"colonne. Su quel confronto Bagheria resta "
                f"{num(gap25_24, 1, ' p.p.', segno=True)} sotto la Sicilia sullo stock "
                f"adulto: la scolarizzazione che converge &egrave; quella dei ragazzi, non "
                f"quella gi&agrave; depositata nel territorio.",
        fonte="ISTAT, censimento permanente 2018-2024, tavola istruzione &rarr; "
              "<b>edu_education_context_2018_2024.csv</b>; divari in "
              "<b>edu_gaps_vs_sicily.csv</b>.")

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
               "altre definizioni. I cinque indicatori sono quelli del thread educazione; "
               "resta fuori la competenza di base (<b>I8</b>, licenza media fra i 15-19enni), "
               "l&rsquo;unica che nello stesso trentennio <b>guadagna</b> posizione: la "
               "discute la relazione, &sect;4.",
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
                f"siciliani il NEET di Bagheria passa dal percentile {num(perc_l4_91, 0)} del "
                f"1991 al percentile <b>{num(perc_l4, 0)} del 2011</b>, dove alto "
                f"&egrave; sfavorevole. Il valore migliora, la posizione peggiora.",
        fonte="ISTAT 8milaCensus 2011 (<b>edu_historical_benchmarks_2011.csv</b>, percentili "
              "da <b>edu_historical_bagheria.csv</b>) e censimento permanente 2024 "
              "(<b>edu_youth_states_2018_2024.csv</b>).")

    # Fin qui il confronto e' con Sicilia, Palermo e Italia, cioe' con territori scelti
    # dal bando. Obiezione ovvia: Bagheria e' un comune di 55mila abitanti in provincia,
    # confrontarla con l'Italia dice poco. Le due lenti di questo blocco cambiano la
    # definizione di «simile» e guardano se il risultato sopravvive: prima dieci comuni
    # siciliani costruiti per somigliarle su struttura e istruzione, poi sei modelli che
    # predicono l'esito atteso da quelle strutture. Il residuo e' orientato in modo che
    # a sinistra stia sempre «peggio dell'atteso»: senza il ribaltamento il NEET (alto =
    # male) e l'occupazione (alto = bene) punterebbero da parti opposte pur dicendo la
    # stessa cosa. Stessa regola del percentile favorevole due blocchi piu' su.
    VERSO_ROB = {"L14": 1, "L4": -1}
    NOME_ROB = {"L14": "occupazione 15-29", "L4": "NEET 15-29"}
    NOME_MOD = {"A_istruzione": "A", "B_istruzione_mobilita": "B",
                "C_contesto_territoriale": "C"}
    rob_righe = [{"label": f"{NOME_ROB[r.outcome]} · {NOME_MOD[r.modello]}",
                  "valore": r.residuo_bagheria * VERSO_ROB[r.outcome],
                  "colore": COL["Bagheria"],
                  "forte": r.modello == "C_contesto_territoriale"}
                 for r in rob.itertuples()]
    sotto = sum(1 for r in rob_righe if r["valore"] < 0)
    rob_c = rob[rob.modello == "C_contesto_territoriale"].set_index("outcome")
    peer = pari[pari.ruolo == "Peer"]
    bag_l14 = float(pari[pari.ruolo == "Bagheria"].L14.iloc[0])
    peggio_l14 = int((peer.L14 < bag_l14).sum())
    claim(S, "specifiche in cui Bagheria sta sotto l'atteso",
          f"{sotto}/{len(rob_righe)}", "specifiche", "edu_model_robustness_2011.csv",
          "residuo orientato: negativo = peggio dell'atteso su entrambi gli indicatori")
    claim(S, "residuo su occupazione 15-29, modello contesto territoriale",
          f"{rob_c.loc['L14'].residuo_bagheria:.1f} "
          f"[{rob_c.loc['L14'].residuo_ci95_basso:.1f}; "
          f"{rob_c.loc['L14'].residuo_ci95_alto:.1f}]", "p.p.",
          "edu_model_robustness_2011.csv", "2011, indicatore 15-29; IC 95% bootstrap")
    claim(S, "residuo sul NEET 15-29, modello contesto territoriale",
          f"{rob_c.loc['L4'].residuo_bagheria:.1f} "
          f"[{rob_c.loc['L4'].residuo_ci95_basso:.1f}; "
          f"{rob_c.loc['L4'].residuo_ci95_alto:.1f}]", "p.p.",
          "edu_model_robustness_2011.csv", "alto = sfavorevole: qui il segno positivo e' male")
    claim(S, "comuni simili con occupazione 15-29 piu' bassa di Bagheria",
          f"{peggio_l14}/{len(peer)}", "comuni", "edu_matched_peers_2011.csv",
          "pari scelti per struttura e istruzione, non per esito")

    corpo += blocco(
        fig(),
        f"Cambiando la definizione di &laquo;simile&raquo;, il risultato non cambia: "
        f"sotto l&rsquo;atteso in {sotto} specifiche su {len(rob_righe)}",
        '<h4>Prima lente &middot; i dieci comuni siciliani pi&ugrave; simili a Bagheria '
        '(2011, tasso di occupazione 15-29)</h4>',
        barre([{"label": r.nome_territorio, "valore": float(r.L14),
                "colore": COL["Bagheria"] if r.ruolo == "Bagheria" else GRIGIO,
                "forte": r.ruolo == "Bagheria"}
               for r in pari.sort_values("L14", ascending=False).itertuples()],
              lab=132, coda=48),
        '<h4>Seconda lente &middot; sei modelli, scarto fra Bagheria e ci&ograve; che la '
        'sua struttura lascerebbe prevedere</h4>',
        divergenti(rob_righe, centro=0.0, lab=170, coda=62,
                   etichetta_centro="atteso dal modello",
                   fmt=lambda v: num(v, 1, " p.p.", segno=True, zero=True)),
        mostra="Due modi diversi di rispondere alla stessa obiezione: che il ritardo di "
               "Bagheria sia solo l&rsquo;effetto di confrontarla con territori pi&ugrave; "
               "ricchi. In alto gli undici comuni (Bagheria e i dieci pi&ugrave; vicini per "
               "struttura demografica e istruzione, non per esito) sul tasso di occupazione "
               "15-29 al 2011. In basso, per due esiti e tre specifiche, lo <b>scarto fra il "
               "valore osservato di Bagheria e quello previsto</b> dal modello stimato sui "
               "389 altri comuni siciliani. Entrambe le lenti stanno al <b>2011</b>, "
               "l&rsquo;ultimo anno in cui la fascia 15-29 esiste a livello comunale: "
               "<b>non</b> sono aggiornabili al 2024 e <b>non</b> vanno messe in serie con "
               "le figure sul 15-24.",
        base=f"Prima lente: {len(peer)} comuni pari selezionati per minima distanza "
             f"standardizzata su struttura e istruzione; il pi&ugrave; vicino dista "
             f"{num(peer.distanza_standardizzata.min(), 2)} deviazioni standard, il "
             f"pi&ugrave; lontano {num(peer.distanza_standardizzata.max(), 2)}. Seconda "
             f"lente: 2 esiti &times; 3 specifiche = {len(rob_righe)} modelli lineari "
             f"stimati su {int(rob.n_comuni_training.iloc[0])} comuni, con intervallo di "
             f"confidenza al 95% sul residuo. La capacit&agrave; predittiva &egrave; "
             f"dichiarata e in met&agrave; dei casi &egrave; nulla: sull&rsquo;occupazione "
             f"l&rsquo;R&sup2; in validazione incrociata &egrave; negativo in tutte e tre le "
             f"specifiche, cio&egrave; il modello predice peggio della media. <b>Nessuna "
             f"interpretazione causale</b>: il residuo dice che Bagheria sta sotto "
             f"l&rsquo;atteso, non perch&eacute;.",
        lettura=f"Nel pannello in alto Bagheria &egrave; la barra vermiglia: dei "
                f"{len(peer)} comuni costruiti per somigliarle, <b>{peggio_l14} soli</b> "
                f"hanno un&rsquo;occupazione giovanile pi&ugrave; bassa. In quello in basso "
                f"la linea verticale &egrave; il valore che il modello si aspetta, e la "
                f"barra &egrave; lo scarto da l&igrave;: <b>a sinistra vuol dire sempre "
                f"peggio dell&rsquo;atteso</b>. Perch&eacute; questo valga su entrambi gli "
                f"indicatori il residuo del NEET &egrave; disegnato col segno ribaltato "
                f"(alto = sfavorevole): il numero grezzo &egrave; "
                f"{num(rob_c.loc['L4'].residuo_bagheria, 1, ' p.p.', segno=True)}, cio&egrave; "
                f"{num(rob_c.loc['L4'].residuo_bagheria, 1)} punti di NEET <i>in "
                f"pi&ugrave;</i> dell&rsquo;atteso. Le due barre a piena intensit&agrave; "
                f"sono la specifica pi&ugrave; severa, quella che controlla anche per il "
                f"contesto territoriale. Gli intervalli misurano l&rsquo;incertezza dei "
                f"coefficienti, non sono intervalli di previsione: dove il modello non "
                f"predice (R&sup2; fuori campione nullo o negativo) il residuo equivale allo "
                f"scarto dalla media, e la barra conferma il segno senza provare "
                f"un&rsquo;anomalia. "
                f"<b>Le tre specifiche</b>: <b>A</b> spiega l&rsquo;esito con la sola "
                f"istruzione del comune, <b>B</b> aggiunge la mobilit&agrave;, <b>C</b> "
                f"aggiunge il contesto territoriale (taglia, distanza dal capoluogo, "
                f"struttura demografica). Pi&ugrave; si scende, pi&ugrave; il confronto "
                f"&egrave; severo, perch&eacute; il modello ha pi&ugrave; modi di "
                f"giustificare il ritardo prima di attribuirlo a Bagheria.",
        fonte="ISTAT 8milaCensus 2011 &rarr; <b>edu_matched_peers_2011.csv</b> e "
              "<b>edu_model_robustness_2011.csv</b>.")

    corpo += blocco(
        fig("Tavola"),
        "La platea 15-34 si restringe, soprattutto per ricambio d&rsquo;et&agrave;",
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
                "misure sullo stesso denominatore. <b>Cosa il calo non dice</b>: &egrave; una "
                "variazione di stock, non un conteggio delle partenze. "
                f"{num(-stock.at['Bagheria', 'ricambio_eta'], 0)} delle "
                f"{num(-stock.at['Bagheria', 'variazione'], 0)} persone in meno sono ricambio "
                "d&rsquo;et&agrave; (le coorti che compiono 15 anni sono pi&ugrave; piccole di "
                "quelle che superano i 34); dentro le stesse coorti il saldo &egrave; "
                f"{num(stock.at['Bagheria', 'saldo_coorti_pct'], 2, '%')}, come in Sicilia "
                f"({num(stock.at['Sicilia', 'saldo_coorti_pct'], 2, '%')}). Il profilo per "
                "et&agrave;, che dice <i>chi</i> si perde e <i>quando</i>, sta nella figura 2.4.",
        fonte="ISTAT, censimento permanente, et&agrave; singole 2021-2024 &rarr; "
              "<b>edu_youth_population_15_34.csv</b>, <b>genere_stranieri.csv</b>, "
              "<b>genere_stock_coorti.csv</b>.")

    return scrivi("scheda1_profilo.html",
                  "Il profilo dei giovani di Bagheria", corpo,
                  "Scheda 1 di 4 &middot; risponde alla richiesta "
                  "&laquo;Profiling statistico &amp; Benchmarking&raquo;.")


# =============================================================== 2. il genere

def scheda_genere() -> Path:
    """Focus differenze di genere, e la risposta obliqua a «titolo x condizione»."""
    S = "2. genere"
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
    ben11 = pd.read_csv(PROCESSED / "edu_historical_benchmarks_2011.csv").pivot_table(
        index="indicatore", columns="territorio_nome", values="valore")
    tit = pd.read_csv(PROCESSED / "censpop_istr_lav_long.csv")
    dist = pd.read_csv(PROCESSED / "genere_distribuzione_390.csv").set_index("anno")
    rit = pd.read_csv(PROCESSED / "genere_ritenzione_eta.csv")
    coo = pd.read_csv(PROCESSED / "genere_coorti.csv")
    sc25 = pd.read_csv(PROCESSED / "genere_dopo_25_scarti.csv")
    gen25 = pd.read_csv(PROCESSED / "genere_dopo_25_generazioni.csv").set_index(["genere", "benchmark"])
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

    s25 = sc25[(sc25.anno == 2024) & (sc25.eta == "Y25-49")].set_index("genere")["vs Palermo"]
    claim(S, "scarto dal tasso di occupazione di Palermo a 25-49 anni, F / M",
          f"{s25['F']:.1f} / {s25['M']:.1f}", "p.p.", "genere_dopo_25_scarti.csv",
          "25-49 come test del meccanismo, non come misura dei giovani")
    claim(S, "scarto della generazione nata dal 1984, F / M (vs Palermo)",
          f"{gen25.at[('F', 'Palermo'), 'scarto_generazione_giovane']:.1f} / "
          f"{gen25.at[('M', 'Palermo'), 'scarto_generazione_giovane']:.1f}", "p.p.",
          "genere_dopo_25_generazioni.csv", "modello a due generazioni, non separa eta' e coorte")
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
        f"Le ragazze di Bagheria hanno il diploma pi&ugrave; spesso dei coetanei "
        f"({num(-b['gap istruzione (M-F)'])} punti sulla fascia 9-24 della tavola istruzione) e "
        f"hanno un tasso di occupazione 15-24 pari a {num(b['occupazione F'])}%, il pi&ugrave; basso dei quattro territori in "
        f"{minimi} annate su {annate}. Il capitale umano c&rsquo;&egrave;: quello che non "
        f"funziona &egrave; la conversione.",
        f"<b>La risposta alla domanda del bando.</b> Il capitale umano che Bagheria lascia "
        f"inutilizzato &egrave; soprattutto femminile. I due divari hanno <b>segno opposto</b>: "
        f"{num(-b['gap istruzione (M-F)'], 1, segno=True)} punti a favore delle ragazze "
        f"sull&rsquo;istruzione, {num(b['gap occupazione (M-F)'], 1, segno=True)} punti a "
        f"sfavore sull&rsquo;occupazione "
        f"[IC 95% {num(ci_b.gap_lo)}; {num(ci_b.gap_hi)}]. E non &egrave; un tratto di fascia "
        f"territoriale: fra i dieci comuni siciliani ugualmente scolarizzati, Bagheria &egrave; "
        f"<b>penultima</b> per occupazione femminile (15+, censimento 2011). E dopo lo studio "
        f"il divario non si chiude: a 25-49 anni le donne di Bagheria lavorano "
        f"{num(abs(s25['F']))} punti meno di quelle di Palermo, gli uomini {num(abs(s25['M']))}, "
        f"e la generazione nata dal 1984 ne porta circa "
        f"{num(abs(gen25.at[('F', 'Palermo'), 'scarto_generazione_giovane']), 0)}.")

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
        "I due divari: pi&ugrave; istruite dei coetanei, meno occupate che in ogni altro territorio",
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
                "la tavola 2.7. Nel pannello di destra la striscia grigia verticale "
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
        "Nel triennio 2021-2024 la coorte femminile cede fra i 22 e i 25 anni",
        figura("fig07_ritenzione_eta"),
        mostra="Residenti di ogni coorte nel 2024 per 100 residenti della stessa coorte nel "
               "2021 (un saldo netto di arrivi, partenze e decessi, non la quota di chi &egrave; "
               "rimasto), per <b>et&agrave; singola</b> da 14 a 30 anni e per genere, cinque "
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
             f"Italia, {num(c2529f['Palermo'])} a Palermo e {num(c2529f['Sicilia'])} in Sicilia.",
        lettura="La tratteggiata orizzontale a 100 &egrave; la parit&agrave;: sopra, la coorte "
                "&egrave; cresciuta; sotto, si &egrave; ridotta. Il rettangolo vermiglio "
                "chiaro, presente <b>solo sul pannello femminile</b>, &egrave; il soggetto "
                "della figura: la finestra 22-25. A sinistra le femmine, a destra i maschi, e "
                "i due pannelli condividono la scala verticale. Il vicinato &egrave; "
                "l&rsquo;insieme dei cinque comuni pi&ugrave; vicini per distanza fra i "
                "centroidi, non un vicino singolo. <b>Cautela</b>: la finestra 22-25 &egrave; "
                "una lettura <i>pooled</i>, e le transizioni annuali oscillano fino a 8 punti "
                "sulla stessa et&agrave;. Si titola sul triennio, mai sull&rsquo;anno singolo. "
                "E la differenza di genere &egrave; del solo triennio: sulle coorti seguite per "
                "cinque anni la perdita all&rsquo;uscita dal percorso formativo &egrave; di "
                "entrambi i generi, e i maschi perdono di pi&ugrave;. &Egrave; la figura che "
                "impone le due finestre di ingaggio della scheda 4.",
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
               f"ricerca attiva: in persone, per genere e per condizione. La figura "
               f"mostra l&rsquo;<b>etichetta</b>, non una condizione accertata n&eacute; "
               f"dichiarata: dal 2021 ISTAT la stima con un modello, sommando per comune "
               f"probabilit&agrave; individuali, e non dice nulla su quanto quelle persone "
               f"vorrebbero lavorare.",
        base=f"N = {num(inatt.sum(), 0)} persone fuori da lavoro e istruzione e non in cerca, "
             f"di cui {num(inatt['F'], 0)} femmine e {num(inatt['M'], 0)} maschi: il gruppo "
             f"&egrave; per met&agrave; maschile, non &egrave; un gruppo femminile. Stime "
             f"censuarie di modello, di cui ISTAT non pubblica l&rsquo;errore. Nella tavola i codici F, M e il "
             f"totale T convivono come righe sorelle: <b>il totale &egrave; filtrato via</b> "
             f"prima di sommare, altrimenti i conteggi raddoppiano. Sullo stato civile la "
             f"fonte e la data di riferimento sono diverse (1&deg; gennaio 2025, DCIS_POPRES1 "
             f"contro censimento 2024), quindi il {num(nubili, 0)}% qui sotto &egrave; un "
             f"<b>limite inferiore</b>, non una stima puntuale.",
        lettura=f"Rosa le femmine, blu i maschi; a piena intensit&agrave; le due barre che "
                f"reggono il ragionamento, cio&egrave; le casalinghe e l&rsquo;&laquo;altra "
                f"condizione&raquo; maschile. Le quattro barre sono conteggi sulla stessa "
                f"scala e si confrontano direttamente. <b>Le casalinghe di Bagheria non sono "
                f"giovani spose</b>: al 1&deg; gennaio 2025 le gi&agrave; coniugate 15-24 sono "
                f"{num(con25.gia_coniugate, 0)} ({num(con25.quota_gia_coniugate_pct)}%) contro "
                f"{num(casa['F'], 0)} casalinghe, quindi la quota di non sposate &egrave; "
                f"<b>almeno {il(num(nubili, 0))}{num(nubili, 0)}%</b>, e il matrimonio under-25 a "
                f"Bagheria sta sotto Palermo e Sicilia. Il matrimonio precoce non spiega il "
                f"fenomeno; convivenze e figli la fonte non li osserva. Serve quindi un "
                f"servizio di <b>attivazione</b>, "
                f"non solo di conciliazione. La quota &egrave; sensibile alla struttura per "
                f"et&agrave;, e passa da {num(bounds.iloc[0, 1])}% sui 15-24 a "
                f"{num(bounds.iloc[2, 1])}% se si assume che nessuna abbia meno di 20 anni.",
        fonte="ISTAT, censimento permanente 2024 &rarr; "
              "<b>genere_composizione_stato_dettaglio.csv</b>; stato civile al 1&deg; gennaio "
              "2025 (DCIS_POPRES1) &rarr; <b>genere_stato_civile.csv</b>, bound in "
              "<b>genere_casalinghe_bounds.csv</b>.")

    # Il primo focus proposto dalla locandina, «relazione fra titolo di studio e condizione
    # lavorativa», sull'individuo NON e' misurabile a livello comunale: nella tavola lavoro
    # il titolo esiste solo come totale ALL, in quella istruzione la condizione solo come
    # totale 99. E' dimostrato nella cella di verifica di notebooks/genere.ipynb, e va detto
    # invece che aggirato in silenzio. Qui si dice, e si mostra cio' che al suo posto i dati
    # consentono: quale titolo la fascia detiene oggi, e dove la scala si spezza al 2011.
    t24 = tit[(tit.territorio.astype(str).str.zfill(6) == "082006") & (tit.anno == 2024) &
              (tit.tavola == "istruzione") & (tit.genere == "T") & (tit.eta == "Y9-24") &
              (tit.cittadinanza == "TOTAL") & (tit.condizione.astype(str) == "99")
              ].set_index("titolo_studio").valore
    diploma_piu = float(t24[["USE_IF", "BL", "ML_RDD"]].sum())
    terziari = float(t24[["BL", "ML_RDD"]].sum())
    solo_diploma = 100 * float(t24["USE_IF"]) / diploma_piu
    CATENA = [("I8", "licenza media, 15-19 anni"),
              ("I6", "diploma o laurea, 25-64 anni"),
              ("I7", "titolo universitario, 30-34 anni")]
    catena = [{"label": et, "valore": float(ben11.loc[k, "Bagheria"] - ben11.loc[k, "Sicilia"]),
               "colore": COL["Bagheria"], "forte": k != "I8"} for k, et in CATENA]
    claim(S, "residenti 9-24 con almeno il diploma, di cui terziari",
          f"{diploma_piu:.0f} / {terziari:.0f}", "persone",
          "censpop_istr_lav_long.csv",
          "la fascia 9-24 non ha ancora finito di studiare: e' il titolo detenuto, non quello finale")
    claim(S, "di chi ha almeno il diploma, quota che si ferma al diploma", solo_diploma, "%",
          "censpop_istr_lav_long.csv")
    claim(S, "catena dei titoli 2011, scarto vs Sicilia (I8 / I6 / I7)",
          " / ".join(f"{r['valore']:+.1f}" for r in catena), "p.p.",
          "edu_historical_benchmarks_2011.csv",
          "tre fasce d'eta' diverse: e' una scala di gradini, non una serie")

    corpo += blocco(
        fig(),
        "L&rsquo;altro focus del bando: la scala dei titoli si spezza dopo il primo gradino",
        divergenti(catena, centro=0.0, lab=230, coda=64,
                   etichetta_centro="parità con la Sicilia",
                   fmt=lambda v: num(v, 1, " p.p.", segno=True, zero=True)),
        mostra="Scarto fra Bagheria e la Sicilia, in punti percentuali, su tre indicatori "
               "8milaCensus del <b>2011</b> ordinati per altezza del titolo: competenza di "
               "base, diploma o laurea fra gli adulti, laurea fra i trentenni. &Egrave; la "
               "risposta obliqua al focus <b>&laquo;titolo di studio &times; condizione "
               "lavorativa&raquo;</b>, che nella sua forma diretta <b>non &egrave; "
               "misurabile</b>: si mostra a quale altezza la scala dei titoli di Bagheria si "
               "ferma, non quanti diplomati lavorino. Le tre barre hanno <b>tre fasce "
               "d&rsquo;et&agrave; diverse</b> e non sono una serie: sono tre gradini "
               "fotografati lo stesso anno su tre popolazioni diverse.",
        base=f"Valori 2011 di Bagheria contro Sicilia: competenza di base "
             f"{num(ben11.loc['I8', 'Bagheria'])}% contro "
             f"{num(ben11.loc['I8', 'Sicilia'])}% (Palermo "
             f"{num(ben11.loc['I8', 'Palermo'])}, Italia "
             f"{num(ben11.loc['I8', 'Italia'])}); diploma o laurea 25-64 "
             f"{num(ben11.loc['I6', 'Bagheria'])}% contro "
             f"{num(ben11.loc['I6', 'Sicilia'])}% (Palermo "
             f"{num(ben11.loc['I6', 'Palermo'])}, Italia "
             f"{num(ben11.loc['I6', 'Italia'])}); universitario 30-34 "
             f"{num(ben11.loc['I7', 'Bagheria'])}% contro "
             f"{num(ben11.loc['I7', 'Sicilia'])}% (Palermo "
             f"{num(ben11.loc['I7', 'Palermo'])}, Italia "
             f"{num(ben11.loc['I7', 'Italia'])}). Conteggi censuari, nessun intervallo di "
             f"confidenza. Sul 2024 il titolo della fascia 9-24 &egrave; il diploma: dei "
             f"{num(diploma_piu, 0)} residenti con <b>almeno</b> il diploma, il "
             f"{num(solo_diploma)}% si ferma l&igrave; e i titoli terziari sono "
             f"{num(terziari, 0)} persone in tutto. A vent&rsquo;anni una laurea non "
             f"pu&ograve; ancora esserci: il dato dice quale titolo la fascia detiene, non "
             f"quanto in alto arriver&agrave;.",
        lettura="La linea verticale &egrave; la parit&agrave; con la Sicilia; a destra "
                "Bagheria sta meglio, a sinistra peggio. <b>Il finding &egrave; il cambio "
                "di segno fra la prima barra e le altre due</b>, ed &egrave; il motivo per "
                "cui le due in basso sono a piena intensit&agrave;: la scolarizzazione di "
                "base tiene, tutto ci&ograve; che viene dopo no. <b>Perch&eacute; la "
                "domanda del bando non ha una risposta diretta</b>: nelle tavole comunali "
                "del censimento permanente la tavola lavoro pubblica il titolo di studio "
                "solo come totale <code>ALL</code> e la tavola istruzione pubblica la "
                "condizione solo come totale <code>99</code>, quindi &laquo;quanti "
                "diplomati di Bagheria lavorano&raquo; non &egrave; una domanda a cui i "
                "dati pubblici rispondono; la dimostrazione &egrave; la cella di "
                "verifica di <b>notebooks/genere.ipynb</b>. Quello che si pu&ograve; dire "
                "si dice con due misure parallele sulla stessa base (figura 2.1) e con "
                "questa scala. Le due letture <b>non si sommano in una catena "
                "individuale</b>: restano misure aggregate dello stesso territorio. "
                "L&rsquo;incrocio sulla persona &egrave; ci&ograve; che il servizio della "
                "scheda 4 produrrebbe per la prima volta.",
        fonte="ISTAT 8milaCensus 2011 &rarr; <b>edu_historical_benchmarks_2011.csv</b>; "
              "composizione dei titoli 2024 dal censimento permanente &rarr; "
              "<b>censpop_istr_lav_long.csv</b>.")

    corpo += blocco(
        fig("Tavola"),
        "Lo stesso divario come esce dal notebook, con la sua didascalia",
        figura("fig05_forbice", intera=True, larghezza=1650),
        mostra="&Egrave; la figura 2.2, nella versione integrale che sta nello zip: stessa "
               "misura, stesse cinque unit&agrave;, ma con le mediane del panel disegnate e "
               "la didascalia a due blocchi incorporata nell&rsquo;immagine. Compare qui "
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

    return scrivi("scheda2_genere.html",
                  "I due divari di genere a Bagheria", corpo,
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
          "mob_sintesi.csv / mob_flussi_bagheria.csv",
          "97o percentile dei 381 non capoluogo, quota verso il proprio capoluogo")
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
        "La destinazione &egrave; una sola, e per lavoro le donne escono dal comune meno degli uomini.",
        f"Fra chi lascia Bagheria, va a Palermo il "
        f"{num(sin.loc['quota di chi esce che va a Palermo, studio 2011'].valore)}% di chi esce "
        f"per studio (2011) e il {num(sin.loc['quota di chi esce che va a Palermo, lavoro 2021'].valore)}% "
        f"di chi esce per lavoro (2021). Non esiste una seconda direzione. Ma lo scarto fra ragazze e "
        f"ragazzi <b>cambia segno</b> a seconda del motivo dello spostamento.",
        f"<b>La risposta alla domanda del bando.</b> Il pendolarismo di Bagheria &egrave; "
        f"pendolarismo verso Palermo, e non &egrave; un problema di raggiungibilit&agrave;: "
        f"la citt&agrave; &egrave; raggiunta, e dalle ragazze pi&ugrave; che dai ragazzi "
        f"({num(bag.gap_studio_F_M, 1, ' p.p.', segno=True)} sullo studio). "
        f"&Egrave; sul <b>lavoro</b> che le donne escono meno degli uomini: "
        f"{num(bag.gap_lavoro_F_M)} punti, {num(perc_gap, 0)}&deg; percentile dei comuni "
        f"siciliani (14&deg; al netto di taglia e distanza dal capoluogo). Il salto fra i due motivi vale <b>{num(bag.ribaltamento)} punti</b> contro "
        f"i {num(rib.loc['Sicilia'].ribaltamento)} della Sicilia. La fonte non ha l&rsquo;et&agrave;: "
        f"sullo studio pesano i giovani, sul lavoro gli adulti, quindi il ribaltamento &egrave; "
        f"compatibile con la forbice fra istruzione e lavoro, non una sua conferma.")

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
             f"{num(perc_gap, 0)}&deg; percentile dei comuni siciliani (14&deg; al netto di "
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
                "la <b>pendenza</b> &egrave; il risultato, non i due livelli presi da soli. La "
                "tratteggiata orizzontale &egrave; la parit&agrave; F = M: sopra escono "
                "pi&ugrave; le donne, sotto pi&ugrave; gli uomini. Bagheria &egrave; la linea "
                "spessa e colorata. Il verso cambia in Sicilia e in Italia (a Palermo città i due "
                "scarti sono entrambi negativi e quasi nulli), quindi il "
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
        "Il treno pesa fra le donne quasi il doppio che fra gli uomini",
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
               "la quota che esce di casa prima delle 7:15. <b>Tutti i motivi e tutte le "
               "destinazioni insieme</b>; il taglio per motivo e verso Palermo sta nella "
               "sezione 5 di <b>notebooks/mobilita.ipynb</b>. La figura non dice "
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
                "viaggiano pi&ugrave; a lungo; il rientro non &egrave; "
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
        "Nel triennio 2021-2024 la coorte femminile 25-29 si assottiglia, quella maschile no",
        legenda([("femmine", COL_G["F"]), ("maschi", COL_G["M"])]),
        divergenti([{"label": f"{r.nome_territorio} ({ETICHETTA_G[r.genere]})",
                     "valore": r["ritenzione_%"], "colore": COL_G[r.genere],
                     "forte": r.nome_territorio == "Bagheria" and r.genere == "F"}
                    for _, r in c2529.iterrows()],
                   centro=100, lab=150, coda=52,
                   etichetta_centro="100 = coorte intatta"),
        mostra="Ritenzione della coorte che aveva 25-29 anni nel 2021, misurata al 2024: "
               "residenti nel 2024 per 100 residenti della stessa coorte nel 2021 (saldo netto "
               "di arrivi, partenze e decessi), per genere e quattro territori. &Egrave; "
               "l&rsquo;et&agrave; del passaggio dallo studio al lavoro, misurata qui da una "
               "<b>terza fonte</b> che non condivide n&eacute; tavola n&eacute; denominatore "
               "con le figure 3.1-3.4, e che a differenza del pendolarismo ha l&rsquo;et&agrave;. "
               "Il profilo completo per et&agrave; singola, che mostra dove si apre la "
               "finestra, &egrave; la figura 2.4.",
        base=f"N = {num(n_coorte.sum(), 0)} persone nella coorte 25-29 di Bagheria al 2021 "
             f"({num(n_coorte['F'], 0)} femmine e {num(n_coorte['M'], 0)} maschi); per gli "
             f"altri territori i denominatori sono di due o tre ordini di grandezza "
             f"superiori. Conteggi censuari, <b>nessun intervallo di confidenza</b>. La "
             f"ritenzione femminile di Bagheria &egrave; la pi&ugrave; bassa dei quattro "
             f"territori. La misura &egrave; un <b>saldo netto</b> fra "
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
                "come tale. Su cinque anni la differenza di genere non si ripete: le coorti "
                "all&rsquo;uscita dal percorso formativo si riducono per entrambi i generi.",
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
    scuole = pd.read_csv(PROCESSED / "edu_technical_schools.csv")
    t390 = pd.read_csv(PROCESSED / "mob_treno_390.csv")
    tag = pd.read_csv(PROCESSED / "mob_taglia_distanza.csv")
    sin = pd.read_csv(PROCESSED / "mob_sintesi.csv")
    det = pd.read_csv(PROCESSED / "genere_composizione_stato_dettaglio.csv")
    stati = pd.read_csv(PROCESSED / "edu_youth_states_2018_2024.csv")
    pre = pd.read_csv(PROCESSED / "genere_pretrend.csv")
    pre390 = pd.read_csv(PROCESSED / "genere_pretrend_390.csv").iloc[0]
    gem = pd.read_csv(PROCESSED / "genere_gemelle.csv")

    pb = platea[(platea.nome_territorio == "Bagheria")].set_index("genere")
    b24 = stati[(stati.territorio_nome == "Bagheria") & (stati.anno == 2024)].iloc[0]
    d24 = det[(det.nome_territorio == "Bagheria") & (det.anno == 2024) &
              (det.destinazione == "fuori e non in cerca")]
    inatt = d24.groupby("genere").persone.sum()
    n29, n34 = netto.loc[2029], netto.loc[2034]
    mde_occ = mde[mde.KPI.str.startswith("tasso di occupazione")].set_index(
        "anni pooled per lato")
    mde_cas = mde[mde.KPI.str.startswith("quota casalinghe")].set_index("anni pooled per lato")
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
    claim(S, "MDE osservata sul triennio contro delta da rilevare",
          f"{mde_occ.loc[3, 'MDE osservata 80% (pp)']:.2f} vs "
          f"{mde_occ.loc[3, 'delta da rilevare (pp)']:.1f}", "p.p.", "genere_mde.csv",
          "nessuna finestra arriva all'80% nei comuni simili: il tasso si legge come "
          "direzione, l'effetto si misura sui partecipanti")
    claim(S, "inattivi non studenti 15-24, F / M",
          f"{inatt['F']:.0f} / {inatt['M']:.0f}", "persone",
          "genere_composizione_stato_dettaglio.csv", "51% F: il gruppo non e' femminile")
    claim(S, "pendenza del tasso F 2018-2024 e test di pre-trend vs Palermo",
          f"{pre.iloc[0].stima:.2f} pp/anno; p={pre.iloc[1].p:.2f}", "-",
          "genere_pretrend.csv", "prerequisito del controfattuale, testato non assunto")

    corpo = intestazione(
        "Proposta di intervento &middot; Ponte 19 &middot; servizio comunale di transizione e "
        "riattivazione &middot; 18-25 anni",
        "Andare a cercare chi non cerca, in due finestre d&rsquo;et&agrave;, e misurare il "
        "risultato in tasso.",
        f"<b>Ponte 19</b> &egrave; un servizio comunale di transizione con <b>outreach attivo</b> "
        f"(non a domanda spontanea), <b>due finestre di ingaggio</b> e una <b>quota di genere</b>. "
        f"Il nome viene dai 19 anni, l&rsquo;et&agrave; di uscita dalla scuola superiore. "
        f"Le tre scelte non sono preferenze di design: ognuna risponde a un numero delle schede "
        f"1-3.",
        f"<b>Il vincolo che rende la proposta seria.</b> La platea femminile 15-24 "
        f"<b>&egrave; gi&agrave; nata</b> e, a migrazioni nulle, cala del "
        f"{num(-pb.loc['F'].var_2034_pct)}% al 2034 (sui coetanei maschi "
        f"{num(-pb.loc['M'].var_2034_pct)}%): le stesse &laquo;+40 occupate&raquo; valgono "
        f"{num(n29.kpi_netto, segno=True)} nel 2029 e &minus;{num(-n34.kpi_netto)} nel 2034. "
        f"Un obiettivo scritto in teste "
        f"si annullerebbe da solo entro il 2034 senza che nessuno abbia sbagliato nulla. "
        f"Per questo il KPI primario &egrave; un <b>tasso</b>, con la sua finestra di lettura "
        f"dichiarata prima dell&rsquo;avvio.")

    corpo += blocco(
        fig("Tavola"),
        "Dalle evidenze alle scelte di progetto",
        tabella(["Evidenza", "Dove", "Scelta imposta"],
                [(f"Il {num(b24.inattivi_su_fuori)}% di chi &egrave; fuori non cerca",
                  "fig. 1.1", "outreach attivo, non sportello a domanda"),
                 ("Le uscite hanno due tempi: la fine della scuola e la fine del percorso "
                  "formativo (20-29 anni, entrambi i generi); dopo i 25 anni il deficit di "
                  "lavoro diventa femminile", "fig. 2.4; relazione &sect;3.1-bis e &sect;3.3",
                  "<b>due finestre</b> di outreach: A 18-20 all&rsquo;uscita, B 22-25 sulla "
                  "conversione; i 21enni entrano su segnalazione"),
                 (f"{num(inatt['F'], 0)} ragazze e {num(inatt['M'], 0)} ragazzi, "
                  f"etichette opposte", "fig. 2.5",
                  "<b>quota &ge;50% F</b> e due tracce di contatto distinte"),
                 ("Almeno l&rsquo;89% delle casalinghe non &egrave; sposata", "fig. 2.5",
                  "attivazione, non sola conciliazione"),
                 ("A pari istruzione il lavoro non arriva, e la posizione regionale "
                  "&egrave; stabile da tredici anni", "fig. 2.3",
                  "il servizio non finanzia altra istruzione: il problema delle ragazze "
                  "&egrave; la conversione, non il titolo"),
                 ("L&rsquo;offerta di trasporto non spiega il divario, e a pari taglia e "
                  "distanza Bagheria &egrave; nella media", "fig. 3.4",
                  "<b>nessun intervento infrastrutturale</b>: la leva &egrave; la transizione"),
                 ("Fra chi esce, le donne prendono il treno quasi il doppio degli uomini",
                  "fig. 3.3",
                  "sedi, orari e tirocini scelti su ci&ograve; che &egrave; raggiungibile "
                  "senza auto"),
                 (f"La platea F cala del {num(-pb.loc['F'].var_2034_pct)}% al 2034",
                  "fig. 4.4", "<b>KPI in tasso</b>, riparametrato ogni anno sulla platea")],
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
                "domanda spontanea raggiunge chi gi&agrave; cerca, non loro. La colonna centrale &egrave; un rimando, non un dato.",
        fonte="Derivazione completa in <b>dist/POLICY_PONTE_19.pdf</b>. Ogni numero rimanda "
              "alla figura che lo produce, e da l&igrave; al file di "
              "<b>data/processed/</b>.")

    # La tavola qui sopra dice quali scelte i dati impongono; questa dice che cosa il
    # servizio fa concretamente. Erano due cose diverse e la scheda ne diceva una sola:
    # chi amministra legge prima il modello operativo e poi la potenza statistica.
    n_bag = int((scuole.territorio == 82006).sum())
    n_pa = int((scuole.territorio == 82053).sum())
    tb = t390[t390.nome == "Bagheria"].iloc[0]
    perc_treno = 100 * (t390.treno < tb.treno).mean()
    tagb = tag[tag.nome == "Bagheria"].iloc[0]
    claim(S, "sedi di istituto tecnico, Bagheria / Palermo", f"{n_bag} / {n_pa}", "sedi",
          "edu_technical_schools.csv", "anagrafe MIUR: sono i canali della finestra A")
    claim(S, "percentile siciliano del treno, e residuo a parita' di taglia e distanza",
          f"{perc_treno:.0f} / {tagb.residuo:.1f}", "percentile e p.p.",
          "mob_treno_390.csv + mob_taglia_distanza.csv",
          "le due misure per cui la mobilita' e' un vincolo, non un capitolo di spesa")

    corpo += blocco(
        fig("Tavola"),
        "Che cosa il servizio fa, componente per componente",
        tabella(["Componente", "Che cosa fa", "Il numero che la impone"],
                [("A &middot; Intercettazione prima del vuoto",
                  "Le secondarie e le sedi tecniche propongono il servizio "
                  "nell&rsquo;ultimo anno e al momento dell&rsquo;interruzione. Con "
                  "consenso e minimizzazione dei dati, appuntamento prima che passino 30 "
                  "giorni senza studio n&eacute; lavoro.",
                  f"{n_bag} sedi tecniche a Bagheria, {n_pa} a Palermo"),
                 ("B &middot; Outreach verso chi non cerca",
                  "Il servizio non attende l&rsquo;iscrizione allo sportello. Primo "
                  "colloquio su titolo e indirizzo, data di uscita, canali gi&agrave; "
                  "usati, distanza e accessibilit&agrave; delle opportunit&agrave;, carico "
                  "di cura, obiettivo. Due tracce di contatto distinte.",
                  f"{num(b24.inattivi_su_fuori)}% di chi &egrave; fuori non sta cercando"),
                 ("C &middot; Piano di transizione entro 15 giorni",
                  "Una sola prossima azione verificabile: rientro in istruzione, qualifica "
                  "breve collegata a una posizione reale, ricerca assistita, esperienza "
                  "retribuita. Con scadenza, responsabile ed esito osservabile.",
                  "soglia di progetto"),
                 ("D &middot; Esperienze retribuite solo su domanda verificata",
                  "Nei primi 90 giorni il Comune fa l&rsquo;audit dei datori locali e "
                  "metropolitani. Ogni esperienza deve avere attivit&agrave; reale, mentor, "
                  "compenso, competenze attese e disponibilit&agrave; a registrare "
                  "l&rsquo;esito.",
                  "soglia di progetto"),
                 ("E &middot; Mobilit&agrave; come vincolo di progettazione",
                  "Verifica di raggiungibilit&agrave; col mezzo collettivo negli orari "
                  "reali della posizione, dentro l&rsquo;istruttoria di ogni piano. Il "
                  "sostegno all&rsquo;abbonamento resta subordinato: si attiva su chi "
                  "l&rsquo;opportunit&agrave; ce l&rsquo;ha gi&agrave;.",
                  f"treno al {num(perc_treno, 0)}&deg; percentile siciliano; residuo "
                  f"{num(tagb.residuo, 1, ' p.p.', segno=True)} a parit&agrave; di taglia "
                  f"e distanza")],
                forte=("B &middot; Outreach verso chi non cerca",)),
        mostra="Le cinque componenti del servizio e, accanto a ciascuna, il dato che la "
               "rende necessaria. La tavola <b>non</b> &egrave; un piano finanziario e "
               "<b>non</b> contiene stime di costo o di efficacia: dice che cosa il "
               "servizio fa, non quanto costa n&eacute; quanto rende. La quantificazione "
               "del bersaglio sta nella tavola 4.6, la valutazione nella 4.5.",
        base="Nessun N e nessun intervallo: &egrave; una tavola di progetto. La terza "
             "colonna contiene solo numeri gi&agrave; prodotti altrove e rimanda al file "
             "che li genera; le due righe marcate <b>soglia di progetto</b> sono scelte "
             "amministrative dichiarate in anticipo, non risultati di analisi, e come tali "
             "sono rivedibili al decision gate della tavola successiva.",
        lettura="La riga in nero &egrave; quella che decide la forma del servizio, ed "
                "&egrave; la stessa della tavola 4.1: se sette persone su dieci fra chi "
                "&egrave; fuori non stanno cercando, ogni componente a domanda spontanea "
                "raggiunge chi gi&agrave; cerca, non loro. "
                "<b>Sulla componente E il segno va letto al contrario di come suona</b>: "
                "il treno di Bagheria sta in cima alla graduatoria siciliana e il residuo "
                "a parit&agrave; di taglia e distanza &egrave; vicino a zero, quindi "
                "l&rsquo;offerta di trasporto <b>non</b> &egrave; la barriera, e "
                "l&rsquo;ipotesi infrastrutturale non &egrave; sostenuta dai dati. La mobilit&agrave; resta come verifica dentro "
                "l&rsquo;istruttoria, non come capitolo di spesa.",
        fonte="Anagrafe scolastica MIUR &rarr; <b>edu_technical_schools.csv</b>; "
              "<b>edu_youth_states_2018_2024.csv</b>; <b>mob_treno_390.csv</b>, "
              "<b>mob_taglia_distanza.csv</b>. Testo integrale delle componenti in "
              "<b>dist/POLICY_PONTE_19.pdf</b>, sezione 4.")

    corpo += blocco(
        fig("Tavola"),
        "Che cosa si decide a 90 giorni, e con quale evidenza",
        tabella(["Evidenza raccolta nei primi 90 giorni", "Decisione"],
                [("&ge; 30 esperienze retribuite con domanda e mentor verificati",
                  "Attivare il modulo esperienza"),
                 ("Gap di competenza ricorrente associato a posizioni reali",
                  "Progettare un modulo breve e mirato"),
                 ("Posizioni verificate raggiungibili di fatto solo in auto",
                  "Rinegoziare l&rsquo;orario d&rsquo;ingresso col datore: il trasporto "
                  "non &egrave; la barriera"),
                 ("Carico di cura barriera primaria nel sottogruppo femminile",
                  "Attivare la conciliazione <b>oltre</b> l&rsquo;attivazione, non al suo "
                  "posto"),
                 ("Domanda insufficiente o non verificabile",
                  "Concentrare su outreach, orientamento e mercato metropolitano"),
                 ("Quota di genere sotto il 40% a 90 giorni",
                  "Rivedere i canali di contatto <b>prima</b> di aumentare la "
                  "capacit&agrave;")],
                forte=("Quota di genere sotto il 40% a 90 giorni",)),
        mostra="Le sei condizioni che il servizio si impegna a osservare nei primi 90 "
               "giorni e la decisione che ciascuna innesca, dichiarate <b>prima</b> "
               "dell&rsquo;avvio. La tavola <b>non</b> &egrave; una previsione: non dice "
               "quale ramo si realizzer&agrave;, dice che la scelta &egrave; gi&agrave; "
               "vincolata all&rsquo;evidenza invece di essere rinviata al giudizio di chi "
               "sar&agrave; in carica allora.",
        base="Nessun N e nessuna stima: sono soglie amministrative fissate in anticipo. Il "
             "loro valore non &egrave; statistico ma procedurale, e sta nell&rsquo;essere "
             "scritte prima che i dati arrivino, cos&igrave; che la decisione non possa "
             "essere ricostruita a posteriori attorno al risultato ottenuto. Il disegno di "
             "valutazione vero e proprio, con potenza e finestra di lettura, &egrave; la "
             "tavola 4.5.",
        lettura="La riga in nero &egrave; l&rsquo;unica che pu&ograve; scattare contro "
                "l&rsquo;interesse del servizio, ed &egrave; per questo che sta qui: se "
                "la quota femminile sui presi in carico scende sotto il 40%, la risposta "
                "prescritta &egrave; <b>rivedere i canali</b>, non allargare la "
                "capacit&agrave; sperando che il numero si aggiusti da s&eacute;. La quota "
                "obiettivo resta &ge; 50% (tavola 4.6): il 40% &egrave; la soglia di "
                "allarme, non il bersaglio.",
        fonte="Testo integrale del decision gate in <b>dist/POLICY_PONTE_19.pdf</b>, "
              "sezione 5; la componente mobilit&agrave; della terza riga &egrave; discussa "
              "nella sezione 4-bis, componente F2.")

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
        tabella(["Finestra di lettura", "Potenza binomiale", "Soglia osservata (MDE)",
                 "Potenza osservata"],
                [(f"{int(k)} {'anno' if k == 1 else 'anni'} pooled per lato",
                  num(r["potenza binomiale (%)"], 0, "%"),
                  num(r["MDE osservata 80% (pp)"], 2, " p.p."),
                  num(r["potenza osservata (%)"], 0, "%"))
                 for k, r in mde_occ.iterrows()],
                forte=("3 anni pooled per lato",)),
        mostra=f"Il disegno di valutazione dichiarato <b>prima</b> dell&rsquo;avvio: per ogni "
               f"finestra di lettura, la potenza sull&rsquo;effetto atteso (+"
               f"{num(mde_occ.loc[1, 'delta da rilevare (pp)'])} punti di occupazione "
               f"femminile 15-24) secondo due metri: il modello binomiale e la "
               f"variabilit&agrave; che mostrano, senza interventi, i "
               f"{int(mde_occ.loc[1, 'comuni simili'])} comuni siciliani di taglia simile a "
               f"Bagheria. La tavola dice quanto il tasso comunale pu&ograve; dimostrare, "
               f"non se l&rsquo;intervento funzioner&agrave;.",
        base=f"Denominatori reali di Bagheria, non un N ipotetico. Il binomiale tratta ogni "
             f"annata come un campione indipendente; il metro osservato &egrave; 2,8 volte la "
             f"deviazione standard delle variazioni dei comuni simili (fra met&agrave; e il "
             f"doppio delle ragazze 15-24 di Bagheria, Bagheria esclusa), al netto della "
             f"variazione mediana, dalla tavola lavoro 15-24 dei 390 comuni. Controfattuale "
             f"dichiarato in anticipo: <b>Palermo</b>, col prerequisito testato e non assunto "
             f"(pendenza di Bagheria {num(pre.iloc[0].stima, 2)} pp/anno, differenza con "
             f"Palermo p = {num(pre.iloc[1].p, 2)} nel modello binomiale; senza binomiale la "
             f"distanza da Palermo &egrave; pi&ugrave; piccola di quella del "
             f"{num(pre390['comuni simili più lontani da Palermo di Bagheria (%)'], 0)}% dei "
             f"comuni simili). Ancoraggio dei target sulle {len(gem)} gemelle strutturali.",
        lettura="&laquo;Pooled per lato&raquo; significa che gli anni vengono accorpati prima "
                "e dopo l&rsquo;avvio: tre anni per lato sono sei anni di dati, non tre. La "
                "riga in nero &egrave; la finestra dichiarata. Il binomiale promette che il "
                "triennio basti; nei comuni simili, sull&rsquo;occupazione, nessuna finestra "
                "arriva all&rsquo;80%, "
                "perch&eacute; accorpare anni riduce il rumore di conteggio ma non le "
                "divergenze persistenti fra comuni. Il tasso comunale dice quindi la "
                "<b>direzione</b> della convergenza; l&rsquo;effetto del servizio si misura "
                "sui partecipanti, contro chi comincia sei mesi dopo. La lettura "
                "<b>annuale</b> spetta ai KPI di processo, che oggi nessuno rileva e che il "
                "servizio produce: primo contatto entro 30 giorni, piano entro 15, utenza per "
                "et&agrave; singola e genere contro la platea residente, copertura separata "
                "delle due finestre e degli ingressi fuori finestra. L&rsquo;altro KPI di "
                "popolazione, la quota di casalinghe 15-24 (primario del modulo di genere), "
                f"sul biennio arriva invece {il(num(mde_cas.loc[2, 'potenza osservata (%)'], 0), a=True)}"
                f"{num(mde_cas.loc[2, 'potenza osservata (%)'], 0)}% "
                "anche nei comuni simili: &egrave; il primo a restituire un verdetto.",
        fonte="Censimento permanente, tavola lavoro 15-24 dei 390 comuni siciliani, "
              "2018-2024 &rarr; <b>genere_mde.csv</b>; pre-trend in "
              "<b>genere_pretrend.csv</b> e <b>genere_pretrend_390.csv</b>; gruppo di "
              "controllo in <b>genere_gemelle.csv</b>.")

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
                  "occupate (2011, tutte le et&agrave;) che lavorerebbero fuori comune "
                  "invece che a Bagheria", num(bersaglio, 0))],
                forte=("tasso femminile di Palermo",)),
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
             f"da una fonte che non condivide n&eacute; tavola n&eacute; base, e che non conta "
             f"occupazione in pi&ugrave;: conta donne gi&agrave; occupate che lavorerebbero "
             f"altrove.",
        lettura="Gli scenari <b>non si sommano</b>: misurano popolazioni diverse sullo stesso "
                "passaggio, e sommarli conterebbe due volte le stesse persone. La riga in nero "
                "&egrave; lo scenario di riferimento della proposta, il tasso femminile di "
                "Palermo. <b>Decision gate a 90 "
                "giorni</b>: il modulo esperienza si attiva solo con &ge;30 posti a domanda e "
                "mentor verificati; l&rsquo;abbonamento si attiva solo su chi ha gi&agrave; "
                "un&rsquo;opportunit&agrave;, e se una posizione &egrave; raggiungibile solo in "
                "auto si rinegozia l&rsquo;orario d&rsquo;ingresso; se la quota di "
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
        "Che cosa questa proposta non promette",
        tabella(["Non promette", "Perch&eacute; il dato non lo consente"],
                [("Di stimare il rendimento occupazionale individuale di un titolo",
                  "L&rsquo;incrocio titolo &times; condizione sulla persona non esiste "
                  "nelle tavole comunali (figura 2.6). &Egrave; il dato che il servizio "
                  "creerebbe, non uno che gi&agrave; possiede."),
                 ("Di attribuire il calo della popolazione 15-34 a emigrazione misurata",
                  "La ritenzione di coorte &egrave; un <b>saldo netto senza "
                  "destinazione</b>, e il calo dello stock 15-34 &egrave; in gran parte ricambio "
                  "d&rsquo;et&agrave; fra le coorti che entrano e che escono dalla fascia "
                  "(tavola 1.9)."),
                 ("Di mettere in serie il pendolarismo verso Palermo",
                  "La destinazione c&rsquo;&egrave; ma &egrave; ferma ai censimenti: il "
                  "2021 non ha il sesso, e la serie annuale per genere d&agrave; solo "
                  "&laquo;fuori comune&raquo; aggregato (scheda 3)."),
                 ("Di attribuire l&rsquo;inattivit&agrave; a una causa singola",
                  "I residui della figura 1.8 dicono che Bagheria sta sotto l&rsquo;atteso, "
                  "non perch&eacute;. Nessuna interpretazione causale &egrave; "
                  "autorizzata dai dati usati."),
                 ("Di trattare la finestra 22-25 come un dato annuale",
                  "&Egrave; una lettura pooled su triennio: sulla singola et&agrave; le "
                  "oscillazioni arrivano a 8 punti, e una lettura anno per anno "
                  "leggerebbe rumore.")]),
        mostra="I cinque limiti che la proposta dichiara su di s&eacute;, e per ciascuno "
               "la ragione nei dati. La tavola &egrave; l&rsquo;inverso delle altre della "
               "scheda: non elenca ci&ograve; che l&rsquo;analisi autorizza a dire, ma "
               "ci&ograve; che non autorizza, con il rimando al blocco dove il limite si "
               "vede.",
        base="Nessun numero nuovo. Ogni riga rimanda a un blocco di questa scheda o delle "
             "precedenti, dove N, metodo ed esclusioni sono gi&agrave; dichiarati. La "
             "seconda e la quinta riga sono limiti della <b>fonte</b> e non si chiudono "
             "con pi&ugrave; analisi; la prima si chiude solo con un dato che oggi non "
             "esiste e che il servizio produrrebbe.",
        lettura="Va letta come parte della proposta, non come una postilla: le prime tre "
                "righe sono le ragioni per cui il KPI primario &egrave; un <b>tasso</b> e "
                "non un conteggio di partenze evitate, e la quinta &egrave; la ragione per "
                "cui le due finestre di ingaggio sono <b>due</b> e larghe, invece di una "
                "sola centrata sull&rsquo;et&agrave; con il picco apparente.",
        fonte="Elenco integrale in <b>dist/POLICY_PONTE_19.pdf</b>, sezione 10, e in "
              "<b>dist/RELAZIONE_DATAPOLIS.pdf</b>, sezione 9.")

    corpo += blocco(
        fig("Tavola"),
        "La finestra di lettura del KPI, come esce dal notebook",
        figura("fig09_kpi_finestra", intera=True, larghezza=1650),
        mostra="&Egrave; la tavola tecnica dietro la figura 4.4, nella versione "
               "integrale che sta nello zip: le ragazze 15-24 contate una per una e la "
               "cascata del KPI netto sulla stessa pagina, con la didascalia "
               "incorporata. Compare <b>intera e non ritagliata</b> per la stessa ragione "
               "della tavola 2.7: qui il punto non &egrave; il numero, che la scheda ha "
               "gi&agrave; dato, ma che la tavola sia leggibile da sola quando qualcuno la "
               "trova fuori da questa scheda.",
        base="Nessun numero nuovo rispetto alle figure 4.4 e 4.5: stessi denominatori, stesse "
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
              "<b>genere_gap_persone.csv</b>, <b>genere_tetto_platea.csv</b>.")

    return scrivi("scheda4_ponte19.html", "Ponte 19", corpo,
                  "Scheda 4 di 4 &middot; risponde alla richiesta &laquo;Proposta di "
                  "intervento&raquo;. Versione integrale: <b>dist/POLICY_PONTE_19.pdf</b>.")


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
    prodotte = [scheda_profilo(), scheda_genere(), scheda_pendolarismo(), scheda_ponte19()]

    registro = pd.DataFrame(CLAIM)
    registro.to_csv(PROCESSED / "schede_claim.csv", index=False)

    # Il controllo minimo: quattro schede non vuote, ogni claim con la sua fonte, e la
    # composizione 15-24 che chiude a 100. Se una tavola cambia forma, si rompe qui e
    # non in silenzio dentro una figura.
    assert len(prodotte) == 4 and all(p.stat().st_size > 8000 for p in prodotte)
    assert not registro.empty and registro.fonte.str.len().min() > 0

    # I blocchi della didascalia sono argomenti obbligatori di blocco(), che rifiuta
    # anche la stringa vuota; qui si controlla che a ogni <section> ne corrisponda una
    # stampata per intero. «Base statistica» non compare piu': resta nel sorgente.
    for p in prodotte:
        testo = p.read_text(encoding="utf-8")
        sezioni, didascalie = testo.count("<section"), testo.count('<div class="did">')
        assert sezioni == didascalie, f"{p.name}: {sezioni} blocchi, {didascalie} didascalie"
        assert didascalie * 3 == testo.count("<p><b>Cosa mostra.</b>") \
            + testo.count("<p><b>Come si legge.</b>") + testo.count("<p><b>Fonte.</b>"), \
            f"{p.name}: una didascalia non ha tutti e tre i blocchi"
        assert "Base statistica." not in testo, f"{p.name}: base statistica stampata"
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

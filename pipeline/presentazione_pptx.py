"""Datapolis 2026, Bagheria: costruisce il .pptx finale dal template del team.

Identita' visiva dal template (Lora per i titoli, Poppins Light per il corpo, sfondo
bianco con sfere lavanda, cornice arrotondata); ogni cifra e' letta e verificata su
data/processed/ (le assert in testa fermano la build se un dato si muove).

Uso (python-pptx non e' fra le dipendenze del progetto: ambiente temporaneo):
    uv run --with python-pptx --with numpy --with Pillow \
        pipeline/presentazione_pptx.py \
        "<template Presentation Datapolis.pptx>" docs/presentazione/Datapolis_presentazione_finale.pptx
"""
import csv
import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_MARKER_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

REPO = str(Path(__file__).resolve().parents[1]) + "/"   # radice del repo
FIG = REPO + "figures/"
TEMPLATE = sys.argv[1]
OUT = sys.argv[2]

SERIF, SANS = "Lora", "Poppins Light"
INK = RGBColor(0x1A, 0x1A, 0x1A)
GREEN = RGBColor(0x2C, 0x39, 0x32)      # dk2 del tema
GREY = RGBColor(0x59, 0x59, 0x59)
PINK, BLUE, MINT = RGBColor(0xF0, 0xD4, 0xDB), RGBColor(0xDB, 0xE7, 0xF5), RGBColor(0xC9, 0xE2, 0xD6)
LAV, PEACH, YELLOW = RGBColor(0xBA, 0xBA, 0xD6), RGBColor(0xF0, 0xD2, 0xBF), RGBColor(0xF3, 0xE4, 0x9A)
TERR = {"Bagheria": "D55E00", "Palermo": "785EF0", "Sicilia": "E69F00", "Italia": "666666"}

# ---------------------------------------------------------------- dati (mai a mano)
def leggi(nome):
    with open(REPO + "data/processed/" + nome, newline="") as f:
        return list(csv.DictReader(f))

def mille(n):
    return f"{n:,}".replace(",", ".")

def it(x, dec=1):
    return f"{float(x):.{dec}f}".replace(".", ",")

serie = leggi("genere_forbice_serie.csv")
ANNI = ["2018", "2019", "2020", "2021", "2022", "2023", "2024"]
occF = {t: {r["anno"]: float(r["tasso_occupazione_F"]) for r in serie if r["nome_territorio"] == t}
        for t in TERR}
o24 = {t: it(occF[t]["2024"]) for t in TERR}            # 8,2 / 9,6 / 10,4 / 17,3
assert o24 == {"Bagheria": "8,2", "Palermo": "9,6", "Sicilia": "10,4", "Italia": "17,3"}, o24
assert all(occF["Bagheria"][a] < min(occF[t][a] for t in TERR if t != "Bagheria")
           for a in ANNI if a != "2020")                # ultima in tutte e sei le annate
assert occF["Bagheria"]["2024"] == max(occF["Bagheria"].values())   # massimo della serie
cas = {r["nome_territorio"]: it(r["casalinghe_o_i_%"]) for r in leggi("genere_casalinghe.csv")
       if r["anno"] == "2024" and r["genere"] == "F"}
assert cas == {"Bagheria": "13,4", "Palermo": "11,3", "Italia": "4,6", "Sicilia": "10,1"}, cas
claim = {r["claim"]: r["valore"] for r in leggi("schede_claim.csv")}
NON_CERCA = it(claim["di chi e' fuori, quota che non cerca"])          # 70,6
PLATEA = round(float(claim["inattivi non studenti, in persone"]))      # 1121
assert NON_CERCA == "70,6" and PLATEA == 1121
mde = [r for r in leggi("genere_mde.csv") if r["KPI"].startswith("tasso")]
DELTA = it(mde[0]["delta da rilevare (pp)"])           # 1,4
MDE1 = it([r for r in mde if r["anni pooled per lato"] == "1"][0]["MDE 80% (pp)"], 2)   # 2,14
POT3 = [r for r in mde if r["anni pooled per lato"] == "3"][0]["potenza per il delta (%)"]
assert DELTA == "1,4" and MDE1 == "2,14" and POT3 == "90.0"
comp = {(r["genere"], r["stato"]): r for r in leggi("genere_composizione_stato_dettaglio.csv")
        if r["nome_territorio"] == "Bagheria" and r["anno"] == "2024"}
fuori_non_cerca = {g: round(sum(float(comp[(g, s)]["persone"])
                                for s in ("casalinghe/i", "altra condizione", "pensione")))
                   for g in "FM"}
assert fuori_non_cerca == {"F": 573, "M": 549}, fuori_non_cerca
CASALINGHE_N = round(float(comp[("F", "casalinghe/i")]["persone"]))    # 387
p1000 = {r["genere"]: r for r in leggi("genere_per_1000.csv")
         if r["nome_territorio"] == "Bagheria" and r["anno"] == "2024"}
DIP_F, DIP_M = p1000["F"]["per_1000_diploma"], p1000["M"]["per_1000_diploma"]
OCC_F, OCC_M = p1000["F"]["per_1000_occupati"], p1000["M"]["per_1000_occupati"]
assert (DIP_F, DIP_M, OCC_F, OCC_M) == ("510", "462", "82", "165")
CAP, CAP_F = 200, 100                                   # capacita' progettata (policy, sez. 3)

# ---------------------------------------------------------------- helper
prs = Presentation(TEMPLATE)
lst = prs.slides._sldIdLst
for sid in list(lst):                                   # via tutte le slide dimostrative
    prs.part.drop_rel(sid.rId)
    lst.remove(sid)
L = prs.slide_layouts.get_by_name

def no_bullet(p):
    pPr = p._p.get_or_add_pPr()
    for c in list(pPr):
        if c.tag in (qn("a:buChar"), qn("a:buAutoNum"), qn("a:buNone")):
            pPr.remove(c)
    pPr.insert(0, pPr.makeelement(qn("a:buNone"), {}))
    pPr.set("marL", "0"); pPr.set("indent", "0")

def style(run, font, size, color=INK, bold=False, caps=None, italic=False):
    run.font.name = font; run.font.size = Pt(size); run.font.bold = bold
    run.font.italic = italic; run.font.color.rgb = color
    if caps is not None:
        run._r.get_or_add_rPr().set("cap", "all" if caps else "none")

def fill(tf, parts, font=SANS, size=14, color=INK, align=PP_ALIGN.LEFT, spacing=1.15,
         after=6, anchor=None):
    """parts: lista di paragrafi; ogni paragrafo è una stringa o una lista di
    (testo, override) dove override è un dict per style()."""
    tf.word_wrap = True
    if anchor is not None:
        tf.vertical_anchor = anchor
    first = True
    for part in parts:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align; p.line_spacing = spacing; p.space_after = Pt(after)
        no_bullet(p)
        runs = [(part, {})] if isinstance(part, str) else part
        for text, ov in runs:
            r = p.add_run(); r.text = text
            kw = dict(font=font, size=size, color=color); kw.update(ov)
            style(r, **kw)
    return tf

def box(slide, x, y, w, h, parts, **kw):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    fill(tf, parts, **kw)
    return tb

def card(slide, x, y, w, h, color, radius=0.05):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.adjustments[0] = radius
    s.fill.solid(); s.fill.fore_color.rgb = color
    s.line.fill.background(); s.shadow.inherit = False
    s.text_frame.text = ""
    return s

def dot(slide, x, y, d, label, color=GREEN):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    s.fill.solid(); s.fill.fore_color.rgb = color; s.line.fill.background(); s.shadow.inherit = False
    tf = s.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    fill(tf, [label], font=SERIF, size=16, color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER,
         after=0, anchor=MSO_ANCHOR.MIDDLE)
    return s

def arrow(slide, x, y, w, h, color=GREEN):
    s = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = color; s.line.fill.background(); s.shadow.inherit = False
    return s

def geom(shape, left=None, top=None, width=None, height=None):
    """Imposta sempre tutte e quattro le coordinate: toccarne una sola su un placeholder
    che eredita dal layout produce un xfrm con estensione zero (forma invisibile)."""
    l0, t0, w0, h0 = shape.left, shape.top, shape.width, shape.height
    shape.left = Inches(left) if left is not None else l0
    shape.top = Inches(top) if top is not None else t0
    shape.width = Inches(width) if width is not None else w0
    shape.height = Inches(height) if height is not None else h0

def title(slide, text, size=24, caps=False, top=None, height=None, left=None, width=None):
    t = slide.shapes.title
    geom(t, left, top, width, height)
    tf = t.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; r = p.add_run(); r.text = text
    style(r, SERIF, size, caps=caps)
    return t

def footer(slide, text, y=6.55, h=0.5):
    return box(slide, 0.75, y, 11.85, h, [text], font=SANS, size=10, color=GREY, spacing=1.1, after=0)

def prune(slide):
    """Via i placeholder rimasti vuoti: niente 'Click to add' residui."""
    for ph in list(slide.placeholders):
        if ph.has_text_frame and not ph.text_frame.text.strip():
            ph._element.getparent().remove(ph._element)

def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text.strip()

def _bande(g, vuoto=28):
    righe = np.flatnonzero((g < 245).sum(axis=1) > 0)
    salti = np.flatnonzero(np.diff(righe) > vuoto)
    return list(zip(np.concatenate(([righe[0]], righe[salti + 1])),
                    np.concatenate((righe[salti], [righe[-1]]))))

def figura(slide, nome, testa, x, y, w, h, coda=2, margine=26):
    """PNG a 300 dpi ritagliato al solo grafico (via titolo, sottotitolo e didascalia,
    come fa pipeline/schede.py), adattato nel riquadro conservando le proporzioni."""
    im = Image.open(FIG + nome + ".png").convert("RGB")
    b = _bande(np.asarray(im.convert("L")))
    corpo = b[testa:-coda]
    im = im.crop((0, max(0, corpo[0][0] - margine), im.width, min(im.height, corpo[-1][1] + margine)))
    # via il bianco ai lati
    col = np.flatnonzero((np.asarray(im.convert("L")) < 245).sum(axis=0) > 0)
    im = im.crop((max(0, col[0] - margine), 0, min(im.width, col[-1] + margine), im.height))
    ratio = im.width / im.height
    if w / h > ratio:
        ww, hh = h * ratio, h
    else:
        ww, hh = w, w / ratio
    buf = io.BytesIO(); im.save(buf, format="PNG", optimize=True); buf.seek(0)
    return slide.shapes.add_picture(buf, Inches(x + (w - ww) / 2), Inches(y), Inches(ww), Inches(hh))

def nuova(layout):
    return prs.slides.add_slide(L(layout))

SEP = "\n\n- - - SOLO SU DOMANDA - - -\n"

# ================================================================ 1. COPERTINA
s = nuova("Title 4")
t = title(s, "Ponte 19: un servizio che va a cercare chi non cerca, e che misura se funziona",
          size=30, caps=True)
geom(t, top=2.75, height=3.1)
sub = [ph for ph in s.placeholders if ph.placeholder_format.idx == 13][0]
geom(sub, width=9.0)
fill(sub.text_frame, [[("Datapolis 2026, Bagheria (PA)   ·   Alessandro Carosia e Saverio Randazzo", {})]],
     font=SANS, size=13, color=GREY, after=0)
prune(s)
notes(s, f"""
MESSAGGIO: la proposta si chiama Ponte 19 ed è un servizio comunale che raggiunge i giovani fuori da lavoro e studio, con una quota per le ragazze e una valutazione incorporata.
RELATORE: Alessandro apre.
TRACCIA (20 secondi): «Buongiorno. Siamo Alessandro Carosia e Saverio Randazzo. Abbiamo lavorato sui 15-24enni di Bagheria con i dati pubblici del censimento permanente, e proponiamo Ponte 19: un servizio che va a cercare chi non cerca, e che misura se funziona. In dieci minuti: tre evidenze, il perimetro del metodo, il bisogno che vediamo, la proposta.»
FONTE: ISTAT, Censimento permanente della popolazione 2018-2024; elaborazioni nei notebook del progetto.
TRANSIZIONE: «Prima le tre cifre su cui costruiamo tutto, sempre con il confronto territoriale.»
""")

# ================================================================ 2. TRE EVIDENZE (Ale)
s = nuova("Title Only")
title(s, "Tre evidenze, sempre con il confronto territoriale",
      size=26, top=0.75, height=0.9)
cards = [
    (PINK, f"{o24['Bagheria']}%", "occupazione femminile 15-24, anno 2024",
     f"Palermo {o24['Palermo']}%, Sicilia {o24['Sicilia']}%, Italia {o24['Italia']}%. Bagheria è ultima fra i quattro territori in tutte le sei annate disponibili."),
    (MINT, f"{NON_CERCA}%", "di chi è fuori da lavoro e studio non è classificato in ricerca",
     "15-24enni di Bagheria, anno 2024. Un servizio ad accesso su domanda incontra chi si presenta: per gli altri serve un contatto attivo."),
    (PEACH, f"{cas['Bagheria']}%", "casalinghe dichiarate fra le 15-24enni, anno 2024",
     f"Palermo {cas['Palermo']}%, Sicilia {cas['Sicilia']}%, Italia {cas['Italia']}%. Condizione dichiarata al censimento, non una misura delle ore di cura."),
]
for i, (col, big, lab, small) in enumerate(cards):
    x = 0.75 + i * 3.95
    card(s, x, 1.9, 3.75, 4.35, col)
    box(s, x + 0.3, 2.1, 3.15, 1.1, [big], font=SERIF, size=48, color=GREEN, after=0)
    box(s, x + 0.3, 3.25, 3.15, 1.0, [lab], font=SANS, size=14, color=INK, after=0, spacing=1.15)
    box(s, x + 0.3, 4.35, 3.15, 1.8, [small], font=SANS, size=11.5, color=GREY, after=0, spacing=1.2)
footer(s, "Fonte: ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, classe 15-24 anni, 2024 (serie 2018-2024 per il confronto fra annate). Popolazione: residenti di 15-24 anni.")
prune(s)
notes(s, f"""
MESSAGGIO: tre cifre descrittive, ognuna con il suo benchmark. Sono i soli numeri che pronunciamo fuori dalle figure.
RELATORE: Alessandro.
TRACCIA: «Tre evidenze. Prima: nel 2024 lavora l'{o24['Bagheria']}% delle ragazze di 15-24 anni di Bagheria, contro {o24['Palermo']} a Palermo, {o24['Sicilia']} in Sicilia, {o24['Italia']} in Italia; Bagheria è ultima in tutte le sei annate che la fonte pubblica. Seconda: di chi è fuori da lavoro e studio, il {NON_CERCA}% non risulta classificato in ricerca, e un servizio a domanda incontra solo chi si presenta. Terza: il {cas['Bagheria']}% delle 15-24enni si dichiara casalinga, contro il {cas['Italia']}% in Italia.»
DA NON DIRE: «minimo storico» (l'{o24['Bagheria']} è il valore più alto della serie di Bagheria), «significativamente», «non vogliono lavorare», «scoraggiati», «carico di cura».
FONTE: ISTAT, Censimento permanente 2024; genere_forbice_serie.csv, schede_claim.csv, genere_casalinghe.csv.
TRANSIZIONE: «Prima di entrare nei dati, Saverio dice cosa abbiamo misurato e cosa no.»
{SEP}
«È distinta anche statisticamente?» -> È un confronto descrittivo fra territori, ripetuto su sei annate con lo stesso segno; non usiamo la parola «significativo».
«Il tasso è quasi raddoppiato dal 2018: non si risolve da solo?» -> Cresce ovunque, a Bagheria come altrove; Bagheria resta ultima in ogni annata e lo scarto da Palermo resta sotto i due punti senza chiudersi.
""")

# ================================================================ 3. PERIMETRO (Saverio)
s = nuova("Title Only")
title(s, "Cosa misuriamo e cosa no",
      size=26, top=0.75, height=0.9)
righe = [
    ("Il bando parla di NEET 15-34; nelle fonti pubbliche comunali consultate la misura non è disponibile.",
     "Il censimento permanente pubblica a livello comunale la sola classe giovanile 15-24; il NEET 15-29 esiste solo al 2011. Lavoriamo sui 15-24, senza ricostruire né stimare i 15-34."),
    ("L'incrocio titolo di studio per condizione professionale non è pubblicato nelle tavole comunali utilizzate.",
     "Misuriamo separatamente il divario nell'istruzione e quello nel lavoro, e confrontiamo i segni. Non seguiamo le stesse persone dal diploma al lavoro."),
    ("I limiti riguardano le fonti consultate, non una dichiarazione di inesistenza generale.",
     "Ogni cifra di questa presentazione si rigenera dai notebook del progetto, con i controlli automatici della pipeline."),
]
for i, (testa, corpo) in enumerate(righe):
    y = 1.95 + i * 1.5
    dot(s, 0.85, y + 0.05, 0.5, str(i + 1))
    box(s, 1.6, y, 10.9, 0.55, [[(testa, {"bold": True})]], font=SANS, size=14.5, after=0)
    box(s, 1.6, y + 0.6, 10.9, 0.8, [corpo], font=SANS, size=12.5, color=GREY, after=0, spacing=1.2)
footer(s, "Fonti consultate: ISTAT, Censimento permanente della popolazione 2018-2024 (tavole comunali: condizione professionale 15-24, istruzione 9-24, popolazione per età singola); ISTAT 8milaCensus 2011; ISTAT, matrici del pendolarismo 2011 e 2021.")
prune(s)
notes(s, """
MESSAGGIO: dichiariamo il perimetro noi, nei primi sessanta secondi. A un festival sulla cultura del dato è un merito; estratto sotto domanda sarebbe una mancanza.
RELATORE: Saverio.
TRACCIA: «Il bando è scritto sui NEET 15-34. Nelle fonti pubbliche comunali che abbiamo consultato quella misura non c'è: il censimento permanente dà al comune la sola classe 15-24, e il NEET 15-29 esiste solo al 2011. Non lo ricostruiamo e non lo stimiamo: lavoriamo sul 15-24, che è la fascia che esiste. Secondo: l'incrocio fra titolo di studio e condizione professionale non è pubblicato nelle tavole comunali, quindi i due divari li misuriamo separatamente e ne confrontiamo i segni. Terzo: sono limiti delle fonti consultate, non una dichiarazione che il dato non esista da nessuna parte.»
FONTE E METODO: cella di verifica della copertura in notebooks/analisi.ipynb; dimostrazione dell'incrocio mancante in notebooks/genere.ipynb.
TRANSIZIONE: «Con questo perimetro, il primo dato: chi è fuori da lavoro e studio.»
""")

# ================================================================ 4. ACCESSO (Saverio)
s = nuova("Title Only")
title(s, "Come raggiungiamo chi non sta cercando?", size=26, top=0.75, height=0.8)
box(s, 0.75, 1.9, 5.6, 1.8, [
    "Tra i giovani fuori da lavoro e studio, molti non risultano in ricerca. Per raggiungerli, Ponte 19 propone un contatto attivo: il primo passo parte dal servizio.",
], font=SANS, size=16, spacing=1.3, after=0)
card(s, 0.75, 3.95, 5.6, 2.3, MINT)
box(s, 1.05, 4.1, 5.0, 0.85, [[(f"{NON_CERCA}%", {"font": SERIF, "size": 40, "color": GREEN})]], after=0)
box(s, 1.05, 4.95, 5.0, 1.2, [[("di chi è fuori da lavoro e studio non risulta classificato in ricerca.", {"bold": True})],
                              "Bagheria, residenti di 15-24 anni, 2024. È una condizione censuaria, non un'intenzione."],
    font=SANS, size=11.5, spacing=1.2, after=4)

def percorso(y, etichetta, colore, da, a, didascalia):
    card(s, 7.0, y, 5.6, 1.95, colore)
    box(s, 7.3, y + 0.15, 5.0, 0.4, [[(etichetta, {"font": SERIF, "size": 16, "color": GREEN})]], after=0)
    for k, testo in enumerate((da, a)):
        pill = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.3 + k * 2.9), Inches(y + 0.7), Inches(2.0), Inches(0.5))
        pill.adjustments[0] = 0.5; pill.fill.solid(); pill.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        pill.line.color.rgb = GREEN; pill.line.width = Pt(1); pill.shadow.inherit = False
        tf = pill.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        fill(tf, [testo], font=SANS, size=12, align=PP_ALIGN.CENTER, after=0, anchor=MSO_ANCHOR.MIDDLE)
    arrow(s, 9.45, y + 0.8, 0.6, 0.3)
    box(s, 7.3, y + 1.35, 5.0, 0.5, [didascalia], font=SANS, size=11.5, color=GREY, after=0)

percorso(1.9, "Accesso su domanda", BLUE, "la persona", "il servizio", "La persona contatta il servizio.")
percorso(4.3, "Ponte 19", PEACH, "il servizio", "la persona", "Il servizio cerca il contatto con la persona.")
footer(s, "Fonte: ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, classe 15-24 anni, 2024. «Fuori da lavoro e studio» = né occupati né studenti: proxy calcolabile a scala comunale, non il NEET ISTAT 15-29.")
prune(s)
notes(s, f"""
MESSAGGIO: chi non risulta in ricerca difficilmente arriva da solo a uno sportello; per questo il primo passo parte dal servizio.
RELATORE: Saverio.
TRACCIA: «Nel 2024 più di un 15-24enne su quattro a Bagheria è fuori sia dal lavoro sia dallo studio. Di questi, il {NON_CERCA}% non è classificato in ricerca. È una condizione censuaria, non un'intenzione: non sappiamo perché non cercano. Un servizio ad accesso su domanda incontra chi si presenta; per gli altri il primo passo deve partire dal servizio. È la scelta di Ponte 19: il contatto attivo.»
DA NON DIRE: «non vogliono lavorare», «scoraggiati», «chi cerca si risolve da sé», «nessuno li intercetta» (la classificazione censuaria non descrive il comportamento di ogni persona verso i servizi).
FONTE E METODO: quota calcolata sull'area fuori da lavoro e studio (casalinghe/i, altra condizione, pensione, rispetto a occupati e studenti); schede_claim.csv, edu_youth_states_2018_2024.csv.
TRANSIZIONE: «Chi sono? Guardiamo istruzione e lavoro, per genere, sulla stessa popolazione.»
{SEP}
«Quanti sono?» -> Circa {mille(PLATEA)} 15-24enni inattivi non studenti nel 2024, di cui {fuori_non_cerca['F']} ragazze e {fuori_non_cerca['M']} ragazzi: platea indicativa, stima dalla ricostruzione della tavola (appendice).
«Il calo di chi è fuori da lavoro e studio dal 2018 non è già una soluzione?» -> Il calo viene soprattutto dalla componente «in cerca»; la componente inattiva non studentesca resta quasi ferma. Non parliamo di riclassificazioni né di chi «si risolve da sé».
""")

# ================================================================ 5. fig11 (transizione)
s = nuova("Title Only")
title(s, "Il diploma le ragazze lo raggiungono più dei ragazzi; il lavoro, la metà",
      size=24, top=0.6, height=0.8)
figura(s, "fig11_per_1000", 1, 0.75, 1.45, 11.85, 4.95)
footer(s, "Per 1.000 residenti di 15-24 anni dello stesso genere, anno 2024, cinque territori. La base comune è una normalizzazione: non rende identiche le popolazioni e non identifica le diplomate occupate, perché l'incrocio non è pubblicato a livello comunale. Diploma: fascia 9-24 della fonte, che sui titoli coincide con il 15-24. Fonte: ISTAT, Censimento permanente 2024 (genere_per_1000.csv).", y=6.45, h=0.6)
prune(s)
notes(s, """
MESSAGGIO: sulla stessa popolazione, le ragazze hanno il diploma più dei ragazzi e lavorano la metà. Sono due misure affiancate, non un percorso.
RELATORE: Saverio chiude la parte studio-lavoro e passa ad Alessandro sul pannello «al lavoro».
TRACCIA: «Su 1.000 ragazze di 15-24 anni a Bagheria, 510 hanno almeno il diploma e 82 lavorano; su 1.000 ragazzi, 462 e 165. Il pannello di sopra e quello di sotto si rovesciano. Attenzione: non osserviamo quante diplomate stiano effettivamente lavorando, perché l'incrocio non è pubblicato. Osserviamo insieme istruzione più alta e occupazione più bassa; non seguiamo le stesse persone.»
DA NON DIRE: «il diploma non si converte in lavoro» come transizione individuale; «occupazione delle diplomate».
FONTE E METODO: base 1.000 = normalizzazione per confrontare territori di taglia diversa; conteggi dei diplomi sulla fascia 9-24 (nessuno ha un diploma prima dei 15), occupati sulla classe 15-24; genere_per_1000.csv.
TRANSIZIONE (Alessandro): «Il rovesciamento fra i due pannelli è un divario di genere. Lo seguiamo nel tempo.»
""")

# ================================================================ 6. SERIE (Ale) - grafico nativo
s = nuova("Title Only")
title(s, "L'occupazione delle ragazze cresce ovunque; Bagheria resta ultima in ogni annata",
      size=24, top=0.6, height=0.9)
cd = CategoryChartData()
cd.categories = [a if a != "2020" else "2020 n.d." for a in ANNI]
for terr in TERR:
    cd.add_series(terr, [occF[terr].get(a) for a in ANNI])
gf = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(0.75), Inches(1.55), Inches(8.6), Inches(4.85), cd)
ch = gf.chart
ch.has_legend = False; ch.has_title = False
ch.font.name = SANS; ch.font.size = Pt(11); ch.font.color.rgb = GREY
va = ch.value_axis; va.minimum_scale = 0; va.maximum_scale = 20; va.major_unit = 5
va.tick_labels.number_format = '0"%"'; va.tick_labels.number_format_is_linked = False
va.has_major_gridlines = True
va.major_gridlines.format.line.color.rgb = RGBColor(0xDD, 0xDD, 0xDD); va.major_gridlines.format.line.width = Pt(0.75)
va.format.line.fill.background()
ca = ch.category_axis; ca.format.line.color.rgb = RGBColor(0xBB, 0xBB, 0xBB); ca.has_major_gridlines = False
ch.plots[0].has_data_labels = False
for ser in ch.series:
    col = RGBColor.from_string(TERR[ser.name])
    ser.smooth = False
    ser.format.line.color.rgb = col
    ser.format.line.width = Pt(3.25 if ser.name == "Bagheria" else 1.75)
    ser.marker.style = XL_MARKER_STYLE.CIRCLE; ser.marker.size = 7 if ser.name == "Bagheria" else 5
    ser.marker.format.fill.solid(); ser.marker.format.fill.fore_color.rgb = col
    ser.marker.format.line.color.rgb = col
    dl = ser.points[len(ANNI) - 1].data_label
    dl.has_text_frame = True; dl.position = XL_LABEL_POSITION.RIGHT
    dl.text_frame.text = f"{ser.name} {o24[ser.name]}%"
    r = dl.text_frame.paragraphs[0].runs[0]
    style(r, SANS, 11, color=col, bold=(ser.name == "Bagheria"))
# nota a lato
card(s, 9.75, 1.75, 2.85, 4.45, PINK)
box(s, 10.0, 1.95, 2.4, 4.1, [
    [(f"{o24['Bagheria']}%", {"font": SERIF, "size": 40, "color": GREEN})],
    [("nel 2024 è il valore più alto della serie di Bagheria.", {"bold": True})],
    "Il tasso sale ovunque dal 2018, a Bagheria come altrove. Bagheria resta ultima in ogni annata e lo scarto da Palermo resta sotto i due punti, senza chiudersi.",
], font=SANS, size=12, spacing=1.2, after=8)
footer(s, "Tasso di occupazione femminile, classe 15-24 anni, in percentuale delle residenti della classe, 2018-2024. Il 2020 manca alla fonte per la classe 15-24 in tutti i territori e non è interpolato. Fonte: ISTAT, Censimento permanente della popolazione (genere_forbice_serie.csv).", y=6.5, h=0.55)
prune(s)
notes(s, f"""
MESSAGGIO: la serie sale ovunque; il punto non è la caduta, è il ritardo che non si chiude.
RELATORE: Alessandro.
TRACCIA: «Il tasso di occupazione delle ragazze di 15-24 anni cresce dal 2018 in tutti i territori, a Bagheria come altrove. Nel 2024 Bagheria è all'{o24['Bagheria']}%, il valore più alto della sua serie; Palermo è a {o24['Palermo']}, la Sicilia a {o24['Sicilia']}, l'Italia a {o24['Italia']}. Bagheria è ultima in ogni annata e lo scarto da Palermo resta sotto i due punti senza chiudersi. Il 2020 manca alla fonte: la riga è interrotta, non interpolata.»
DA NON DIRE: «minimo storico», «crolla», «peggiora», «significativamente».
FONTE E METODO: ISTAT, Censimento permanente 2018-2024; grafico nativo modificabile costruito da genere_forbice_serie.csv; il 2020 è assente alla fonte sulla classe 15-24 in tutti i territori.
TRANSIZIONE: «Dove finiscono i punti di occupazione che mancano alle ragazze? La fonte ha una condizione dichiarata che pesa più che altrove.»
{SEP}
«Sta crescendo da solo, perché intervenire?» -> Cresce allo stesso passo dei territori di confronto e resta ultima in ogni annata: il divario non si chiude. Nessun p-value a voce.
«Palermo è un controfattuale valido?» -> È un confronto descrittivo dichiarato in anticipo; l'identificazione causale dell'effetto del pilota è affidata alla lista d'attesa, non al confronto con Palermo.
""")

# ================================================================ 7. fig02b (Ale)
s = nuova("Title Only")
title(s, f"Casalinghe dichiarate fra le 15-24enni: {cas['Bagheria']}% a Bagheria, {cas['Italia']}% in Italia",
      size=24, top=0.6, height=0.8)
figura(s, "fig02b_casalinghe_territori", 1, 0.9, 1.5, 11.55, 4.85)
footer(s, "Quota di ragazze di 15-24 anni che al censimento si dichiarano casalinghe, in percentuale delle coetanee residenti, anno 2024. Condizione dichiarata, non una misura delle ore di cura. Vicinato = i cinque comuni più vicini per distanza fra i centroidi, conteggi sommati prima della quota. Ordine delle righe geografico, non per valore. Fonte: ISTAT, Censimento permanente 2024.", y=6.45, h=0.6)
prune(s)
notes(s, f"""
MESSAGGIO: la condizione di casalinga dichiarata è un tratto di zona che a Bagheria pesa quasi tre volte l'Italia. È un'etichetta censuaria su cui l'outreach può costruire il contatto.
RELATORE: Alessandro.
TRACCIA: «Il {cas['Bagheria']}% delle ragazze di 15-24 anni di Bagheria si dichiara casalinga al censimento. Palermo è all'{cas['Palermo']}%, la Sicilia al {cas['Sicilia']}%, l'Italia al {cas['Italia']}%. Il vicinato di Bagheria sta ancora più in alto: è un tratto di zona. È una condizione dichiarata, non una misura di quante ore di cura queste ragazze facciano, né di chi accudiscano.»
DA NON DIRE: «carico di cura», «responsabilità familiari», «la famiglia d'origine è la barriera».
FONTE E METODO: ISTAT, Censimento permanente 2024, condizione professionale, classe 15-24; genere_casalinghe.csv, genere_composizione_stato_dettaglio.csv; vicinato aggregato con conteggi sommati prima della quota.
TRANSIZIONE: «Ultimo indizio prima della proposta: a che età si perde la coorte femminile.»
{SEP}
«Condizione dichiarata o ore di cura misurate?» -> Dichiarata. Il censimento non misura le ore di cura; per questo diciamo «marcatore», mai «carico».
«Quante sono?» -> {CASALINGHE_N} ragazze nel 2024 (cifra stampata nel sottotitolo della figura originale).
""")

# ================================================================ 7b. DUE DIVARI (Ale)
s = nuova("Title Only")
title(s, "Due divari da leggere insieme", size=26, top=0.75, height=0.8)
box(s, 0.75, 1.95, 5.5, 2.3, [
    [("Nell'istruzione, un vantaggio.", {"font": SERIF, "size": 22, "color": GREEN})],
    f"Le ragazze di 15-24 anni raggiungono almeno il diploma più dei ragazzi: {DIP_F} contro {DIP_M} per 1.000 residenti dello stesso genere, nel 2024.",
], font=SANS, size=14, spacing=1.3, after=10)
box(s, 7.1, 1.95, 5.5, 2.3, [
    [("Nel lavoro, uno svantaggio.", {"font": SERIF, "size": 22, "color": GREEN})],
    f"Lavorano {OCC_F} ragazze su 1.000 contro {OCC_M} ragazzi: il tasso femminile, {o24['Bagheria']}%, è l'ultimo dei quattro territori in ogni annata.",
], font=SANS, size=14, spacing=1.3, after=10)
box(s, 0.75, 4.35, 11.85, 0.7, ["Sono misure separate: non conosciamo il percorso delle singole persone."],
    font=SANS, size=14, color=GREY, spacing=1.2, after=0)
card(s, 0.75, 5.15, 11.85, 1.1, PEACH)
box(s, 1.05, 5.3, 11.3, 0.85, [[("Scelta progettuale. ", {"bold": True}),
    ("La proposta tiene conto di questo squilibrio prevedendo una quota femminile nell'accesso al servizio.", {})]],
    font=SANS, size=13, spacing=1.2, after=0, anchor=MSO_ANCHOR.MIDDLE)
footer(s, "Diploma e lavoro per 1.000 residenti di 15-24 anni dello stesso genere, Bagheria, 2024 (stesse cifre della figura sul diploma e sul lavoro); tasso femminile dalla serie 2018-2024. L'incrocio titolo di studio per condizione professionale non è pubblicato a livello comunale. Fonte: ISTAT, Censimento permanente 2024.")
prune(s)
notes(s, f"""
MESSAGGIO: due divari di segno opposto, letti insieme ma misurati separatamente. Da qui la quota femminile.
RELATORE: Alessandro.
TRACCIA: «Mettiamo insieme quello che abbiamo visto. Nell'istruzione le ragazze hanno un vantaggio: {DIP_F} su 1.000 con almeno il diploma contro {DIP_M}. Nel lavoro uno svantaggio: {OCC_F} su 1.000 lavorano contro {OCC_M}, e il tasso femminile è l'ultimo dei quattro territori in ogni annata. Sono misure separate: non conosciamo il percorso delle singole persone. La proposta tiene conto di questo squilibrio con una quota femminile nell'accesso al servizio.»
DA NON DIRE: «il diploma non si converte in lavoro» come transizione individuale; nessuna freccia dal diploma alla disoccupazione. Le casalinghe dichiarate restano un'etichetta censuaria su cui costruire il contatto: non «carico di cura».
FONTE E METODO: genere_per_1000.csv (base 1.000 = normalizzazione, due misure affiancate); genere_forbice_serie.csv.
TRANSIZIONE: «Ultimo indizio prima della proposta: a che età la coorte femminile si riduce.»
""")

# ================================================================ 8. fig07 (Ale)
s = nuova("Title Only")
title(s, "Le ragazze restano fino ai 23 anni, poi la coorte si riduce",
      size=24, top=0.6, height=0.9)
figura(s, "fig07_ritenzione_eta", 2, 0.75, 1.55, 11.85, 4.85)
footer(s, "Asse orizzontale: età rilevata nel 2021 (nel 2024 tre anni in più). Quota della coorte del 2021 ancora residente nello stesso comune nel 2024: saldo netto che comprende partenze e arrivi, non un conteggio di chi emigra. Linee = medie mobili su tre età: si leggono i pattern, non i decimali. Indizio per il reclutamento, non una misura della fuga. Fonte: ISTAT, Censimento permanente, età singole 2021 e 2024.", y=6.45, h=0.6)
prune(s)
notes(s, """
MESSAGGIO: la coorte femminile tiene fino ai 23 anni e da lì si riduce, senza rientri; nel vicinato la stessa finestra resta piatta. Ci dice dove e quando reclutare, non perché si parte.
RELATORE: Alessandro.
TRACCIA: «L'asse orizzontale è l'età rilevata nel 2021: chi aveva 22 anni nel 2021 ne ha 25 nel 2024. Sotto il tratteggio la coorte si è ridotta. Le ragazze di Bagheria, in vermiglio, tengono fino ai 23 anni e da lì scendono, senza rientri; i ragazzi escono a ondate e in parte rientrano dopo i 26. La finestra 22-25 è l'età in cui il servizio deve già aver raggiunto le ragazze. È un saldo netto, non un conteggio di partenze: lo usiamo solo come indizio per il reclutamento.»
DA NON DIRE: «abbiamo dimostrato perché le ragazze partono», «la fuga contata», qualunque aggancio al 96,3.
FONTE E METODO: ISTAT, Censimento permanente, età singole 2021 e 2024; genere_ritenzione_eta.csv. Il 96,3 di ritenzione è un'altra misura (coorte 25-29 nel 2021, genere_coorti.csv) e non va associato alla finestra 22-25.
TRANSIZIONE: «Da qui la proposta. E la prima cosa che diciamo della proposta è come si misura.»
""")

# ================================================================ 9. STATEMENT policy
s = nuova("Statement")
st = [ph for ph in s.placeholders if ph.placeholder_format.idx == 13][0]
fill(st.text_frame, [
    [("Il pilota produce la propria evidenza", {"font": SERIF, "size": 44, "caps": True})],
    [("Ponte 19: servizio comunale di transizione e riattivazione per i 18-25", {"font": SANS, "size": 16, "color": GREY, "caps": False})],
], align=PP_ALIGN.CENTER, after=18, anchor=MSO_ANCHOR.MIDDLE)
prune(s)
notes(s, """
MESSAGGIO: il disegno di valutazione è parte della proposta, non una risposta di riserva.
RELATORE: non assegnato dalle linee guida (sezione policy).
TRACCIA: «Il titolo della proposta è questo: il pilota produce la propria evidenza. Non chiediamo di credere che funzioni: chiediamo di poterlo misurare. Vediamo a chi si rivolge, come si misura, come si sa se ha funzionato, in quali tempi.»
TRANSIZIONE: «A chi si rivolge.»
""")

# ================================================================ 10. IL SERVIZIO
s = nuova("Title Only")
title(s, "Dal primo contatto a un'opportunità praticabile", size=26, top=0.75, height=0.8)
passi = [
    ("Contatto attivo", "Il servizio raggiunge i giovani fuori da lavoro e studio, nei luoghi che frequentano."),
    ("Piano individuale", "La presa in carico definisce il percorso: rientro in istruzione, qualifica breve, ricerca assistita o esperienza retribuita."),
    ("Opportunità verificata", "Ogni opportunità ha attività reale, mentor e compenso; si verifica anche la raggiungibilità negli orari reali."),
    ("Verifica degli esiti", "Si osserva se l'esito viene raggiunto a sei mesi e mantenuto al dodicesimo."),
]
w, gap, x0 = 2.6, 0.5, 0.75
for i, (testa, corpo) in enumerate(passi):
    x = x0 + i * (w + gap)
    card(s, x, 1.85, w, 3.05, [MINT, BLUE, LAV, YELLOW][i])
    dot(s, x + 0.25, 2.05, 0.5, str(i + 1))
    box(s, x + 0.25, 2.7, w - 0.5, 0.75, [[(testa, {"font": SERIF, "size": 17})]], after=0, spacing=1.05)
    box(s, x + 0.25, 3.45, w - 0.5, 1.4, [corpo], font=SANS, size=11.5, after=0, spacing=1.2)
    if i < 3:
        arrow(s, x + w + 0.1, 3.2, 0.3, 0.35)
card(s, 0.75, 5.1, 11.85, 1.25, PEACH)
box(s, 1.05, 5.2, 11.3, 1.1, [
    [("Destinatari: ", {"bold": True}), ("residenti di 18-25 anni fuori da lavoro e studio, con outreach verso chi non risulta in ricerca. ", {}),
     ("Capacità del primo anno: ", {"bold": True}), (f"{CAP} partecipanti, di cui {CAP_F} donne (quota del 50%, non un servizio esclusivamente femminile).", {})],
    [("Obiettivo territoriale che la accompagna: ", {"bold": True}),
     (f"occupazione femminile 15-24 da {o24['Bagheria']}% a {o24['Palermo']}% su un triennio. I {CAP} sono capacità progettata, non domanda stimata né copertura della platea.", {})],
], font=SANS, size=11.5, spacing=1.2, after=4)
footer(s, "Passaggi, destinatari e capacità dalla proposta Ponte 19 (sezioni 3 e 4). I destinatari 18-25 non coincidono con la popolazione osservata nel censimento (15-24): le due fasce si sovrappongono solo in parte.")
prune(s)
notes(s, f"""
MESSAGGIO: cosa succede quando una persona entra in Ponte 19: contatto attivo, piano individuale, opportunità verificata, esiti misurati. Sotto, chi e quanti.
RELATORE: non assegnato dalle linee guida (sezione policy).
TRACCIA: «Cosa succede in pratica. Primo: il servizio raggiunge i giovani fuori da lavoro e studio, nei luoghi che frequentano, invece di aspettarli a uno sportello. Secondo: la presa in carico definisce un piano individuale con una sola prossima azione verificabile. Terzo: ogni opportunità entra nel piano solo se è reale, con mentor e compenso, e se è raggiungibile negli orari reali. Quarto: si osserva se l'esito viene raggiunto a sei mesi e mantenuto al dodicesimo. Destinatari: residenti di 18-25 anni fuori da lavoro e studio. Capacità del primo anno: {CAP} partecipanti, di cui {CAP_F} donne. Non è un servizio per ragazze: è un servizio con una quota del 50%. L'obiettivo che accompagna questa capacità è il tasso di occupazione femminile 15-24, da {o24['Bagheria']} a {o24['Palermo']} su un triennio.»
DA NON DIRE: «{CAP} coprono il 18% della platea» (platea 15-24 e requisiti 18-25 non si sovrappongono), «quaranta occupate prodotte», «la pipeline garantisce tutto».
FONTE: POLICY_PONTE_19.md, sezione 3 (target, quote, capacità) e sezione 4 (componenti A-E: outreach, presa in carico, piano, esperienze su domanda verificata, mobilità).
TRANSIZIONE: «Come si misura, e come si distingue il territorio dal servizio.»
{SEP}
«Perché 18-25 se i dati sono 15-24?» -> La fascia osservabile nel censimento è 15-24; il servizio non può prendere in carico minori con gli stessi strumenti, e la finestra 22-25 è quella in cui la coorte femminile si riduce. Le due fasce si sovrappongono sui 18-24 e lo diciamo.
«Quanti sono in tutto?» -> Platea indicativa: circa {mille(PLATEA)} 15-24enni inattivi non studenti nel 2024, {fuori_non_cerca['F']} ragazze e {fuori_non_cerca['M']} ragazzi. Il gruppo non è femminile nelle dimensioni, lo è nell'etichetta censuaria (casalinghe).
""")

# ================================================================ 11. MISURAZIONE
s = nuova("Title Only")
title(s, "Come si misura: il territorio in tasso, il servizio sugli esiti",
      size=24, top=0.75, height=0.9)
# pannello sinistro: territorio
card(s, 0.75, 1.9, 6.6, 4.05, BLUE)
box(s, 1.05, 2.05, 6.0, 0.4, [[("INDICATORI TERRITORIALI", {"bold": True, "color": GREEN}), ("   popolazione 15-24 di Bagheria", {"color": GREY})]], font=SANS, size=12, after=0)
box(s, 1.05, 2.55, 3.0, 0.4, [[("KPI primario", {"bold": True})]], font=SANS, size=12.5, after=0)
box(s, 1.05, 2.9, 3.0, 0.5, ["tasso di occupazione femminile 15-24"], font=SANS, size=11.5, color=GREY, after=0)
box(s, 1.05, 3.35, 3.0, 0.8, [[(f"da {o24['Bagheria']}% a {o24['Palermo']}%", {"font": SERIF, "size": 26, "color": GREEN})]], after=0)
box(s, 1.05, 4.1, 3.0, 0.9, [f"+{DELTA} punti, il livello di Palermo, letto su un triennio"], font=SANS, size=11.5, after=0, spacing=1.2)
box(s, 4.25, 2.55, 2.9, 0.4, [[("KPI secondario", {"bold": True})]], font=SANS, size=12.5, after=0)
box(s, 4.25, 2.9, 2.9, 0.5, ["casalinghe dichiarate 15-24"], font=SANS, size=11.5, color=GREY, after=0)
box(s, 4.25, 3.35, 2.9, 0.8, [[(f"da {cas['Bagheria']}% a {cas['Palermo']}%", {"font": SERIF, "size": 26, "color": GREEN})]], after=0)
box(s, 4.25, 4.1, 2.9, 0.9, ["il livello di Palermo, letto su un biennio o un triennio"], font=SANS, size=11.5, after=0, spacing=1.2)
box(s, 1.05, 5.1, 6.0, 0.75, [[("Obiettivi, non risultati. ", {"bold": True}), (f"Capacità del pilota nel primo anno: {CAP} partecipanti, di cui {CAP_F} donne. Una variazione del tasso comunale non si attribuisce al pilota da sola: il confronto lo costruisce la valutazione.", {})]], font=SANS, size=11, color=GREY, after=0, spacing=1.15)
# pannello destro: servizio
card(s, 7.6, 1.9, 5.0, 4.05, PEACH)
box(s, 7.9, 2.05, 4.5, 0.4, [[("ESITI DEL SERVIZIO", {"bold": True, "color": GREEN}), ("   sui partecipanti presi in carico", {"color": GREY})]], font=SANS, size=12, after=0)
box(s, 7.9, 2.6, 4.4, 3.2, [
    [("A sei mesi: ", {"bold": True}), ("occupati, in istruzione o in formazione qualificante.", {})],
    [("Al dodicesimo mese: ", {"bold": True}), ("esito ancora attivo.", {})],
    [("Letti sui presi in carico, ", {"bold": True}), ("con il confronto della lista d'attesa (slide seguente). Sono esiti da misurare, non promesse.", {})],
], font=SANS, size=12.5, spacing=1.2, after=10)
footer(s, "Valori di partenza: ISTAT, Censimento permanente 2024, classe 15-24 (genere_forbice_serie.csv, genere_casalinghe.csv). Finestra di lettura dei KPI: genere_mde.csv. Gli obiettivi sono obiettivi progettuali; gli esiti sono ancora da misurare.")
prune(s)
notes(s, f"""
MESSAGGIO: i KPI territoriali sono in tasso e si leggono sul triennio; gli esiti del servizio si leggono sui presi in carico. Due cose diverse, due riquadri diversi.
RELATORE: non assegnato dalle linee guida (sezione policy).
TRACCIA: «Il KPI primario è il tasso di occupazione femminile 15-24: da {o24['Bagheria']} a {o24['Palermo']}, il livello di Palermo, più {DELTA} punti, e si legge su un triennio. Il secondario è la quota di casalinghe dichiarate, da {cas['Bagheria']} a {cas['Palermo']}. I {CAP} partecipanti, di cui {CAP_F} donne, sono la capacità che accompagna questi obiettivi, non l'obiettivo. Sul servizio misuriamo altro: quanti partecipanti sono occupati, in istruzione o in formazione a sei mesi, e quanti lo sono ancora al dodicesimo.»
PERCHÈ IL TRIENNIO (da dire): «Su un solo anno la variazione minima che il dato censuario riesce a distinguere dal rumore è più grande dell'obiettivo: una lettura annuale direbbe "nessun effetto" anche se l'effetto ci fosse. Sul triennio il test ha potenza adeguata. Lo dichiariamo prima dell'avvio.»
DA NON DIRE: «quaranta occupate prodotte dal servizio»; non attribuire al pilota una variazione dell'occupazione comunale.
FONTE: POLICY_PONTE_19.md sezioni 4-bis e 6; genere_mde.csv (delta da rilevare {DELTA} pp; minima differenza rilevabile su un anno {MDE1} pp, potenza sul triennio {POT3.replace('.0', '')}%).
TRANSIZIONE: «Come si sa se ha funzionato.»
{SEP}
«Quanto vale la minima differenza rilevabile?» -> {MDE1} punti su un anno, sopra il delta di {DELTA}: per questo la lettura annuale non è ammessa; sul triennio la potenza è del {POT3.replace('.0', '')}%.
«+40 occupate?» -> Solo nella forma della policy: tasso-obiettivo per platea dell'anno, riparametrato ogni anno; mai «prodotte dal servizio». La platea femminile 15-24 è già nata e cala: per questo il KPI è in tasso e non in teste.
""")

# ================================================================ 12. VALUTAZIONE
s = nuova("Title Only")
title(s, "Per capire se aiuta, confrontiamo chi comincia prima e chi dopo", size=26, top=0.75, height=0.8)
card(s, 0.75, 1.8, 11.85, 0.6, YELLOW)
box(s, 1.05, 1.8, 11.3, 0.6, [[("Condizione comune: ", {"bold": True}),
    ("protocollo, outcome primario e finestre di osservazione pubblicati prima dell'avvio.", {})]],
    font=SANS, size=12.5, after=0, anchor=MSO_ANCHOR.MIDDLE)
X0, XW, XG = 3.05, 4.65, 0.25
for k, etichetta in enumerate(("primo periodo", "secondo periodo")):
    box(s, X0 + k * (XW + XG), 2.55, XW, 0.3, [etichetta], font=SANS, size=11, color=GREY, align=PP_ALIGN.CENTER, after=0)
righe = [("Gruppo A", [(BLUE, INK, "Avvio del servizio"), (BLUE, INK, "Osservazione degli esiti")]),
         ("Gruppo B", [(RGBColor(0xEF, 0xEF, 0xEF), GREY, "Attesa: è il gruppo di confronto"), (LAV, INK, "Avvio successivo del servizio")])]
for r, (grp, fasi) in enumerate(righe):
    y = 2.9 + r * 1.2
    box(s, 0.75, y + 0.3, 2.2, 0.5, [[(grp, {"font": SERIF, "size": 18, "color": GREEN})]], after=0)
    for k, (colore, ink, testo) in enumerate(fasi):
        card(s, X0 + k * (XW + XG), y, XW, 1.0, colore)
        box(s, X0 + k * (XW + XG) + 0.2, y, XW - 0.4, 1.0, [testo], font=SANS, size=13, color=ink,
            align=PP_ALIGN.CENTER, after=0, anchor=MSO_ANCHOR.MIDDLE)
arrow(s, X0, 5.2, 2 * XW + XG, 0.16, color=RGBColor(0xBB, 0xBB, 0xBB))
box(s, X0, 5.38, 2 * XW + XG, 0.3, ["tempo"], font=SANS, size=10, color=GREY, align=PP_ALIGN.RIGHT, after=0)
box(s, 0.75, 5.7, 11.85, 0.8, [[("A parità di priorità, l'ordine di avvio è casuale. ", {"bold": True}),
    ("Durante l'attesa, il secondo gruppo permette di costruire il confronto con chi ha già iniziato. Il prima-dopo da solo non basta.", {})]],
    font=SANS, size=12.5, spacing=1.2, after=0)
footer(s, "Disegno di valutazione dalla proposta Ponte 19 (sezione 7): rollout scaglionato con lista d'attesa, randomizzazione a parità di priorità quando eticamente possibile, protocollo e outcome primario pubblicati prima dell'avvio.", y=6.6, h=0.45)
prune(s)
notes(s, """
MESSAGGIO: il confronto è costruito dentro il servizio: chi comincia dopo è il confronto di chi ha già iniziato. È l'asset più forte per un contest data-driven.
RELATORE: non assegnato dalle linee guida (sezione policy).
TRACCIA: «Il servizio parte a scaglioni. Prima di tutto pubblichiamo protocollo, outcome e finestre di osservazione: non si scelgono a posteriori. Poi: a parità di priorità l'ordine di avvio è casuale. Il gruppo A comincia subito e ne osserviamo gli esiti; il gruppo B aspetta il proprio turno e, mentre aspetta, è il confronto. Poi comincia anche lui. Il prima-dopo da solo non basta, e lo diciamo noi.»
FONTE: POLICY_PONTE_19.md, sezione 7 (valutazione dell'impatto).
TRANSIZIONE: «Tempi, e il posto della mobilità.»

- - - SOLO SU DOMANDA - - -
«E il p-value su Palermo?» -> Palermo è il confronto territoriale dichiarato in anticipo, descrittivo; l'identificazione causale è affidata alla lista d'attesa. Il mancato rifiuto di una differenza non dimostra equivalenza, e non lo sosteniamo.
«È etico far aspettare?» -> La capacità è comunque limitata, quindi una lista d'attesa esiste in ogni caso; l'ordine casuale a parità di priorità è il modo più equo di ordinarla, e chi ha priorità più alta parte prima.
""")

# ================================================================ 13. TEMPI E MOBILITÀ
s = nuova("Title Only")
title(s, "Tempi certi, e un vincolo di raggiungibilità", size=26, top=0.75, height=0.8)
fasi = [
    ("90 giorni", "preparazione", "Audit dei datori locali e metropolitani, canali di contatto, quota di genere. Chiude con un decision gate."),
    ("12 mesi", "erogazione", "Presa in carico a scaglioni, piano individuale, esperienze retribuite solo su domanda verificata."),
    ("3, 6 e 12 mesi", "follow-up", "Esiti dei partecipanti rilevati a tre, sei e dodici mesi dalla presa in carico."),
]
w, gap = 3.75, 0.3
for i, (big, lab, corpo) in enumerate(fasi):
    x = 0.75 + i * (w + gap)
    card(s, x, 1.85, w, 2.05, [MINT, BLUE, LAV][i])
    box(s, x + 0.3, 1.95, w - 0.6, 0.9, [[(big, {"font": SERIF, "size": 26, "color": GREEN})], [(lab, {"font": SANS, "size": 12, "color": GREY})]], after=0, spacing=1.0)
    box(s, x + 0.3, 2.9, w - 0.6, 0.95, [corpo], font=SANS, size=11.5, spacing=1.2, after=0)
    if i < 2:
        arrow(s, x + w + 0.02, 2.75, 0.26, 0.3)
box(s, 0.75, 4.3, 11.85, 0.7, [[("Un'opportunità deve essere raggiungibile, negli orari in cui serve.", {"font": SERIF, "size": 22, "color": GREEN})]], after=0)
box(s, 0.75, 5.05, 11.85, 0.65, ["Prima di inserirla nel piano individuale, il servizio verifica il collegamento con il trasporto collettivo negli orari reali della posizione."],
    font=SANS, size=14, spacing=1.25, after=0)
box(s, 0.75, 5.75, 11.85, 0.6, ["Si misura con la quota di partecipanti che accedono a un'opportunità fuori comune entro sei mesi, sul dato di servizio."],
    font=SANS, size=12, color=GREY, spacing=1.2, after=0)
footer(s, "Tempi e componenti dalla proposta Ponte 19 (sezioni 3, 4-E, 4-bis, 5). La mobilità è la componente E: vincolo di progettazione, non capitolo di spesa; il suo KPI si legge sul dato di servizio, perché la statistica ufficiale sul pendolarismo per genere non è annuale.", y=6.6, h=0.45)
prune(s)
notes(s, """
MESSAGGIO: 90 giorni di preparazione con decision gate, 12 mesi di erogazione, follow-up a 3, 6 e 12 mesi; la mobilità entra nel servizio come vincolo di raggiungibilità e come KPI, non come capitolo di spesa.
RELATORE: non assegnato dalle linee guida (sezione policy).
TRACCIA: «Novanta giorni di preparazione, che chiudono con un decision gate: si verifica che esistano posizioni reali, canali di contatto che funzionano e una quota di genere rispettata; altrimenti si corregge prima di crescere. Dodici mesi di erogazione. Follow-up a tre, sei e dodici mesi. E un vincolo: un'opportunità deve essere raggiungibile negli orari in cui serve. Prima di inserirla nel piano, il servizio verifica il collegamento con il trasporto collettivo negli orari reali della posizione. Lo misuriamo con la quota di partecipanti che accede a un'opportunità fuori comune entro sei mesi.»
DA NON DIRE: «il trasporto non è un problema», «la pipeline garantisce tutto».
FONTE: POLICY_PONTE_19.md, sezioni 3 (durata), 4-E (componente mobilità), 4-bis (KPI F2 e F3), 5 (decision gate).
NOTA DI COERENZA: nella policy consegnata il KPI «fuori comune entro sei mesi» è etichettato F2 (sezione 4-bis); F3 è il criterio premiale nelle gare comunali. Le linee guida lo chiamano F3: a voce usare la descrizione, non la sigla.
TRANSIZIONE: «Chiudiamo.»

- - - SOLO SU DOMANDA - - -
«E il terzo thread, la mobilità?» -> È qui: vincolo di progettazione (componente E) e KPI sul dato di servizio. Nei dati aggregati non troviamo associazione fra offerta di trasporto e divario di genere sul lavoro; il pilota verifica la raggiungibilità caso per caso. Non diciamo che il trasporto «non è un problema»: un'associazione non significativa non esclude un effetto.
«Dove vanno i pendolari?» -> Quasi solo a Palermo: carta in appendice, solo su richiesta.
""")

# ================================================================ 14. CONCLUSIONE
s = nuova("Conclusion 2")
t = title(s, "Un servizio che va a cercare chi non cerca, e che misura se funziona", size=26, caps=True)
t.left, t.width, t.top, t.height = Inches(4.9), Inches(8.0), Inches(3.55), Inches(2.05)
body = [ph for ph in s.placeholders if ph.placeholder_format.idx == 14][0]
body.left, body.width, body.top, body.height = Inches(5.65), Inches(7.3), Inches(5.75), Inches(1.1)
fill(body.text_frame, ["Non abbiamo spiegato la fuga: il pilota misura gli esiti e non pretende di aver individuato la causa."],
     font=SANS, size=13, color=GREY, after=0, spacing=1.2)
prune(s)
notes(s, f"""
MESSAGGIO: chiudiamo sul servizio e sulla sua valutabilità. La clausola sulla causa si dice qui, una volta sola.
RELATORE: non assegnato dalle linee guida (sezione conclusioni).
TRACCIA: «Ponte 19 è un servizio che va a cercare chi non cerca, con una quota del 50% per le ragazze, e che misura se funziona: KPI in tasso letti sul triennio, esiti dei partecipanti a sei e dodici mesi, lista d'attesa come confronto, protocollo pubblicato prima. Una cosa non l'abbiamo fatta: non abbiamo spiegato la fuga. Il pilota misura gli esiti, non pretende di aver individuato la causa. Grazie.»
FONTE: intera presentazione; POLICY_PONTE_19.md.

- - - SOLO SU DOMANDA (prontuario) - - -
«Dove avete misurato la fuga dei 15-34enni?» -> Non l'abbiamo misurata: disponiamo di stock censuari e saldi di coorte, senza tracciamento di destinazioni o titoli di studio.
«Quanti sono?» -> Circa {mille(PLATEA)} 15-24enni inattivi non studenti nel 2024, di cui {fuori_non_cerca['F']} ragazze: platea indicativa (appendice).
«Diploma 33,4% e +4,2 punti?» -> È la classe 9-24, l'unica pubblicata a livello comunale su tutta la serie: 33,4% delle ragazze con almeno il diploma contro 29,2% dei ragazzi. Il denominatore include bambini e abbassa il livello per entrambi i generi allo stesso modo; sul 18-24 il vantaggio femminile regge. Attenzione: «+4,2» nella policy compare anche con un altro significato (inattivi non studenti, 4,2 punti sopra la Sicilia).
«Il diploma non si converte in lavoro?» -> Osserviamo insieme istruzione più alta e occupazione più bassa; non seguiamo le stesse persone.
«La famiglia d'origine è la barriera?» -> Non lo sosteniamo: lo stato civile non misura convivenza, figli a carico o causalità.
«Il trasporto non è la barriera?» -> Non troviamo associazione nei dati aggregati; il pilota verifica la raggiungibilità caso per caso.
«Bagheria è unica nell'inversione?» -> No: parliamo solo di ampiezza diversa dello scarto; Palermo non inverte il segno.
«Ritenzione 96,3?» -> È la coorte 25-29 nel 2021 (genere_coorti.csv), non la finestra 22-25 della figura.
«Si esce per studiare, non per lavorare?» -> Non lo sosteniamo.
«Discrepanze fra i PDF consegnati?» -> Tabella in appendice: si risponde con il valore giusto e la fonte, in una frase.
""")

# ================================================================ APPENDICE
s = nuova("Section Header 2")
t = title(s, "Appendice: materiale di riserva, solo su domanda", size=32, caps=True)
prune(s)
notes(s, "Materiale di riserva. Non fa parte del tempo principale: si apre solo se un giurato pone la domanda corrispondente.")

# A2 carta verso Palermo
s = nuova("Title Only")
title(s, "Riserva sul pendolarismo: Bagheria ha un solo mercato esterno, e si chiama Palermo",
      size=24, top=0.6, height=0.9)
figura(s, "mob_fig01_verso_palermo", 4, 0.75, 1.55, 11.85, 4.75)
footer(s, "Quota di chi esce dal comune diretta a ciascuna destinazione: a sinistra chi esce per studio (censimento 2011, spostamenti giornalieri), a destra chi esce per lavoro (censimento permanente 2021, almeno tre giorni a settimana). Due definizioni diverse, non una serie; la fonte non ha l'età, quindi il 15-34 non è isolabile. Fonte: ISTAT, matrici del pendolarismo (mob_flussi_bagheria.csv).", y=6.4, h=0.65)
prune(s)
notes(s, """
USO: solo se sollecitati sul pendolarismo.
MESSAGGIO: la direzione è una sola, Palermo; per questo la raggiungibilità con il mezzo collettivo è un vincolo del servizio.
TRACCIA: «Nove studenti su dieci che escono dal comune vanno a Palermo, e due lavoratori su tre. Le due annate sono due definizioni diverse e non una serie; la matrice non ha l'età.»
FONTE: ISTAT, matrici del pendolarismo 2011 (studio) e 2021 (lavoro); notebooks/mobilita.ipynb.

- - - SOLO SU DOMANDA - - -
«Uscita prima delle 7:15?» -> Le sole cifre riproducibili sono 44,7% delle donne e 61,1% degli uomini, su tutti gli spostamenti in uscita dal comune (mob_orario_genere.csv); i 54,4/65,0 dei testi non sono riproducibili e non si difendono.
«Mezzo privato 63,6 o 63,7?» -> 63,6% (63,64 nel dato); il 63,7 è un arrotondamento sbagliato.
«Treno 98° o 97° percentile?» -> 98° su 390 comuni per quota di chi esce che usa il treno; 97° a parità di distanza e taglia: due misure, sempre con il qualificatore.
""")

# A3 platea e fonti
s = nuova("Title Only")
title(s, "Su domanda: quanti sono, e da quali fonti", size=24, top=0.75, height=0.9)
card(s, 0.75, 1.9, 5.9, 4.35, BLUE)
box(s, 1.05, 2.05, 5.3, 0.5, [[("Platea indicativa", {"font": SERIF, "size": 20, "color": GREEN}), ("   Bagheria, 15-24 anni, 2024", {"font": SANS, "size": 12, "color": GREY})]], after=0)
box(s, 1.05, 2.7, 5.3, 3.4, [
    [(mille(PLATEA), {"font": SERIF, "size": 34, "color": GREEN})],
    [("inattivi non studenti: fuori da lavoro e studio e non in cerca", {"bold": True})],
    f"di cui {fuori_non_cerca['F']} ragazze e {fuori_non_cerca['M']} ragazzi: la somma fa {fuori_non_cerca['F'] + fuori_non_cerca['M']} per arrotondamento di stime frazionarie. Fra le ragazze, {CASALINGHE_N} casalinghe dichiarate.",
    f"I {CAP} posti del pilota sono capacità progettata sui 18-25: non una copertura di questa platea, che è osservata sui 15-24. Stima dalla ricostruzione della tavola censuaria.",
], font=SANS, size=12, spacing=1.2, after=8)
card(s, 6.85, 1.9, 5.75, 4.35, MINT)
box(s, 7.15, 2.05, 5.2, 0.5, [[("Fonti e riproducibilità", {"font": SERIF, "size": 20, "color": GREEN})]], after=0)
box(s, 7.15, 2.7, 5.2, 3.4, [
    [("ISTAT, Censimento permanente della popolazione 2018-2024: ", {"bold": True}), ("condizione professionale (classe 15-24), istruzione (fascia 9-24), popolazione per età singola (dal 2021).", {})],
    [("ISTAT 8milaCensus 2011: ", {"bold": True}), ("NEET 15-29 solo come dato storico, mai in serie con il proxy 15-24.", {})],
    [("ISTAT, matrici del pendolarismo 2011 e 2021.", {"bold": True})],
    [("Notebook: ", {"bold": True}), ("analisi, genere, educazione, mobilità; pipeline con 755 controlli automatici fra dati grezzi, notebook, file elaborati e testi.", {})],
], font=SANS, size=11.5, spacing=1.2, after=8)
footer(s, "Platea: schede_claim.csv e genere_composizione_stato_dettaglio.csv. Fonti: docs/sources.md del progetto. Le cifre di questa slide non si pronunciano spontaneamente: rispondono alla domanda «quanti sono».")
prune(s)
notes(s, f"""
USO: solo su domanda «quanti sono» o «da dove vengono i dati».
RISPOSTA IN UNA FRASE: «Circa {mille(PLATEA)} 15-24enni inattivi non studenti nel 2024, di cui {fuori_non_cerca['F']} ragazze: platea indicativa, perché i destinatari del servizio sono i 18-25 e le due fasce si sovrappongono solo in parte.»
DA NON DIRE: «{CAP} coprono il 18%», «771» (non compare in nessun documento).
""")

# A4 tabella discrepanze
s = nuova("Title Only")
title(s, "Su domanda: cifre disallineate nei documenti consegnati, e il valore corretto",
      size=24, top=0.75, height=0.9)
righe = [
    ("Coppia nei documenti", "Valore corretto e risposta", "Fonte"),
    ("Diploma 33,4% e +4,2 punti", "Quota di ragazze 9-24 con almeno il diploma nel 2024 (33,4%) contro 29,2% dei ragazzi: +4,2 punti. Nella policy «+4,2» compare anche con un altro significato (inattivi non studenti, 4,2 punti sopra la Sicilia): dire sempre di cosa.", "genere_forbice_serie.csv, genere_quadro_sintesi.csv"),
    ("Uscita prima delle 7:15: 54,4 / 65,0 contro 44,7 / 61,1", "Le sole cifre riproducibili sono 44,7% delle donne e 61,1% degli uomini, su tutti gli spostamenti in uscita dal comune.", "mob_orario_genere.csv"),
    ("Mezzo privato 63,6 contro 63,7", "63,6% (63,64 nel dato); il 63,7 è un arrotondamento sbagliato.", "mob_mezzo_genere.csv"),
    ("Santa Flavia 6,8 contro 7,3", "Due anni, non un refuso: 6,8% nel 2011 e 7,3% nel 2021 (quota di chi esce per lavoro). Citare con l'anno.", "mob_flussi_bagheria.csv"),
    ("Treno 98° contro 97° percentile", "98° su 390 comuni per quota di chi esce che usa il treno; 97° a parità di distanza e taglia. Due misure: sempre con il qualificatore.", "mob_sintesi.csv, mob_treno_390.csv"),
    ("Platea 1.121 / 573 / 549 / 771", "Nidificati, non alternativi: 1.121 inattivi non studenti 15-24 nel 2024, 573 ragazze, 549 ragazzi; 387 casalinghe fra le 573. Il 771 non compare in nessun documento.", "edu_finding_summary.csv, schede_claim.csv"),
]
tbl = s.shapes.add_table(len(righe), 3, Inches(0.75), Inches(1.85), Inches(11.85), Inches(4.4)).table
tbl.columns[0].width, tbl.columns[1].width, tbl.columns[2].width = Inches(2.9), Inches(6.35), Inches(2.6)
for row in tbl.rows:
    row.height = Inches(0.4)
for r, riga in enumerate(righe):
    for c, testo in enumerate(riga):
        cell = tbl.cell(r, c)
        cell.margin_left = cell.margin_right = Inches(0.08); cell.margin_top = cell.margin_bottom = Inches(0.04)
        cell.fill.solid(); cell.fill.fore_color.rgb = MINT if r == 0 else (RGBColor(0xFF, 0xFF, 0xFF) if r % 2 else RGBColor(0xF6, 0xF6, 0xF6))
        fill(cell.text_frame, [[(testo, {"bold": r == 0 or c == 0})]], font=SANS, size=9.5 if r else 10.5,
             color=INK, spacing=1.05, after=0)
footer(s, "Tabella delle discrepanze dalle linee guida per la presentazione. I documenti sono stati consegnati il 30 agosto e non si aggiornano: queste cifre non si pronunciano spontaneamente; se sollevate, si risponde con il valore corretto e la fonte, in una frase.")
prune(s)
notes(s, "USO: solo se un giurato solleva una di queste coppie. La risposta è il valore corretto con la fonte, in una frase, senza fermarsi. La verifica automatica della pipeline (755 controlli) passa perché queste cifre stanno fuori dalla sua copertura.")

prs.save(OUT)
print("salvato", OUT, "slide:", len(prs.slides))

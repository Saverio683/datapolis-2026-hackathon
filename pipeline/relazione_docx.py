"""docs/relazione/RELAZIONE_DATAPOLIS.md -> docs/relazione/RELAZIONE_DATAPOLIS.docx, con le figure incorporate.

Il .docx e' un artefatto *derivato*: il testo, e quindi ogni cifra, vive nel .md, che sta
dentro il perimetro di pipeline/verifica.py. Qui non si riscrive nulla a mano, si impagina.

Tre cose che questo modulo fa e che non sono ovvie.

1. **Le figure si ritagliano al solo grafico.** I PNG di R sono impilati: titolo e
   sottotitolo in testa, il grafico, la didascalia a quattro blocchi in coda. Un PNG di 22
   cm rimpicciolito a 17 cm di specchio porta quella didascalia sotto i 6 punti, cioe'
   illeggibile. Quindi si ritaglia via il testo e lo si rimette come testo di Word, alla
   tipografia del documento: selezionabile, cercabile e a corpo leggibile. E' la stessa
   regola gia' applicata alle schede HTML da pipeline/schede.py.
2. **Il testo rimesso e' quello calcolato, non uno riscritto.** Titoli e quattro blocchi
   arrivano da figures/didascalie.csv, che viz/dump_didascalie.R estrae intercettando le
   funzioni del tema: i numeri restano quelli che R ha letto dai CSV.
3. **Times New Roman ovunque, tranne il codice.** Il font si cambia nel tema del
   reference.docx, cosi' vale per corpo, titoli e tabelle in un colpo solo. I nomi di file,
   i codici territoriali (082006) e i blocchi di comandi restano a spaziatura fissa: in un
   documento che si legge per verificarlo, 082006 e ITG1 devono essere inequivocabili.

Uso:  uv run python -m pipeline.relazione_docx
"""

from __future__ import annotations

import csv
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
DOCS = RADICE / "docs" / "relazione"
FIGURE = RADICE / "figures"
SORGENTE = DOCS / "RELAZIONE_DATAPOLIS.md"
USCITA = DOCS / "RELAZIONE_DATAPOLIS.docx"
DIDASCALIE = FIGURE / "didascalie.csv"

AUTORI = ("Alessandro Carosia", "Saverio Randazzo")

# Specchio di stampa: A4 meno i margini laterali. Le figure ci vanno larghe quanto lui.
LARGHEZZA_CM = 17.0

# ------------------------------------------------------------------ dove va ogni figura
# (frammento ancora nel .md, nome della figura). Il frammento deve comparire una volta
# sola: se il testo cambia, la build si ferma invece di piazzare la figura altrove.
INLINE: list[tuple[str, str]] = [
    ("sono giovani che non arrivano a cercare.", "edu_fig03_composizione"),
    ("Bagheria migliora alla velocità del contesto, non di più.", "edu_fig04_scomposizione"),
    ("Bagheria **migliora in assoluto e arretra in posizione**.", "edu_fig01_storia_posizione"),
    ("`genere_madri_recente.csv`, `genere_frattura_istruzione.csv`", "fig10_muro_recente"),
    ("`genere_mappa_2011_2024.csv`, sezione «I claim reggono al 2024?» di `notebooks/genere.ipynb`",
     "fig04_mappa_sicilia"),
    ("mai come quantità attribuibile al comune.", "fig08_posizionamento"),
    ("→ `genere_quadro_sintesi.csv`, `genere_forbice_quadrante.csv`", "fig05_forbice"),
    ("«Trend 2018-2024» di `notebooks/genere.ipynb`", "fig01_gap_tre_scale"),
    ("→ `genere_per_1000.csv`, `genere_forbice_quadrante.csv`", "fig11_per_1000"),
    ("→ `genere_composizione_stato_dettaglio.csv` (fig02)", "fig02_composizione_stato"),
    ("→ `genere_coorti.csv`, `genere_ritenzione_eta.csv`", "fig03_coorti"),
    ("l'anno singolo è un controllo, non un titolo. → `genere_ritenzione_transizioni.csv`", "fig07_ritenzione_eta"),
    ("→ `edu_historical_benchmarks_2011.csv`", "edu_fig02_catena_2011"),
    ("non c'è\nda scegliere quale destinazione servire.", "mob_fig01_verso_palermo"),
    ("più ragazze all'università, che è a Palermo.", "mob_fig02_ribaltamento"),
    ("stesse persone. → `genere_pendolarismo.csv`, fig12", "fig12_pendolarismo"),
    ("È chi si muove, e per quale motivo.**", "mob_fig04_taglia_distanza"),
    ("Aumentarne l'uso non è la leva che manca.", "mob_fig03_treno_genere"),
    ("12,4% in Italia. → `genere_stranieri.csv`", "edu_fig08_popolazione"),
    ("a tasso 2024 costante: `genere_tetto_platea.csv`)", "fig09_kpi_finestra"),
    ("→ `genere_mde.csv` (fig09b)", "fig09b_potenza"),
]

# Le figure di R hanno la didascalia negli ultimi due blocchi di inchiostro: una
# convenzione garantita da didascalia_2b() in viz/theme.R, non una stima.
#
# Si ritaglia SOLO la coda, e il titolo resta nell'immagine. La ragione e' una misura,
# non un gusto: i PNG sono larghi 22-26 cm e sullo specchio di 17 cm si riducono al
# 65-77%. Il titolo, che R compone a 16 punti, arriva cosi' a 10-12 punti e si legge; la
# didascalia, a 8,6 punti, arriva sotto i 6 e non si legge piu'. Quindi si toglie e si
# rifa' in Word col testo estratto da figures/didascalie.csv, cioe' con i numeri che R
# ha calcolato dai CSV. Ritagliare anche la testa costringerebbe invece a indovinare
# quante bande occupano titolo e sottotitolo prima della legenda, che va tenuta: una
# soglia che cambia da figura a figura, per riscrivere un testo che si legge gia'.
CODA_DIDASCALIA = 2

# Nel .docx gli emoji di stato non servono e in Times New Roman non esistono: la
# locandina chiede una risposta, non un semaforo.
SOSTITUZIONI = [
    # La locandina chiede una risposta, non un semaforo: nel documento gli stati
    # diventano parole. Le due frasi che parlano *degli* stati vanno riscritte per
    # intero, altrimenti la sostituzione secca le rende sgrammaticate.
    ("I 🟡 non sono lavori a metà", "Le risposte parziali non sono lavori a metà"),
    ("Un 🟡 è diventato ✅, e vale la pena dire come.",
     "Una risposta parziale è diventata piena, e vale la pena dire come."),
    ("| 🔴→🟡 ", "| **Solo in parte.** "),
    ("| ✅ ", "| **Sì**, "), ("| 🟡 ", "| **In parte**: "), ("| 🔴 ", "| **No**: "),
    ("✔ ", "Sì, "),
]

def _bande(grigia, vuoto: int = 28):
    """Le bande orizzontali di inchiostro, separate da almeno `vuoto` righe bianche."""
    import numpy as np

    righe = np.flatnonzero((grigia < 245).sum(axis=1) > 0)
    salti = np.flatnonzero(np.diff(righe) > vuoto)
    return list(zip(np.concatenate(([righe[0]], righe[salti + 1])),
                    np.concatenate((righe[salti], [righe[-1]]))))


def ritaglia(nome: str, dest: Path, margine: int = 26) -> Path:
    """Il PNG senza la didascalia a due blocchi: nel .docx la rifà Word, come testo."""
    import numpy as np
    from PIL import Image

    im = Image.open(FIGURE / f"{nome}.png").convert("RGB")
    bande = _bande(np.asarray(im.convert("L")))
    assert len(bande) > CODA_DIDASCALIA + 1, (
        f"{nome}: {len(bande)} bande, non bastano per togliere i {CODA_DIDASCALIA} "
        f"blocchi di didascalia. La figura ha cambiato impaginazione.")
    im = im.crop((0, 0, im.width,
                  min(im.height, bande[-CODA_DIDASCALIA - 1][1] + margine)))
    fuori = dest / f"{nome}.png"
    im.save(fuori, format="PNG", optimize=True)
    return fuori


# ------------------------------------------------------------------- il reference.docx
# Il font si cambia una volta sola, nel *tema*: gli stili di pandoc non nominano un
# carattere, puntano a "minorHAnsi"/"majorHAnsi", cioe' al tema. Cambiato li', cambia in
# corpo, titoli, tabelle e note insieme, senza toccare stile per stile.
STILE_DIDASCALIA = """
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="Didascalia">
    <w:name w:val="Didascalia" />
    <w:basedOn w:val="Normal" />
    <w:qFormat />
    <w:pPr>
      <w:spacing w:before="60" w:after="60" w:line="230" w:lineRule="auto" />
      <w:ind w:left="284" w:right="284" />
      <w:jc w:val="both" />
    </w:pPr>
    <w:rPr>
      <w:sz w:val="17" /><w:szCs w:val="17" />
      <w:color w:val="1F1F1F" />
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="TitoloFigura">
    <w:name w:val="Titolo figura" />
    <w:basedOn w:val="Normal" />
    <w:next w:val="Didascalia" />
    <w:qFormat />
    <w:pPr>
      <w:keepNext />
      <w:spacing w:before="120" w:after="40" />
      <w:ind w:left="284" w:right="284" />
    </w:pPr>
    <w:rPr><w:sz w:val="19" /><w:szCs w:val="19" /></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="Copertina">
    <w:name w:val="Copertina" />
    <w:basedOn w:val="Normal" />
    <w:qFormat />
    <w:pPr><w:spacing w:before="0" w:after="140" /><w:jc w:val="center" /></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="CopertinaTitolo">
    <w:name w:val="Copertina titolo" />
    <w:basedOn w:val="Copertina" />
    <w:qFormat />
    <w:pPr><w:spacing w:before="360" w:after="160" /><w:jc w:val="center" /></w:pPr>
    <w:rPr><w:b /><w:sz w:val="48" /><w:szCs w:val="48" /></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="CopertinaSottotitolo">
    <w:name w:val="Copertina sottotitolo" />
    <w:basedOn w:val="Copertina" />
    <w:qFormat />
    <w:pPr><w:spacing w:before="0" w:after="400" /><w:jc w:val="center" /></w:pPr>
    <w:rPr><w:sz w:val="28" /><w:szCs w:val="28" /></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="IndiceUno">
    <w:name w:val="Indice uno" />
    <w:basedOn w:val="Normal" />
    <w:qFormat />
    <w:pPr><w:spacing w:before="140" w:after="20" /><w:jc w:val="left" /></w:pPr>
    <w:rPr><w:b /></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="IndiceDue">
    <w:name w:val="Indice due" />
    <w:basedOn w:val="Normal" />
    <w:qFormat />
    <w:pPr>
      <w:spacing w:before="0" w:after="20" />
      <w:ind w:left="454" /><w:jc w:val="left" />
    </w:pPr>
    <w:rPr><w:sz w:val="21" /><w:szCs w:val="21" /></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="CopertinaAutori">
    <w:name w:val="Copertina autori" />
    <w:basedOn w:val="Copertina" />
    <w:qFormat />
    <w:pPr><w:spacing w:before="0" w:after="360" /><w:jc w:val="center" /></w:pPr>
    <w:rPr><w:b /><w:sz w:val="26" /><w:szCs w:val="26" /></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="CopertinaEnte">
    <w:name w:val="Copertina ente" />
    <w:basedOn w:val="Copertina" />
    <w:qFormat />
    <w:pPr><w:spacing w:before="600" w:after="0" /><w:jc w:val="center" /></w:pPr>
    <w:rPr><w:b /><w:caps /><w:sz w:val="22" /><w:szCs w:val="22" /></w:rPr>
  </w:style>
"""

# A4 e margini, in twip (1 cm = 567). Lo specchio che ne esce e' LARGHEZZA_CM.
SECTPR_TESTA = '<w:footerReference w:type="default" r:id="rIdPieDiPagina" />'
SECTPR_CODA = ('<w:pgSz w:w="11906" w:h="16838" />'
               '<w:pgMar w:top="1418" w:right="1134" w:bottom="1418" w:left="1134" '
               'w:header="709" w:footer="709" w:gutter="0" />')

# Numero di pagina in fondo: e' un documento che si cita a voce in una commissione, e
# «pagina 31» deve poter essere detto. PAGE e' un campo, non un numero: Word e
# LibreOffice lo risolvono da soli, ed e' l'unico modo di averlo giusto dopo un'aggiunta.
PIE_DI_PAGINA = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:p>
    <w:pPr><w:spacing w:before="0" w:after="0" /><w:jc w:val="center" /></w:pPr>
    <w:r><w:rPr><w:sz w:val="18" /></w:rPr><w:t xml:space="preserve">- </w:t></w:r>
    <w:r><w:fldChar w:fldCharType="begin" /></w:r>
    <w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>
    <w:r><w:fldChar w:fldCharType="separate" /></w:r>
    <w:r><w:rPr><w:sz w:val="18" /></w:rPr><w:t>1</w:t></w:r>
    <w:r><w:fldChar w:fldCharType="end" /></w:r>
    <w:r><w:rPr><w:sz w:val="18" /></w:rPr><w:t xml:space="preserve"> -</w:t></w:r>
  </w:p>
</w:ftr>
"""


def reference_docx(dest: Path) -> Path:
    """Il reference.docx di pandoc, ritipografato: Times New Roman, A4, italiano."""
    base = dest / "reference-base.docx"
    base.write_bytes(subprocess.run(
        ["pandoc", "--print-default-data-file", "reference.docx"],
        check=True, capture_output=True).stdout)

    aperto = dest / "reference"
    if aperto.exists():
        shutil.rmtree(aperto)
    with zipfile.ZipFile(base) as z:
        z.extractall(aperto)

    tema = aperto / "word" / "theme" / "theme1.xml"
    t = tema.read_text(encoding="utf-8")
    t = re.sub(r'typeface="Aptos Display"', 'typeface="Times New Roman"', t)
    t = re.sub(r'typeface="Aptos"', 'typeface="Times New Roman"', t)
    tema.write_text(t, encoding="utf-8")

    stili = aperto / "word" / "styles.xml"
    s = stili.read_text(encoding="utf-8")
    # Il codice resta a spaziatura fissa: in un documento che si legge per verificarlo,
    # 082006 e ITG1 non devono poter essere confusi con del testo corrente.
    s = re.sub(r'w:ascii="Consolas" w:hAnsi="Consolas" />(\s*)<w:sz w:val="22" />',
               r'w:ascii="Courier New" w:hAnsi="Courier New" />\1<w:sz w:val="18" />', s)
    assert "Courier New" in s, "stile del codice non trovato nel reference.docx"
    # Corpo a 11 punti e lingua italiana (altrimenti Word segna in rosso tutta la relazione).
    s = s.replace('<w:sz w:val="24" />\n        <w:szCs w:val="24" />',
                  '<w:sz w:val="22" />\n        <w:szCs w:val="22" />', 1)
    s = s.replace('<w:lang w:val="en-US" w:eastAsia="en-US" w:bidi="ar-SA" />',
                  '<w:lang w:val="it-IT" w:eastAsia="it-IT" w:bidi="ar-SA" />', 1)
    # Giustificato sul solo corpo: sui titoli allargherebbe le righe spezzate.
    s = s.replace('<w:spacing w:before="180" w:after="180" />',
                  '<w:spacing w:before="0" w:after="150" w:line="252" w:lineRule="auto" />'
                  '<w:jc w:val="both" />', 1)
    assert "</w:styles>" in s
    s = s.replace("</w:styles>", STILE_DIDASCALIA + "</w:styles>", 1)
    stili.write_text(s, encoding="utf-8")

    (aperto / "word" / "footer1.xml").write_text(PIE_DI_PAGINA, encoding="utf-8")
    rels = aperto / "word" / "_rels" / "document.xml.rels"
    r = rels.read_text(encoding="utf-8")
    r = r.replace("</Relationships>",
                  '<Relationship Id="rIdPieDiPagina" Target="footer1.xml" Type='
                  '"http://schemas.openxmlformats.org/officeDocument/2006/relationships'
                  '/footer" /></Relationships>', 1)
    rels.write_text(r, encoding="utf-8")
    tipi = aperto / "[Content_Types].xml"
    c = tipi.read_text(encoding="utf-8")
    c = c.replace("</Types>",
                  '<Override PartName="/word/footer1.xml" ContentType="application/vnd.'
                  'openxmlformats-officedocument.wordprocessingml.footer+xml" /></Types>', 1)
    tipi.write_text(c, encoding="utf-8")

    doc = aperto / "word" / "document.xml"
    d = doc.read_text(encoding="utf-8")
    assert "<w:sectPr>" in d, "sectPr assente nel reference.docx di pandoc"
    assert "</w:footnotePr>" in d, "footnotePr assente: l'ordine dello schema va rifatto"
    d = d.replace("<w:sectPr>", "<w:sectPr>" + SECTPR_TESTA, 1)
    d = d.replace("</w:footnotePr>", "</w:footnotePr>" + SECTPR_CODA, 1)
    doc.write_text(d, encoding="utf-8")

    fuori = dest / "reference.docx"
    with zipfile.ZipFile(fuori, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(aperto.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(aperto).as_posix())
    return fuori


# ----------------------------------------------------------------------- il markdown
def _esc(t: str) -> str:
    """Le didascalie sono prosa, non markdown: `genere_gap_persone.csv` ha due trattini
    bassi e diventerebbe corsivo. Si neutralizzano i caratteri attivi, non il testo."""
    for c in "\\*_[]<>`#":
        t = t.replace(c, "\\" + c)
    return t


def _didascalie() -> dict[str, dict[str, str]]:
    assert DIDASCALIE.exists(), (
        f"{DIDASCALIE} assente: esegui prima `Rscript viz/dump_didascalie.R`")
    with DIDASCALIE.open(encoding="utf-8") as f:
        return {r["nome"]: r for r in csv.DictReader(f)}


def blocco_figura(nome: str, numero: int, dida: dict, dest: Path) -> str:
    """Figura ritagliata + titolo e due blocchi come testo di Word."""
    d = dida[nome]
    png = ritaglia(nome, dest)
    # Il titolo NON si ripete qui: sta gia' nell'immagine, a corpo leggibile. La riga di
    # Word porta il numero, che l'immagine non puo' avere perche' non sa dove finira'.
    righe = [
        "",
        f"![]({png.as_posix()}){{width={LARGHEZZA_CM}cm}}",
        "",
        '::: {custom-style="Didascalia"}',
    ]
    for etichetta, campo in (("Come si legge", "lettura"), ("Fonte", "fonte")):
        righe.append(f"**Figura {numero}. {etichetta}:** {_esc(d[campo].strip())}"
                     if campo == "lettura"
                     else f"**{etichetta}:** {_esc(d[campo].strip())}")
        righe.append("")
    righe += [f"*Figura* `{nome}`*, in* `figures/` *come PNG a 300 dpi e SVG; "
              f"rigenerata da* `viz/{nome}.R`*.*", ":::", ""]
    return "\n".join(righe)


def promuovi_titoli(testo: str) -> str:
    """`##` -> `#`: tolta la testata, le sezioni diventano il primo livello. I `#` dentro
    i blocchi di codice sono commenti di shell e non si toccano."""
    fuori, dentro = [], False
    for r in testo.split("\n"):
        if r.startswith("```"):
            dentro = not dentro
        if not dentro and re.match(r"^#{2,6} ", r):
            r = r[1:]
        fuori.append(r)
    return "\n".join(fuori)


SALTO_PAGINA = '\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n\n'

COPERTINA = """::: {{custom-style="CopertinaEnte"}}
DataPolis 2026 · Bagheria (PA)
:::

::: {{custom-style="CopertinaTitolo"}}
{titolo}
:::

::: {{custom-style="CopertinaSottotitolo"}}
{sottotitolo}
:::

::: {{custom-style="CopertinaAutori"}}
{autori}
:::

::: {{custom-style="Copertina"}}
{data}

&nbsp;

Relazione tecnica, visualizzazioni e proposta di intervento

Analisi condotta su statistica ufficiale ISTAT, interamente riproducibile

&nbsp;

{quante} figure · {controlli} controlli di regressione indipendenti, tutti superati

&nbsp;
:::

::: {{custom-style="Didascalia"}}
Ogni cifra in questo documento è riconducibile alle analisi svolte in ambiente Jupyter:
proviene da una cella di notebook o da un file di `data/processed/`. Il controllo di
regressione `pipeline/verifica.py` ricalcola ogni cifra dai dati grezzi, con
un'implementazione indipendente, e verifica che il testo la riporti alla lettera. Il
documento può essere rigenerato tramite `uv run python -m pipeline.relazione_docx`.
:::
"""


def indice(corpo: str) -> str:
    """Sommario statico, non un campo di Word: si legge anche senza aggiornare i campi,
    e in un PDF esportato da chiunque resta quello che era al momento della build.

    Le voci sono paragrafi con uno stile, non una lista: «1. Metodo» in testa a un
    elemento di elenco farebbe rinumerare tutto a Word, che ricomincerebbe da capo a
    ogni sezione e stamperebbe i suoi numeri accanto ai nostri.
    """
    voci, dentro = [], False
    for r in corpo.split("\n"):
        if r.startswith("```"):
            dentro = not dentro
        if dentro:
            continue
        m = re.match(r"^(#{1,2}) (.+?)\s*$", r)
        if m:
            voci.append((len(m.group(1)), re.sub(r"^(\d+)\.", r"\1\\.", m.group(2))))

    # L'indice parte dalla prima sezione numerata: i titoli del blocco di apertura
    # («Il quadro in una pagina» nella policy, «In una pagina» nella relazione) sono il
    # riassunto del documento, non la sua struttura, e in indice si leggono come commenti.
    prima = next((i for i, (liv, testo) in enumerate(voci)
                  if liv == 1 and re.match(r"\d+\\?\.", testo)), 0)
    voci = voci[prima:]

    fuori, corrente = ["# Indice", ""], None
    for livello, testo in voci:
        stile = "IndiceUno" if livello == 1 else "IndiceDue"
        if stile != corrente:
            if corrente:
                fuori += [":::", ""]
            fuori.append(f'::: {{custom-style="{stile}"}}')
            corrente = stile
        fuori += [testo, ""]
    fuori += [":::", ""]
    return "\n".join(fuori)


def inserisci_figure(testo: str, inline, dida: dict, dest: Path) -> tuple[str, int]:
    """Mette ogni figura dopo la sua ancora e la numera nell'ordine in cui compare.

    L'ancora si cerca ignorando gli a-capo del .md, perche' riandare a capo non deve
    spostare una figura; deve comparire una volta sola, altrimenti la build si ferma. La
    numerazione segue la posizione nel testo, non l'ordine della lista.
    """
    posti = []
    for ancora, nome in inline:
        schema = r"\s+".join(map(re.escape, ancora.split()))
        if ancora[-1].isspace():
            schema += r"\s"
        trovate = list(re.finditer(schema, testo))
        assert len(trovate) == 1, (
            f"ancora per {nome} trovata {len(trovate)} volte: «{ancora[:60]}»")
        posti.append((trovate[0].end(), nome))
    posti.sort()
    blocchi = [(fine, blocco_figura(nome, i, dida, dest))
               for i, (fine, nome) in enumerate(posti, start=1)]
    for fine, blocco in reversed(blocchi):
        testo = testo[:fine] + "\n" + blocco + testo[fine:]
    return testo, len(posti)


def markdown(dest: Path) -> tuple[str, int]:
    testo = SORGENTE.read_text(encoding="utf-8")
    dida = _didascalie()

    # La testata del .md diventa la copertina e sparisce dal flusso.
    righe = testo.split("\n")
    titolo = righe[0].lstrip("# ").strip()
    sottotitolo = righe[2].lstrip("# ").strip()
    assert righe[0].startswith("# ") and righe[2].startswith("## "), "testata inattesa"
    data = re.match(r"^(Bagheria, \d{4}-\d{2}-\d{2}(?:, versione rivista del \d{4}-\d{2}-\d{2})?)\.",
                    righe[4]).group(1)
    testo = "\n".join(righe[4:])

    testo, numero = inserisci_figure(testo, INLINE, dida, dest)

    # Appendice: le figure che il testo non incorpora, cosi' l'atlante e' completo.
    restanti = [n for n in dida if n not in {f for _, f in INLINE}]
    restanti.sort(key=lambda n: (not n.startswith("fig"), n))
    coda = ["", "---", "", "## Appendice B - Atlante completo delle figure", "",
            "Le figure che il testo non incorpora, nell'ordine dei tre thread. "
            "Non sono materiale di scarto: sono i controlli, le repliche e le "
            "scomposizioni su cui poggiano le affermazioni delle sezioni precedenti, e "
            "compaiono qui perché una relazione che chiede di essere verificata deve "
            "portarsi dietro anche ciò che non ha messo in prima pagina.", ""]
    for nome in restanti:
        numero += 1
        coda.append(blocco_figura(nome, numero, dida, dest))
    testo = testo + "\n".join(coda)

    for vecchio, nuovo in SOSTITUZIONI:
        testo = testo.replace(vecchio, nuovo)
    # La cautela che apre una frase diventa un'etichetta; dentro una frase, dopo una
    # parentesi o un punto e virgola, resta minuscola e il periodo continua.
    testo = re.sub(r"(\A|\n\n|[.!?]\s+)⚠️ ", r"\1**Cautela.** ", testo)
    testo = testo.replace("⚠️ ", "cautela: ")
    testo = promuovi_titoli(testo)

    # Anche il conteggio dei controlli si legge dal testo, invece di essere ribattuto in
    # copertina: se il pin cresce e la relazione lo dice, la copertina lo dice con lei.
    controlli = re.search(r"\*\*(\d+)/\1 PASS\*\*", testo)
    assert controlli, "in relazione non si trova il conteggio dei controlli di verifica"

    testa = COPERTINA.format(titolo=titolo, sottotitolo=sottotitolo, data=data,
                             autori=" · ".join(AUTORI),
                             quante=numero, controlli=controlli.group(1))
    return testa + SALTO_PAGINA + indice(testo) + SALTO_PAGINA + testo, numero


def dichiara_png(docx: Path) -> None:
    """Aggiunge il Default per i PNG al Content_Types del .docx finito.

    Pandoc dichiara ogni immagine con un Override suo, il che e' gia' conforme a OPC:
    Word e LibreOffice aprono senza storcere il naso. Ma un validatore che cerca il
    Default per l'estensione segnala 37 errori, e un documento che chiede di essere
    verificato non puo' permettersi 37 errori che vanno spiegati a voce. Va fatto qui e
    non nel reference.docx perche' quel file pandoc lo riscrive da zero.
    """
    marca = ('<Default Extension="rels" ContentType='
             '"application/vnd.openxmlformats-package.relationships+xml" />')
    png = '<Default Extension="png" ContentType="image/png" />'
    with zipfile.ZipFile(docx) as z:
        parti = {n: z.read(n) for n in z.namelist()}
    tipi = parti["[Content_Types].xml"].decode("utf-8")
    assert marca in tipi and png not in tipi, "Content_Types inatteso in uscita da pandoc"
    parti["[Content_Types].xml"] = tipi.replace(marca, marca + png, 1).encode("utf-8")
    with zipfile.ZipFile(docx, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, dati in parti.items():
            z.writestr(nome, dati)


def main() -> None:
    dest = RADICE / ".docx-build"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir()
    try:
        rif = reference_docx(dest)
        testo, quante = markdown(dest)
        sorgente = dest / "relazione.md"
        sorgente.write_text(testo, encoding="utf-8")
        subprocess.run(
            ["pandoc", str(sorgente), "-o", str(USCITA),
             "--reference-doc", str(rif),
             "--from", "markdown+pipe_tables+fenced_divs+raw_attribute",
             "--resource-path", str(dest)],
            check=True, cwd=RADICE)
        dichiara_png(USCITA)
    finally:
        shutil.rmtree(dest, ignore_errors=True)
    print(f"scritto: {USCITA.relative_to(RADICE)} "
          f"({USCITA.stat().st_size / 1e6:.1f} MB, {quante} figure)")


if __name__ == "__main__":
    sys.exit(main())

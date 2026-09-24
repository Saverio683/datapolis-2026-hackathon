"""Esporta i deliverable in `dist/` e impacchetta lo zip da spedire.

Non ricalcola niente: converte quello che le altre pipeline hanno già prodotto.
Va quindi eseguito per ultimo, dopo `relazione_docx`, `policy_docx` e `schede`.

  .docx -> .pdf   LibreOffice headless (lento: qualche minuto per la relazione)
  .pptx -> .pdf   LibreOffice headless, il deck proiettato; nello zip entra solo il PDF
  .html -> .pdf   Chromium o Chrome headless, che rispettano le regole `@page A4`
  .md   -> .pdf   pandoc per l'HTML, poi Chromium (senza LaTeX non c'è via diretta)
  .ipynb -> .html nbconvert, per chi legge il notebook senza avere Jupyter
  zip             dist/datapolis2026_bagheria.zip, con una cartella radice

I notebook restano .ipynb: sono il deliverable tecnico e devono girare, non stamparsi.
"""

import glob
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
FUORI = RADICE / "dist"
PACCHETTO = "datapolis2026_bagheria"

DOCX = ["docs/relazione/RELAZIONE_DATAPOLIS.docx", "docs/policy/POLICY_PONTE_19.docx"]
PAGINE = ["docs/schede/scheda1_profilo.html", "docs/schede/scheda2_genere.html",
          "docs/schede/scheda3_pendolarismo.html", "docs/schede/scheda4_ponte19.html"]
TESTI = [("LEGGIMI_GIURIA.md", "Guida alla lettura - DataPolis 2026")]
NOTEBOOK = ["notebooks/analisi.ipynb", "notebooks/genere.ipynb",
            "notebooks/educazione.ipynb", "notebooks/mobilita.ipynb"]
# Il deck del 2026-09-24 entra come PDF, mai il .pptx. E' la v5: la v4 proiettata con
# quattro slide allineate alla relazione rivista (docs/presentazione/MODIFICHE_PPTX_2026-09-24.md).
DECK = ("docs/presentazione/presentazione_hackaton_v5.pptx", "PRESENTAZIONE_PONTE_19.pdf")

# Nello zip entra solo cio' che serve a leggere e a rifare: il resto del repo (note di
# lavoro, contesto per i membri del team, sorgenti della presentazione) resta fuori. Del
# deck entra solo il PDF, fra i prodotti di dist/.
NEL_PACCHETTO = ("README.md", "LEGGIMI_GIURIA.md", "pyproject.toml", "uv.lock",
                 "data/", "pipeline/", "notebooks/", "viz/", "figures/", "tests/",
                 "docs/README.md", "docs/sources.md", "docs/analisi/educazione/",
                 "docs/concorso/", "docs/relazione/RELAZIONE_DATAPOLIS.md",
                 "docs/policy/POLICY_PONTE_19.md", "docs/team/SCELTE_ANALITICHE.md", "docs/schede/")
# Dentro il perimetro ma fuori dal pacchetto: il generatore del deck sta in pipeline/ e porta
# testi e note delle slide, cioe' la presentazione, che alla giuria non va.
FUORI_PACCHETTO = ("pipeline/presentazione_pptx.py",
                   # La proposta del solo thread educazione (18-24, una finestra) e' superata
                   # dalla policy unificata: nello zip sarebbe una seconda «Ponte 19» diversa.
                   "docs/analisi/educazione/POLICY_PONTE_19_BAGHERIA.md")

A4 = "<style>@page { size: A4; margin: 2cm; } body { font-family: sans-serif; max-width: none; }</style>"


def trova(*nomi, glob_extra=()):
    """Il primo comando disponibile fra i nomi dati: i nomi cambiano da sistema a sistema."""
    for nome in nomi:
        if percorso := shutil.which(nome):
            return percorso
    for schema in glob_extra:
        if trovati := sorted(glob.glob(schema)):
            return trovati[-1]
    sys.exit(f"FALLITO: serve uno fra {', '.join(nomi)} nel PATH")


def esegui(*argomenti):
    esito = subprocess.run([str(a) for a in argomenti], capture_output=True, text=True)
    if esito.returncode:
        sys.exit(f"FALLITO: {argomenti[0]} {argomenti[-1]}\n{esito.stderr[-2000:]}")


def stampa_html(browser, sorgente, uscita):
    # ponytail: Chromium snap legge solo dentro la home, e dist/ ci sta dentro.
    esegui(browser, "--headless", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer", f"--print-to-pdf={uscita}", sorgente)


def impacchetta(prodotti):
    """Lo zip: i file versionati o nuovi del perimetro, piu' i prodotti di dist/."""
    elenco = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                            cwd=RADICE, capture_output=True, text=True, check=True).stdout.split("\n")
    file = sorted(f for f in elenco if f.startswith(NEL_PACCHETTO) and f not in FUORI_PACCHETTO
                  and (RADICE / f).is_file())
    zip_path = FUORI / f"{PACCHETTO}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in file:
            z.write(RADICE / f, f"{PACCHETTO}/{f}")
        for p in prodotti:
            z.write(p, f"{PACCHETTO}/dist/{p.name}")
    return zip_path, len(file) + len(prodotti)


def main():
    FUORI.mkdir(exist_ok=True)
    browser = trova("chromium", "google-chrome", "chromium-browser")
    office = trova("libreoffice", "soffice", glob_extra=("/opt/libreoffice*/program/soffice",))
    attesi = []

    for nome in DOCX:
        print(f"docx -> pdf: {nome} (minuti, non secondi)", flush=True)
        esegui(office, "--headless", "--convert-to", "pdf", "--outdir", FUORI, RADICE / nome)
        attesi.append(FUORI / (Path(nome).stem + ".pdf"))

    sorgente, nome_pdf = DECK
    print(f"pptx -> pdf: {sorgente}", flush=True)
    esegui(office, "--headless", "--convert-to", "pdf", "--outdir", FUORI, RADICE / sorgente)
    (FUORI / (Path(sorgente).stem + ".pdf")).replace(FUORI / nome_pdf)
    attesi.append(FUORI / nome_pdf)

    for nome in PAGINE:
        print(f"html -> pdf: {nome}", flush=True)
        uscita = FUORI / (Path(nome).stem + ".pdf")
        stampa_html(browser, RADICE / nome, uscita)
        attesi.append(uscita)

    for nome, titolo in TESTI:
        print(f"md -> pdf: {nome}", flush=True)
        ponte = FUORI / (Path(nome).stem + ".html")
        stile = FUORI / "a4.html"
        stile.write_text(A4, encoding="utf-8")
        esegui("pandoc", "--standalone", "--metadata", f"pagetitle={titolo}",
               "--metadata", "lang=it", "--include-in-header", stile,
               "-o", ponte, RADICE / nome)
        uscita = FUORI / (Path(nome).stem + ".pdf")
        stampa_html(browser, ponte, uscita)
        ponte.unlink()
        stile.unlink()
        attesi.append(uscita)

    for nome in NOTEBOOK:
        print(f"ipynb -> html: {nome}", flush=True)
        esegui("jupyter", "nbconvert", "--to", "html", "--embed-images",
               "--output-dir", FUORI, RADICE / nome)
        attesi.append(FUORI / (Path(nome).stem + ".html"))

    # Il collaudo: LibreOffice e Chromium possono uscire con 0 senza scrivere niente.
    vuoti = [f for f in attesi if not f.exists() or f.stat().st_size == 0]
    if vuoti:
        sys.exit("FALLITO, file mancanti o vuoti:\n" + "\n".join(f.name for f in vuoti))

    print(f"\n{len(attesi)} file in {FUORI.relative_to(RADICE)}/")
    for f in sorted(attesi):
        print(f"  {f.stat().st_size / 1e6:6.1f} MB  {f.name}")

    zip_path, n = impacchetta(attesi)
    print(f"\nzip: {zip_path.relative_to(RADICE)} ({n} file, {zip_path.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()

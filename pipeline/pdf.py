"""Esporta i deliverable in `dist/`, pronti da zippare e da spedire.

Non ricalcola niente: converte quello che le altre pipeline hanno già prodotto.
Va quindi eseguito per ultimo, dopo `relazione_docx`, `policy_docx` e `schede`.

  .docx -> .pdf   LibreOffice headless (lento: qualche minuto per la relazione)
  .html -> .pdf   Chromium headless, che rispetta le regole `@page A4` delle schede
  .md   -> .pdf   pandoc per l'HTML, poi Chromium (senza LaTeX non c'è via diretta)
  .ipynb -> .html nbconvert, per chi legge il notebook senza avere Jupyter

I notebook restano .ipynb: sono il deliverable tecnico e devono girare, non stamparsi.
"""

import subprocess
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
FUORI = RADICE / "dist"

DOCX = ["docs/RELAZIONE_DATAPOLIS.docx", "docs/POLICY_PONTE_19.docx"]
PAGINE = ["docs/schede/scheda1_profilo.html", "docs/schede/scheda2_genere.html",
          "docs/schede/scheda3_pendolarismo.html", "docs/schede/scheda4_ponte19.html"]
TESTI = ["LEGGIMI_GIURIA.md"]
NOTEBOOK = ["notebooks/analisi.ipynb", "notebooks/genere.ipynb",
            "notebooks/educazione.ipynb", "notebooks/mobilita.ipynb"]


def esegui(*argomenti):
    esito = subprocess.run([str(a) for a in argomenti], capture_output=True, text=True)
    if esito.returncode:
        sys.exit(f"FALLITO: {argomenti[0]} {argomenti[-1]}\n{esito.stderr[-2000:]}")


def stampa_html(sorgente, uscita):
    # ponytail: Chromium snap legge solo dentro la home, e dist/ ci sta dentro.
    esegui("chromium", "--headless", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer", f"--print-to-pdf={uscita}", sorgente)


def main():
    FUORI.mkdir(exist_ok=True)
    attesi = []

    for nome in DOCX:
        print(f"docx -> pdf: {nome} (minuti, non secondi)", flush=True)
        esegui("libreoffice", "--headless", "--convert-to", "pdf", "--outdir", FUORI,
               RADICE / nome)
        attesi.append(FUORI / (Path(nome).stem + ".pdf"))

    for nome in PAGINE:
        print(f"html -> pdf: {nome}", flush=True)
        uscita = FUORI / (Path(nome).stem + ".pdf")
        stampa_html(RADICE / nome, uscita)
        attesi.append(uscita)

    for nome in TESTI:
        print(f"md -> pdf: {nome}", flush=True)
        ponte = FUORI / (Path(nome).stem + ".html")
        esegui("pandoc", "--standalone", "--metadata", f"title={Path(nome).stem}",
               "-o", ponte, RADICE / nome)
        uscita = FUORI / (Path(nome).stem + ".pdf")
        stampa_html(ponte, uscita)
        ponte.unlink()
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


if __name__ == "__main__":
    main()

"""docs/policy/POLICY_PONTE_19.md -> docs/policy/POLICY_PONTE_19.docx, con le figure incorporate.

Gemello di pipeline/relazione_docx.py, da cui prende tutto l'impianto tipografico:
reference.docx ritipografato (Times New Roman, A4, pie' di pagina), ritaglio della
didascalia dai PNG di R, sommario statico. Vale qui la stessa regola: il .docx e' un
artefatto *derivato*, il testo (e quindi ogni cifra) vive nel .md, che sta dentro il
perimetro di pipeline/verifica.py. Qui non si riscrive nulla a mano, si impagina.

Tre cose che questo modulo fa in piu' del gemello, e che non sono ovvie.

1. **Il quadro sinottico non e' nel .md, quindi non e' nemmeno scritto a mano.** Le due
   tabelle che aprono il documento (le cifre della diagnosi sui quattro territori, e la
   sinossi evidenza -> intervento -> target -> KPI richiesta da CLAUDE.md) non esistono
   nel markdown: si compongono qui leggendo `data/processed/` con gli stessi accessi che
   usa `pipeline/verifica.py`. La scelta e' deliberata. Metterle nel .md avrebbe
   significato ribattere a mano venti cifre gia' pinnate altrove; calcolarle qui le lega
   agli stessi CSV che verifica.py confronta con i raw, quindi si muovono con i dati
   invece di divergerne in silenzio.
2. **Niente atlante in appendice.** La relazione porta tutte le figure perche' chiede di
   essere verificata; una proposta di intervento chiede di essere decisa, e le sedici
   figure che incorpora sono quelle su cui poggia una decisione. Le altre restano nella
   relazione, e il documento dice dove.
3. **Gli avvisi diventano parole.** Le dieci cautele del .md sono marcate con un emoji
   che in Times New Roman non esiste e che in un documento istituzionale non ha registro:
   diventano un «Cautela.» in grassetto, che e' quello che l'emoji sta dicendo.

Uso:  uv run python -m pipeline.policy_docx
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pandas as pd

from pipeline.relazione_docx import (
    AUTORI,
    SALTO_PAGINA,
    _didascalie,
    blocco_figura,
    dichiara_png,
    indice,
    inserisci_figure,
    promuovi_titoli,
    reference_docx,
)

RADICE = Path(__file__).resolve().parent.parent
DOCS = RADICE / "docs"
PROCESSED = RADICE / "data" / "processed"
SORGENTE = DOCS / "policy" / "POLICY_PONTE_19.md"
USCITA = DOCS / "policy" / "POLICY_PONTE_19.docx"
# Il conteggio dei controlli non si ribatte: si legge dalla relazione, che e' il documento
# che lo dichiara e che verifica.py tiene allineato.
RELAZIONE = DOCS / "relazione" / "RELAZIONE_DATAPOLIS.md"

# ------------------------------------------------------------------ dove va ogni figura
# (frammento ancora nel .md, nome della figura). Il frammento deve comparire una volta
# sola: se il testo cambia, la build si ferma invece di piazzare la figura altrove.
#
# Le ancore sono quasi tutte le righe «-> file.csv» con cui il .md chiude ogni evidenza:
# la figura atterra dove il documento stesso dichiara la propria fonte, quindi il
# posizionamento segue il testo invece di essere una scelta editoriale a parte.
INLINE: list[tuple[str, str]] = [
    # 1. L'evidenza che motiva l'intervento
    ("→ `edu_youth_states_2018_2024.csv`, `edu_kpi_dashboard.csv`", "edu_fig03_composizione"),
    ("`genere_quadro_sintesi.csv`, `genere_forbice_serie.csv`, `genere_posizionamento.csv`",
     "fig05_forbice"),
    ("smettono quando il motivo diventa il lavoro.\n→ `genere_pendolarismo.csv`",
     "fig12_pendolarismo"),
    ("→ `genere_coorti.csv`, `genere_ritenzione_decennale.csv`", "fig03_coorti"),
    # 3. Target, quote e capacita'
    # L'a-capo fa parte dell'ancora: senza, il frammento ricompare dentro la riga di fonti
    # della sezione 4-bis e la figura finirebbe a meta' di quell'elenco.
    ("→ `genere_composizione_stato_dettaglio.csv`\n", "fig02_composizione_stato"),
    # 4E. Componente mobilita'
    ("→ `mob_taglia_distanza.csv`, `mob_treno_390.csv`, `mob_sintesi.csv`, mob_fig03, mob_fig04",
     "mob_fig04_taglia_distanza"),
    # 4-bis. Rotta F, un anello per componente
    ("→ `genere_casalinghe.csv`, `genere_casalinghe_bounds.csv`, `genere_stato_civile.csv`, fig02b",
     "fig02b_casalinghe_territori"),
    ("→ `mob_ribaltamento_territori.csv`, sezione 4 di `notebooks/mobilita.ipynb`, mob_fig02",
     "mob_fig02_ribaltamento"),
    ("`genere_pari_lenti.csv`, `genere_posizionamento.csv`, fig05, fig08",
     "fig08_posizionamento"),
    ("→ `genere_forbice_serie.csv`, `genere_nuvola_390.csv`, `edu_kpi_dashboard.csv`, fig05b, fig06",
     "fig05b_forbice_serie"),
    ("`notebooks/mobilita.ipynb`, mob_fig03", "mob_fig03_treno_genere"),
    ("→ `genere_composizione_stato_dettaglio.csv`, `genere_ritenzione_eta.csv`",
     "fig07_ritenzione_eta"),
    ("→ `genere_mde.csv`, fig09b", "fig09b_potenza"),
    ("→ `genere_platea.csv`, fig09", "fig09_kpi_finestra"),
    # 6. KPI
    ("→ `mob_flussi_bagheria.csv`, `mob_sintesi.csv`, mob_fig01", "mob_fig01_verso_palermo"),
    # 7. Valutazione dell'impatto
    ("→ `genere_pretrend.csv`, `genere_pretrend_390.csv`, `genere_gemelle.csv`", "edu_fig07_pari_2011"),
]

# Il triangolo di avviso non esiste in Times New Roman e non ha il registro di un
# documento che va in commissione. Prima la variante seguita da grassetto, poi la secca:
# invertirle lascerebbe «**Cautela.** **...**» irraggiungibile.
SOSTITUZIONI = [
    ("⚠️ **", "**Cautela.** **"),
    ("⚠️ ", "**Cautela.** "),
]


# --------------------------------------------------------------- cifre dai CSV
def ita(x, d=1) -> str:
    """Numero come lo scrivono i documenti: 1.121 - 8,2 - 19,0.

    Identica a quella di pipeline/verifica.py, e deve restarlo: e' la formattazione su
    cui quel file confronta le frasi del .md.
    """
    return f"{x:,.{d}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def _csv(nome: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / nome)


TERRITORI = ("Bagheria", "Palermo", "Sicilia", "Italia")


def riga_larghezze(pesi: list[int], destra=()) -> str:
    """La riga di trattini di una tabella pipe, dosata colonna per colonna.

    Pandoc non misura il contenuto: le larghezze delle colonne le prende *da qui*, in
    proporzione ai trattini che separano le intestazioni dal corpo. Lasciate tutte uguali
    (`|---|---|`) danno cinque colonne identiche, e la colonna delle etichette va a capo
    quattro volte mentre quelle dei numeri restano mezze vuote. `pesi` e' quindi la
    ripartizione percentuale dello specchio, non un dettaglio di sintassi.
    """
    celle = []
    for i, p in enumerate(pesi):
        celle.append("-" * (p - 1) + ":" if i in destra else "-" * p)
    return "|" + "|".join(celle) + "|"


def tabella_diagnosi() -> str:
    """Le cifre della diagnosi sui quattro territori di confronto.

    Righe scelte per essere la versione compatta della sezione 1 e della sezione 4-bis:
    chi resta fuori, chi si e' istruito, chi lavora, chi si sposta. Ogni riga e' una
    colonna di un CSV di data/processed/, mai una media ricalcolata qui.
    """
    stati = _csv("edu_youth_states_2018_2024.csv")
    quadro = _csv("genere_quadro_sintesi.csv").set_index("nome_territorio")
    casa = _csv("genere_casalinghe.csv")
    pend = _csv("genere_pendolarismo.csv")

    def st(terr, col, anno=2024):
        r = stati[stati["territorio_nome"].eq(terr) & stati["anno"].eq(anno)]
        return float(r[col].iloc[0])

    def cas(terr, anno=2024):
        r = casa[casa["nome_territorio"].eq(terr) & casa["anno"].eq(anno)
                 & casa["genere"].eq("F")]
        return float(r["casalinghe_o_i_%"].iloc[0])

    def pe(terr, motivo, col, anno=2019):
        r = pend[pend["nome_territorio"].eq(terr) & pend["motivo"].eq(motivo)
                 & pend["anno"].eq(anno)]
        return float(r[col].iloc[0])

    righe = [
        ("Giovani 15-24 fuori da lavoro e studio",
         lambda t: f"{ita(st(t, 'quota_fuori_lavoro_studio'))}%"),
        ("di cui inattivi, cioè che non cercano",
         lambda t: f"{ita(st(t, 'inattivi_su_fuori'))}%"),
        ("Inattivi non studenti 15-24, in persone",
         lambda t: ita(st(t, "inattivi_non_studenti"), 0)),
        ("Tasso di occupazione femminile 15-24",
         lambda t: f"{ita(quadro.at[t, 'occupazione F'])}%"),
        ("Tasso di occupazione maschile 15-24",
         lambda t: f"{ita(quadro.at[t, 'occupazione M'])}%"),
        ("Divario di occupazione (M − F)",
         lambda t: f"{ita(quadro.at[t, 'gap occupazione (M-F)'])} pp"),
        ("Almeno il diploma, femmine 15-24",
         lambda t: f"{ita(quadro.at[t, 'almeno diploma F'])}%"),
        ("Vantaggio educativo femminile (F − M)",
         lambda t: f"+{ita(-quadro.at[t, 'gap istruzione (M-F)'])} pp"),
        ("Casalinghe su tutte le 15-24", lambda t: f"{ita(cas(t))}%"),
        ("Esce dal comune per lavoro: divario (M − F)",
         lambda t: f"{ita(pe(t, 'WK', 'gap_M_meno_F'))} pp"),
        ("Esce dal comune per studio: divario (M − F)",
         lambda t: f"{ita(pe(t, 'STD', 'gap_M_meno_F'))} pp"),
    ]

    fuori = ["| Misura | " + " | ".join(f"**{t}**" if t == "Bagheria" else t
                                        for t in TERRITORI) + " |",
             riga_larghezze([38, 15, 15, 15, 15], destra=range(1, 5))]
    for etichetta, valore in righe:
        # I quattro territori portano solo numeri, quindi qui un trattino e' sempre un
        # segno: si scrive col meno tipografico, come fa il resto dei documenti.
        celle = [valore(t).replace("-", "−") for t in TERRITORI]
        celle[0] = f"**{celle[0]}**"
        fuori.append(f"| {etichetta} | " + " | ".join(celle) + " |")
    return "\n".join(fuori)


def tabella_sinossi() -> str:
    """Evidenza -> intervento -> target -> KPI, la forma richiesta da CLAUDE.md.

    Le celle sono prosa, ma ogni cifra che contengono si legge qui dai CSV: la sinossi
    non e' una riscrittura del documento, e' il documento proiettato su quattro colonne.
    """
    stati = _csv("edu_youth_states_2018_2024.csv")
    quadro = _csv("genere_quadro_sintesi.csv").set_index("nome_territorio")
    comp = _csv("genere_composizione_stato_dettaglio.csv")
    casa = _csv("genere_casalinghe.csv")
    civ = _csv("genere_stato_civile.csv")
    pend = _csv("genere_pendolarismo.csv")
    mezzo = _csv("mob_mezzo_genere.csv")
    platea = _csv("genere_platea.csv")
    mde = _csv("genere_mde.csv")
    posiz = _csv("genere_posizionamento.csv").set_index("indicatore")
    quad = _csv("genere_forbice_quadrante.csv")
    vant_15_24 = float(quad[quad["nome_territorio"].eq("Bagheria")
                            & quad["anno"].eq(2024)]["vantaggio_diploma_15_24_pp"].iloc[0])

    def st(col, terr="Bagheria", anno=2024):
        r = stati[stati["territorio_nome"].eq(terr) & stati["anno"].eq(anno)]
        return float(r[col].iloc[0])

    def cp(gen, stato, anno=2024):
        r = comp[comp["nome_territorio"].eq("Bagheria") & comp["anno"].eq(anno)
                 & comp["genere"].eq(gen) & comp["stato"].eq(stato)]
        return float(r["persone"].iloc[0])

    def fuori_f(anno=2024):
        r = comp[comp["nome_territorio"].eq("Bagheria") & comp["anno"].eq(anno)
                 & comp["genere"].eq("F")
                 & comp["destinazione"].eq("fuori e non in cerca")]
        return float(r["persone"].sum())

    def pe(terr, motivo, col, anno=2019):
        r = pend[pend["nome_territorio"].eq(terr) & pend["motivo"].eq(motivo)
                 & pend["anno"].eq(anno)]
        return float(r[col].iloc[0])

    def mz(gen, classe):
        r = mezzo[mezzo["genere"].eq(gen) & mezzo["classe"].eq(classe)]
        return float(r["quota"].iloc[0])

    def pl(gen, col):
        r = platea[platea["nome_territorio"].eq("Bagheria") & platea["genere"].eq(gen)]
        return float(r[col].iloc[0])

    def md(kpi, anni, col):
        r = mde[mde["KPI"].str.startswith(kpi) & mde["anni pooled per lato"].eq(anni)]
        return float(r[col].iloc[0])

    def cas(terr, anno=2024):
        r = casa[casa["nome_territorio"].eq(terr) & casa["anno"].eq(anno)
                 & casa["genere"].eq("F")]
        return float(r["casalinghe_o_i_%"].iloc[0])

    # L'ultimo anno del registro, non il 2024: lo stato civile e' una fonte diversa dal
    # censimento permanente e arriva piu' avanti, come dichiara il .md («al 1.1.2025»).
    civ_b = civ[civ["nome_territorio"].eq("Bagheria") & civ["genere"].eq("F")
                & civ["fascia"].eq("15-24")]
    coniugate = civ_b[civ_b["anno"].eq(civ_b["anno"].max())]
    q_coniugate = float(coniugate["quota_gia_coniugate_pct"].iloc[0])
    n_coniugate = float(coniugate["gia_coniugate"].iloc[0])
    # Posizione di Bagheria fra i comuni ugualmente scolarizzati: il CSV conta quanti
    # stanno sotto, la posizione e' il complemento.
    n_pari = int(posiz.at["L11", "n_istruiti"]) + 1          # i pari piu' Bagheria
    pos_pari = n_pari - int(posiz.at["L11", "istruiti_sotto"])

    inattivi = ita(st("inattivi_non_studenti"), 0)
    righe = [
        ("§1",
         f"Il {ita(st('quota_inattivi_non_studenti'))}% dei 15-24enni è inattivo non "
         f"studente ({inattivi} persone) e il {ita(st('inattivi_su_fuori'))}% di chi è "
         f"fuori da lavoro e studio non cerca.",
         "Outreach attivo verso chi non cerca, al posto dello sportello a domanda "
         "(sezione 4B).",
         f"200 presi in carico nel primo anno, il "
         f"{ita(100 * 200 / st('inattivi_non_studenti'), 0)}% dei {inattivi}.",
         "Quota che avvia l'azione concordata entro 30 giorni; giorni medi consecutivi "
         "fuori da lavoro, studio e formazione."),
        ("§1",
         "Le uscite hanno due tempi: i ragazzi si assottigliano a 17-19 e 23-24 con "
         "rientri dopo i 26, le ragazze si perdono dai 24-25 in poi senza rientri.",
         "Due finestre di ingaggio invece di una soglia unica (sezione 3).",
         "Residenti 18-20 all'uscita dalla secondaria e 22-25 fuori da lavoro e studio.",
         "Copertura delle due finestre misurata separatamente, mai in aggregato."),
        ("§1, §4-bis",
         f"A pari istruzione il lavoro non arriva: le ragazze 15-24 superano i coetanei "
         f"di {ita(vant_15_24)} punti sul diploma e hanno un tasso di occupazione pari a "
         f"{ita(quadro.at['Bagheria', 'occupazione F'])}%; nel 2011 Bagheria era "
         f"{pos_pari}ª su {n_pari} per occupazione femminile fra i comuni ugualmente "
         f"scolarizzati.",
         "Quota di genere sui presi in carico e modulo dedicato, la Rotta F "
         "(sezioni 3 e 4-bis).",
         f"Minimo 50% donne, cioè 100 nel primo anno sulle {ita(fuori_f(), 0)} fuori da "
         f"lavoro e studio.",
         f"Tasso di occupazione F 15-24 da "
         f"{ita(md('tasso di occupazione', 3, 'attuale (%)'))}% a "
         f"{ita(md('tasso di occupazione', 3, 'obiettivo (%)'))}%, letto sul triennio "
         f"pooled come direzione della convergenza (potenza "
         f"{ita(md('tasso di occupazione', 3, 'potenza osservata (%)'), 0)}% contro la "
         f"variabilità dei comuni simili)."),
        ("§4-bis, F1",
         f"{ita(cp('F', 'casalinghe/i'), 0)} ragazze fra i 15 e i 24 anni si dichiarano "
         f"casalinghe, il {ita(cas('Bagheria'))}% della fascia (Palermo: "
         f"{ita(cas('Palermo'))}%), e le già coniugate sono "
         f"{ita(n_coniugate, 0)} ({ita(q_coniugate)}%): il matrimonio precoce non spiega "
         f"il fenomeno.",
         "Contatto attraverso i luoghi che quella popolazione già la vedono, non "
         "attraverso una lista: sedi secondarie, servizi sociali, consultori, "
         "associazioni.",
         f"Le {ita(cp('F', 'casalinghe/i'), 0)} per etichetta censuaria, mai per nome: il "
         f"dato è aggregato e nessun elenco nominativo esiste o va costruito.",
         f"Quota casalinghe F 15-24 da "
         f"{ita(md('quota casalinghe', 2, 'attuale (%)'))}% a "
         f"{ita(md('quota casalinghe', 2, 'obiettivo (%)'))}%, leggibile già sul biennio "
         f"(potenza {ita(md('quota casalinghe', 2, 'potenza osservata (%)'), 0)}% contro la "
         f"variabilità dei comuni simili)."),
        ("§4-bis, F2",
         f"Fra chi già si sposta per lavoro esce dal comune il "
         f"{ita(pe('Bagheria', 'WK', 'quota_M'))}% degli uomini e il "
         f"{ita(pe('Bagheria', 'WK', 'quota_F'))}% delle donne (2019); fra chi esce dal "
         f"comune il treno vale il {ita(mz('F', 'di cui: treno'))}% degli spostamenti "
         f"femminili contro il {ita(mz('M', 'di cui: treno'))}% di quelli maschili (2011).",
         "Nessuna opportunità entra nel piano di transizione senza verifica di "
         "raggiungibilità col mezzo collettivo negli orari reali della posizione. È un "
         "filtro di istruttoria, non un capitolo di spesa.",
         "Tutte le prese in carico con un'opportunità fuori comune.",
         f"Partecipanti F con un'opportunità fuori comune entro 6 mesi, da "
         f"{ita(pe('Bagheria', 'WK', 'quota_F'))}% a "
         f"{ita(pe('Bagheria', 'WK', 'quota_M'))}%, misurato sul dato di servizio."),
        ("§4-bis, F3",
         "La domanda non arriva a chi il titolo ce l'ha, e il Comune ha già in mano uno "
         "strumento amministrativo per renderla verificabile.",
         "Criteri premiali di pari opportunità nelle gare e nelle concessioni comunali, "
         "sul modello dell'art. 47 del DL 77/2021. Premialità, non riserva.",
         "Fornitori e concessionari del Comune, senza tetto di platea.",
         "Procedure con criterio premiale attivo, e assunzioni di donne 22-25 residenti "
         "verificate a 6 e 12 mesi."),
        ("§6",
         f"La platea femminile 15-24 è già nata e cala da "
         f"{ita(pl('F', 'platea_2024'), 0)} (2024) a {ita(pl('F', 'platea_2034'), 0)} "
         f"(2034), −{ita(abs(pl('F', 'var_2034_pct')))}%, mentre quella maschile perde il "
         f"{ita(abs(pl('M', 'var_2034_pct')))}%.",
         "KPI scritti in tasso e non in teste, con la finestra di lettura dichiarata "
         "prima dell'avvio (sezione 6).",
         "Nessun target aggiuntivo: è un vincolo su come si scrivono tutti gli altri.",
         "Target riparametrato ogni anno come tasso obiettivo × platea dell'anno, con la "
         "formula pubblicata."),
    ]

    fuori = ["| Evidenza | Intervento | Target | KPI misurabile |",
             riga_larghezze([30, 24, 20, 26])]
    for sez, evid, interv, target, kpi in righe:
        fuori.append(f"| *({sez})* {evid} | {interv} | {target} | {kpi} |")
    return "\n".join(fuori)


def sinossi() -> str:
    """La sezione che apre il documento: due tabelle, nessuna cifra trascritta."""
    stati = _csv("edu_youth_states_2018_2024.csv")
    quadro = _csv("genere_quadro_sintesi.csv").set_index("nome_territorio")

    def st(col, anno):
        r = stati[stati["territorio_nome"].eq("Bagheria") & stati["anno"].eq(anno)]
        return float(r[col].iloc[0])

    # Dal 2021 in poi: fra 2019 e 2021 cambia la misura della condizione «in cerca», e
    # un confronto 2018-2024 delle componenti leggerebbe la rottura come un fatto.
    quad = _csv("genere_forbice_quadrante.csv")
    vant_15_24 = float(quad[quad["nome_territorio"].eq("Bagheria")
                            & quad["anno"].eq(2024)]["vantaggio_diploma_15_24_pp"].iloc[0])

    return f"""# Il quadro in sintesi

> **A Bagheria il diploma arriva, il lavoro no. E chi resta fuori non è chi cerca lavoro.**
> Nel 2024 il {ita(st('inattivi_su_fuori', 2024))}% dei 15-24enni fuori da lavoro e studio
> non cerca nemmeno; a definizione costante, fra il 2021 e il 2024, la quota di chi cerca
> scende da {ita(st('quota_in_cerca', 2021))}% a {ita(st('quota_in_cerca', 2024))}% mentre
> quella degli inattivi non studenti resta ferma
> ({ita(st('quota_inattivi_non_studenti', 2021))}% → {ita(st('quota_inattivi_non_studenti', 2024))}%).
> Le ragazze 15-24 hanno il diploma {ita(vant_15_24)} punti più spesso dei coetanei e
> lavorano la metà: {ita(quadro.at['Bagheria', 'occupazione F'])}% contro
> {ita(quadro.at['Bagheria', 'occupazione M'])}%. Un servizio a domanda spontanea
> raggiungerebbe chi già cerca, non il segmento che non si muove.

**Ponte 19** è la risposta che questa proposta argomenta: un servizio comunale di
transizione e riattivazione con due finestre di ingaggio, un target esplicito sul genere e
obiettivi scritti in tasso, non in teste. Le due tabelle che seguono sono la proposta in
forma compatta; le sezioni che seguono la argomentano una evidenza alla volta, e ogni
cifra rimanda al file di `data/processed/` che la produce.

## Le cifre della diagnosi

{tabella_diagnosi()}

::: {{custom-style="Didascalia"}}
**Cosa mostra:** i quattro territori di confronto sulle undici misure che motivano
l'intervento. Fascia 15-24, anno 2024, tranne il pendolarismo, che il censimento
permanente scompone per genere solo fino al 2019. Il divario di pendolarismo è calcolato
su chi già si sposta, quindi non è un riflesso del divario occupazionale. La tabella non
dice come Bagheria si collochi fra comuni simili: lo dicono le figure delle sezioni 1 e
4-bis, che confrontano con due gruppi di comuni pari dichiarati.

**Come si legge:** in grassetto la colonna di Bagheria. Un divario positivo significa
valore maschile più alto. Sul pendolarismo per lavoro Bagheria ha il divario più ampio dei
quattro territori, circa il doppio di Sicilia e Italia; sul pendolarismo per studio il
segno si inverte ovunque a favore delle ragazze, e a Bagheria più che altrove. Il vantaggio educativo è riportato col segno già ribaltato (F − M), perché è
positivo ovunque e leggerlo al negativo sarebbe una trappola.

**Fonte:** ISTAT, censimento permanente della popolazione e delle abitazioni, 2018-2024.
Rigenerata da `edu_youth_states_2018_2024.csv`, `genere_quadro_sintesi.csv`,
`genere_casalinghe.csv` e `genere_pendolarismo.csv`.
:::

## Dall'evidenza all'intervento

Ogni riga segue la forma che il progetto si è dato: un'evidenza quantitativa, l'intervento
che ne discende, il target su cui agisce, il KPI con cui si misura. Un'evidenza che non
porta a un intervento derivabile resta nell'analisi e non entra qui.

{tabella_sinossi()}

::: {{custom-style="Didascalia"}}
**Cosa mostra:** le sette catene evidenza, intervento, target e KPI su cui poggia la
proposta, con il rimando alla sezione che le argomenta. Non mostra la dotazione né il
cronoprogramma di attuazione, che stanno nelle sezioni 3 e 4, e non mostra le condizioni
che possono fermare una componente, che stanno nel decision gate della sezione 5.

**Come si legge:** la colonna KPI distingue gli obiettivi di popolazione, che si leggono su
biennio o triennio, dagli indicatori di processo, che si leggono ogni anno. La distinzione
non è una cautela di stile: il delta da rilevare sta sotto il minimo rilevabile su un anno
solo, e dichiararlo prima dell'avvio è parte della proposta.

**Fonte:** ISTAT, censimento permanente e matrice del pendolarismo; registro della
popolazione residente per lo stato civile. Rigenerata dai CSV citati sezione per sezione
nel testo che segue.
:::
"""


# ------------------------------------------------------------------- copertina
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
Bagheria, {data}

&nbsp;

Proposta di intervento data-driven

Ogni evidenza porta un intervento, un target e un KPI con la sua finestra di lettura

&nbsp;

{quante} figure · {controlli} controlli di regressione indipendenti, tutti superati

&nbsp;
:::

::: {{custom-style="Didascalia"}}
Nessuna cifra di questo documento è scritta a mano, comprese quelle delle due tabelle di
sintesi che aprono il testo. Ogni numero è prodotto da una cella di notebook o da un file
di `data/processed/`, e il pin di regressione `pipeline/verifica.py` lo ricalcola dai dati
grezzi con un'implementazione indipendente, verificando poi che la frase di questa
proposta lo riporti alla lettera. L'analisi che la sostiene, con l'atlante completo delle
figure e la ricostruzione metodologica, sta in `dist/RELAZIONE_DATAPOLIS.pdf`. Il documento
si rigenera da zero, nel repository che ne ha il sorgente, con `uv run python -m pipeline.policy_docx`.
:::
"""


def celle_a_bandiera(rif: Path) -> None:
    """Nelle celle di tabella il testo va a bandiera, non giustificato.

    Il corpo del documento e' giustificato, e nelle tabelle lo stile `Compact` di pandoc
    eredita quella scelta da `BodyText`. In una colonna larga quattro centimetri il
    giustificato apre fiumi bianchi larghi mezza parola, e la sinossi ha quattro colonne
    di prosa: e' lo stesso testo, ma illeggibile. Si sovrascrive `Compact`, che pandoc usa
    solo nelle celle e negli elenchi fitti, cosi' il corpo resta giustificato com'e'.

    `w:jc` va dopo `w:spacing`: l'ordine dei figli di `w:pPr` e' imposto dallo schema, e
    invertirlo produce un file che Word rifiuta di aprire.
    """
    marca = '<w:spacing w:before="36" w:after="36" />'
    with zipfile.ZipFile(rif) as z:
        parti = {n: z.read(n) for n in z.namelist()}
    stili = parti["word/styles.xml"].decode("utf-8")
    assert stili.count(marca) == 1, "stile Compact inatteso nel reference.docx di pandoc"
    parti["word/styles.xml"] = stili.replace(
        marca, marca + '<w:jc w:val="left" />', 1).encode("utf-8")
    with zipfile.ZipFile(rif, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, dati in parti.items():
            z.writestr(nome, dati)


def markdown(dest: Path) -> tuple[str, int]:
    testo = SORGENTE.read_text(encoding="utf-8")
    dida = _didascalie()

    # La testata del .md diventa la copertina e sparisce dal flusso.
    righe = testo.split("\n")
    assert righe[0].startswith("# ") and righe[2].startswith("## "), "testata inattesa"
    titolo = righe[0].lstrip("# ").strip()
    sottotitolo = righe[2].lstrip("# ").strip()
    data = re.search(r"versione rivista del (\d{4}-\d{2}-\d{2})", righe[4]).group(1)
    testo = "\n".join(righe[4:])

    testo, numero = inserisci_figure(testo, INLINE, dida, dest)

    for vecchio, nuovo in SOSTITUZIONI:
        testo = testo.replace(vecchio, nuovo)
    assert "⚠️" not in testo, "avviso non sostituito: la forma nel .md è cambiata"
    testo = promuovi_titoli(testo)
    testo = sinossi() + SALTO_PAGINA + testo

    controlli = re.search(r"\*\*(\d+)/\1 PASS\*\*", RELAZIONE.read_text(encoding="utf-8"))
    assert controlli, f"in {RELAZIONE.name} non si trova il conteggio dei controlli"

    testa = COPERTINA.format(titolo=titolo, sottotitolo=sottotitolo, data=data,
                             autori=" · ".join(AUTORI),
                             quante=numero, controlli=controlli.group(1))
    return testa + SALTO_PAGINA + indice(testo) + SALTO_PAGINA + testo, numero


def main() -> None:
    dest = RADICE / ".policy-docx-build"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir()
    try:
        rif = reference_docx(dest)
        celle_a_bandiera(rif)
        testo, quante = markdown(dest)
        sorgente = dest / "policy.md"
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

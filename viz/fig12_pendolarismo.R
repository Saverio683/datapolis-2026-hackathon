# Figura 12 - il pendolarismo per genere: la direzione dello scarto cambia col motivo.
# Il punto: le ragazze di Bagheria si spostano per studiare, non per lavorare, e in
# entrambe le direzioni lo scarto è il più ampio del panel.
#
# Terza fonte del thread sullo stesso punto di rottura, e l'unica sulla mobilità. Il
# denominatore è già condizionato al motivo (chi si sposta per lavoro un lavoro ce l'ha),
# quindi non è un riflesso del divario occupazionale di fig01/fig05: è una misura
# indipendente. Vincoli della fonte in caption e in docs/sources.md §11.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 24   # stessa misura del salvataggio: su questa il testo va a capo

ANNO <- 2019          # ultimo disponibile; il 2018 fa da controllo, citato nel sottotitolo
ANNO_CONTROLLO <- 2018

pend <- read_csv(file.path(PROCESSED, "genere_pendolarismo.csv"), show_col_types = FALSE)
mob <- read_csv(file.path(PROCESSED, "genere_mobilita_2011.csv"), show_col_types = FALSE)

# I titoli dei pannelli dicono il verso: senza, i due scarti sono due lunghezze senza segno
# e il lettore deve dedurre la direzione dall'ordine dei colori.
ETICHETTE_MOTIVO <- c(
  WK  = "PER LAVORO: esce dal comune più chi è maschio",
  STD = "PER STUDIO: esce dal comune più chi è femmina"
)

dati <- pend |>
  filter(anno == ANNO) |>
  mutate(
    nome_territorio = factor(nome_territorio, levels = rev(ORDINE)),
    motivo = factor(motivo, levels = names(ETICHETTE_MOTIVO), labels = ETICHETTE_MOTIVO),
    scarto = abs(gap_M_meno_F),
    meta = (quota_F + quota_M) / 2,
    soggetto = nome_territorio == "Bagheria",
    # La freccia si ferma prima del pallino: disegnata fino al valore, la punta finirebbe
    # sotto il punto che viene dopo e il verso - che è tutto il finding - sparirebbe.
    # L'arretramento è una FRAZIONE dello scarto, non un valore fisso: con un fisso, ogni
    # scarto più corto dell'arretramento produceva una freccia rivolta dalla parte
    # sbagliata (Palermo sullo studio, 0,1 punti, puntava a sinistra pur avendo F > M).
    fine = quota_F - sign(quota_F - quota_M) * pmin(1.2, scarto * 0.35)
  )

# Diametri diversi e femmine disegnate per prime: dove i due valori quasi coincidono
# (Palermo sullo studio, 0,6 contro 0,7) si vede un anello rosa attorno al punto blu
# invece di un pallino solo, che passerebbe per un dato mancante. Stesso idioma di fig03.
punti <- dati |>
  pivot_longer(c(quota_M, quota_F), names_to = "genere", values_to = "quota") |>
  mutate(genere = sub("^quota_", "", genere)) |>
  arrange(genere)

# Valori per il testo: si leggono dalla tabella, non si scrivono a mano.
scarto_di <- function(territorio, mot, an = ANNO) {
  abs(pend$gap_M_meno_F[pend$nome_territorio == territorio &
                        pend$motivo == mot & pend$anno == an])
}
percentile_m2 <- mob$percentile_390[mob$indicatore == "M2"]

figura <- ggplot(dati, aes(y = nome_territorio)) +
  geom_segment(aes(x = quota_M, xend = fine, yend = nome_territorio, colour = soggetto),
               linewidth = 1.2, arrow = arrow(length = unit(0.18, "cm"), type = "closed")) +
  geom_point(data = punti, aes(x = quota, fill = genere, size = genere),
             shape = 21, colour = "white", stroke = 0.8) +
  geom_text(aes(x = meta, label = virgola(scarto, 1, " punti"), colour = soggetto,
                fontface = ifelse(soggetto, "bold", "plain")),
            vjust = -1.5, size = 3.0, show.legend = FALSE) +
  facet_wrap(~motivo, ncol = 1) +
  scale_fill_manual(values = COLORI_GENERE, labels = ETICHETTE_GENERE) +
  scale_size_manual(values = c(F = 4.3, M = 2.8), guide = "none") +
  scale_colour_manual(values = c(`TRUE` = COLORI_TERRITORIO[["Bagheria"]], `FALSE` = "grey65"),
                      guide = "none") +
  scale_y_discrete(expand = expansion(add = c(0.55, 1.0))) +
  scale_x_continuous(labels = function(x) virgola(x, 0, "%"),
                     expand = expansion(mult = c(0.06, 0.08))) +
  labs(
    title = "Le ragazze di Bagheria si spostano per studiare, non per lavorare",
    subtitle = sommario(paste0(
      "Quota di residenti che esce dal comune, in percentuale di chi si sposta ogni giorno per quel motivo, per genere e per motivo dello spostamento, ", ANNO,
      ", su quattro territori: il pannello di sopra riguarda gli spostamenti per lavoro, quello di sotto gli spostamenti per studio.",
      " Il verso dello scarto cambia col motivo in tutti i territori: la particolarità di Bagheria è l'ampiezza, la maggiore del panel in entrambi i pannelli",
      ".\n", virgola(scarto_di("Bagheria", "WK"), 1), " punti sul lavoro, il doppio della Sicilia (",
      virgola(scarto_di("Sicilia", "WK"), 1), "), e ", virgola(scarto_di("Bagheria", "STD"), 1),
      " sullo studio contro ", virgola(scarto_di("Sicilia", "STD"), 1), ".",
      "\nIl denominatore è già condizionato al motivo: chi si sposta per lavoro un lavoro ce l'ha. Lo scarto è quindi",
      " una\nmisura indipendente sullo stesso passaggio, e sta in piedi da sola accanto al divario occupazionale di fig01 e fig05. Stabile sul ",
      ANNO_CONTROLLO, ": ", virgola(scarto_di("Bagheria", "WK", ANNO_CONTROLLO), 1, taglia_zero = FALSE),
      " e ", virgola(scarto_di("Bagheria", "STD", ANNO_CONTROLLO), 1, taglia_zero = FALSE), " punti."
    ), LARGHEZZA),
    x = "residenti che escono dal comune, in % di chi si sposta per quel motivo", y = NULL,
    caption = didascalia_2b(
      lettura = paste0(
        "ogni riga è un territorio. Il pallino grande rosa è il valore femminile, quello piccolo blu il maschile: i diametri sono diversi apposta, così dove i due valori quasi coincidono si vede un anello e non un pallino solo. ",
        "La freccia parte dal valore maschile e punta verso quello femminile, quindi il suo verso è la direzione dello scarto; si ferma prima del pallino di arrivo perché una punta sotto il pallino nasconderebbe proprio il verso. ",
        "La cifra sopra la freccia è l'ampiezza dello scarto in punti percentuali, in valore assoluto. ",
        "Bagheria è in vermiglio, gli altri territori in grigio. ",
        "Palermo compare con valori bassissimi perché è un comune grande e quasi tutti gli spostamenti restano dentro il suo confine: su questa misura va letta come artefatto della geografia, non come un dato sui palermitani. ",
        "La serie esiste solo per il ", ANNO_CONTROLLO, " e il ", ANNO,
        ", quindi resta separata dal 2021-2024 delle altre figure del thread; il ", ANNO_CONTROLLO,
        " serve da controllo di stabilità, citato nel sottotitolo e non disegnato."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola del pendolarismo, ", ANNO_CONTROLLO, "-", ANNO,
        ". La destinazione è «fuori comune» aggregata e la fonte non identifica il comune di arrivo: questa figura non misura il pendolarismo verso Palermo, che è invece l'oggetto di mob_fig01 su un'altra fonte. ",
        "Contesto al 2011 (8milaCensus, 390 comuni siciliani): Bagheria sta al ", virgola(percentile_m2, 0),
        "° percentile per mobilità fuori comune (indicatore M2), cioè si esce poco in assoluto; mob_fig04 mostra che quel percentile è un effetto della taglia del comune. ",
        "Elaborazione: notebooks/genere.ipynb (data/processed/genere_pendolarismo.csv e genere_mobilita_2011.csv)."),
      larghezza = LARGHEZZA)
  )

figura <- figura + tema_figura()

salva(figura, "fig12_pendolarismo", larghezza = LARGHEZZA, altezza = 21)

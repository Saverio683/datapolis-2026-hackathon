# Figura 5 — la forbice: vantaggio educativo femminile contro conversione in lavoro,
# più la striscia che dice quanto regge nel tempo.
# L'occupazione è in rapporto M/F, non in punti: in punti il gap locale non è un'anomalia
# (LPM nel notebook), la scala che distingue Bagheria è quella relativa.
# La riga in basso esiste perché la fotografia dell'ultimo anno da sola inganna: delle due
# classifiche che la figura racconta una regge su tutte le annate (il livello femminile,
# minimo del panel ogni anno) e una no (il rapporto, dove nel 2022 e nel 2023 Bagheria non
# è la peggiore del gruppo locale). Mostrarle entrambe è ciò che rende il claim difendibile.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# Una sola tabella per i tre pannelli: la fotografia è l'ultimo anno della serie, così i
# due blocchi non possono raccontare numeri diversi. Il notebook lo verifica con un assert
# contro genere_forbice.csv, che resta come tavola esportata.
serie <- read_csv(file.path(PROCESSED, "genere_forbice_serie.csv"),
                  col_types = cols(territorio = "c", nome_territorio = "c", .default = "d"))

ETICHETTA_VICINATO <- grep("^vicinato", unique(serie$nome_territorio), value = TRUE)
stopifnot(length(ETICHETTA_VICINATO) == 1)
COLORI <- c(COLORI_TERRITORIO, setNames(COLORE_VICINATO, ETICHETTA_VICINATO))
LIVELLI <- c("Bagheria", ETICHETTA_VICINATO, "Palermo", "Sicilia", "Italia")
ANNO <- max(serie$anno)
PRIMO <- min(serie$anno)

dati <- mutate(serie, nome_territorio = factor(nome_territorio, levels = rev(LIVELLI)))
foto <- filter(dati, anno == ANNO)
valore <- function(terr, colonna) foto[[colonna]][foto$nome_territorio == terr]

istruzione <- ggplot(foto, aes(vantaggio_istruzione_F_pp, nome_territorio,
                               fill = nome_territorio)) +
  geom_col(width = 0.62) +
  geom_text(aes(label = paste0("+", virgola(vantaggio_istruzione_F_pp))),
            hjust = -0.25, size = 3.6, fontface = "bold", colour = "grey20") +
  scale_fill_manual(values = COLORI, guide = "none") +
  scale_x_continuous(limits = c(0, 5.4), expand = expansion(mult = c(0, 0.02))) +
  labs(subtitle = "Vantaggio educativo delle ragazze\nquota con almeno il diploma, 9-24 anni (F − M, punti)",
       x = "punti percentuali", y = NULL)

occupazione <- ggplot(foto, aes(rapporto_M_F_occupazione, nome_territorio,
                                colour = nome_territorio)) +
  geom_vline(xintercept = 1, linetype = "dashed", colour = "grey55", linewidth = 0.4) +
  geom_segment(aes(x = 1, xend = rapporto_M_F_occupazione, yend = nome_territorio),
               linewidth = 2.6, lineend = "round") +
  geom_point(size = 4.6) +
  geom_text(aes(label = virgola(rapporto_M_F_occupazione, 2, "×", taglia_zero = FALSE)),
            hjust = -0.45, size = 3.6, fontface = "bold", colour = "grey20") +
  scale_colour_manual(values = COLORI, guide = "none") +
  scale_x_continuous(limits = c(1, 2.35), expand = expansion(mult = c(0, 0.02))) +
  labs(subtitle = "Svantaggio occupazionale delle ragazze\nrapporto fra i tassi di occupazione M/F, 15-24 anni",
       x = "tasso maschile / tasso femminile (1 = parità)", y = NULL)

# --- la striscia: le stesse misure su tutte le annate disponibili ----------------------
# `verso` dice quale estremo è la posizione "sbagliata" di ciascuna misura: il minimo per
# il tasso femminile, il massimo per le altre due. Serve solo a contare in quanti anni
# Bagheria è in testa — è una lettura dei valori già calcolati, non un ricalcolo
# (stessa natura dello slice_max con cui fig01 trova il comune peggiore).
MISURE <- tribble(
  ~colonna,                     ~verso, ~pannello,
  "vantaggio_istruzione_F_pp",   "max", "vantaggio educativo F (punti)",
  "rapporto_M_F_occupazione",    "max", "rapporto M/F occupazione",
  "tasso_occupazione_F",         "min", "tasso di occupazione F (%)"
)

lungo <- dati |>
  select(anno, nome_territorio, all_of(MISURE$colonna)) |>
  pivot_longer(all_of(MISURE$colonna), names_to = "colonna", values_to = "valore") |>
  left_join(MISURE, by = "colonna") |>
  mutate(pannello = factor(pannello, levels = MISURE$pannello)) |>
  # Il 2020 manca alla fonte su ogni classe che contenga i 15-24: la riga vuota interrompe
  # la linea invece di farla passare dritta sopra il buco. Nessun valore inventato.
  complete(nesting(colonna, verso, pannello), nome_territorio, anno = PRIMO:ANNO)

pieno <- filter(lungo, !is.na(valore))
in_testa <- pieno |>
  summarise(testa = nome_territorio[if (first(verso) == "max") which.max(valore)
                                    else which.min(valore)],
            .by = c(pannello, anno))
conteggio <- in_testa |>
  summarise(anni = n(), bagheria = sum(testa == "Bagheria"), .by = pannello) |>
  left_join(summarise(pieno, alto = max(valore), basso = min(valore), .by = pannello),
            by = "pannello") |>
  mutate(etichetta = paste0("Bagheria in testa in ", bagheria, " anni su ", anni),
         y = alto + 0.17 * (alto - basso))

striscia <- ggplot(lungo, aes(anno, valore, colour = nome_territorio)) +
  geom_line(aes(linewidth = nome_territorio == "Bagheria")) +
  geom_point(size = 1.5) +
  geom_text(data = conteggio, aes(x = PRIMO - 0.2, y = y, label = etichetta),
            inherit.aes = FALSE, hjust = 0, vjust = 1, size = 3, fontface = "bold",
            colour = "grey25") +
  facet_wrap(~pannello, scales = "free_y", nrow = 1) +
  scale_colour_manual(values = COLORI, breaks = LIVELLI) +
  scale_linewidth_manual(values = c(`TRUE` = 1.3, `FALSE` = 0.6), guide = "none") +
  scale_x_continuous(breaks = seq(PRIMO, ANNO, 2)) +
  scale_y_continuous(expand = expansion(mult = c(0.06, 0.20))) +
  guides(colour = guide_legend(override.aes = list(linewidth = 1.1, size = 2))) +
  labs(subtitle = paste0("E quanto regge: le stesse misure su tutte le annate disponibili (",
                         PRIMO, "-", ANNO, ", il 2020 manca alla fonte)"),
       x = NULL, y = NULL) +
  theme(legend.position = "bottom")

figura <- (istruzione | occupazione) / striscia +
  plot_layout(heights = c(1, 1.05)) +
  plot_annotation(
    title = "Il capitale umano che Bagheria spreca di più è femminile",
    subtitle = paste0(
      "Anno ", ANNO, ". Le ragazze di Bagheria hanno il vantaggio educativo più ampio del panel (+",
      virgola(valore("Bagheria", "vantaggio_istruzione_F_pp")),
      " punti sui coetanei) e la peggiore conversione in lavoro:\n",
      "un ragazzo ha il doppio della probabilità di essere occupato (tasso femminile ",
      virgola(valore("Bagheria", "tasso_occupazione_F"), 1, "%"), ", il minimo del panel).\n",
      "I cinque comuni vicini hanno lo stesso rapporto occupazionale (",
      virgola(valore(ETICHETTA_VICINATO, "rapporto_M_F_occupazione"), 2, "×", taglia_zero = FALSE),
      " contro ", virgola(valore("Bagheria", "rapporto_M_F_occupazione"), 2, "×", taglia_zero = FALSE),
      ") ma un vantaggio educativo di appena +",
      virgola(valore(ETICHETTA_VICINATO, "vantaggio_istruzione_F_pp")), " punti:\n",
      "lo svantaggio occupazionale è di zona, la forbice è di Bagheria.\n",
      "La striscia in basso dice quale delle due classifiche regge: il livello femminile è il minimo del panel in ogni anno misurato,\n",
      "e la forbice si allarga; il rapporto M/F invece oscilla e non mette sempre Bagheria in testa.\n",
      "Il claim da portare nella proposal è il livello femminile, non il rapporto."),
    caption = paste0(
      "Fonte: ISTAT, Censimento permanente della popolazione - istruzione 9-24 anni, condizione professionale 15-24 anni.\n",
      "Le due fasce non sono la stessa popolazione. In punti percentuali il gap occupazionale di Bagheria non è un'anomalia (LPM nel notebook):\n",
      "a distinguerla sono il rapporto e il livello femminile, il minimo del panel.\n",
      "Vicinato = i cinque comuni più vicini per distanza fra i centroidi: conteggi sommati e poi i tassi, non media dei cinque tassi.\n",
      "Le tre misure della striscia escono dalle stesse formule della fotografia, ripetute anno per anno; il notebook verifica che sull'ultimo anno coincidano.\n",
      "«In testa» = il territorio all'estremo che definisce la forbice: il massimo per vantaggio educativo e rapporto M/F, il minimo per il tasso femminile.\n",
      "Un vantaggio educativo ampio non è di per sé un male: lo diventa accoppiato alla peggiore conversione in lavoro, ed è quella coppia la misura del sistema.\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_forbice_serie.csv (fotografia e serie)"),
    theme = tema_figura()
  )

salva(figura, "fig05_forbice", larghezza = 28, altezza = 22)

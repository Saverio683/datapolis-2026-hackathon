# Figura 1 — il gap di genere sull'occupazione 15-24 nelle due scale.
# Il punto: punti percentuali e rapporto ordinano i territori in modo opposto.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# Il vicinato entra aggregato, come in tutte le altre figure: una serie sola con la sua
# banda, non cinque linee. Sui conteggi sommati dei cinque comuni l'intervallo si stringe
# abbastanza da reggere il confronto con Bagheria; le serie per singolo comune restano nel
# CSV e sono troppo rumorose per essere lette anno su anno.
gap_vicini <- read_csv(file.path(PROCESSED, "genere_gap_occupazione_ci_vicini.csv"),
                       col_types = cols(territorio = "c", nome_territorio = "c", .default = "d"))
vicinato <- filter(gap_vicini, territorio == "VICINI5")
ETICHETTA_VICINATO <- vicinato$nome_territorio[1]
COLORI <- c(COLORI_TERRITORIO, setNames(COLORE_VICINATO, ETICHETTA_VICINATO))

dati <- bind_rows(
    read_csv(file.path(PROCESSED, "genere_gap_occupazione_ci.csv"), show_col_types = FALSE),
    vicinato
  ) |>
  mutate(nome_territorio = factor(nome_territorio, levels = names(COLORI))) |>
  # Il 2020 manca alla fonte sulla classe 15-24: la riga vuota interrompe la linea invece
  # di farla passare dritta sopra il buco. Nessun valore inventato.
  complete(nome_territorio, anno = 2018:2024)

ULTIMO_ANNO <- max(dati$anno[!is.na(dati$rapporto_M_F)])
rapporto_di <- function(territorio) {
  dati$rapporto_M_F[dati$nome_territorio == territorio & dati$anno == ULTIMO_ANNO]
}
# Il comune più sbilanciato resta un fatto anche se non è disegnato: senza questa riga il
# sottotitolo lascerebbe credere che nessuno in zona superi Bagheria, e non è vero.
PEGGIORE_COMUNE <- gap_vicini |>
  filter(territorio != "VICINI5", anno == ULTIMO_ANNO) |>
  slice_max(rapporto_M_F, n = 1)

comune <- list(
  scale_colour_manual(values = COLORI, breaks = names(COLORI)),
  scale_x_continuous(breaks = c(2018, 2019, 2021, 2022, 2023, 2024)),
  labs(x = NULL)
)

#' Il vuoto del 2020, nominato. La linea interrotta dice che manca qualcosa ma non cosa:
#' letta di corsa passa per una scelta di impaginazione. La banda grigia è la stessa
#' soluzione dello stacco fra le due epoche in fig10 — occupa lo spazio del dato assente
#' invece di lasciarlo bianco. `y` è dove sta la scritta: le due scale sono diverse.
#' Va messa come primo layer, altrimenti copre bande e linee invece di stare sotto.
buco_2020 <- function(y) {
  list(
    annotate("rect", xmin = 2019.35, xmax = 2020.65, ymin = -Inf, ymax = Inf, fill = "grey95"),
    # verticale dentro la banda, come in fig10: orizzontale sarebbe più larga della banda.
    annotate("text", x = 2020, y = y, size = 2.7, colour = "grey45", angle = 90,
             label = "2020 non rilevato alla fonte")
  )
}

punti <- ggplot(dati, aes(anno, gap, colour = nome_territorio, fill = nome_territorio)) +
  buco_2020(y = 7.5) +
  geom_ribbon(aes(ymin = gap_lo, ymax = gap_hi), alpha = 0.15, colour = NA) +
  scale_fill_manual(values = COLORI) +
  geom_line(linewidth = 0.9) +
  geom_point(size = 1.7) +
  comune +
  # Il fill serve solo alle bande: senza questo la sua legenda resta distinta da quella
  # del colore e patchwork non riesce ad accorparle in una sola.
  guides(fill = "none") +
  labs(subtitle = "In punti percentuali (M − F)",
       y = "punti percentuali")

rapporto <- ggplot(dati, aes(anno, rapporto_M_F, colour = nome_territorio)) +
  buco_2020(y = 1.75) +
  geom_hline(yintercept = 1, linetype = "dashed", colour = "grey55", linewidth = 0.4) +
  annotate("text", x = 2018, y = 1.04, label = "parità", hjust = 0,
           size = 3, colour = "grey45") +
  geom_line(linewidth = 0.9) +
  geom_point(size = 1.7) +
  comune +
  # coord_cartesian e non limits: taglia la vista, non le righe. Qualche vicino ha rapporti
  # fuori scala su conteggi minuscoli, la linea esce dal riquadro e non sparisce in silenzio.
  scale_y_continuous(labels = function(x) virgola(x, 1, taglia_zero = FALSE)) +
  coord_cartesian(ylim = c(0.95, max(dati$rapporto_M_F, na.rm = TRUE) + 0.05)) +
  labs(subtitle = "In rapporto (tasso M / tasso F)",
       y = "quante volte")

# La legenda in una riga tutta sua, in cima (come in fig07): `guide_area()` è il posto
# che patchwork dà ai guide raccolti, e come prima riga della composizione finisce sopra
# i titoli dei due pannelli invece che incastrata fra i titoli e i grafici. Centrata
# sull'intera figura, non sul solo pannello che la produce.
figura <- guide_area() / (punti | rapporto) +
  plot_layout(heights = c(0.08, 1), guides = "collect") +
  plot_annotation(
    title = "Il divario di genere di Bagheria è medio in punti, il peggiore in proporzione",
    subtitle = paste("Tasso di occupazione 15-24 anni, 2018-2024. In punti percentuali il gap di Bagheria (8,3 nel 2024)",
                     "sta sotto Sicilia e Italia;\nin rapporto è il più sbilanciato del panel: un ragazzo ha il doppio",
                     "della probabilità di lavorare di una coetanea.",
                     paste0("\nMa il vicinato lo segue a un soffio (",
                            virgola(rapporto_di(ETICHETTA_VICINATO), 2, "×", taglia_zero = FALSE), " contro ",
                            virgola(rapporto_di("Bagheria"), 2, "×", taglia_zero = FALSE),
                            " nel ", ULTIMO_ANNO, "): in rapporto il divario è un tratto di zona.",
                            "\nPreso comune per comune, ", PEGGIORE_COMUNE$nome_territorio, " arriva a ",
                            virgola(PEGGIORE_COMUNE$rapporto_M_F, 2, "×", taglia_zero = FALSE), ".")),
    caption = paste("Fonte: ISTAT, Censimento permanente della popolazione - tavola condizione professionale, classe 15-24 anni.",
                    "\nBande: intervalli di confidenza 95% (Wilson per i tassi, Newcombe per la differenza).",
                    "Il 2020 manca alla fonte sulla classe 15-24: la linea è interrotta, non interpolata.",
                    "\nVicinato = i cinque comuni più vicini per distanza fra i centroidi: conteggi sommati e poi i tassi, non media dei cinque tassi.",
                    "\nLe serie dei singoli comuni stanno in genere_gap_occupazione_ci_vicini.csv: su 10-28 mila abitanti gli intervalli sono larghi il quintuplo.",
                    "\nElaborazione: notebooks/genere.ipynb - data/processed/genere_gap_occupazione_ci.csv, genere_gap_occupazione_ci_vicini.csv"),
    theme = tema_figura()
  )

salva(figura, "fig01_gap_due_scale", larghezza = 26, altezza = 15)

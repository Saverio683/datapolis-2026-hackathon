# Figura 1 — il gap di genere sull'occupazione 15-24 nelle due scale.
# Il punto: punti percentuali e rapporto ordinano i territori in modo opposto.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

dati <- read_csv(file.path(PROCESSED, "genere_gap_occupazione_ci.csv"), show_col_types = FALSE) |>
  mutate(nome_territorio = factor(nome_territorio, levels = ORDINE)) |>
  # Il 2020 manca alla fonte sulla classe 15-24: la riga vuota interrompe la linea invece
  # di farla passare dritta sopra il buco. Nessun valore inventato.
  complete(nome_territorio, anno = 2018:2024)

comune <- list(
  scale_colour_manual(values = COLORI_TERRITORIO),
  scale_x_continuous(breaks = c(2018, 2019, 2021, 2022, 2023, 2024)),
  labs(x = NULL)
)

punti <- ggplot(dati, aes(anno, gap, colour = nome_territorio, fill = nome_territorio)) +
  geom_ribbon(aes(ymin = gap_lo, ymax = gap_hi), alpha = 0.15, colour = NA) +
  scale_fill_manual(values = COLORI_TERRITORIO) +
  geom_line(linewidth = 0.9) +
  geom_point(size = 1.7) +
  comune +
  # Il fill serve solo alle bande: senza questo la sua legenda resta distinta da quella
  # del colore e patchwork non riesce ad accorparle in una sola.
  guides(fill = "none") +
  labs(subtitle = "In punti percentuali (M − F)",
       y = "punti percentuali")

rapporto <- ggplot(dati, aes(anno, rapporto_M_F, colour = nome_territorio)) +
  geom_hline(yintercept = 1, linetype = "dashed", colour = "grey55", linewidth = 0.4) +
  annotate("text", x = 2018, y = 1.04, label = "parità", hjust = 0,
           size = 3, colour = "grey45") +
  geom_line(linewidth = 0.9) +
  geom_point(size = 1.7) +
  comune +
  scale_y_continuous(limits = c(0.95, 2.6)) +
  labs(subtitle = "In rapporto (tasso M / tasso F)",
       y = "quante volte")

figura <- (punti | rapporto) +
  plot_layout(guides = "collect") +
  plot_annotation(
    title = "Il divario di genere di Bagheria è medio in punti, il peggiore in proporzione",
    subtitle = paste("Tasso di occupazione 15-24 anni, 2018-2024. In punti percentuali il gap di Bagheria (8,3 nel 2024)",
                     "sta sotto Sicilia e Italia;\nin rapporto è il più sbilanciato dei quattro: un ragazzo ha il doppio",
                     "della probabilità di lavorare di una coetanea."),
    caption = paste("Fonte: ISTAT, Censimento permanente della popolazione — tavola condizione professionale, classe 15-24 anni.",
                    "\nBande: intervalli di confidenza 95% (Wilson per i tassi, Newcombe per la differenza).",
                    "Il 2020 manca alla fonte sulla classe 15-24: la linea è interrotta, non interpolata.",
                    "\nElaborazione: notebooks/genere.ipynb — data/processed/genere_gap_occupazione_ci.csv"),
    theme = tema_datapolis()
  ) &
  theme(legend.position = "top")

salva(figura, "fig01_gap_due_scale", larghezza = 26, altezza = 15)

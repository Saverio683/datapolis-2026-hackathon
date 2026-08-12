# Figura 4 — mappa dei 390 comuni siciliani: dove sta Bagheria nella distribuzione.
# I poligoni arrivano già proiettati da pipeline/build.py (ISTAT 2026 generalizzati,
# EPSG:32633 — WGS 84 / UTM 33N): qui non si tocca la geometria, si disegna.
# Niente sf: le librerie di sistema GDAL/GEOS non sono installabili su questa macchina.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

mappa <- read_csv(file.path(PROCESSED, "genere_mappa_occupazione_femminile.csv"),
                  col_types = cols(territorio = "c", nome_comune = "c", .default = "d"))
etichette <- read_csv(file.path(PROCESSED, "genere_mappa_etichette.csv"),
                      col_types = cols(territorio = "c", nome_comune = "c", .default = "d"))

# Un valore per comune: deduplicazione dei vertici, non un ricalcolo. Misiliscemi non ha
# dato 2011 e va tolto qui, altrimenti l'istogramma lo scarta con un warning.
valori <- mappa |>
  distinct(territorio, nome_comune, occupazione_femminile_2011) |>
  filter(!is.na(occupazione_femminile_2011))
bagheria <- filter(etichette, nome_comune == "Bagheria")

# group = comune × parte (le isole sono parti separate), subgroup = anello (i buchi).
forma <- aes(x, y, group = interaction(territorio, parte), subgroup = anello)

carta <- ggplot() +
  geom_polygon(data = mappa, modifyList(forma, aes(fill = occupazione_femminile_2011)),
               rule = "evenodd", colour = "white", linewidth = 0.08) +
  # Bagheria ridisegnata sopra con un bordo che stacca dalla scala viridis.
  geom_polygon(data = filter(mappa, territorio == "082006"), forma,
               rule = "evenodd", fill = NA, colour = "#D55E00", linewidth = 0.9) +
  geom_segment(data = bagheria, aes(x = x, y = y, xend = x + 62000, yend = y + 46000),
               colour = "#D55E00", linewidth = 0.4) +
  geom_label(data = bagheria, aes(x = x + 62000, y = y + 46000, label = "Bagheria 18,1%"),
             hjust = 0, vjust = 0.5, size = 3.6, fontface = "bold", colour = "#D55E00",
             linewidth = 0, fill = "white") +
  scale_fill_viridis_c(name = "occupazione femminile 2011 (%)", na.value = "grey88",
                       breaks = c(15, 20, 25, 30, 35),
                       guide = guide_colourbar(barwidth = 12, barheight = 0.5, title.position = "top")) +
  # Riquadro sull'isola: Lampedusa e Linosa (250 km più a sud) lascerebbero mezza tela
  # vuota. Il comune resta nella distribuzione qui sotto e nel dato, solo fuori inquadratura.
  coord_equal(ylim = c(4050000, 4300000), clip = "off") +
  labs(x = NULL, y = NULL) +
  # panel.grid da solo non basta: tema_datapolis fissa esplicitamente major e minor,
  # e un figlio impostato vince sul genitore azzerato.
  theme(axis.text = element_blank(), axis.ticks = element_blank(),
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        legend.position = "top", legend.title = element_text(size = rel(0.85)))

# Striscia di distribuzione: la stessa scala colore, per leggere il percentile.
distribuzione <- ggplot(valori, aes(occupazione_femminile_2011)) +
  geom_histogram(aes(fill = after_stat(x)), binwidth = 1, colour = "white", linewidth = 0.15) +
  geom_vline(xintercept = bagheria$valore, colour = "#D55E00", linewidth = 0.7) +
  annotate("text", x = bagheria$valore - 0.6, y = 34, label = "Bagheria", hjust = 1,
           colour = "#D55E00", fontface = "bold", size = 3.3) +
  scale_fill_viridis_c(guide = "none") +
  scale_x_continuous(labels = function(x) paste0(x, "%")) +
  labs(x = "tasso di occupazione femminile, 390 comuni siciliani (2011, 15 anni e più)",
       y = "comuni") +
  theme(panel.grid.major.x = element_blank())

figura <- carta / distribuzione +
  plot_layout(heights = c(3.4, 1)) +
  plot_annotation(
    title = "Bagheria è nel 12° percentile siciliano per occupazione femminile",
    subtitle = paste("Solo 48 comuni su 390 stavano più in basso nel 2011: 18,1% contro una mediana regionale del 23,6%",
                     "e il 36,1% italiano.\nNon è un comune medio della Sicilia, è nella coda bassa di una regione già ultima in Italia."),
    caption = paste("Fonte: ISTAT 8milaCensus, indicatore L11 — tasso di occupazione femminile, censimento 2011, popolazione 15 anni e più.",
                    "\nFascia e anno diversi dalle serie 15-24 del thread: contesto di lungo periodo, non termine di paragone.",
                    "\nConfini: ISTAT, unità amministrative generalizzate al 01/01/2026, EPSG:32633 (WGS 84 / UTM 33N).",
                    "In grigio Misiliscemi,\nistituito nel 2021 da Trapani: nel 2011 non esisteva e il dato non gli è attribuibile.",
                    "Lampedusa e Linosa è fuori riquadro, nella distribuzione c'è.",
                    "\nElaborazione: notebooks/genere.ipynb — data/processed/genere_mappa_occupazione_femminile.csv"),
    theme = tema_datapolis()
  )

salva(figura, "fig04_mappa_sicilia", larghezza = 24, altezza = 20)

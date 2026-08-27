# Figura 6 — il piano istruzione × occupazione, in due scale non confrontabili e per
# questo affiancate ed etichettate: i quattro territori per genere (2018-2024, giovani)
# e i 390 comuni siciliani (2011, 15+). Il punto: la freccia M→F punta ovunque in basso
# a destra — più istruite, meno occupate — e Bagheria è l'estremo in entrambi i pannelli.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

quadrante <- read_csv(file.path(PROCESSED, "genere_quadrante.csv"), show_col_types = FALSE)
# territorio esplicitamente stringa: lo zero iniziale del codice ISTAT non deve sparire,
# serve per appaiare i vicini calcolati nel notebook.
nuvola <- read_csv(file.path(PROCESSED, "genere_nuvola_390.csv"),
                   col_types = cols(territorio = "c", nome_comune = "c", evidenzia = "c",
                                    gemella = "l", .default = "d"))
anno <- unique(quadrante$anno)

largo <- quadrante |>
  pivot_wider(id_cols = c(territorio, nome_territorio),
              names_from = genere, values_from = c(tasso_occupazione, `almeno_diploma_%`))
etichette_a <- largo |>
  mutate(nudge_x = c(0, 0, 0.25, 0.25), nudge_y = c(-1.1, 1.1, -1.1, 1.1),
         hjust = c(0.5, 0.5, 0.5, 0.5))  # ordine: come nel csv (Bagheria, Palermo, Italia, Sicilia)

pannello_a <- ggplot(largo) +
  geom_segment(aes(x = `almeno_diploma_%_M`, y = tasso_occupazione_M,
                   xend = `almeno_diploma_%_F`, yend = tasso_occupazione_F),
               colour = "grey65", linewidth = 0.7,
               arrow = arrow(length = unit(2.6, "mm"), type = "closed")) +
  geom_point(data = quadrante,
             aes(`almeno_diploma_%`, tasso_occupazione, colour = genere), size = 3.4) +
  geom_text(data = etichette_a,
            aes(`almeno_diploma_%_F` + nudge_x, tasso_occupazione_F + nudge_y,
                label = nome_territorio),
            size = 3.5, fontface = "bold", colour = "grey25") +
  scale_colour_manual(values = COLORI_GENERE, labels = ETICHETTE_GENERE) +
  labs(subtitle = paste0("I quattro territori per genere - ", anno, ", censimento permanente\n",
                         "istruzione 9-24 anni · occupazione 15-24 anni"),
       x = "quota con almeno il diploma, 9-24 anni (%)",
       y = "tasso di occupazione 15-24 anni (%)") +
  theme(legend.position = "top")

bag <- filter(nuvola, evidenzia == "Bagheria")
pal <- filter(nuvola, evidenzia == "Palermo")

# I cinque comuni geograficamente più vicini a Bagheria: stessa selezione della fig04
# (distanza fra centroidi, calcolata nel notebook). Un colore pieno e diverso per ciascuno,
# non una gradazione: dentro una nuvola di 390 punti grigi le tonalità non si distinguono.
vicini <- vicini_di_bagheria()
COLORI_VICINI <- setNames(vicini$colore, vicini$nome_comune)
# Le gemelle restano nel grafico ma come contesto: grigio scuro, una classe sola.
CLASSI <- c("altri comuni" = "grey78", "gemelle strutturali" = "grey45", COLORI_VICINI,
            "Palermo" = COLORI_TERRITORIO[["Palermo"]],
            "Bagheria" = COLORI_TERRITORIO[["Bagheria"]])
sovrapposte <- intersect(vicini$nome_comune, filter(nuvola, gemella)$nome_comune)
nuvola <- nuvola |>
  mutate(classe = factor(case_when(!is.na(evidenzia) ~ evidenzia,
                                   territorio %in% vicini$territorio ~ nome_comune,
                                   gemella ~ "gemelle strutturali",
                                   TRUE ~ "altri comuni"), levels = names(CLASSI))) |>
  arrange(classe)  # i punti evidenziati disegnati sopra la nuvola
# Un vicino non appaiato sparirebbe muto nella nuvola grigia.
stopifnot(!anyNA(nuvola$classe),
          all(vicini$nome_comune %in% levels(droplevels(nuvola$classe))))

pannello_b <- ggplot(nuvola, aes(I1, L11, colour = classe, size = classe)) +
  geom_vline(xintercept = 100, linetype = "dashed", colour = "grey55", linewidth = 0.4) +
  geom_point(alpha = 0.9) +
  # Etichetta in alto a destra del punto (asse invertito): sotto e a sinistra ci sono
  # Villabate e Misilmeri, che sono a un passo da Bagheria anche nel piano.
  annotate("text", x = bag$I1 - 1, y = bag$L11 + 1.3, label = "Bagheria", hjust = 0,
           size = 3.6, fontface = "bold", colour = COLORI_TERRITORIO[["Bagheria"]]) +
  # Palermo etichettato sul punto: con dieci blu in legenda il suo non è più riconoscibile
  # dal solo colore.
  annotate("text", x = pal$I1, y = pal$L11 + 1.7, label = "Palermo", hjust = 0.5,
           size = 3.4, fontface = "bold", colour = COLORI_TERRITORIO[["Palermo"]]) +
  scale_colour_manual(values = CLASSI) +
  scale_size_manual(values = c(1.6, 2, rep(3.2, nrow(vicini)), 3.4, 4.2), guide = "none") +
  # asse invertito: verso destra I1 scende, le donne sono relativamente più istruite
  scale_x_reverse() +
  guides(colour = guide_legend(nrow = 2, override.aes = list(size = 3))) +
  labs(subtitle = "I 390 comuni siciliani - 2011, 8milaCensus\nistruzione 6+ · occupazione femminile 15+ · tratteggio = parità",
       x = "I1 = rapporto educativo M/F × 100 (a destra le donne sono più istruite)",
       y = "tasso di occupazione femminile 15+ (%)") +
  theme(legend.position = "top")

figura <- (pannello_a | pannello_b) +
  plot_annotation(
    title = "Più istruite, meno occupate: la freccia punta nella stessa direzione a ogni scala",
    subtitle = paste("A sinistra, la freccia va dal punto maschile a quello femminile: ovunque verso più istruzione e meno lavoro, e a Bagheria arriva più in basso.",
                     "\nA destra, il contesto strutturale: dove le donne sono relativamente più istruite l'occupazione femminile di solito è più alta (Spearman -0,24, p<0,001);",
                     "\nBagheria è nel quadrante che contraddice il pattern, al 12° percentile di occupazione femminile."),
    caption = paste("Pannelli non confrontabili fra loro: fasce d'età, popolazioni e fonti diverse, dichiarate su ciascuno. Correlazione ecologica: orienta, non dimostra.",
                    paste0("\nIn colore i ", nrow(vicini), " comuni più vicini a Bagheria (distanza fra i centroidi, tutti entro 8 km), in legenda dal più vicino."),
                    paste0("\nIn grigio scuro le gemelle strutturali: comuni comparabili per dimensione, densità, età, stranieri, abitazioni e distanza da Palermo (matching nel notebook).",
                           "\n", paste(sovrapposte, collapse = " e "), " sono entrambe le cose: prevale il colore di vicino."),
                    "\nFonti: ISTAT, Censimento permanente; ISTAT, 8milaCensus 2011. Elaborazione: notebooks/genere.ipynb -",
                    "genere_quadrante.csv, genere_nuvola_390.csv, genere_mappa_etichette.csv"),
    theme = tema_figura()
  )

salva(figura, "fig06_quadrante", larghezza = 30, altezza = 18)

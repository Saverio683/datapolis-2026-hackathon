# Figura 4 — la Sicilia del 2024, e quanto somiglia a quella del 2011.
# I poligoni arrivano già proiettati da pipeline/build.py (ISTAT 2026 generalizzati,
# EPSG:32633 — WGS 84 / UTM 33N): qui non si tocca la geometria, si disegna.
# Niente sf: le librerie di sistema GDAL/GEOS non sono installabili su questa macchina.
# Il punto per la proposal: la mappa è al 2024, ma la graduatoria che disegna è quasi la
# stessa del 2011 (rho di Spearman nel pannello a destra). Un claim di posizionamento
# costruito sul censimento 2011 non era una scommessa sul passato: era una previsione.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

confini <- read_csv(file.path(PROCESSED, "genere_mappa_occupazione_femminile.csv"),
                    col_types = cols(territorio = "c", nome_comune = "c", .default = "d"))
# Un valore per comune alle due estremità della serie: la geometria sta nel file dei
# vertici, i valori qui. Il join è assemblaggio, non trasformazione — nessun ricalcolo.
comuni <- read_csv(file.path(PROCESSED, "genere_mappa_2011_2024.csv"),
                   col_types = cols(territorio = "c", nome_comune = "c", ruolo = "c",
                                    .default = "d"))
distribuzione <- read_csv(file.path(PROCESSED, "genere_distribuzione_390.csv"),
                          col_types = cols(fonte = "c", .default = "d"))

ANNO <- max(distribuzione$anno)
BASE <- min(distribuzione$anno)
riga <- function(anno) distribuzione[distribuzione$anno == anno, ]
prima <- riga(BASE)
dopo <- riga(ANNO)

mappa <- left_join(confini, select(comuni, territorio, occ_2024), by = "territorio")
bagheria <- filter(comuni, ruolo == "Bagheria")
vicini <- filter(comuni, ruolo == "vicino") |> arrange(distanza_km)

# I cinque vicini stanno dentro 8 km: alla scala dell'isola sono un punto solo, quindi le
# etichette si impilano in mare con una linea di richiamo ciascuna. Nome e valore in una
# stringa sola: con due colonne allineate il nome più lungo tocca il valore, e il blocco
# non ha spazio per allargarsi (deve stare fra Ustica, x 341000, e Alicudi, x 442000).
# Le coordinate cadono su tratti di Tirreno senza comuni (verificato sui vertici).
# Gli estremi regionali non sono più etichettati sulla carta: cambiano comune fra le due
# annate e si leggono meglio agli estremi dell'istogramma qui sotto.
X_NOME <- 370000
pila <- bind_rows(bagheria, vicini) |>
  mutate(y_lab = 4288000 - 11000 * (row_number() - 1),
         colore = if_else(ruolo == "Bagheria", COLORI_TERRITORIO[["Bagheria"]], "grey20"),
         faccia = if_else(ruolo == "Bagheria", "bold", "plain"),
         testo = paste0(nome_comune, "  ", virgola(occ_2024, 1, "%")))

# group = comune × parte (le isole sono parti separate), subgroup = anello (i buchi).
forma <- aes(x, y, group = interaction(territorio, parte), subgroup = anello)
SCALA <- c(12, 40)   # comune a carta e istogramma: i due pannelli si leggono insieme

carta <- ggplot() +
  geom_polygon(data = mappa, modifyList(forma, aes(fill = occ_2024)),
               rule = "evenodd", colour = "white", linewidth = 0.08) +
  geom_polygon(data = filter(mappa, territorio %in% vicini$territorio),
               forma, rule = "evenodd", fill = NA, colour = "grey15", linewidth = 0.3) +
  # Bagheria ridisegnata sopra con un bordo che stacca dalla scala viridis.
  geom_polygon(data = filter(mappa, territorio == bagheria$territorio), forma,
               rule = "evenodd", fill = NA, colour = "#D55E00", linewidth = 0.9) +
  geom_segment(data = pila, aes(x = x, y = y, xend = X_NOME - 5000, yend = y_lab,
                                colour = colore), linewidth = 0.3) +
  geom_text(data = pila, aes(X_NOME, y_lab, label = testo, colour = colore,
                             fontface = faccia), hjust = 0, size = 3.2) +
  scale_colour_identity() +
  scale_fill_viridis_c(name = paste0("occupazione femminile ", ANNO, " (%)"),
                       limits = SCALA, na.value = "grey88", breaks = seq(15, 40, 5),
                       guide = guide_colourbar(barwidth = 9, barheight = 0.45,
                                               title.position = "top")) +
  # Riquadro sull'isola: Lampedusa e Linosa (250 km più a sud) lascerebbero mezza tela
  # vuota. Il comune resta nella distribuzione qui sotto e nel dato, solo fuori inquadratura.
  # Il clip resta acceso, altrimenti Lampedusa viene disegnata fuori dal pannello, sopra
  # l'istogramma; le etichette stanno tutte dentro il riquadro. xlim ritagliato sui
  # vertici effettivi (Pantelleria a ovest, Messina a est): il default lascia bande vuote.
  coord_equal(xlim = c(224000, 559000), ylim = c(4050000, 4300000)) +
  labs(x = NULL, y = NULL) +
  # panel.grid da solo non basta: tema_datapolis fissa esplicitamente major e minor,
  # e un figlio impostato vince sul genitore azzerato.
  # Legenda dentro il pannello, nel Tirreno a nord-ovest: fuori si prendeva una fascia
  # orizzontale intera e la carta, vincolata dall'altezza da coord_equal, restava piccola
  # con bande vuote ai lati. Quel tratto di mare è libero (nessun comune sopra x 340000
  # a ovest di Ustica) e il fondo bianco la stacca dall'azzurro dei comuni più bassi.
  theme(axis.text = element_blank(), axis.ticks = element_blank(),
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        legend.position = "inside", legend.position.inside = c(0.01, 0.99),
        legend.justification = c(0, 1), legend.direction = "horizontal",
        legend.background = element_rect(fill = "white", colour = NA),
        legend.margin = margin(4, 8, 4, 8),
        legend.title = element_text(size = rel(0.85)))

# --- pannello B: la distribuzione si è spostata, Bagheria si è spostata con lei --------
# Barre piene = 2024 (stessa scala colore della carta), profilo grigio = 2011. Sovrapposti
# e non affiancati perché il finding è lo scorrimento dell'intera distribuzione.
spostamento <- ggplot(comuni, aes(occ_2024)) +
  geom_histogram(aes(fill = after_stat(x)), binwidth = 1, colour = "white", linewidth = 0.15) +
  geom_histogram(aes(x = occ_2011), binwidth = 1, fill = NA, colour = "grey35",
                 linewidth = 0.4) +
  annotate("segment", x = prima$bagheria, xend = dopo$bagheria, y = 43, yend = 43,
           colour = COLORI_TERRITORIO[["Bagheria"]], linewidth = 0.5,
           arrow = arrow(length = unit(0.18, "cm"), type = "closed")) +
  annotate("segment", x = c(prima$bagheria, dopo$bagheria),
           xend = c(prima$bagheria, dopo$bagheria), y = 0, yend = 43,
           colour = COLORI_TERRITORIO[["Bagheria"]], linetype = c("dashed", "solid"),
           linewidth = c(0.4, 0.8)) +
  annotate("text", x = prima$bagheria - 0.7, y = 43, hjust = 1, vjust = 0.4, size = 3.1,
           colour = COLORI_TERRITORIO[["Bagheria"]], lineheight = 1.05,
           label = paste0("Bagheria ", BASE, "\n", virgola(prima$bagheria, 1, "%"))) +
  annotate("text", x = dopo$bagheria + 0.7, y = 43, hjust = 0, vjust = 0.4, size = 3.1,
           fontface = "bold", colour = COLORI_TERRITORIO[["Bagheria"]], lineheight = 1.05,
           label = paste0("Bagheria ", ANNO, "\n", virgola(dopo$bagheria, 1, "%"))) +
  # Le due mediane: la distanza fra loro è lo scorrimento che Bagheria ha solo inseguito.
  annotate("segment", x = c(prima$mediana, dopo$mediana),
           xend = c(prima$mediana, dopo$mediana), y = 0, yend = 34,
           colour = "grey35", linetype = c("dashed", "solid"), linewidth = c(0.4, 0.7)) +
  annotate("text", x = dopo$mediana + 0.6, y = 40, hjust = 0, vjust = 1, size = 3,
           colour = "grey30", lineheight = 1.05,
           label = paste0("mediana siciliana\n", BASE, ": ", virgola(prima$mediana, 1, "%"),
                          "   ", ANNO, ": ", virgola(dopo$mediana, 1, "%"))) +
  scale_fill_viridis_c(limits = SCALA, guide = "none") +
  # xlim su coord e non su scale: la scala scarterebbe i comuni fuori intervallo prima
  # del binning (e infatti avvisava), il coord si limita a ritagliare la vista.
  scale_x_continuous(labels = function(x) paste0(x, "%")) +
  coord_cartesian(xlim = SCALA, clip = "off") +
  labs(subtitle = paste0("Tutta la Sicilia si è spostata a destra, Bagheria l'ha seguita\n",
                         "barre piene ", ANNO, ", profilo grigio ", BASE,
                         "; 390 comuni, 15 anni e più"),
       x = "tasso di occupazione femminile", y = "comuni") +
  theme(panel.grid.major.x = element_blank())

# --- pannello C: il rango del 2011 predice quello del 2024 -----------------------------
# La prova che la fotografia vecchia non era una speculazione: ogni punto è un comune,
# la diagonale è "stessa posizione nelle due annate". Il quadrato in basso a sinistra è
# il quintile più basso in entrambe le annate — chi ci entra, tendenzialmente ci resta.
# Bagheria non ha etichetta dentro il pannello: sta nel mucchio del quadrato e qualunque
# testo lì sopra coprirebbe altri comuni. Il colore è quello della carta, il valore sta
# nel sottotitolo. Le due annotazioni vivono negli angoli vuoti (alto-sinistra = chi è
# risalito molto, basso-destra = chi è crollato: entrambi rari).
QUINTILE <- 20
punto <- function(dati, colore, dimensione) {
  # alone bianco sotto: sul grigio dei 390 un punto pieno da solo non si stacca.
  list(geom_point(data = dati, colour = "white", size = dimensione + 1.4),
       geom_point(data = dati, colour = colore, size = dimensione))
}

persistenza <- ggplot(comuni, aes(pct_2011, pct_2024)) +
  annotate("rect", xmin = 0, xmax = QUINTILE, ymin = 0, ymax = QUINTILE,
           fill = "grey92", colour = NA) +
  geom_abline(slope = 1, intercept = 0, colour = "grey60", linetype = "dashed",
              linewidth = 0.4) +
  geom_point(colour = "grey55", size = 0.9, alpha = 0.55) +
  punto(vicini, COLORE_VICINATO, 2.1) +
  punto(bagheria, COLORI_TERRITORIO[["Bagheria"]], 3.4) +
  annotate("text", x = 3, y = 98, hjust = 0, vjust = 1, size = 2.9, colour = "grey35",
           lineheight = 1.15,
           label = paste0("nel quintile più basso\nin entrambe le annate:\n",
                          virgola(prima$quintile_basso_ancora_tale_nel_2024_pct, 0, "%"),
                          " dei comuni")) +
  annotate("text", x = 99, y = 15, hjust = 1, size = 3.3, fontface = "bold", colour = "grey25",
           label = paste0("rho di Spearman ", virgola(prima$rho_vs_2024, 3))) +
  annotate("text", x = 99, y = 9, hjust = 1, vjust = 1, size = 2.9, colour = "grey45",
           lineheight = 1.15,
           label = paste0("dentro il solo permanente\n(2018 contro ", ANNO, "): ",
                          virgola(riga(2018)$rho_vs_2024, 3))) +
  scale_x_continuous(limits = c(0, 100), breaks = seq(0, 100, 25)) +
  scale_y_continuous(limits = c(0, 100), breaks = seq(0, 100, 25)) +
  coord_equal() +
  labs(subtitle = paste0("E la graduatoria è quasi la stessa\n",
                         "Bagheria in arancio, dal ", virgola(bagheria$pct_2011, 0, "°"),
                         " al ", virgola(bagheria$pct_2024, 0, "°")),
       x = paste0("percentile ", BASE), y = paste0("percentile ", ANNO))

figura <- carta / (spostamento | persistenza) +
  plot_layout(heights = c(4.4, 1.7)) +
  plot_annotation(
    title = paste0("Nel ", ANNO, " Bagheria arriva dove stava la mediana siciliana nel ", BASE),
    subtitle = paste0(
      "Il tasso di occupazione femminile sale da ", virgola(prima$bagheria, 1, "%"), " a ",
      virgola(dopo$bagheria, 1, "%"), ", ma la mediana regionale sale da ",
      virgola(prima$mediana, 1, "%"), " a ", virgola(dopo$mediana, 1, "%"), ".\n",
      "La posizione quasi non cambia: dal ", virgola(prima$percentile, 0, "°"), " al ",
      virgola(dopo$percentile, 0, "°"), " percentile, con ", dopo$comuni_sotto,
      " comuni su 390 più in basso.\n",
      "Non è un comune medio della Sicilia: è nella coda bassa, e ci era già nel ", BASE,
      ". Anche i cinque vicini restano sotto la mediana.\n",
      "Il pannello a destra dice perché vale la pena affermarlo: la graduatoria del ", BASE,
      " predice quella del ", ANNO, " (rho ", virgola(prima$rho_vs_2024, 3), ").\n",
      "Il posizionamento non è una fotografia scaduta, è una previsione verificata."),
    caption = paste0(
      "Fonte: ISTAT - 8milaCensus, indicatore L11 (censimento ", BASE,
      ") e Censimento permanente della popolazione (2018-", ANNO, ", il 2020 manca alla fonte).\n",
      "Tasso di occupazione femminile, popolazione 15 anni e più. Due rilevazioni con disegni diversi: universale a questionario la prima,\n",
      "campionaria sui registri la seconda. Il livello ne risente, il rango dentro l'anno molto meno, perché lo scarto di definizione sposta\n",
      "tutti i comuni nello stesso verso: per questo il pannello a destra confronta percentili e non punti percentuali.\n",
      "Fascia e anno diversi dalle serie 15-24 del thread: contesto di lungo periodo, non termine di paragone.\n",
      "390 comuni ai confini ", BASE, " in entrambe le annate. In grigio Misiliscemi, istituito nel 2021 da Trapani: nel ", BASE,
      " non esisteva, il dato\nnon gli è attribuibile ed è fuori dai 390. Lampedusa e Linosa è fuori riquadro, nella distribuzione c'è.\n",
      "Confini: ISTAT, unità amministrative generalizzate al 01/01/2026, EPSG:32633 (WGS 84 / UTM 33N).\n",
      "Etichettati sulla carta Bagheria e i cinque comuni più vicini (distanza fra i centroidi, tutti entro 8 km);\n",
      "gli estremi regionali si leggono agli estremi dell'istogramma. Rho di Spearman e persistenza del quintile: notebooks/genere.ipynb.\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_mappa_occupazione_femminile.csv, genere_mappa_2011_2024.csv,\n",
      "genere_distribuzione_390.csv"),
    theme = tema_figura()
  )

# Più alta dell'originale: coord_equal vincola la carta dall'altezza, quindi l'altezza
# del pannello è ciò che decide quanto la Sicilia riempie i 26 cm di larghezza.
salva(figura, "fig04_mappa_sicilia", larghezza = 26, altezza = 33)

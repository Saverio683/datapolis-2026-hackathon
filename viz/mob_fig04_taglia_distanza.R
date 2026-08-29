# Mobilità, figura 4 — perché «Bagheria si muove poco» è una lettura sbagliata di un
# numero giusto. Il percentile grezzo di M2 dice 25°, e sembra un'anomalia; ma fuori
# comune si va per mancanza di lavoro dentro, e Bagheria è il comune più grande della
# corona di Palermo. A parità di distanza dal capoluogo e di taglia, sta nella media.
# La figura serve a togliere di mezzo un claim, non a stabilirne uno: è la ragione per cui
# sta in questo thread e non in appendice.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 28

comuni <- read_csv(file.path(PROCESSED, "mob_taglia_distanza.csv"),
                   col_types = cols(territorio = "c", nome = "c", .default = "d"))
curve <- read_csv(file.path(PROCESSED, "mob_curva_attesa.csv"),
                  col_types = cols(scenario = "c", .default = "d"))
BAG <- "082006"
bagheria <- filter(comuni, territorio == BAG)

percentile_grezzo <- 100 * mean(comuni$quota_fuori < bagheria$quota_fuori)
percentile_residuo <- 100 * mean(comuni$residuo < bagheria$residuo)

# --- A: la nuvola --------------------------------------------------------------------
# Asse x logaritmico perché il modello è in log della distanza: la curva attesa deve
# apparire come la retta che è, altrimenti la figura e il modello dicono cose diverse.
# La dimensione del punto è il numero di pendolari, cioè la variabile che spiega l'apparente
# anomalia: si vede a occhio che i comuni grandi stanno in basso.
vicini_30 <- filter(comuni, km_capoluogo <= 30, substr(territorio, 1, 3) == "082",
                    pendolari >= 2000, territorio != BAG) |>
  slice_max(pendolari, n = 5)

nuvola <- ggplot(comuni, aes(km_capoluogo, quota_fuori)) +
  geom_point(aes(size = pendolari), colour = "grey70", alpha = 0.5) +
  # Due curve e non una: l'atteso dipende anche dalla taglia, quindi una linea sola
  # attraverso i punti sarebbe una spezzata senza significato. Le due curve a taglia
  # fissata mostrano proprio la cosa che spiega l'apparente anomalia — la taglia sposta
  # la curva in basso di una decina di punti.
  geom_line(data = curve, aes(km_capoluogo, atteso, linetype = scenario),
            colour = "grey25", linewidth = 0.7) +
  geom_point(data = bagheria, aes(size = pendolari),
             colour = COLORI_TERRITORIO[["Bagheria"]]) +
  geom_segment(data = bagheria, aes(xend = km_capoluogo, yend = atteso),
               colour = COLORI_TERRITORIO[["Bagheria"]], linewidth = 0.6) +
  geom_text(data = vicini_30, aes(label = nome), size = 2.8, colour = "grey40",
            hjust = 0, nudge_x = 0.6) +
  annotate("text", x = bagheria$km_capoluogo + 1.5, y = bagheria$quota_fuori - 9, hjust = 0,
           size = 3.2, fontface = "bold", colour = COLORI_TERRITORIO[["Bagheria"]],
           lineheight = 1.05,
           label = paste0("Bagheria\n", virgola(bagheria$quota_fuori, 1, "%"), " osservato\n",
                          virgola(bagheria$atteso, 1, "%"), " atteso")) +
  scale_size_continuous(name = "pendolari del comune", range = c(0.8, 9),
                        breaks = c(1000, 5000, 10000), labels = migliaia) +
  scale_linetype_manual(name = NULL, values = c(`comune mediano` = "solid",
                                                `taglia di Bagheria` = "22")) +
  guides(linetype = guide_legend(order = 2, override.aes = list(linewidth = 0.5))) +
  scale_x_log10(breaks = c(2, 5, 10, 20, 40, 80), labels = function(x) paste0(virgola(x, 0), " km")) +
  scale_y_continuous(labels = function(y) virgola(y, 0, "%")) +
  labs(subtitle = paste0("A. Più lontani dal capoluogo e più grandi si è, meno si esce\n",
                         "le curve sono l'atteso del modello a due taglie fissate"),
       x = "distanza dal capoluogo di provincia (scala logaritmica)",
       y = "quota che esce dal comune per lavoro, 2021")

# --- B: il percentile, prima e dopo ---------------------------------------------------
# Due istogrammi impilati: sopra il grezzo, sotto il residuo. È lo stesso comune, la stessa
# misura, e la posizione cambia di dodici punti di percentile.
confronto <- bind_rows(
  transmute(comuni, valore = quota_fuori, pannello = "quota grezza"),
  transmute(comuni, valore = residuo, pannello = "residuo del modello\n(a parità di distanza e taglia)"))
righe_bagheria <- tibble::tibble(
  pannello = unique(confronto$pannello),
  valore = c(bagheria$quota_fuori, bagheria$residuo),
  percentile = c(percentile_grezzo, percentile_residuo))
mediane <- summarise(confronto, mediana = median(valore), .by = pannello)

posizione <- ggplot(confronto, aes(valore)) +
  geom_histogram(bins = 34, fill = "grey80", colour = "white", linewidth = 0.2) +
  geom_vline(data = mediane, aes(xintercept = mediana), colour = "grey35", linewidth = 0.5) +
  geom_vline(data = righe_bagheria, aes(xintercept = valore),
             colour = COLORI_TERRITORIO[["Bagheria"]], linewidth = 1) +
  geom_text(data = righe_bagheria, aes(x = valore, y = 36,
                                       label = paste0("Bagheria\n", virgola(percentile, 0, "° percentile"))),
            hjust = -0.1, vjust = 1, size = 3.1, fontface = "bold", lineheight = 1.05,
            colour = COLORI_TERRITORIO[["Bagheria"]]) +
  facet_wrap(~pannello, ncol = 1, scales = "free_x") +
  scale_x_continuous(labels = function(x) virgola(x, 0)) +
  labs(subtitle = paste0("B. La stessa Bagheria, prima e dopo il controllo\n",
                         "dal ", virgola(percentile_grezzo, 0, "°"), " al ",
                         virgola(percentile_residuo, 0, "° percentile"), ": l'anomalia era la taglia"),
       x = "quota che esce dal comune (%) e residuo (punti percentuali)", y = "comuni") +
  theme(panel.grid.major.x = element_blank())

figura <- (nuvola | posizione) +
  plot_layout(widths = c(1.25, 1)) +
  plot_annotation(
    title = "Bagheria non si muove poco: si muove quanto un comune della sua taglia a quella distanza",
    subtitle = paste0(
      "Il dato grezzo mette Bagheria al ", virgola(percentile_grezzo, 0, "° percentile"),
      " dei 381 comuni siciliani non capoluogo per quota di chi esce a lavorare.\n",
      "Sembra un'anomalia, e i vicini la rafforzano: Ficarazzi manda fuori tre pendolari su quattro, Bagheria due su cinque.\n",
      "Ma fuori comune si va per mancanza di lavoro dentro, e Bagheria è il comune più grande della corona: ",
      "12.000 pendolari contro i 3.000 di Ficarazzi.\n",
      "Controllando distanza e dimensione — due variabili geografiche, non di comportamento — il residuo è di ",
      virgola(bagheria$residuo, 1), " punti e il percentile sale al ",
      virgola(percentile_residuo, 0, "°"), ".\n",
      "La particolarità di Bagheria non è quanto si muove: è chi si muove, e per quale motivo (figure 2 e 3)."),
    caption = didascalia(paste0(
      "Fonte: ISTAT — Matrice del pendolarismo, censimento permanente 2021 (motivo lavoro), origine-destinazione comune per comune, conteggio esaustivo.\n",
      "Modello: minimi quadrati di quota_fuori su log(distanza dal capoluogo) e log(pendolari del comune), errori standard HC3, n = 381 comuni non capoluogo, R² = 0,31. ",
      "Entrambi i coefficienti sono negativi e significativi.\n",
      "Il modello serve a togliere di mezzo taglia e posizione, non a spiegare la mobilità: due regressori geografici, nessuna pretesa causale. ",
      "I nove capoluoghi sono esclusi perché per loro la misura non è definita.\n",
      "Distanza in linea d'aria fra i centroidi ISTAT (EPSG:32633): non è distanza stradale né tempo di viaggio, e per i comuni montani la sottostima.\n",
      "Elaborazione: notebooks/mobilita.ipynb — data/processed/mob_taglia_distanza.csv, mob_curva_attesa.csv"), LARGHEZZA),
    theme = tema_figura())

salva(figura, "mob_fig04_taglia_distanza", larghezza = LARGHEZZA, altezza = 18)

# Figura edu-06 — il gap con la Sicilia non si chiude (port R della fig06 del thread
# educazione). Dimostratore dell'assimilazione sul branch unison: dati da
# edu_gaps_vs_sicily.csv (pipeline/edu), tema e tipografia condivisi di theme.R.
# Fuori dal glob di build_all.R (^fig[0-9]+_): si lancia a mano finché il team non
# decide la numerazione delle figure educazione.
#
# Palette: qui le serie sono metriche, non territori né generi, quindi i colori
# riservati (vermiglio Bagheria, blu/rosa genere, viola/ambra territori) non si
# applicano ai loro significati. Il vermiglio marca la metrica-problema (fuori da
# lavoro e studio); nero e sky restano neutre. Da rivedere col team se queste
# figure entrano nel deck accanto alle fig01-11.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

SPEC <- tibble::tibble(
  metrica = c("quota_fuori_lavoro_studio", "quota_inattivi_non_studenti", "quota_occupati"),
  nome = c("fuori da lavoro e studio", "inattivi non studenti", "occupazione"),
  colore = c("#D55E00", "#000000", "#56B4E9"))

serie <- read_csv(file.path(PROCESSED, "edu_gaps_vs_sicily.csv"), show_col_types = FALSE) |>
  filter(dominio == "giovani", metrica %in% SPEC$metrica) |>
  inner_join(SPEC, by = "metrica")

ultimi <- serie |> slice_max(anno, n = 1, by = metrica)
gap_occ_18 <- serie$gap_bagheria_sicilia_pp[serie$metrica == "quota_occupati" & serie$anno == 2018]
gap_occ_24 <- serie$gap_bagheria_sicilia_pp[serie$metrica == "quota_occupati" & serie$anno == 2024]

figura <- ggplot(serie, aes(anno, gap_bagheria_sicilia_pp, colour = nome)) +
  buco_2020(-2.2) +
  geom_hline(yintercept = 0, linewidth = 0.5, colour = "grey30") +
  geom_line(linewidth = 1.05) +
  geom_point(size = 2) +
  geom_text(data = ultimi,
            aes(label = paste0(nome, "  ", virgola(gap_bagheria_sicilia_pp, 1, " p.p."))),
            hjust = 0, nudge_x = 0.12, size = 3.3, fontface = "bold", show.legend = FALSE) +
  scale_colour_manual(values = setNames(SPEC$colore, SPEC$nome), guide = "none") +
  scale_x_continuous(breaks = 2018:2024, limits = c(2018, 2026.6)) +
  scale_y_continuous(labels = function(x) virgola(x, 0)) +
  labs(
    title = "Il recupero non si è trasformato in convergenza con la Sicilia",
    subtitle = paste(
      "Giovani 15-24, differenza Bagheria − Sicilia in punti percentuali, 2018-2024.",
      paste0("\nL'occupazione resta ", virgola(abs(gap_occ_24), 1), " punti sotto (era ",
             virgola(abs(gap_occ_18), 1), " nel 2018); inattività e area fuori da lavoro e studio restano sopra."),
      "\nIl confronto in differenze regge alla rottura di misura 2019-2021 (comune a tutti i territori);",
      "\ni livelli delle singole componenti no — per questo qui si mostrano solo i gap."),
    x = NULL, y = "Bagheria − Sicilia (punti percentuali)",
    caption = paste(
      "Fonte: ISTAT, Censimento permanente della popolazione - condizione professionale, classe 15-24 anni, 2018-2024 (2020 non pubblicato).",
      "\nPer l'occupazione un gap negativo è sfavorevole; per inattivi e fuori da lavoro e studio è sfavorevole un gap positivo.",
      "\nElaborazione: pipeline/edu (thread educazione) - data/processed/edu_gaps_vs_sicily.csv")
  ) +
  tema_figura()

salva(figura, "edu_fig06_gap_sicilia", larghezza = 26, altezza = 15)

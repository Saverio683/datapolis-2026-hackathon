# Figura 3 — ritenzione di coorte 2021-2024 per genere.
# Il punto: il drenaggio ha tempi diversi per ragazzi e ragazze.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

dati <- read_csv(file.path(PROCESSED, "genere_coorti.csv"), show_col_types = FALSE) |>
  mutate(nome_territorio = factor(nome_territorio, levels = rev(ORDINE))) |>
  pivot_wider(id_cols = c(nome_territorio, coorte), names_from = genere,
              values_from = `ritenzione_%`, names_prefix = "rit_")

figura <- ggplot(dati, aes(y = nome_territorio)) +
  geom_vline(xintercept = 100, linetype = "dashed", colour = "grey55", linewidth = 0.4) +
  geom_segment(aes(x = rit_F, xend = rit_M, yend = nome_territorio),
               colour = "grey70", linewidth = 1.1) +
  # Diametri diversi: dove i due valori coincidono (Sicilia, 25-29) si vede un anello
  # invece di un punto solo, che sembrerebbe un dato mancante.
  geom_point(aes(x = rit_F, colour = "F"), size = 4.2) +
  geom_point(aes(x = rit_M, colour = "M"), size = 2.8) +
  facet_wrap(~coorte, ncol = 1) +
  scale_colour_manual(values = COLORI_GENERE, labels = ETICHETTE_GENERE) +
  scale_x_continuous(labels = function(x) paste0(x, "%")) +
  labs(
    title = "I ragazzi se ne vanno presto, le ragazze dopo i 25 anni",
    subtitle = paste("Quota della coorte ancora residente dopo tre anni (chi aveva 15-19 anni nel 2021 ne ha 18-22 nel 2024).",
                     "\nSotto il 100% la coorte si è ridotta. Bagheria non raggiunge il livello italiano in nessuna cella,",
                     "ma la perdita femminile\nsi concentra dopo i 25 anni — l'età in cui il vantaggio educativo dovrebbe",
                     "convertirsi in lavoro."),
    x = "residenti nel 2024 in % della coorte 2021", y = NULL,
    caption = paste("Fonte: ISTAT, Censimento permanente della popolazione — età singole, 2021 e 2024.",
                    "\nMisura netta su tre anni: comprende chi arriva, non distingue le destinazioni e include l'aggiustamento",
                    "post-censuario delle stime.\nSi leggono i pattern rispetto al riferimento nazionale, non i decimali.",
                    "\nElaborazione: notebooks/genere.ipynb — data/processed/genere_coorti.csv")
  )

salva(figura, "fig03_coorti", larghezza = 24, altezza = 18)

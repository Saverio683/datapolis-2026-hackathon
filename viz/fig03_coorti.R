# Figura 3 — ritenzione di coorte 2021-2024 per genere.
# Il punto: il drenaggio ha tempi diversi per ragazzi e ragazze.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# Il vicinato aggregato come quinta riga: coorti dei cinque comuni sommate e poi il
# rapporto (nel notebook), stessa metrica della fig07.
vicinato <- read_csv(file.path(PROCESSED, "genere_coorti_vicini.csv"), show_col_types = FALSE)
ETICHETTA_VICINATO <- vicinato$nome_territorio[1]
LIVELLI <- c("Bagheria", ETICHETTA_VICINATO, "Palermo", "Sicilia", "Italia")

dati <- bind_rows(
    read_csv(file.path(PROCESSED, "genere_coorti.csv"), show_col_types = FALSE),
    vicinato
  ) |>
  mutate(nome_territorio = factor(nome_territorio, levels = rev(LIVELLI))) |>
  pivot_wider(id_cols = c(nome_territorio, coorte), names_from = genere,
              values_from = `ritenzione_%`, names_prefix = "rit_")

# Serve al sottotitolo: la coorte in cui Bagheria e vicinato divergono.
COORTE_CHIAVE <- "25-29 nel 2021"
ritenzione_F <- function(territorio) {
  dati$rit_F[dati$nome_territorio == territorio & dati$coorte == COORTE_CHIAVE]
}

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
  scale_x_continuous(labels = function(x) virgola(x, 1, "%")) +
  labs(
    title = "I ragazzi se ne vanno presto, le ragazze dopo i 25 anni",
    subtitle = paste("Quota della coorte ancora residente dopo tre anni (chi aveva 15-19 anni nel 2021 ne ha 18-22 nel 2024).",
                     "\nSotto il 100% la coorte si è ridotta. Bagheria non raggiunge il livello italiano in nessuna cella,",
                     "ma la perdita femminile\nsi concentra dopo i 25 anni, l'età in cui il vantaggio educativo dovrebbe",
                     "convertirsi in lavoro.",
                     paste0("\nSulla coorte ", sub(" nel .*", "", COORTE_CHIAVE),
                            " le ragazze di Bagheria scendono a ", virgola(ritenzione_F("Bagheria"), 1, "%"),
                            ", nel vicinato salgono a ", virgola(ritenzione_F(ETICHETTA_VICINATO), 1, "%"),
                            ": non è di zona.")),
    x = "residenti nel 2024 in % della coorte 2021", y = NULL,
    caption = paste("Fonte: ISTAT, Censimento permanente della popolazione - età singole, 2021 e 2024.",
                    "\nMisura netta su tre anni: comprende chi arriva, non distingue le destinazioni e include l'aggiustamento",
                    "post-censuario delle stime.\nSi leggono i pattern rispetto al riferimento nazionale, non i decimali.",
                    "\nVicinato = i cinque comuni più vicini per distanza fra i centroidi: coorti sommate prima del rapporto, non media dei cinque rapporti.",
                    "\nElaborazione: notebooks/genere.ipynb - data/processed/genere_coorti.csv, genere_coorti_vicini.csv")
  )

# Figura a pannello unico: titolo e sottotitolo qui sono quelli della figura, non di un
# pannello, quindi vale il tema della figura (vedi la gerarchia in theme.R).
figura <- figura + tema_figura()

salva(figura, "fig03_coorti", larghezza = 24, altezza = 18)

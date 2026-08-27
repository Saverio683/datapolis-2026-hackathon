# Figura 2 — come si ripartisce la popolazione 15-24 fra i sei stati, per genere.
# Il punto: la quota di inattivi è simile fra i generi, la sua composizione no.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

STATI <- names(COLORI_STATO)

# Il vicinato aggregato entra come quinta barra, subito sotto Bagheria: conteggi dei
# cinque comuni sommati e poi le quote (nel notebook), non media delle cinque quote.
vicinato <- read_csv(file.path(PROCESSED, "genere_composizione_stato_dettaglio_vicini.csv"),
                     show_col_types = FALSE)
ETICHETTA_VICINATO <- vicinato$nome_territorio[1]
LIVELLI <- c("Bagheria", ETICHETTA_VICINATO, "Palermo", "Sicilia", "Italia")

dati <- bind_rows(
    read_csv(file.path(PROCESSED, "genere_composizione_stato_dettaglio.csv"),
             show_col_types = FALSE),
    vicinato
  ) |>
  filter(anno == 2024, genere %in% c("F", "M")) |>
  mutate(
    nome_territorio = factor(nome_territorio, levels = rev(LIVELLI)),
    stato = factor(stato, levels = STATI),
    genere = factor(ETICHETTE_GENERE[genere], levels = ETICHETTE_GENERE),
    # Etichette solo sui due segmenti che portano il finding. Restano nel dataset completo:
    # position_stack calcola le posizioni sullo stack intero, non sul sottoinsieme.
    etichetta = if_else(stato == "occupati" | (stato == "casalinghe/i" & quota >= 3),
                        virgola(quota, taglia_zero = FALSE), "")
  )

quota <- function(territorio, stato_scelto) {
  dati$quota[dati$nome_territorio == territorio & dati$stato == stato_scelto &
               dati$genere == ETICHETTE_GENERE[["F"]]]
}

figura <- ggplot(dati, aes(quota, nome_territorio, fill = stato)) +
  geom_col(width = 0.68, colour = "white", linewidth = 0.3,
           position = position_stack(reverse = TRUE)) +
  geom_text(aes(label = etichetta), position = position_stack(vjust = 0.5, reverse = TRUE),
            colour = "white", size = 3.1, fontface = "bold") +
  facet_wrap(~genere, ncol = 1) +
  scale_fill_manual(values = COLORI_STATO) +
  scale_x_continuous(expand = expansion(mult = c(0, 0.01)),
                     labels = function(x) paste0(x, "%")) +
  guides(fill = guide_legend(nrow = 1)) +
  labs(
    title = "Stessa quota di inattivi, ragioni opposte: una ragazza su sette è casalinga",
    subtitle = paste("Popolazione 15-24 anni per condizione, 2024. A Bagheria gli \"altri inattivi\" pesano quasi uguale nei due generi",
                     "\n(19,9% F contro 18,2% M), ma sono casalinghe il 13,4% delle ragazze e l'1,7% dei ragazzi: il triplo dell'incidenza",
                     "\nnazionale (4,6%). Etichette: quota di occupati e di casalinghe/i.",
                     paste0("\nNel vicinato la quota è la stessa (", virgola(quota(ETICHETTA_VICINATO, "casalinghe/i")),
                            "%), a Palermo il ", virgola(quota("Palermo", "casalinghe/i")),
                            "%: non è un'anomalia comunale ma un tratto di zona.")),
    x = NULL, y = NULL,
    caption = paste("Fonte: ISTAT, Censimento permanente della popolazione - tavola condizione professionale, classe 15-24 anni, 2024.",
                    "\nLa condizione è autodichiarata al censimento: marcatore del carico di cura, non sua misura diretta.",
                    "\nVicinato = i cinque comuni più vicini per distanza fra i centroidi: conteggi sommati e poi le quote, non media delle cinque quote.",
                    "\nElaborazione: notebooks/genere.ipynb - data/processed/genere_composizione_stato_dettaglio.csv, genere_composizione_stato_dettaglio_vicini.csv")
  )

# Figura a pannello unico: titolo e sottotitolo qui sono quelli della figura, non di un
# pannello, quindi vale il tema della figura (vedi la gerarchia in theme.R).
figura <- figura + tema_figura()

salva(figura, "fig02_composizione_stato", larghezza = 26, altezza = 16)

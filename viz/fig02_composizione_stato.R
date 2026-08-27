# Figura 2 — come si ripartisce la popolazione 15-24 fra i sei stati, per genere.
# Il punto: la quota di inattivi è simile fra i generi, la sua composizione no.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# L'ordine di impilamento non è quello della palette: prima chi è dentro lavoro o studio
# (occupati, studenti), poi tutti gli altri — così la graffa del «fuori da lavoro e
# istruzione» copre segmenti contigui. Le adiacenze nuove passano i check CVD (ΔE
# peggiore 13,1 in deutanopia), con in più lo stacco bianco fra i segmenti.
STATI <- c("occupati", "studenti", "in cerca", "casalinghe/i", "altra condizione", "pensione")
stopifnot(setequal(STATI, names(COLORI_STATO)))

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

quota <- function(territorio, stato_scelto, genere_scelto = "F") {
  dati$quota[dati$nome_territorio == territorio & dati$stato == stato_scelto &
               dati$genere == ETICHETTE_GENERE[[genere_scelto]]]
}

#' Somma delle quote disegnate per un gruppo di stati di Bagheria: serve al sottotitolo
#' (gli "altri inattivi" dei due generi) — lettura dei valori già in figura, non ricalcolo.
quota_stati <- function(stati_scelti, genere_scelto) {
  sum(dati$quota[dati$nome_territorio == "Bagheria" & dati$stato %in% stati_scelti &
                   dati$genere == ETICHETTE_GENERE[[genere_scelto]]])
}
ALTRI_INATTIVI <- c("casalinghe/i", "altra condizione", "pensione")

# La graffa del proxy: quota e persone arrivano dal notebook (la convenzione di calcolo
# sta lì, come chiede CLAUDE.md); qui si calcolano solo le POSIZIONI sullo stack, cioè
# da dove a dove corre la parentesi: dalla fine di occupati+studenti alla fine della barra.
fuori <- read_csv(file.path(PROCESSED, "genere_fuori_lavoro_istruzione.csv"),
                  show_col_types = FALSE) |>
  filter(nome_territorio == "Bagheria", anno == 2024, genere %in% c("F", "M")) |>
  mutate(genere = factor(ETICHETTE_GENERE[genere], levels = ETICHETTE_GENERE))

graffa <- dati |>
  filter(nome_territorio == "Bagheria") |>
  summarise(x0 = sum(quota[stato %in% c("occupati", "studenti")]),
            x1 = sum(quota), .by = genere) |>
  left_join(select(fuori, genere, quota_pct, persone), by = "genere") |>
  mutate(y = length(LIVELLI) + 0.58,
         etichetta = paste0("fuori da lavoro e istruzione: ", virgola(quota_pct),
                            "% — ", persone,
                            if_else(genere == ETICHETTE_GENERE[["F"]], " ragazze", " ragazzi")))

# Le casalinghe non sono spose: già coniugate dal registro (1° gennaio successivo al
# censimento) contro il conteggio delle casalinghe. Il floor tiene il claim prudente
# («almeno»): nulla dice che le coniugate siano tutte casalinghe.
casalinghe_n <- read_csv(file.path(PROCESSED, "genere_casalinghe.csv"), show_col_types = FALSE) |>
  filter(nome_territorio == "Bagheria", anno == 2024, genere == "F") |>
  pull(conteggio) |> round()
coniugate <- read_csv(file.path(PROCESSED, "genere_stato_civile.csv"), show_col_types = FALSE) |>
  filter(nome_territorio == "Bagheria", genere == "F", fascia == "15-24") |>
  filter(anno == max(anno))
NUBILI_PCT <- floor(100 * (casalinghe_n - coniugate$gia_coniugate) / casalinghe_n)

figura <- ggplot(dati, aes(quota, nome_territorio, fill = stato)) +
  geom_col(width = 0.68, colour = "white", linewidth = 0.3,
           position = position_stack(reverse = TRUE)) +
  geom_text(aes(label = etichetta), position = position_stack(vjust = 0.5, reverse = TRUE),
            colour = "white", size = 3.1, fontface = "bold") +
  # La graffa: tre segmenti (linea e due tacche) più l'etichetta, solo sulla barra di
  # Bagheria — annotare tutte e cinque le righe sarebbe rumore, e Bagheria è il soggetto.
  geom_segment(data = graffa, aes(x = x0, xend = x1, y = y, yend = y),
               inherit.aes = FALSE, colour = "grey35", linewidth = 0.35) +
  geom_segment(data = graffa, aes(x = x0, xend = x0, y = y, yend = y - 0.16),
               inherit.aes = FALSE, colour = "grey35", linewidth = 0.35) +
  geom_segment(data = graffa, aes(x = x1, xend = x1, y = y, yend = y - 0.16),
               inherit.aes = FALSE, colour = "grey35", linewidth = 0.35) +
  geom_text(data = graffa, aes(x = x1, y = y + 0.34, label = etichetta),
            inherit.aes = FALSE, hjust = 1, size = 3, colour = "grey25", fontface = "bold") +
  facet_wrap(~genere, ncol = 1) +
  scale_fill_manual(values = COLORI_STATO, breaks = STATI) +
  scale_x_continuous(expand = expansion(mult = c(0, 0.01)),
                     labels = function(x) paste0(x, "%")) +
  # aria sopra la prima barra, in entrambi i facet: è lo spazio di graffa ed etichetta
  scale_y_discrete(expand = expansion(add = c(0.55, 1.25))) +
  guides(fill = guide_legend(nrow = 1)) +
  labs(
    title = "Stessa quota di inattivi, ragioni opposte: una ragazza su sette è casalinga",
    subtitle = paste0(
      "Popolazione 15-24 anni per condizione, 2024. La graffa somma chi non è né al lavoro né a scuola — il proxy del NEET calcolabile\n",
      "a scala comunale («fuori da lavoro e istruzione»): più di un giovane su quattro, in entrambi i generi.\n",
      "Gli \"altri inattivi\" pesano quasi uguale (", virgola(quota_stati(ALTRI_INATTIVI, "F")),
      "% F contro ", virgola(quota_stati(ALTRI_INATTIVI, "M")),
      "% M), ma sono casalinghe il ", virgola(quota("Bagheria", "casalinghe/i")),
      "% delle ragazze e l'", virgola(quota("Bagheria", "casalinghe/i", "M")),
      "% dei ragazzi:\nquasi il triplo dell'incidenza nazionale (", virgola(quota("Italia", "casalinghe/i")),
      "%). E non sono spose: le già coniugate 15-24 sono ", coniugate$gia_coniugate,
      " contro ", casalinghe_n, " casalinghe — almeno l'", NUBILI_PCT, "% è nubile.\n",
      "Nel vicinato la quota di casalinghe è la stessa (", virgola(quota(ETICHETTA_VICINATO, "casalinghe/i")),
      "%), a Palermo l'", virgola(quota("Palermo", "casalinghe/i")),
      "%: non è un'anomalia comunale ma un tratto di zona."),
    x = NULL, y = NULL,
    caption = paste("Fonte: ISTAT, Censimento permanente della popolazione - tavola condizione professionale, classe 15-24 anni, 2024.",
                    "\nLa graffa è il proxy della convenzione di repo, non il NEET ISTAT 15-29 (a livello comunale esiste solo al 2011: fig08); include chi cerca lavoro.",
                    "\nIl «gruppo invisibile» — fuori anche dalla ricerca — sono gli ultimi tre segmenti: casalinghe/i, altra condizione, pensione.",
                    "\nLa condizione è autodichiarata al censimento: marcatore del carico di cura, non sua misura diretta. Etichette in barra: occupati e casalinghe/i.",
                    "\nStato civile da DCIS_POPRES1 (1° gennaio 2025), fonte diversa dal censimento: denominatori coincidenti alla singola unità; non osserva convivenze né maternità.",
                    "\nVicinato = i cinque comuni più vicini per distanza fra i centroidi: conteggi sommati e poi le quote, non media delle cinque quote.",
                    "\nElaborazione: notebooks/genere.ipynb - data/processed/genere_composizione_stato_dettaglio.csv, genere_composizione_stato_dettaglio_vicini.csv,",
                    "\ngenere_fuori_lavoro_istruzione.csv (graffa), genere_casalinghe.csv e genere_stato_civile.csv (nubili)")
  )

# Figura a pannello unico: titolo e sottotitolo qui sono quelli della figura, non di un
# pannello, quindi vale il tema della figura (vedi la gerarchia in theme.R).
figura <- figura + tema_figura()

salva(figura, "fig02_composizione_stato", larghezza = 26, altezza = 17)

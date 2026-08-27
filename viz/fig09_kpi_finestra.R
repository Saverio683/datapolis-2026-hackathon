# Figura 9 — il KPI della proposal e la sua finestra di lettura.
# Due domande che un amministratore fa prima di firmare: "quante persone?" e "come faccio
# a sapere se ha funzionato?". A sinistra la traduzione in persone (ogni quadratino sono
# dieci ragazze), a destra la soglia di rilevabilità: il +1,40 pp del KPI realistico non
# si vede su una lettura annuale, si vede su un triennio pooled.
# Tutti i numeri arrivano dal notebook: qui si dispongono, non si ricalcolano.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

UNITA <- 10   # ragazze per quadratino
COLONNE <- 20 # 20 x 15: il blocco è un po' più largo che alto, come il pannello che lo ospita,
              # così coord_equal lo fa crescere fino al bordo invece di lasciarlo piccolo in mezzo

# Il tasso di occupazione è il KPI primario della proposal e va letto per primo;
# facet_wrap altrimenti ordina in alfabetico e mette le casalinghe in cima.
ORDINE_KPI <- c("tasso di occupazione F 15-24", "quota casalinghe F 15-24")

#' Interi all'italiana: separatore di migliaia, e decimal.mark esplicito perché
#' altrimenti format() avverte che big.mark e decimal.mark coincidono.
migliaia <- function(x) format(x, big.mark = ".", decimal.mark = ",", trim = TRUE)

base <- read_csv(file.path(PROCESSED, "genere_base_persone.csv"), show_col_types = FALSE)
persone <- read_csv(file.path(PROCESSED, "genere_gap_persone.csv"), show_col_types = FALSE)
mde <- read_csv(file.path(PROCESSED, "genere_mde.csv"), show_col_types = FALSE)

popolazione <- base$popolazione_F_15_24[1]
occupate <- base$occupate_F_15_24[1]
anno <- base$anno[1]
delta <- function(s) persone[["occupate in più (2024)"]][persone$scenario == s]

# --- pannello A: le ragazze 15-24, un quadratino ogni dieci -------------------------
# Le classi sono cumulative e ordinate (oggi -> Palermo -> parità -> Italia -> il resto):
# i quadratini si ricavano dai cumulati arrotondati, così nessuno scarto si accumula.
CLASSI <- c("occupate oggi", "+ tasso di Palermo", "+ parità con i coetanei",
            "+ tasso nazionale", "non occupate")
cumulati <- c(occupate,
              occupate + delta("tasso femminile di Palermo"),
              occupate + delta("parità con i coetanei maschi di Bagheria"),
              occupate + delta("tasso femminile dell'Italia"),
              popolazione)
quadratini <- diff(c(0, round(cumulati / UNITA)))

etichette <- setNames(
  paste0(CLASSI, " (", migliaia(diff(c(0, cumulati))), ")"), CLASSI)

# Rampa ordinale su una tinta sola più il grigio del fondo: le classi hanno un ordine,
# non sono identità, quindi non serve — e non va usata — una palette categorica.
COLORI_WAFFLE <- setNames(
  c("#D55E00", "#EC8B4A", "#F6C4A0", "#FBE4D5", "#E4E4E1"), CLASSI)

griglia <- tibble(
    i = seq_len(sum(quadratini)),
    classe = factor(rep(CLASSI, quadratini), levels = CLASSI)
  ) |>
  mutate(colonna = (i - 1) %% COLONNE, riga = (i - 1) %/% COLONNE)

waffle <- ggplot(griglia, aes(colonna, -riga, fill = classe)) +
  geom_tile(width = 0.86, height = 0.86) +   # lo stacco fra i quadratini è il fondo, non un bordo
  scale_fill_manual(values = COLORI_WAFFLE, labels = etichette, name = NULL,
                    guide = guide_legend(ncol = 2, byrow = TRUE)) +
  coord_equal(clip = "off") +
  labs(subtitle = paste0("Le ", migliaia(popolazione), " ragazze 15-24 di Bagheria, ",
                         anno, "\nun quadratino = ", UNITA, " ragazze"),
       x = NULL, y = NULL) +
  theme(axis.text = element_blank(), panel.grid = element_blank(),
        legend.position = "bottom", legend.justification = "left")

# --- pannello B: la soglia di rilevabilità ------------------------------------------
# Rilevabile = MDE all'80% di potenza non più grande del delta che il KPI promette.
soglie <- mde |>
  rename(kpi = KPI, delta_pp = `delta da rilevare (pp)`, anni = `anni pooled per lato`,
         mde_pp = `MDE 80% (pp)`, potenza = `potenza per il delta (%)`) |>
  mutate(
    rilevabile = mde_pp <= abs(delta_pp),
    finestra = factor(paste0(anni, ifelse(anni == 1, " anno", " anni")),
                      levels = paste0(3:1, ifelse(3:1 == 1, " anno", " anni"))),
    kpi = factor(sub(" \\(obiettivo: Palermo\\)", "", kpi), levels = ORDINE_KPI))

riferimenti <- distinct(soglie, kpi, delta_pp)
# L'etichetta della soglia si scrive una volta sola, nel primo pannello: ripeterla
# raddoppierebbe il testo senza aggiungere niente.
prima_soglia <- filter(riferimenti, kpi == ORDINE_KPI[1])

potenza <- ggplot(soglie, aes(mde_pp, finestra)) +
  facet_wrap(~kpi, ncol = 1, scales = "free_y") +
  geom_vline(data = riferimenti, aes(xintercept = abs(delta_pp)),
             colour = "grey45", linewidth = 0.4, linetype = "dashed") +
  geom_segment(aes(x = 0, xend = mde_pp, yend = finestra, colour = rilevabile),
               linewidth = 2.4, lineend = "round") +
  geom_point(aes(colour = rilevabile), size = 4.2) +
  geom_text(aes(label = paste0("potenza ", virgola(potenza, 0, "%"))),
            hjust = -0.35, size = 3.3, fontface = "bold", colour = "grey20") +
  geom_text(data = prima_soglia, aes(x = abs(delta_pp), y = 3.62, label = "delta da rilevare"),
            hjust = -0.08, vjust = 0.5, size = 3.1, colour = "grey45") +
  scale_colour_manual(values = c(`TRUE` = "#0072B2", `FALSE` = "#9C9C9C"), guide = "none") +
  scale_x_continuous(limits = c(0, 3.9), expand = expansion(mult = c(0, 0.02))) +
  scale_y_discrete(expand = expansion(add = c(0.6, 1.15))) +
  coord_cartesian(clip = "off") +
  labs(subtitle = paste0("Quanto deve essere grande un effetto perché la lettura lo veda\n",
                         "MDE all'80% di potenza, per ampiezza della finestra"),
       x = "punti percentuali", y = NULL)

figura <- (waffle | potenza) +
  plot_layout(widths = c(0.85, 1.25)) +
  plot_annotation(
    title = "Quaranta ragazze: abbastanza poche da essere realistiche, abbastanza poche da non vedersi in un anno",
    subtitle = paste0(
      "Oggi ", occupate, " ragazze 15-24 su ", migliaia(popolazione),
      " lavorano. Allineare il tasso femminile a quello di Palermo vuol dire +",
      delta("tasso femminile di Palermo"), " occupate: il KPI realistico a 2-3 anni.\n",
      "La parità con i coetanei ne vorrebbe +", delta("parità con i coetanei maschi di Bagheria"),
      ", il tasso nazionale +", delta("tasso femminile dell'Italia"),
      ": quelli non sono obiettivi, sono la misura del problema.\n",
      "Ma +", delta("tasso femminile di Palermo"),
      " occupate valgono +1,40 punti, e una lettura annuale non distingue da zero nulla che stia sotto i 2,14.\n",
      "I KPI primari si leggono quindi su trienni pooled (2022-2024 contro 2025-2027); l'anno per anno spetta a\n",
      "indicatori di processo — utenza per età e genere — che oggi nessuno rileva."),
    caption = paste0(
      "Fonte: ISTAT, Censimento permanente della popolazione - condizione professionale, classe 15-24 anni, ", anno, ".\n",
      "MDE = differenza minima rilevabile a potenza 80% e alfa 5% fra due proporzioni (trasformazione arcoseno); \"anni pooled\" = ampiezza di ciascuno dei due lati del confronto.\n",
      "In grigio le finestre in cui l'effetto promesso è più piccolo della soglia. I quadratini sono arrotondati alla decina, i totali in legenda no.\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_base_persone.csv, genere_gap_persone.csv, genere_mde.csv"),
    theme = tema_figura()
  )

salva(figura, "fig09_kpi_finestra", larghezza = 28, altezza = 17)

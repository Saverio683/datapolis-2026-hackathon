# Tema e palette condivisi da tutti gli script di viz/.
# Caricato da ogni figura: nessuno stile inline duplicato, nessun ricalcolo dei dati.
# I dati arrivano già pronti da data/processed/ (Python scrive, R legge).

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(tidyr)
  library(readr)
  library(patchwork)
})

# Radice del repo: gli script funzionano sia lanciati dalla radice sia da viz/.
RADICE <- if (dir.exists("data/processed")) "." else ".."
PROCESSED <- file.path(RADICE, "data", "processed")
FIGURE <- file.path(RADICE, "figures")
dir.create(FIGURE, showWarnings = FALSE)

ORDINE <- c("Bagheria", "Palermo", "Sicilia", "Italia")

# Palette Okabe-Ito (colorblind-safe). Bagheria in vermiglio: è il soggetto, gli altri
# territori sono il contesto.
COLORI_TERRITORIO <- c(Bagheria = "#D55E00", Palermo = "#0072B2",
                       Sicilia = "#CC79A7", Italia = "#666666")

# Genere: mai rosa/azzurro. Arancio e verde-acqua, entrambi Okabe-Ito.
COLORI_GENERE <- c(F = "#E69F00", M = "#009E73")
ETICHETTE_GENERE <- c(F = "femmine", M = "maschi")

# Stati della condizione professionale: casalinghe/i in vermiglio perché è il finding.
COLORI_STATO <- c("occupati" = "#0072B2", "in cerca" = "#56B4E9", "studenti" = "#009E73",
                  "casalinghe/i" = "#D55E00", "altra condizione" = "#E69F00",
                  "pensione" = "#999999")

tema_datapolis <- function(base_size = 12) {
  theme_minimal(base_size = base_size) +
    theme(
      plot.title = element_text(face = "bold", size = rel(1.25), margin = margin(b = 4)),
      plot.subtitle = element_text(colour = "grey30", margin = margin(b = 12)),
      plot.caption = element_text(colour = "grey45", size = rel(0.8), hjust = 0,
                                  margin = margin(t = 12)),
      plot.title.position = "plot",
      plot.caption.position = "plot",
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(colour = "grey92", linewidth = 0.3),
      strip.text = element_text(face = "bold", hjust = 0),
      legend.position = "top",
      legend.title = element_blank(),
      legend.key.height = unit(0.8, "lines"),
      plot.margin = margin(12, 16, 10, 12)
    )
}

theme_set(tema_datapolis())

#' Esporta la figura in PNG 300dpi e SVG, come richiesto dalle convenzioni del repo.
#' svglite/ragg non compilano su questa macchina (mancano gli header di sistema):
#' si usano i device cairo di base, che coprono entrambi i formati.
salva <- function(figura, nome, larghezza = 24, altezza = 16) {
  pollici <- c(larghezza, altezza) / 2.54
  ggsave(file.path(FIGURE, paste0(nome, ".png")), figura, device = grDevices::png,
         width = pollici[1], height = pollici[2], dpi = 300, bg = "white")
  ggsave(file.path(FIGURE, paste0(nome, ".svg")), figura, device = grDevices::svg,
         width = pollici[1], height = pollici[2], bg = "white")
  message("scritto: ", nome, ".png / .svg")
}

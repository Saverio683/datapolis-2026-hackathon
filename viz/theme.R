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

# Tipografia: Lato se il sistema lo conosce (cairo passa da fontconfig), altrimenti
# il sans di default. Il controllo evita che la figura si rompa su una macchina senza.
FAMIGLIA <- tryCatch(
  if (any(grepl("Lato", system2("fc-match", "Lato", stdout = TRUE)))) "Lato" else "",
  error = function(e) ""
)

#' Numeri all'italiana nelle etichette: virgola decimale, zero finale opzionale.
#' virgola(97.5, 1, "%") -> "97,5%"   virgola(100, 1, "%") -> "100%"
#' virgola(2.01, 2, "×", taglia_zero = FALSE) -> "2,01×"
virgola <- function(x, decimali = 1, suffisso = "", taglia_zero = TRUE) {
  testo <- sprintf(paste0("%.", decimali, "f"), x)
  if (taglia_zero) testo <- sub("\\.0+$", "", testo)
  paste0(sub("\\.", ",", testo), suffisso)
}

# Palette Okabe-Ito (colorblind-safe). Bagheria in vermiglio: è il soggetto, gli altri
# territori sono il contesto.
COLORI_TERRITORIO <- c(Bagheria = "#D55E00", Palermo = "#0072B2",
                       Sicilia = "#CC79A7", Italia = "#666666")

# I cinque comuni geograficamente vicini a Bagheria: un colore pieno ciascuno, lo stesso
# in ogni figura che li mostra (fig01, fig06, fig07). L'ordine è per distanza crescente,
# i nomi li appaia ogni script leggendo il CSV: qui stanno i colori, non i comuni.
# Nessuno coincide con l'arancio di Bagheria, il blu di Palermo o i due colori del genere.
PALETTE_VICINI <- c("#56B4E9", "#CC79A7", "#785EF0", "#8C564B", "#000000")

# Il vicinato aggregato (fig07: coorti dei cinque comuni sommate) è un territorio a sé,
# non uno dei cinque: colore proprio, così non si confonde con Villabate & co.
# Il #44AA99 di prima stava sotto il chroma floor e sotto 3:1 di contrasto sul bianco:
# questo teal passa i check CVD contro tutti e quattro gli altri territori.
COLORE_VICINATO <- "#1B9E8F"

# Scala divergente per le figure di posizionamento (fig08): due poli caldo/freddo con un
# grigio neutro al centro, mai una tinta a metà. Vermiglio = Bagheria sta peggio del
# riferimento, blu = meglio, grigio = indicatore descrittivo senza un verso "buono".
DIVERGENTE <- c(peggio = "#D55E00", neutro = "#9C9C9C", meglio = "#0072B2")

#' I comuni vicini a Bagheria in ordine di distanza, con il colore già appaiato.
#' La selezione la fa il notebook sui centroidi: qui si legge, non si ricalcola.
vicini_di_bagheria <- function() {
  read_csv(file.path(PROCESSED, "genere_mappa_etichette.csv"),
           col_types = cols(territorio = "c", nome_comune = "c", ruolo = "c", .default = "d")) |>
    filter(ruolo == "vicino") |>
    arrange(distanza_km) |>
    mutate(colore = PALETTE_VICINI[row_number()])
}

# Genere: mai rosa/azzurro. Arancio e verde-acqua, entrambi Okabe-Ito.
COLORI_GENERE <- c(F = "#E69F00", M = "#009E73")
ETICHETTE_GENERE <- c(F = "femmine", M = "maschi")

# Stati della condizione professionale: casalinghe/i in vermiglio perché è il finding.
COLORI_STATO <- c("occupati" = "#0072B2", "in cerca" = "#56B4E9", "studenti" = "#009E73",
                  "casalinghe/i" = "#D55E00", "altra condizione" = "#E69F00",
                  "pensione" = "#999999")

tema_datapolis <- function(base_size = 12) {
  theme_minimal(base_size = base_size, base_family = FAMIGLIA) +
    theme(
      plot.title = element_text(face = "bold", size = rel(1.25), margin = margin(b = 4)),
      plot.subtitle = element_text(colour = "grey30", margin = margin(b = 12)),
      # Il footer è provenienza e cautele: deve restare leggibile ma non competere con
      # il grafico. grey55 sta a 3,4:1 sul bianco — sotto i 4,5:1 che WCAG chiede al
      # testo normale, sopra il minimo di 3:1: non scendere oltre.
      plot.caption = element_text(colour = "grey55", size = rel(0.72), hjust = 0,
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
# geom_text/geom_label non ereditano la famiglia dal tema: va fissata sui default.
update_geom_defaults("text", list(family = FAMIGLIA))
update_geom_defaults("label", list(family = FAMIGLIA))

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

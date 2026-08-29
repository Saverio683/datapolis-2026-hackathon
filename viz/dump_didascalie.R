# Estrae da ogni figura il titolo, il sottotitolo e i due blocchi della didascalia,
# SENZA ridisegnare i PNG (salva() viene neutralizzato: si costruisce il grafico e si
# butta via). Uscita: figures/didascalie.csv
#
# Perche' esiste. Chi incorpora una figura dentro un documento a larghezza di pagina
# ritaglia via titolo e didascalia del PNG e li rifa' nella tipografia del documento:
# a 16-17 cm quel testo scende sotto i 6 punti, cioe' illeggibile. E' la stessa regola
# gia' applicata alle schede HTML da pipeline/schede.py. Ma il testo rifatto deve
# restare QUELLO, con i numeri che didascalia_2b() ha calcolato dai CSV: riscriverlo a
# mano violerebbe la regola «nessuna cifra scritta a mano». Quindi non si ricopia, si
# intercetta.
#
# Come. Ogni script figura apre con la stessa identica riga di source() del tema; dopo
# quella riga si inietta la ridefinizione di didascalia_2b() e salva(), cosi' le versioni
# vere di theme.R vengono caricate e subito sostituite nell'ambiente dello script.
# Sostituire la riga invece di sourcare il tema a monte serve proprio a questo: e' il
# source() dello script a rimettere in gioco le funzioni originali.

VIZ <- if (dir.exists("viz")) "viz" else "."
source(file.path(VIZ, "theme.R"))

RIGA_SOURCE <- 'source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))'

OVERRIDE <- '
.dida <- c("", "")
didascalia_2b <- function(lettura, fonte, larghezza) {
  .dida <<- c(lettura, fonte)
  ""
}
salva <- function(figura, nome, larghezza = 24, altezza = 16) {
  # L`annotazione di patchwork PRIMA di p$labels: in una figura composta il patchwork
  # eredita le labels dell`ultimo pannello, quindi da p$labels si prende il titolo di quel
  # pannello al posto del sottotitolo della figura. Adesso che il sottotitolo porta il
  # "cosa mostra", quello scambio consegnerebbe il testo sbagliato.
  eti <- function(p, campo) {
    v <- if (!is.null(p$patches)) p$patches$annotation[[campo]] else NULL
    if (is.null(v)) v <- p$labels[[campo]]
    if (is.null(v)) "" else gsub("[\r\n]+", " ", paste(as.character(v), collapse = " "))
  }
  .raccolto[[length(.raccolto) + 1L]] <<- data.frame(
    nome = nome, larghezza_cm = larghezza, altezza_cm = altezza,
    titolo = eti(figura, "title"), sottotitolo = eti(figura, "subtitle"),
    lettura = .dida[1], fonte = .dida[2],
    stringsAsFactors = FALSE)
  message("letto: ", nome)
}
'

.raccolto <- list()

script <- list.files(VIZ, pattern = "^(edu_|mob_)?fig[0-9]+[a-z]?_.*\\.R$", full.names = TRUE)
for (s in script) {
  righe <- readLines(s, warn = FALSE)
  i <- which(trimws(righe) == RIGA_SOURCE)
  stopifnot("riga di source(theme.R) non trovata o ambigua" = length(i) == 1)
  testo <- append(righe, OVERRIDE, after = i)
  eval(parse(text = testo), envir = new.env(parent = globalenv()))
}

fuori <- do.call(rbind, .raccolto)
stopifnot(nrow(fuori) == length(script))
readr::write_csv(fuori, file.path(FIGURE, "didascalie.csv"))
message("scritto: figures/didascalie.csv (", nrow(fuori), " figure)")

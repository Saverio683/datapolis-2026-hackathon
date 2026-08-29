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

#' Interi all'italiana: separatore di migliaia, e decimal.mark esplicito perché
#' altrimenti format() avverte che big.mark e decimal.mark coincidono.
#' `scientific = FALSE` non è pignoleria: senza, format(500) dà «5e+02» — la notazione
#' scientifica scatta quando è più corta, e le etichette tonde sono proprio quelle a rischio.
migliaia <- function(x) format(x, big.mark = ".", decimal.mark = ",", trim = TRUE,
                              scientific = FALSE)

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
# Palermo e Sicilia non usano più blu e rosa: quei due colori adesso significano "maschi"
# e "femmine" in tutta la cartella, e un territorio che li indossa li smentisce.
COLORI_TERRITORIO <- c(Bagheria = "#D55E00", Palermo = "#785EF0",
                       Sicilia = "#E69F00", Italia = "#666666")

# I cinque comuni geograficamente vicini a Bagheria: un colore pieno ciascuno, lo stesso
# in ogni figura che li mostra (fig01, fig06, fig07). L'ordine è per distanza crescente,
# i nomi li appaia ogni script leggendo il CSV: qui stanno i colori, non i comuni.
# Nessuno coincide con il vermiglio di Bagheria, il viola di Palermo o i due colori del
# genere: il rosa e il viola che stavano qui sono usciti quando quei due sono stati presi.
PALETTE_VICINI <- c("#56B4E9", "#E69F00", "#009E73", "#8C564B", "#000000")

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

# Genere: blu per i maschi, rosa per le femmine — scelta esplicita del team, per una
# lettura immediata senza legenda. I due valori restano dentro Okabe-Ito (#0072B2 e
# #CC79A7), quindi la coppia resta distinguibile anche in protanopia e deuteranopia:
# è la convenzione di genere che cambia, non il requisito colorblind-safe.
COLORI_GENERE <- c(F = "#CC79A7", M = "#0072B2")
ETICHETTE_GENERE <- c(F = "femmine", M = "maschi")

# Stati della condizione professionale: casalinghe/i in vermiglio perché è il finding.
COLORI_STATO <- c("occupati" = "#0072B2", "in cerca" = "#56B4E9", "studenti" = "#009E73",
                  "casalinghe/i" = "#D55E00", "altra condizione" = "#E69F00",
                  "pensione" = "#999999")

#' Conteggio di annate in forma leggibile: «Bagheria ha il tasso più basso in tutte le 6
#' annate». Gli estremi si dicono a parole — «in 0 annate su 6» costringe il lettore a
#' tradurre una negazione in un conteggio, e «in 6 su 6» sottovende un primato senza
#' eccezioni. `frase` è l'estremo su quella scala, detto per esteso: «in testa» da solo si
#' legge come una contraddizione su un pannello dove la posizione peggiore è in basso.
frase_annate <- function(k, n, frase) {
  if (k == 0) paste0("Bagheria non ha mai ", frase)
  else if (k == n) paste0("Bagheria ha ", frase, " in tutte le ", n, " annate")
  else paste0("Bagheria ha ", frase, " in ", k, " annate su ", n)
}

#' La striscia del dato che manca: occupa lo spazio del buco invece di lasciarlo bianco,
#' perché la linea interrotta dice che manca qualcosa ma non cosa, e letta di corsa passa
#' per una scelta di impaginazione.
#'
#' A essere stretta è la COLONNA VUOTA, non il rettangolo: è l'asse a comprimersi dove il
#' dato manca (`asse_2020()` qui sotto, `asse()` in fig10), e la striscia riempie quel
#' vuoto per intero meno un margine per lato, così i suoi bordi non combaciano con le
#' annate ai lati. Lasciare largo il vuoto e stretto il rettangolo dice la stessa cosa in
#' peggio: il bianco attorno resta a suggerire un'annata misurata e vuota, che non c'è.
#' `y` è dove sta la scritta, perché ogni pannello ha la sua scala; il testo è verticale
#' (orizzontale sarebbe più largo della striscia) e corto: il dettaglio sta in caption.
#'
#' Va messa come ULTIMO layer, e la ragione è cambiata: prima stava per prima perché le
#' serie attraversavano il buco e la striscia le avrebbe coperte. Adesso non lo attraversa
#' nessuna serie — l'asse è compresso, il valore del 2020 è mancante e `buco_2020()` si
#' rifiuta di disegnare la striscia se non è vero — ma ci passavano ancora le righe di
#' riferimento (la parità in fig01, la mediana regionale in fig10) e le linee della
#' griglia, e una riga tirata dritta sopra un buco dice che lì qualcosa c'è.
#' Da ultima, la striscia le taglia tutte: il blocco è opaco, e sopra non passa niente.
VUOTO <- 0.62          # unità d'asse fra l'ultima annata prima del buco e la prima dopo
MARGINE_VUOTO <- 0.09  # di quanto il rettangolo resta dentro il vuoto, per lato

striscia_mancante <- function(da, a, y, etichetta) {
  list(
    annotate("rect", xmin = da + MARGINE_VUOTO, xmax = a - MARGINE_VUOTO,
             ymin = -Inf, ymax = Inf, fill = "grey93"),
    annotate("text", x = (da + a) / 2, y = y, size = 2.3, colour = "grey45", angle = 90,
             label = etichetta)
  )
}

#' Posizione sull'asse delle serie 2018-2024, dove il 2020 manca alla fonte. Le annate dal
#' 2021 scalano indietro di un anno, così fra il 2019 e il 2021 resta solo `VUOTO`: la
#' colonna stretta che la striscia riempie, invece di un'annata intera di bianco.
#' Il 2020 finisce a metà del vuoto e non fuori scala: le serie che lo tengono come riga a
#' valore mancante (fig01, fig05b) hanno bisogno che quel punto esista per interrompere la
#' linea lì in mezzo — con una x mancante la riga sparirebbe e il tracciato si richiuderebbe
#' sopra il buco, che è esattamente ciò che la striscia dice non essere successo.
#' Le pendenze dentro ciascun tratto restano quelle vere; sopra il vuoto non passa nessuna
#' linea, quindi non c'è nessuna pendenza da falsare.
asse_2020 <- function(anno) {
  ifelse(anno <= 2019, anno - 2018,
         ifelse(anno >= 2021, anno - 2020 + VUOTO, 1 + VUOTO / 2))
}

ANNI_2020 <- c(2018, 2019, 2021, 2022, 2023, 2024)

#' L'asse x delle serie 2018-2024: etichette gli anni, posizioni compresse sul buco.
scala_2020 <- function(...) {
  scale_x_continuous(breaks = asse_2020(ANNI_2020), labels = ANNI_2020, ...)
}

#' Il 2020 che manca alla fonte nelle serie 2018-2024 (fig01, fig05b, edu_fig06).
#' `anno` e `valore` sono le due colonne che la figura disegna, e servono al controllo:
#' la serie deve avere la riga vuota del 2020 (`complete(chiave, anno = ...)` a monte).
#' Senza quella riga la linea unisce 2019 e 2021 passando SOTTO il rettangolo, che è
#' opaco e la nasconde: la figura sembra a posto e non lo è. È la ragione del controllo —
#' questo errore non si vede guardando il PNG, si vede solo qui. Era il caso di edu_fig06.
#' ponytail: verifica che la riga vuota ci sia, non che ci sia per ogni serie; con
#' `complete()` o ci sono tutte o nessuna. Se una figura spezzerà a mano, passare al
#' controllo per gruppo.
#' fig10 non passa di qui: là lo stacco separa due rilevazioni e a tenere distinte le
#' serie è `group = interaction(..., epoca)`, non una riga mancante.
buco_2020 <- function(y, anno, valore) {
  stopifnot("manca la riga vuota del 2020: la linea passerebbe sotto la striscia" =
              any(anno == 2020 & is.na(valore)))
  striscia_mancante(asse_2020(2019), asse_2020(2021), y, "2020 non rilevato")
}

# Tre livelli tipografici, una sola famiglia. La gerarchia la fanno corpo, peso e colore:
# un secondo font richiederebbe che la macchina ce l'abbia (qui è garantito solo il
# fallback di Lato) e cairo in SVG converte comunque il testo in tracciati.
#   1. titolo della figura     grande, nero, bold      -> tema_figura()
#   2. sottotitolo della figura corpo pieno, grigio     -> tema_figura()
#   3. titolo di pannello       piccolo, scuro, bold    -> tema_datapolis(), qui sotto
# `plot.subtitle` porta due ruoli diversi a seconda di dove sta: dentro un sotto-grafico
# è il titolo del pannello (3), nell'annotazione di patchwork è il sottotitolo (2). Per
# questo tema_figura() lo rimette a corpo di testo: senza, i paragrafi verrebbero in bold.
tema_datapolis <- function(base_size = 12) {
  theme_minimal(base_size = base_size, base_family = FAMIGLIA) +
    theme(
      plot.title = element_text(face = "bold", size = rel(1.25), margin = margin(b = 4)),
      plot.subtitle = element_text(face = "bold", colour = "grey15", size = rel(0.98),
                                   lineheight = 1.05, margin = margin(b = 12)),
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
      # La legenda sta SEMPRE fra la didascalia e il grafico: "top" la mette sotto titolo
      # e sottotitolo e sopra il pannello, mai in fondo alla figura, dove si legge solo
      # dopo aver già provato a decifrare i colori da soli.
      # `legend.location = "plot"` la centra sulla larghezza della figura invece che su
      # quella del pannello: col default le etichette dell'asse y spostano il pannello a
      # destra e la legenda le segue, e in fig03 e fig12 si vedeva scentrata.
      legend.position = "top",
      legend.location = "plot",
      legend.justification = "center",
      legend.title = element_blank(),
      legend.key.height = unit(0.8, "lines"),
      plot.margin = margin(12, 16, 10, 12)
    )
}

#' Tema dell'annotazione di patchwork (titolo, sottotitolo e caption della figura intera)
#' e delle figure a pannello unico. Stacca il titolo dai titoli dei pannelli: un corpo e
#' mezzo più grande, nero pieno, e sotto un sottotitolo che torna testo normale.
tema_figura <- function(base_size = 12) {
  tema_datapolis(base_size) +
    theme(
      # 1,35 e non di più: a 1,45 il titolo di fig07, che è il più lungo del gruppo,
      # usciva dai 28 cm. Il salto sui titoli di pannello (rel 0,98) resta di un terzo.
      plot.title = element_text(face = "bold", size = rel(1.35), colour = "grey10",
                                lineheight = 1.1, margin = margin(b = 6)),
      plot.subtitle = element_text(face = "plain", colour = "grey30", size = rel(0.92),
                                   lineheight = 1.25, margin = margin(b = 14))
    )
}

theme_set(tema_datapolis())
# geom_text/geom_label non ereditano la famiglia dal tema: va fissata sui default.
update_geom_defaults("text", list(family = FAMIGLIA))
update_geom_defaults("label", list(family = FAMIGLIA))

#' Scosta verticalmente le etichette di fine linea quel tanto che basta a non
#' sovrapporsi. Serve quando due serie arrivano quasi allo stesso valore — ed è proprio
#' il caso interessante: in edu-08 Bagheria e la Sicilia finiscono a 0,02 punti l'una
#' dall'altra, che È il finding, e le due scritte finivano una sopra l'altra rendendo
#' illeggibile la cosa che la figura vuole mostrare.
#' Lo scostamento tocca SOLO il testo: i punti restano sul valore vero, e ogni figura che
#' la usa lo dichiara in caption. `gap` è nelle unità dell'asse y di quella figura.
scosta_etichette <- function(y, gap) {
  ordine <- order(y)
  scostato <- y[ordine]
  for (i in seq_along(scostato)[-1]) {
    scostato[i] <- max(scostato[i], scostato[i - 1] + gap)
  }
  scostato[order(ordine)]
}

#' Manda a capo un blocco di testo sulla larghezza della figura. Titoli, sottotitoli e
#' caption di questo repo sono lunghi — provenienza, fasce, cautele — e una riga che
#' supera la larghezza del PNG viene tagliata dal bordo senza che nulla lo segnali: il
#' testo sparisce e la figura sembra a posto. Qui ogni riga logica (separata da "\n" nel
#' testo di partenza) viene rimandata a capo sul budget di caratteri che entra davvero
#' nella larghezza dichiarata; le righe già corte restano dove sono, quindi gli "a capo"
#' scritti a mano per il ritmo del testo sopravvivono.
#' `larghezza` è la STESSA che si passa a salva(): tenerle legate è ciò che impedisce di
#' rimpicciolire una figura e scoprire il taglio solo guardando il PNG.
#' I due budget vengono da una misura sui rispettivi corpi con Lato: il sottotitolo sta a
#' rel 0,92 su base 12, la caption a rel 0,72, quindi nella stessa larghezza ci stanno
#' meno caratteri di sottotitolo che di caption.
#' ponytail: è una stima in caratteri, non una misura del testo renderizzato; se una
#' figura userà un corpo diverso, passare da strwrap a strwidth() su un device aperto.
CARATTERI_PER_CM <- c(sottotitolo = 5.5, didascalia = 6.6)

a_capo <- function(testo, larghezza, corpo) {
  budget <- floor(CARATTERI_PER_CM[[corpo]] * larghezza)
  righe <- strsplit(testo, "\n", fixed = TRUE)[[1]]
  paste(vapply(righe, function(r) paste(strwrap(r, width = budget), collapse = "\n"),
               character(1), USE.NAMES = FALSE),
        collapse = "\n")
}

sommario <- function(testo, larghezza) a_capo(testo, larghezza, "sottotitolo")
didascalia <- function(testo, larghezza) a_capo(testo, larghezza, "didascalia")

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

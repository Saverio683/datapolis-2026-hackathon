# Figura 4c — la graduatoria dei 390 comuni siciliani: chi sta in cima, chi in fondo, e
# dove ci stanno Bagheria, i suoi vicini e Palermo.
#
# Perché serviva. Le altre figure sui 390 rispondono ad altre domande e nessuna NOMINA gli
# estremi: la carta di fig04 non permette di ordinare (un choropleth non è una graduatoria),
# l'istogramma sotto mostra la distribuzione ma non le identità, fig04b etichetta solo
# Bagheria, i vicini e Palermo e parla di persistenza, non di posizione. Qui la domanda è
# una sola — chi sono i primi, chi gli ultimi, e dove cadiamo noi — e la forma è quella che
# le risponde: una graduatoria con i nomi.
#
# Perché NON uno slopegraph. Uno slopegraph esiste per mostrare il movimento fra due stati,
# e il movimento è già in fig04b. Peggio: fra il 2011 e il 2024 cambiano rilevazione e
# disegno (fig04 lo dichiara in caption), quindi le due annate si confrontano in percentili
# e non in punti percentuali — uno slopegraph sui livelli mentirebbe in silenzio. Questa
# figura sta su una sola annata, il 2024, e il problema non si pone.
#
# Un'annata sola, quindi: nessun confronto fra rilevazioni diverse, nessun percentile
# necessario. Il rango è stampato riga per riga perché le righe sono ordinate per valore ma
# spaziate uniformemente: fra due righe adiacenti possono starci ottanta comuni.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 28   # stessa misura del salvataggio: su questa il testo va a capo

QUANTI <- 8      # quanti comuni nominare in cima e quanti in fondo
X_MIN <- 12      # da dove partono le linee guida: sotto il minimo regionale
X_VALORE <- 41.5 # colonna del tasso, fuori dai dati
X_RANGO <- 46.5  # colonna del rango

comuni <- read_csv(file.path(PROCESSED, "genere_mappa_2011_2024.csv"),
                   col_types = cols(territorio = "c", nome_comune = "c", ruolo = "c",
                                    .default = "d"))
distribuzione <- read_csv(file.path(PROCESSED, "genere_distribuzione_390.csv"),
                          col_types = cols(fonte = "c", .default = "d"))
ANNO <- max(distribuzione$anno)
dopo <- distribuzione[distribuzione$anno == ANNO, ]

N <- nrow(comuni)
stopifnot(N == 390, !anyNA(comuni$rango_2024), !anyNA(comuni$donne_15piu_2024))

# I riferimenti del thread: Bagheria, i cinque comuni vicini, Palermo. Palermo nel file non
# ha `ruolo` — lì la colonna marca chi va etichettato sulla CARTA di fig04, e Palermo ha un
# richiamo suo — quindi si aggiunge per codice, come fa fig04.
PALERMO <- "082053"
RIFERIMENTI <- comuni |>
  filter(ruolo %in% c("Bagheria", "vicino") | territorio == PALERMO) |>
  mutate(gruppo = case_when(ruolo == "Bagheria" ~ "Bagheria",
                            territorio == PALERMO ~ "Palermo",
                            .default = "vicino"))
stopifnot(nrow(RIFERIMENTI) == 7)

# Dai riferimenti, non da `comuni$ruolo == "Bagheria"`: read_csv legge la cella vuota di
# `ruolo` come NA, il confronto restituisce NA sulle 383 righe senza ruolo e il subsetting
# lo propaga — il rango usciva NA nel titolo.
riferimento <- function(g) RIFERIMENTI[RIFERIMENTI$gruppo == g, ]
RANGO_BAGHERIA <- riferimento("Bagheria")$rango_2024
VICINI_RANGHI <- range(RIFERIMENTI$rango_2024[RIFERIMENTI$gruppo == "vicino"])

migliori <- comuni |> slice_min(rango_2024, n = QUANTI) |> mutate(gruppo = "estremo")
peggiori <- comuni |> slice_max(rango_2024, n = QUANTI) |> mutate(gruppo = "estremo")
# Se un riferimento finisse fra gli estremi comparirebbe due volte, con due righe e due
# ranghi uguali: meglio accorgersene qui che nel PNG.
stopifnot(!any(RIFERIMENTI$territorio %in% c(migliori$territorio, peggiori$territorio)))

# Il titolo e il sottotitolo affermano due cose sulle code: che quella alta è un blocco
# contiguo della costa ionica messinese e che quella bassa è tutta interna. La contiguità
# non sta in nessuna colonna — è una lettura della carta — quindi il claim va ancorato ai
# comuni che lo sostengono: se un'annata nuova li spinge fuori dagli otto, la figura si
# rifiuta di dirlo invece di dirlo a vuoto.
IONICI <- c("Taormina", "Letojanni", "Sant'Alessio Siculo", "Santa Teresa di Riva",
            "Furci Siculo")
stopifnot(all(IONICI %in% migliori$nome_comune))

# La città e il paese della coda bassa: non due nomi scelti a mano ma il comune con la
# platea più grande e quello con la più piccola fra gli otto in fondo. Se la coda cambia,
# cambiano da soli.
citta_coda <- slice_max(peggiori, donne_15piu_2024, n = 1)
paese_coda <- slice_min(peggiori, donne_15piu_2024, n = 1)

# L'altra coppia di claim del sottotitolo: Palermo sopra la mediana regionale, tutti gli
# altri riferimenti sotto. Vale oggi; se un'annata la ribalta, meglio un errore che una
# figura che continua a dirlo.

#' Una riga di rottura: dice quanti comuni stanno nel salto che il blocco successivo apre.
#' Il conto viene dai ranghi veri, non da una stima: se cambia la platea si aggiorna da sé.
rottura <- function(da, a) {
  tibble(nome_comune = paste0("· · ·   ", a - da - 1, " comuni   · · ·"), gruppo = "rottura")
}

righe <- bind_rows(
  arrange(migliori, rango_2024),
  rottura(max(migliori$rango_2024), min(RIFERIMENTI$rango_2024)),
  arrange(RIFERIMENTI, rango_2024),
  rottura(max(RIFERIMENTI$rango_2024), min(peggiori$rango_2024)),
  arrange(peggiori, rango_2024)
) |>
  mutate(ordine = row_number(),
         y = -ordine,
         etichetta = if_else(gruppo == "Bagheria", toupper(nome_comune), nome_comune))

punti <- filter(righe, gruppo != "rottura")
stacchi <- filter(righe, gruppo == "rottura")

# Il colore dice il ruolo, non il valore: gli estremi sono nominati e tanto basta, i
# riferimenti portano i colori che hanno in tutta la cartella.
COLORI_GRUPPO <- c(estremo = "grey35",
                   Bagheria = COLORI_TERRITORIO[["Bagheria"]],
                   Palermo = COLORI_TERRITORIO[["Palermo"]],
                   vicino = COLORE_VICINATO)

stopifnot(riferimento("Palermo")$occ_2024 > dopo$mediana,
          all(RIFERIMENTI$occ_2024[RIFERIMENTI$gruppo != "Palermo"] < dopo$mediana))

figura <- ggplot(punti, aes(occ_2024, y)) +
  # La mediana regionale attraversa tutto: senza, «23,7%» è un numero e non una posizione.
  geom_vline(xintercept = dopo$mediana, colour = "grey55", linetype = "dashed",
             linewidth = 0.4) +
  annotate("text", x = dopo$mediana - 0.25, y = 0.4, hjust = 1, vjust = 0, size = 3,
           colour = "grey40", fontface = "bold",
           label = paste0("mediana siciliana ", virgola(dopo$mediana, 1, "%"))) +
  # Linea guida piena, nel colore del suo punto: il punteggiato grigio era così tenue che
  # su venticinque righe l'occhio perdeva l'aggancio fra il nome e il pallino, e il colore
  # ripete a inizio riga il gruppo che il punto dichiara a fine corsa. Resta sottile e
  # trasparente perché NON è una barra: parte da X_MIN e non da zero, quindi la sua
  # lunghezza non misura niente — lo dice anche la caption.
  geom_segment(aes(x = X_MIN, xend = occ_2024, yend = y, colour = gruppo),
               linewidth = 0.45, alpha = 0.45) +
  geom_segment(data = stacchi, aes(x = X_MIN, xend = X_RANGO, y = y, yend = y),
               inherit.aes = FALSE, colour = "grey78", linewidth = 0.3, linetype = "dotted") +
  geom_point(aes(colour = gruppo, size = donne_15piu_2024)) +
  geom_text(aes(X_VALORE, label = virgola(occ_2024, suffisso = "%", taglia_zero = FALSE)),
            hjust = 1, size = 3.1, fontface = "bold", colour = "grey20") +
  geom_text(aes(X_RANGO, label = paste0(rango_2024, "°")),
            hjust = 1, size = 3.1, colour = "grey45") +
  scale_colour_manual(values = COLORI_GRUPPO, guide = "none") +
  # Scala logaritmica: le platee vanno da qualche centinaio di donne a qualche centinaio di
  # migliaia, tre ordini di grandezza. Su scala lineare Palermo sarebbe un disco e tutti gli
  # altri puntini invisibili. Il diametro qui è un ordine di grandezza, non una quantità.
  scale_size_continuous(trans = "log10", range = c(1.8, 7),
                        breaks = c(500, 5000, 50000, 200000),
                        labels = function(x) migliaia(x),
                        name = "residenti femmine 15+") +
  scale_y_continuous(breaks = righe$y, labels = righe$etichetta,
                     expand = expansion(add = c(0.8, 1.6))) +
  scale_x_continuous(limits = c(X_MIN, X_RANGO + 0.5), expand = expansion(0),
                     breaks = seq(15, 40, 5), labels = function(x) paste0(x, "%")) +
  guides(size = guide_legend(nrow = 1, override.aes = list(colour = "grey55"))) +
  labs(
    title = paste0("In cima la costa ionica, in fondo l'entroterra: Bagheria è ",
                   RANGO_BAGHERIA, "ª su ", N),
    subtitle = paste0(
      "Tasso di occupazione femminile 15 anni e più nei ", N, " comuni siciliani, ", ANNO,
      ". Gli otto in cima e gli otto in fondo, più i territori del thread al loro rango.\n",
      "Bagheria è al ", RANGO_BAGHERIA, "° posto con ",
      virgola(dopo$bagheria, 1, "%"), ", sotto la mediana regionale (",
      virgola(dopo$mediana, 1, "%"), "): e sotto la mediana ci stanno tutti e cinque i comuni\n",
      "vicini, dal ", VICINI_RANGHI[1], "° al ", VICINI_RANGHI[2],
      "°. Palermo è l'unico riferimento sopra la mediana (",
      virgola(riferimento("Palermo")$occ_2024, 1, "%"), ", ",
      riferimento("Palermo")$rango_2024, "°), ma non è in alto.\n",
      "La coda alta è un blocco geografico, non una lista di casi: ",
      paste(IONICI, collapse = ", "), "\nsono comuni contigui della costa ionica messinese.",
      " La coda bassa è tutta interna, ma mescola città vere come ", citta_coda$nome_comune,
      " (", migliaia(citta_coda$donne_15piu_2024), " donne 15+)\ne paesi minuscoli come ",
      paese_coda$nome_comune, " (", migliaia(paese_coda$donne_15piu_2024),
      "), dove il tasso è instabile: è la ragione per cui il punto ha la dimensione della platea."),
    x = NULL, y = NULL,
    caption = didascalia_4b(
      mostra = paste0(
        "graduatoria dei ", N, " comuni siciliani per tasso di occupazione femminile sulla popolazione di 15 anni e più, anno ", ANNO,
        ". Sono nominati gli ", QUANTI, " comuni in cima e gli ", QUANTI,
        " in fondo, più i sette territori di riferimento del thread (Bagheria, i cinque comuni vicini e Palermo) collocati al loro rango. ",
        "Una sola annata, quindi nessun confronto fra rilevazioni diverse e nessun movimento: il movimento sta in fig04b, la geografia in fig04."),
      base = paste0(
        "N = ", N, " comuni ai confini del 2011, gli stessi di fig04 e fig04b. Misiliscemi, istituito nel 2021 per distacco da Trapani, è l'unica esclusione. ",
        "Nessun intervallo di confidenza sui singoli comuni: sono conteggi censuari e non stime campionarie. ",
        "Nei comuni piccoli il tasso resta però instabile, perché poche persone spostano molti punti percentuali: è la ragione per cui il punto porta la dimensione della platea, e va tenuta presente leggendo le due code. ",
        "La fascia è quella di lungo periodo (15 anni e più, l'indicatore L11 del codebook 8milaCensus), diversa dalle serie 15-24 del thread: è contesto e non un termine di paragone."),
      lettura = paste0(
        "le righe sono ordinate per valore ma spaziate in modo uniforme, quindi la distanza verticale fra due righe non misura niente: fra due righe adiacenti possono starci decine di comuni, e il rango stampato a destra è l'unica misura della distanza. ",
        "Le righe punteggiate di rottura dicono quanti comuni stanno dentro ciascun salto. ",
        "La linea guida colorata parte da ", X_MIN, "% e non da zero, e non è una barra: serve solo a portare l'occhio dal nome al punto, e la sua lunghezza non è una quantità. ",
        "Il diametro del punto è il numero di residenti femmine di 15 anni e più, su scala logaritmica che copre tre ordini di grandezza: è un ordine di grandezza, non una quantità leggibile a occhio. ",
        "La riga tratteggiata verticale è la mediana regionale. Il colore dice il ruolo e non il valore: Bagheria in vermiglio e in maiuscolo, i cinque comuni vicini in verde acqua, Palermo in viola, i comuni delle due code in grigio scuro."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, popolazione di 15 anni e più, anno ", ANNO,
        ". Elaborazione: notebooks/genere.ipynb (data/processed/genere_mappa_2011_2024.csv per tasso, rango e platea femminile, genere_distribuzione_390.csv per la mediana)."),
      larghezza = LARGHEZZA)
  ) +
  theme(panel.grid.major.y = element_blank(), panel.grid.minor.x = element_blank())

# Figura a pannello unico: titolo e sottotitolo sono quelli della figura, non di un
# pannello, quindi vale il tema della figura (vedi la gerarchia in theme.R).
figura <- figura + tema_figura() +
  # Dopo tema_figura(), che è un tema completo e rimpiazza quello accumulato.
  theme(panel.grid.major.y = element_blank(), panel.grid.minor.x = element_blank(),
        axis.text.y = element_text(hjust = 0, colour = "grey20"))

salva(figura, "fig04c_graduatoria_390", larghezza = LARGHEZZA, altezza = 27)

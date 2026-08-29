# Figura 5b — la forbice nel tempo: Bagheria e il vicinato partono appaiati nel 2018-19 e
# si dividono dal 2021. Il vantaggio educativo delle ragazze si allarga solo a Bagheria,
# e in nessuna annata si converte in lavoro (fig05, fig11).
# Gli altri territori restano contesto in grigio: l'enfasi è la forma, l'identità la danno
# le etichette dirette a fine linea.
#
# Era il pannello destro della fig05. Sta in una figura sua perché la serie esiste solo
# sulla fascia 9-24 — l'unica pubblicata dal 2018 — mentre il quadrante della fig05 sta
# tutto sulla 15-24: affiancate, la caption doveva ripetere a ogni sguardo che le due
# misure non si sommano. Separata, la fascia si dichiara una volta e vale per tutto.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 24   # stessa misura del salvataggio: il testo va a capo su questa, non a occhio

serie <- read_csv(file.path(PROCESSED, "genere_forbice_serie.csv"),
                  col_types = cols(territorio = "c", nome_territorio = "c", .default = "d"))

# Il denominatore vero della quota di diplomate: la popolazione 9-24 su cui la tavola
# istruzione calcola i titoli. Serve alla didascalia, non al grafico.
istruzione <- read_csv(file.path(PROCESSED, "genere_istruzione.csv"), show_col_types = FALSE)

ETICHETTA_VICINATO <- grep("^vicinato", unique(serie$nome_territorio), value = TRUE)
stopifnot(length(ETICHETTA_VICINATO) == 1)
COLORI <- c(COLORI_TERRITORIO, setNames(COLORE_VICINATO, ETICHETTA_VICINATO))
ANNO <- max(serie$anno)
PRIMO <- min(serie$anno)

# Il 2020 manca alla fonte su ogni classe che contenga i 15-24: la riga vuota interrompe
# linee e cuneo invece di farli passare sopra il buco. Nessun valore inventato — e l'asse
# (`asse_2020`, in theme.R) non gli lascia nemmeno la sua colonna: fra 2019 e 2021 resta
# il vuoto stretto che la striscia grigia riempie.
lungo <- serie |>
  select(anno, nome_territorio, valore = vantaggio_istruzione_F_pp) |>
  complete(nome_territorio, anno = PRIMO:ANNO)

in_testa <- lungo |>
  filter(!is.na(valore)) |>
  summarise(testa = nome_territorio[which.max(valore)], .by = anno)
CONTEGGIO <- frase_annate(sum(in_testa$testa == "Bagheria"), nrow(in_testa),
                          "il vantaggio più ampio")

# Il cuneo fra le due lame: Bagheria sopra, vicinato sotto, in tutte le annate misurate.
cuneo <- lungo |>
  filter(nome_territorio %in% c("Bagheria", ETICHETTA_VICINATO)) |>
  tidyr::pivot_wider(names_from = nome_territorio, values_from = valore) |>
  rename(bagheria = Bagheria, vicinato = all_of(ETICHETTA_VICINATO))
stopifnot(all(cuneo$bagheria >= cuneo$vicinato, na.rm = TRUE))

contesto <- filter(lungo, !nome_territorio %in% c("Bagheria", ETICHETTA_VICINATO))
protagonisti <- filter(lungo, nome_territorio %in% c("Bagheria", ETICHETTA_VICINATO))

fine_serie <- lungo |>
  filter(anno == ANNO) |>
  mutate(
    protagonista = nome_territorio %in% c("Bagheria", ETICHETTA_VICINATO),
    testo = if_else(protagonista,
                    paste0(sub(" \\(5 comuni\\)", "", nome_territorio), " +", virgola(valore)),
                    nome_territorio),
    colore = case_when(nome_territorio == "Bagheria" ~ COLORI_TERRITORIO[["Bagheria"]],
                       nome_territorio == ETICHETTA_VICINATO ~ COLORE_VICINATO,
                       .default = "grey50"),
    peso = if_else(protagonista, "bold", "plain")
  )

# Il denominatore della fascia, per la didascalia: la popolazione 9-24 dell'ultimo anno.
enne_9_24 <- function(terr, g) {
  istruzione$popolazione_9_24[istruzione$nome_territorio == terr &
                                istruzione$genere == g & istruzione$anno == ANNO]
}

apertura <- filter(cuneo, anno == PRIMO)
chiusura <- filter(cuneo, anno == ANNO)

figura <- ggplot(protagonisti, aes(asse_2020(anno), valore, colour = nome_territorio)) +
  geom_ribbon(data = cuneo, aes(x = asse_2020(anno), ymin = vicinato, ymax = bagheria),
              inherit.aes = FALSE, fill = COLORI_TERRITORIO[["Bagheria"]], alpha = 0.10) +
  geom_line(data = contesto, aes(group = nome_territorio),
            colour = "grey72", linewidth = 0.5) +
  geom_point(data = contesto, colour = "grey72", size = 1.2) +
  geom_line(aes(linewidth = nome_territorio == "Bagheria")) +
  geom_point(size = 1.8) +
  geom_text(data = fine_serie, aes(x = asse_2020(ANNO) + 0.12, label = testo),
            hjust = 0, size = 3, colour = fine_serie$colore,
            fontface = fine_serie$peso) +
  annotate("text", x = asse_2020(PRIMO), y = 4.05, hjust = 0, vjust = 0, lineheight = 0.98,
           label = paste0("partivano appaiati:\n+", virgola(apertura$bagheria),
                          " e +", virgola(apertura$vicinato), " nel ", PRIMO),
           size = 2.9, colour = "grey45") +
  scale_colour_manual(values = COLORI, guide = "none") +
  scale_linewidth_manual(values = c(`TRUE` = 1.3, `FALSE` = 1.1), guide = "none") +
  scala_2020(expand = expansion(mult = c(0.03, 0.17))) +
  scale_y_continuous(expand = expansion(mult = c(0.10, 0.16))) +
  coord_cartesian(clip = "off") +
  buco_2020(y = 2.2, lungo$anno, lungo$valore) +
  labs(
    title = "Dal 2021 il vantaggio educativo delle ragazze\nsi allarga solo a Bagheria",
    subtitle = paste0(
      "Quanti punti separano la quota di diplomate da quella dei diplomati, ", PRIMO, "-", ANNO,
      ", fascia 9-24. Sopra lo zero le ragazze sono più istruite.\n",
      "Bagheria e i cinque comuni vicini partivano appaiati (+", virgola(apertura$bagheria),
      " e +", virgola(apertura$vicinato), " nel ", PRIMO,
      "): dal 2021 il cuneo si apre, e nel ", ANNO, " sono\n",
      "+", virgola(chiusura$bagheria), " contro +", virgola(chiusura$vicinato), ". ",
      CONTEGGIO, ", quindi non è un tratto di zona. In nessuna di queste annate\n",
      "il vantaggio si converte in lavoro (fig05)."),
    # Titolo d'asse corto: ruotato è alto quanto il testo, e per esteso finiva addosso
    # all'ultima riga del sottotitolo. Cosa misura lo dice già la prima riga lì sopra.
    x = NULL, y = "punti (F − M)",
    caption = didascalia_4b(
      mostra = paste0(
        "differenza in punti percentuali fra la quota di ragazze e la quota di ragazzi con almeno il diploma, sulla fascia 9-24 anni, dal ",
        PRIMO, " al ", ANNO, ", su cinque territori. Sopra lo zero le ragazze sono più istruite dei coetanei. ",
        "La fascia è il 9-24 perché è l'unica pubblicata a livello comunale su tutta la serie: la fotografia della fig05, che sta sulla 15-24, ",
        "misura una cosa vicina ma non la stessa, e i due numeri non vanno sommati né letti in sequenza."),
      base = paste0(
        "Denominatori della fascia 9-24 a Bagheria nel ", ANNO, ": ",
        migliaia(round(enne_9_24("Bagheria", "F"))), " ragazze e ",
        migliaia(round(enne_9_24("Bagheria", "M"))), " ragazzi. ",
        "Nessun intervallo di confidenza: sono conteggi censuari e non stime campionarie. ",
        "Il 2020 manca alla fonte su ogni classe che contenga i 15-24, in tutti i territori: la serie è interrotta e nessun valore è interpolato. ",
        "Per il vicinato i conteggi dei cinque comuni sono sommati prima della quota, non è la media delle cinque quote. ",
        "Attenzione al denominatore: la fascia 9-24 include bambini che non hanno ancora l'età del diploma, quindi il livello della quota non va letto come tasso di diplomati; ",
        "a essere confrontabile fra territori e nel tempo è la differenza fra i generi, che è ciò che la figura disegna."),
      lettura = paste0(
        "l'area vermiglio chiaro è il cuneo fra Bagheria e il vicinato, cioè quanto le due lame si sono aperte: la sua altezza è la distanza fra le due linee, non un intervallo di confidenza. ",
        "Bagheria è in vermiglio a tratto pieno, il vicinato in verde acqua; Palermo, Sicilia e Italia restano in grigio perché sono contesto, e si identificano dall'etichetta a fine linea. ",
        "La striscia grigia verticale fra il 2019 e il 2021 occupa l'annata mancante: dove c'è la striscia non c'è misura. ",
        "Vicinato = i cinque comuni più vicini per distanza fra i centroidi."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola istruzione, fascia 9-24 anni, ", PRIMO, "-", ANNO, ". ",
        "Elaborazione: notebooks/genere.ipynb (data/processed/genere_forbice_serie.csv e genere_istruzione.csv per i denominatori)."),
      larghezza = LARGHEZZA)) +
  tema_figura()

salva(figura, "fig05b_forbice_serie", larghezza = LARGHEZZA, altezza = 20)

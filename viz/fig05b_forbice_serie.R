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

serie <- read_csv(file.path(PROCESSED, "genere_forbice_serie.csv"),
                  col_types = cols(territorio = "c", nome_territorio = "c", .default = "d"))

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
      CONTEGGIO, ", quindi non è un tratto di zona — e in nessuna di queste annate\n",
      "il vantaggio si converte in lavoro (fig05)."),
    # Titolo d'asse corto: ruotato è alto quanto il testo, e per esteso finiva addosso
    # all'ultima riga del sottotitolo. Cosa misura lo dice già la prima riga lì sopra.
    x = NULL, y = "punti (F − M)",
    caption = paste0(
      "Fonte: ISTAT, Censimento permanente della popolazione - istruzione, fascia 9-24 anni, ", PRIMO, "-", ANNO, ".\n",
      "La fascia è il 9-24 perché è l'unica pubblicata a livello comunale su tutta la serie: la fotografia della fig05, che sta sulla 15-24, misura una cosa\n",
      "vicina ma non la stessa, e i due numeri non vanno sommati né letti in sequenza.\n",
      "Il 2020 manca alla fonte su ogni classe che contenga i 15-24: la striscia grigia occupa il buco, la linea è interrotta e non interpolata.\n",
      "Vicinato = i cinque comuni più vicini per distanza fra i centroidi: conteggi sommati e poi le quote, non media delle cinque quote.\n",
      "In grigio gli altri territori di confronto (Palermo, Sicilia, Italia): sono il contesto, e si identificano dall'etichetta a fine linea.\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_forbice_serie.csv")) +
  tema_figura()

salva(figura, "fig05b_forbice_serie", larghezza = 24, altezza = 16)

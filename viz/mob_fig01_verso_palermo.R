# Mobilità, figura 1 — dove vanno i pendolari di Bagheria.
# La relazione del progetto dichiara due volte che «nessuna fonte disponibile identifica
# Palermo come destinazione». La matrice del pendolarismo ISTAT lo fa: questa figura è la
# risposta letterale alla domanda del bando, con il nome del comune di arrivo.
# Geometria già proiettata da pipeline/build.py (EPSG:32633): qui si disegna e basta.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 30   # la stessa che va a salva(): a_capo() manda a capo su questa misura

confini <- read_csv(file.path(PROCESSED, "comuni_sicilia_poligoni.csv"),
                    col_types = cols(territorio = "c", nome_comune = "c", .default = "d"))
flussi <- read_csv(file.path(PROCESSED, "mob_flussi_bagheria.csv"),
                   col_types = cols(destinazione = "c", comune = "c", motivo = "c",
                                    .default = "d"))
sintesi <- read_csv(file.path(PROCESSED, "mob_sintesi.csv"),
                    col_types = cols(misura = "c", unita = "c", nota = "c", valore = "d"))

BAGHERIA <- "082006"
# Ritaglio sul corridoio Bagheria-Palermo. Tenere tutta la provincia significava disegnare
# la Sicilia occidentale per mostrare un flusso lungo 17 km: la carta si riduceva a un'unghia
# e le linee della coda lunga uscivano dal riquadro come raggi verso il nulla. Qui il
# riquadro contiene le otto destinazioni che valgono il 90% del flusso; tutto il resto è
# contato in un'unica etichetta, non disegnato come linea che esce dal bordo.
# Il riquadro è più largo del necessario a contenere i punti: le etichette stanno
# DENTRO il pannello, e con il ritaglio stretto "Palermo" e "Termini Imerese"
# venivano tagliate a metà dal bordo. I 7 km di margine per lato sono lo spazio
# che serve alla scritta più lunga.
XLIM <- c(336000, 401000)
YLIM <- c(4197000, 4233000)
provincia <- filter(confini, substr(territorio, 1, 3) == "082")
dentro_riquadro <- function(x, y) x >= XLIM[1] & x <= XLIM[2] & y >= YLIM[1] & y <= YLIM[2]
forma <- aes(x, y, group = interaction(territorio, parte), subgroup = anello)

# Le due scene: come si esce da Bagheria per studiare e come si esce per lavorare.
# Anni diversi perché il 2021 copre il solo lavoro — è scritto nel titolo di pannello e in
# caption, non nascosto in una nota.
SCENE <- tibble::tibble(
  anno = c(2011, 2021), motivo = c("studio", "lavoro"),
  etichetta = c("Per studiare (censimento 2011)", "Per lavorare (censimento permanente 2021)"))

# Le numerosità delle due scene: quante persone escono davvero dal comune. Una quota senza
# la sua base non dice se dietro «due su tre» ci siano duecento persone o duemila.
uscenti <- function(scena) sum(flussi$persone[flussi$anno == scena$anno &
                                                flussi$motivo == scena$motivo])
N_SCENE <- paste(vapply(seq_len(nrow(SCENE)), function(i)
  paste0(SCENE$motivo[i], " ", SCENE$anno[i], ": ", migliaia(round(uscenti(SCENE[i, ]))),
         " persone"), character(1)), collapse = "; ")

quota_dentro <- function(scena) {
  riga <- filter(flussi, anno == scena$anno, motivo == scena$motivo, destinazione == "082053")
  riga$quota_su_chi_esce
}

pannello <- function(i) {
  scena <- SCENE[i, ]
  tutte <- filter(flussi, anno == scena$anno, motivo == scena$motivo)
  d <- filter(tutte, dentro_riquadro(x_dest, y_dest))
  principale <- filter(d, destinazione == "082053")
  # Sotto l'1% le righe diventano un velo indistinguibile: si disegnano, ma sottili e
  # senza etichetta. L'etichetta va alle prime cinque, che coprono l'88% del flusso.
  etichettate <- slice_max(d, persone, n = 5) |>
    # Le destinazioni a est di Bagheria stanno in fila e le etichette si sovrappongono:
    # quelle a ovest di Palermo scrivono a sinistra, le altre a destra del proprio punto.
    mutate(lato = if_else(x_dest < principale$x_orig, 1, 0),
           x_lab = x_dest + if_else(lato == 1, -1200, 1200))
  altrove <- sum(tutte$quota_su_chi_esce) - sum(d$quota_su_chi_esce)

  ggplot() +
    geom_polygon(data = provincia, forma, rule = "evenodd",
                 fill = "grey96", colour = "white", linewidth = 0.15) +
    geom_segment(data = d, aes(x_orig, y_orig, xend = x_dest, yend = y_dest,
                               linewidth = persone, alpha = persone),
                 colour = COLORI_TERRITORIO[["Bagheria"]], lineend = "round") +
    geom_point(data = etichettate, aes(x_dest, y_dest, size = persone),
               colour = "grey20", fill = "white", shape = 21, stroke = 0.5) +
    geom_text(data = etichettate,
              aes(x_lab, y_dest, hjust = lato,
                  label = paste0(comune, "  ", virgola(quota_su_chi_esce, 0, "%"))),
              size = 3.1, colour = "grey15") +
    annotate("text", x = XLIM[1] + 600, y = YLIM[1] + 900, hjust = 0, vjust = 0, size = 2.9,
             colour = "grey45",
             label = paste0("altre destinazioni, fuori riquadro: ", virgola(altrove, 1, "%"))) +
    geom_point(data = distinct(d, x_orig, y_orig), aes(x_orig, y_orig),
               colour = COLORI_TERRITORIO[["Bagheria"]], size = 2.4) +
    annotate("text", x = principale$x_orig, y = principale$y_orig + 5200, label = "Bagheria",
             size = 3.2, fontface = "bold", colour = COLORI_TERRITORIO[["Bagheria"]]) +
    scale_linewidth_continuous(range = c(0.15, 6), guide = "none") +
    scale_alpha_continuous(range = c(0.25, 0.85), guide = "none") +
    scale_size_continuous(range = c(1.2, 5), guide = "none") +
    coord_equal(xlim = XLIM, ylim = YLIM, expand = FALSE) +
    labs(subtitle = paste0(scena$etichetta, "\n", virgola(quota_dentro(scena), 1, "%"),
                           " di chi esce dal comune va a Palermo"), x = NULL, y = NULL) +
    theme(axis.text = element_blank(), axis.ticks = element_blank(),
          panel.grid = element_blank())
}

# La coda: quanto del flusso resta fuori dal ritaglio provinciale, detto in caption.
fuori_provincia <- flussi |>
  summarise(quota = sum(quota_su_chi_esce[substr(destinazione, 1, 3) != "082"]),
            .by = c(anno, motivo))
studio <- filter(fuori_provincia, motivo == "studio")$quota
lavoro <- filter(fuori_provincia, anno == 2021)$quota

figura <- (pannello(1) | pannello(2)) +
  plot_annotation(
    title = "Bagheria ha un solo mercato esterno, e si chiama Palermo",
    # Gli a capo sono scritti a mano, come in fig04: il budget in caratteri di a_capo() è
    # una stima sul corpo del testo, e su 30 cm di larghezza sbordava di una decina di
    # caratteri per riga — il taglio avviene al bordo del PNG e nulla lo segnala.
    subtitle = paste0(
      "Dove vanno i residenti di Bagheria che escono dal comune, per motivo dello spostamento: a sinistra\n",
      "chi esce per studiare (censimento 2011), a destra chi esce per lavorare (censimento permanente 2021).\n",
      "Ogni linea unisce Bagheria a un comune di destinazione, e la percentuale accanto a ciascuna meta è\n",
      "la quota di chi esce che va lì: è la risposta letterale alla domanda del bando sul pendolarismo,\n",
      "con il nome del comune di arrivo.\n",
      "Nove studenti su dieci che escono dal comune vanno a Palermo (",
      virgola(quota_dentro(SCENE[1, ]), 1, "%"), "), e due lavoratori su tre (",
      virgola(quota_dentro(SCENE[2, ]), 1, "%"), ").\n",
      "Il secondo comune di destinazione resta sotto il 7%: la direzione è una sola.\n",
      "Su entrambe le misure Bagheria sta oltre il 90° percentile dei 381 comuni siciliani non capoluogo\n",
      "per quota di chi esce diretta al proprio capoluogo di provincia."),
    caption = didascalia_2b(
      lettura = paste0(
        "spessore e opacità di ogni linea sono proporzionali al numero di persone, e la dimensione del pallino sulla destinazione lo è al numero di arrivi. ",
        "Le linee sono rette fra i centroidi comunali e non percorsi reali: dicono quanti e verso dove, non per quale strada. ",
        "Il riquadro è il corridoio Bagheria-Palermo, 65 per 36 km, e contiene le destinazioni che valgono il 90% del flusso; ",
        "la quota rimasta fuori dal riquadro è annotata in basso a sinistra in ciascun pannello, invece di essere disegnata come una linea che esce dal bordo. ",
        "Sono nominate le prime cinque destinazioni di ogni scena. Il punto vermiglio è Bagheria, origine di tutte le linee. ",
        "Le due annate stanno una per pannello e non in serie: il 2011 conta chi si sposta giornalmente, il 2021 chi si reca al lavoro almeno tre giorni a settimana, e il 2021 copre il solo motivo lavoro. ",
        "Si confronta la composizione, cioè dove vanno su cento che escono, mai quanti escono. ",
        "La matrice non ha la dimensione dell'età, quindi il target 15-34 del bando non è isolabile su questa fonte; chi esce per studio è però quasi solo secondaria superiore e università, perché a Bagheria i cicli precedenti ci sono tutti."),
      fonte = paste0(
        "ISTAT, Matrici del pendolarismo, censimento della popolazione 2011 (studio) e censimento permanente 2021 (lavoro), origine-destinazione comune per comune, su ",
        N_SCENE, ". Confini: ISTAT, unità amministrative generalizzate al 01/01/2026, sistema di riferimento EPSG:32633 (WGS 84 / UTM 33N). ",
        "Elaborazione: notebooks/mobilita.ipynb (data/processed/mob_flussi_bagheria.csv)."),
      larghezza = LARGHEZZA),
    theme = tema_figura())

salva(figura, "mob_fig01_verso_palermo", larghezza = LARGHEZZA, altezza = 21)

# Figura edu-02 — dove si rompe la catena, 2011.
# Claim del thread educazione (invariato): nel 2011 la competenza di base tiene (almeno
# licenza media 15-19 al 96,7%), ma uscita precoce, NEET e occupazione giovanile stanno
# sotto il benchmark — e non solo rispetto all'Italia: anche rispetto alla Sicilia.
# Il passaggio critico non è l'acquisizione della licenza media.
#
# PERCHÉ QUESTA FORMA E NON QUATTRO GRUPPI DI BARRE (figures/edu/03).
# Con quattro indicatori per quattro territori le barre raggruppate sono sedici, e il
# confronto che il claim chiede — "Bagheria contro ciascun riferimento" — va fatto sedici
# volte a mente, perché ogni gruppo ha una scala di valori diversa (96,7% accanto a 20,0%
# schiaccia tutto il resto). Due problemi che spariscono ancorando la figura al soggetto:
#   1. l'asse non porta più il livello ma il VANTAGGIO sul valore di Bagheria, che è la
#      quantità di cui parla il claim. Bagheria sta sullo zero, e "chi è più avanti e di
#      quanto" si legge come distanza da una riga sola.
#   2. i versi si uniformano. Su uscita precoce e NEET scendere è meglio, sugli altri due
#      salire: in punti favorevoli tutti i riferimenti che stanno meglio finiscono a
#      destra, e la riga di I8 — l'unica dove Bagheria è davanti a Palermo e alla Sicilia —
#      diventa l'unica che sporge a sinistra. È esattamente il finding.
# Il livello grezzo di Bagheria non si perde: sta nell'etichetta di riga, dove serve come
# contesto e non come unità di confronto.
#
# Colore: i tre riferimenti prendono il colore che hanno in tutta la cartella
# (COLORI_TERRITORIO). Bagheria non è un pallino ma la riga dello zero: è il metro, non
# un termine di paragone fra gli altri.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# La larghezza sta qui e non solo in fondo: didascalia() ci manda a capo la caption, e
# le due devono restare lo stesso numero — altrimenti il testo esce dal bordo in
# silenzio, che è esattamente il modo in cui una caption sparisce senza accorgersene.
LARGHEZZA <- 28

benchmark <- read_csv(file.path(PROCESSED, "edu_historical_benchmarks_2011.csv"),
                      show_col_types = FALSE)

# La catena, nell'ordine in cui la si percorre: competenza di base, continuità, titolo
# raggiunto, ingresso nel lavoro. L'ordine è la spina dorsale della figura — è quello che
# rende "regge in cima, cede in fondo" una forma e non un elenco.
# `alto_favorevole` è il verso dichiarato dalla pipeline in edu_historical_bagheria.csv:
# qui si ricopia per avere l'anagrafica in un posto solo, e il controllo più sotto
# verifica che le due fonti non si siano separate.
CATENA <- tibble::tribble(
  ~indicatore, ~nome,                                   ~fascia, ~alto_favorevole,
  "I8",        "Almeno la licenza media",               "15-19", TRUE,
  "I5",        "Uscita precoce dalla formazione",       "15-24", FALSE,
  "I6",        "Diploma o laurea",                      "25-64", TRUE,
  "I7",        "Titolo universitario",                  "30-34", TRUE,
  "L4",        "NEET",                                  "15-29", FALSE,
  "L14",       "Occupazione giovanile",                 "15-29", TRUE)

# Il verso non si reinventa qui: se la pipeline cambiasse idea, la figura ribalterebbe in
# silenzio metà delle righe. Il controllo lo impedisce.
versi <- read_csv(file.path(PROCESSED, "edu_historical_bagheria.csv"),
                  show_col_types = FALSE) |>
  distinct(indicatore, direzione)
stopifnot(all(CATENA$indicatore %in% versi$indicatore))
stopifnot(identical(CATENA$alto_favorevole,
                    versi$direzione[match(CATENA$indicatore, versi$indicatore)] ==
                      "alto = favorevole"))

RIFERIMENTI <- c("Palermo", "Sicilia", "Italia")

bagheria <- benchmark |>
  filter(territorio_nome == "Bagheria") |>
  select(indicatore, valore_bagheria = valore)

dati <- benchmark |>
  filter(territorio_nome %in% RIFERIMENTI) |>
  inner_join(bagheria, by = "indicatore") |>
  inner_join(CATENA, by = "indicatore") |>
  mutate(
    # Punti FAVOREVOLI di vantaggio del riferimento su Bagheria. Dove scendere è meglio
    # il segno si ribalta, così un valore positivo significa sempre "il riferimento sta
    # meglio di Bagheria", su tutte e sei le righe.
    vantaggio = ifelse(alto_favorevole, valore - valore_bagheria,
                       valore_bagheria - valore),
    territorio_nome = factor(territorio_nome, levels = RIFERIMENTI),
    riga = factor(indicatore, levels = rev(CATENA$indicatore)))

stopifnot(nrow(dati) == nrow(CATENA) * length(RIFERIMENTI), !any(is.na(dati$vantaggio)))

# Le etichette di riga portano il livello grezzo di Bagheria e la fascia: il confronto
# sta sull'asse, il contesto sta qui, e nessuna delle due cose ruba il posto all'altra.
ETICHETTE <- CATENA |>
  inner_join(bagheria, by = "indicatore") |>
  mutate(testo = paste0(nome, "  ", fascia, "\nBagheria ", virgola(valore_bagheria, 1, "%"),
                        ifelse(alto_favorevole, "   ↑ meglio", "   ↓ meglio")))

# Quante righe hanno TUTTI i riferimenti davanti: è il conteggio che il titolo cita, e
# nasce dal dato invece di essere scritto a mano.
per_riga <- dati |>
  summarise(tutti_avanti = all(vantaggio > 0), .by = c(indicatore, nome))
N_INDIETRO <- sum(per_riga$tutti_avanti)
stopifnot(N_INDIETRO == nrow(CATENA) - 1,
          !per_riga$tutti_avanti[per_riga$indicatore == "I8"])

sicilia <- filter(dati, territorio_nome == "Sicilia")
valore_sicilia <- function(ind) abs(sicilia$vantaggio[sicilia$indicatore == ind])

figura <- ggplot(dati, aes(vantaggio, riga, colour = territorio_nome)) +
  # Lo zero è Bagheria: non una griglia di riferimento ma il soggetto della figura.
  geom_vline(xintercept = 0, linewidth = 0.9, colour = COLORI_TERRITORIO[["Bagheria"]]) +
  # Il segmento dallo zero al pallino: dà alla distanza una lunghezza da leggere, non solo
  # una posizione da stimare.
  geom_segment(aes(x = 0, xend = vantaggio, yend = riga), linewidth = 0.5,
               colour = "grey85") +
  geom_point(size = 4.4) +
  # Etichetta solo sulla Sicilia: è il benchmark del claim, e diciotto numeri su diciotto
  # pallini renderebbero illeggibile proprio il confronto che la figura serve.
  # Sopra il pallino e non di fianco: sulla riga della licenza media la Sicilia sta a
  # −0,2 dallo zero e l'etichetta, messa a sinistra, finiva sopra il pallino di Palermo.
  # Sopra non collide mai, qualunque sia la distanza fra due pallini della stessa riga.
  geom_text(data = sicilia,
            aes(label = paste0(ifelse(vantaggio > 0, "+", "−"),
                               virgola(abs(vantaggio), 1))),
            nudge_y = 0.3, vjust = 0, size = 3.1, fontface = "bold",
            show.legend = FALSE) +
  scale_colour_manual(values = COLORI_TERRITORIO[RIFERIMENTI], name = NULL) +
  scale_x_continuous(limits = c(-2.3, 19.4), breaks = seq(0, 18, 3),
                     labels = function(x) virgola(x, 0),
                     expand = expansion(mult = 0)) +
  scale_y_discrete(labels = setNames(ETICHETTE$testo, ETICHETTE$indicatore)) +
  guides(colour = guide_legend(override.aes = list(size = 4.4))) +
  labs(
    title = "Nel 2011 la scuola dell'obbligo a Bagheria tiene; il distacco comincia subito dopo",
    subtitle = sommario(paste0(
      "Distanza fra Bagheria e tre territori di riferimento (Palermo, Sicilia e Italia) su sei indicatori del censimento 2011, disposti lungo la catena che porta dalla competenza di base all'ingresso nel lavoro. ",
      "Lo zero è Bagheria: ogni pallino dice di quanti punti quel territorio sta MEGLIO di Bagheria, con il segno già ribaltato dove scendere è meglio (uscita precoce, NEET). ",
      "La catena è l'ordine logico dei passaggi, non una serie storica né una coorte seguita nel tempo.\n",
      "Sulla licenza media Bagheria è davanti a Palermo e alla Sicilia, ed è l'unica riga con pallini a sinistra dello zero. Sulle altre ",
      N_INDIETRO, " tutti e tre i riferimenti\n",
      "le stanno davanti, e la sola distanza dalla Sicilia vale ", virgola(valore_sicilia("I5"), 1),
      " punti sull'uscita precoce, ", virgola(valore_sicilia("L4"), 1), " sul NEET e ",
      virgola(valore_sicilia("L14"), 1), " sull'occupazione giovanile.\n",
      "Il passaggio critico sta dopo la licenza media."), LARGHEZZA),
    x = "punti percentuali di vantaggio sul valore di Bagheria (verso già uniformato)",
    y = NULL,
    caption = didascalia_2b(
      lettura = paste0(
        "ogni riga è un indicatore e i tre pallini sono i tre riferimenti. La riga verticale allo zero è la parità con Bagheria: a destra dello zero il riferimento sta meglio, a sinistra Bagheria sta meglio. ",
        "L'etichetta numerica compare solo sulla Sicilia, che è il riferimento citato nel testo; Palermo e Italia si leggono sull'asse. ",
        "Le righe hanno basi diverse e fasce d'età diverse, scritte in ogni riga: si confrontano il segno e l'ordine dei riferimenti, non la lunghezza di una riga contro quella di un'altra, e i sei valori non sono momenti successivi della stessa coorte. ",
        "Diploma o laurea 25-64 e titolo universitario 30-34 sono gli stessi indicatori di edu_fig01, qui al solo livello 2011: là interessa il movimento nel tempo, qui la posizione rispetto ai riferimenti."),
      fonte = paste0(
        "ISTAT, 8milaCensus, censimento 2011. ",
        "Elaborazione: pipeline/edu (thread educazione), data/processed/edu_historical_benchmarks_2011.csv e edu_historical_bagheria.csv."),
      larghezza = LARGHEZZA)
  ) +
  tema_figura() +
  theme(panel.grid.major.y = element_blank())

salva(figura, "edu_fig02_catena_2011", larghezza = LARGHEZZA, altezza = 22)

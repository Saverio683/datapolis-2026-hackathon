# Figura edu-08 — lo stock 15-34, il controllo che NON trova niente.
# Claim del thread educazione (invariato): fra 2021 e 2024 la popolazione 15-34 cala del
# 2,6% a Bagheria e del 2,6% in Sicilia. La dinamica è quasi parallela. Il dato serve come
# denominatore; NON sostiene nessuna conclusione sulla migrazione, perché lo stock non
# separa migrazioni, struttura per età e altri movimenti demografici.
#
# PERCHÉ QUESTA FIGURA ESISTE, ED È QUESTA FORMA.
# È l'unica figura del thread il cui risultato è un'assenza: serve a togliere dal tavolo
# la spiegazione più comoda ("i giovani se ne vanno da Bagheria più che altrove") prima
# che qualcuno la usi. Una figura che nega qualcosa deve rendere visibile la SOVRAPPOSIZIONE,
# non nasconderla: numeri indicizzati alla prima annata, così le quattro serie partono
# dallo stesso punto e la differenza fra le traiettorie è tutto ciò che resta da guardare.
# Le linee di Bagheria e della Sicilia si sovrappongono quasi perfettamente, ed è esattamente
# il messaggio — l'Italia, che invece diverge, è il metro che dimostra che la scala mostra
# le differenze quando ci sono.
# Niente barre: l'indice è una serie continua, e a quattro annate ravvicinate le barre
# renderebbero la coincidenza fra due serie più difficile da vedere, non più facile.
#
# Sui valori assoluti non si può mettere tutto insieme (12 mila contro 12 milioni): sarebbe
# il caso da due pannelli, ma il claim parla di ritmo, e il ritmo È l'indice. Gli assoluti
# di partenza stanno nell'etichetta, dove servono come contesto.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# La larghezza sta qui e non solo in fondo: didascalia() ci manda a capo la caption, e
# le due devono restare lo stesso numero — altrimenti il testo esce dal bordo in
# silenzio, che è esattamente il modo in cui una caption sparisce senza accorgersene.
LARGHEZZA <- 24

popolazione <- read_csv(file.path(PROCESSED, "edu_youth_population_15_34.csv"),
                        show_col_types = FALSE) |>
  mutate(territorio_nome = factor(territorio_nome, levels = ORDINE))

stopifnot(setequal(levels(popolazione$territorio_nome), unique(popolazione$territorio_nome)))

PRIMO <- min(popolazione$anno)
ULTIMO <- max(popolazione$anno)
# La serie 15-34 parte dal 2021 perché le età singole esistono solo da lì: non è una
# scelta di questo grafico ed è la ragione per cui la finestra è più corta delle altre.
stopifnot(PRIMO == 2021, all(popolazione$indice_primo_anno_100[popolazione$anno == PRIMO] == 100))

# Bagheria e la Sicilia arrivano a 0,02 punti l'una dall'altra: senza scostamento le due
# etichette di fine linea finiscono una sopra l'altra, e a diventare illeggibile è
# esattamente la coincidenza che la figura esiste per mostrare. Il punto resta sul valore.
GAP_ETICHETTE <- 0.34   # punti d'indice fra due etichette adiacenti

fine <- filter(popolazione, anno == ULTIMO) |>
  mutate(y_etichetta = scosta_etichette(indice_primo_anno_100, GAP_ETICHETTE))
inizio <- filter(popolazione, anno == PRIMO)

variazione <- function(terr) fine$variazione_da_primo_anno_pct[fine$territorio_nome == terr]
# Il claim dice "quasi parallela": qui si verifica che lo sia davvero, invece di fidarsi.
# Mezzo punto su tre anni è la soglia sotto cui le due serie non si distinguono a occhio.
DIVARIO <- abs(variazione("Bagheria") - variazione("Sicilia"))
stopifnot(DIVARIO < 0.5)

figura <- ggplot(popolazione, aes(anno, indice_primo_anno_100, colour = territorio_nome)) +
  geom_hline(yintercept = 100, linewidth = 0.5, colour = "grey75") +
  geom_line(linewidth = 1.15) +
  geom_point(size = 2.2) +
  geom_text(data = fine,
            aes(y = y_etichetta,
                label = paste0(territorio_nome, "  ",
                               ifelse(variazione_da_primo_anno_pct >= 0, "+", "−"),
                                     virgola(abs(variazione_da_primo_anno_pct), 1, "%"))),
            hjust = 0, nudge_x = 0.07, size = 3.4, fontface = "bold", show.legend = FALSE) +
  scale_colour_manual(values = COLORI_TERRITORIO, guide = "none") +
  scale_x_continuous(breaks = PRIMO:ULTIMO, limits = c(PRIMO, ULTIMO + 1.35),
                     expand = expansion(mult = 0)) +
  scale_y_continuous(labels = function(x) virgola(x, 0)) +
  labs(
    title = "Lo stock di giovani si assottiglia a Bagheria esattamente come in tutta la Sicilia",
    subtitle = sommario(paste0(
      "Popolazione residente nella fascia 15-34 anni dal ", PRIMO, " al ", ULTIMO,
      " su quattro territori, espressa come numero indice con base 100 nel ", PRIMO,
      ": quattro territori di dimensione incomparabile si confrontano così sul ritmo e non sui totali, e l'indice non dice nulla sui livelli.\n",
      "Bagheria perde il ", virgola(abs(variazione("Bagheria")), 1),
      "% dei suoi 15-34enni, la Sicilia il ", virgola(abs(variazione("Sicilia")), 1),
      "%: le due traiettorie divergono di poco a metà periodo e si richiudono, e alla fine distano ",
      virgola(DIVARIO, 2), " punti d'indice.\n",
      "È un risultato negativo, e serve: il calo giovanile di Bagheria è la demografia dell'isola, prima che un'anomalia locale da spiegare con la fuga.\n",
      "Che l'Italia nello stesso periodo faccia ",
      ifelse(variazione("Italia") >= 0, "+", "−"), virgola(abs(variazione("Italia")), 1),
      "% dimostra che questa scala le differenze le mostra, quando ci sono."), LARGHEZZA),
    x = NULL, y = paste0("indice, ", PRIMO, " = 100"),
    caption = didascalia_2b(
      lettura = paste0(
        "ogni linea è un territorio e parte da 100 nel ", PRIMO, ": la sua altezza in un'annata è quindi la variazione percentuale cumulata da quell'anno, non un valore assoluto. ",
        "Le etichette di fine linea sono scostate in verticale quel tanto che basta a non sovrapporsi, perché Bagheria e Sicilia arrivano a ",
        virgola(DIVARIO, 2), " punti d'indice l'una dall'altra: i pallini stanno sul valore vero, le scritte no. ",
        "Che le due linee siano quasi sovrapposte è il finding, e che l'Italia se ne stacchi dimostra che questa scala le differenze le mostra quando ci sono. ",
        "Lo stock non identifica la migrazione: una popolazione che si riduce somma nascite, morti, immigrazioni, emigrazioni e l'invecchiamento delle coorti che entrano ed escono dalla fascia, ",
        "e il numero non va citato come misura di chi se ne va. ",
        "La finestra parte dal ", PRIMO,
        " perché le età singole, necessarie a ricostruire la fascia 15-34, esistono solo da quell'anno: le altre figure del thread usano la classe 15-24 sul ",
        PRIMO - 3, "-", ULTIMO, ", e le due finestre restano separate."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, popolazione residente per età singola, fascia 15-34 anni, ",
        PRIMO, "-", ULTIMO, " (nel ", PRIMO, ": ",
        paste0(inizio$territorio_nome, " ", migliaia(inizio$popolazione_15_34), collapse = "; "),
        " residenti). Elaborazione: pipeline/edu (thread educazione), data/processed/edu_youth_population_15_34.csv."),
      larghezza = LARGHEZZA)
  ) +
  tema_figura()

salva(figura, "edu_fig08_popolazione", larghezza = LARGHEZZA, altezza = 19)

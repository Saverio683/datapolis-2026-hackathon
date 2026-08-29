# Figura edu-05 — istruzione e lavoro dei 25-49enni, due serie sullo stesso asse del tempo.
# Claim del thread educazione (invariato): nella fascia 25-49 Bagheria cresce su entrambe
# le dimensioni ma resta sotto la Sicilia su entrambe (almeno diploma 62,4% contro 66,5%;
# occupazione 53,6% contro 59,3% nel 2024). Il confronto è territoriale, non individuale:
# le due grandezze vengono da tavole aggregate separate e NON misurano l'occupazione dei
# diplomati.
#
# PERCHÉ L'ANNO SULL'ASSE E NON LO SCATTER CONNESSO, che è la forma che stava qui prima.
# La versione precedente metteva le due quote sui due assi e il tempo lungo la linea: una
# traccia per territorio, un punto per annata. Formalmente corretta e più densa — faceva
# vedere che le due traiettorie giacciono quasi sulla stessa retta — ma chiedeva al lettore
# di rinunciare all'asse del tempo, e non è una rinuncia che si fa da soli. Alla prova,
# letta dal team, ha prodotto due volte la stessa domanda: "perché il 2018 è in due punti
# diversi e le due linee non partono dallo stesso posto?". Non è una svista del lettore, è
# la forma: due traiettorie quasi collineari, con l'estremo di una a un passo dal percorso
# dell'altra, si richiudono in un unico percorso che sembra tornare indietro.
# Con l'anno sull'asse quella domanda non nasce. Il 2018 dei due territori sta sulla stessa
# verticale, la distanza VERTICALE fra le linee è il divario di quell'anno, e il ritardo
# diventa una distanza ORIZZONTALE misurabile invece di una lettura da fare a memoria sul
# piano. Si perde la collinearità delle due traiettorie, cioè esattamente il pezzo che
# confondeva; i tre pezzi del claim — sale su entrambe, resta sotto su entrambe, è indietro
# di anni — sopravvivono tutti e tre, e il terzo si legge meglio di prima.
# Due pannelli e non un asse doppio: le due misure hanno la stessa unità ma significati
# diversi, e sovrapporle in un pannello solo è la trappola classica del doppio asse.
#
# Colore: i due territori prendono quello che hanno in tutta la cartella. Il nome sta in
# fondo alla propria linea, dove l'occhio arriva: nessuna legenda da imparare.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# La larghezza sta qui e non solo in fondo: didascalia() ci manda a capo la caption, e
# le due devono restare lo stesso numero — altrimenti il testo esce dal bordo in
# silenzio, che è esattamente il modo in cui una caption sparisce senza accorgersene.
LARGHEZZA <- 30

# L'ordine è l'ordine dei pannelli: prima l'istruzione, poi il lavoro.
METRICHE <- c("quota_almeno_diploma", "quota_occupati_25_49")
TERRITORI <- c("Bagheria", "Sicilia")

gaps <- read_csv(file.path(PROCESSED, "edu_gaps_vs_sicily.csv"), show_col_types = FALSE) |>
  filter(dominio == "adulti", metrica %in% METRICHE)

NOME <- gaps |> distinct(metrica, metrica_label) |> (\(d) setNames(d$metrica_label, d$metrica))()

PRIMO <- min(gaps$anno)
ULTIMO <- max(gaps$anno)

# `complete()` sull'anno pieno serve al buco: la tavola lavoro non pubblica il 2020, e la
# riga a valore mancante è ciò che spezza la linea lì in mezzo. Senza quella riga geom_line
# unirebbe il 2019 al 2021 passando sotto la striscia grigia — la figura sembrerebbe a
# posto e non lo sarebbe. Qui il buco riguarda una sola delle due metriche, quindi l'asse
# NON si comprime come in fig01: comprimerlo disallineerebbe i due pannelli, che è proprio
# ciò che questa forma esiste per garantire.
serie <- gaps |>
  select(metrica, metrica_label, anno, all_of(tolower(TERRITORI))) |>
  pivot_longer(all_of(tolower(TERRITORI)), names_to = "territorio", values_to = "valore") |>
  mutate(territorio = factor(TERRITORI[match(territorio, tolower(TERRITORI))],
                             levels = TERRITORI)) |>
  complete(nesting(metrica, metrica_label), territorio, anno = PRIMO:ULTIMO) |>
  arrange(metrica, territorio, anno)

buchi <- serie |> filter(is.na(valore)) |> distinct(metrica, anno)
stopifnot(nrow(buchi) == 1, buchi$anno == 2020, buchi$metrica == METRICHE[[2]],
          nrow(serie) == length(METRICHE) * length(TERRITORI) * (ULTIMO - PRIMO + 1))

valore_di <- function(m, terr, a) {
  filter(serie, metrica == m, territorio == terr, anno == a)$valore
}

# Il ritardo, letto sui punti disegnati e non stimato: si prende il livello di Bagheria
# nell'ultima annata e si cerca la PRIMA annata in cui la Sicilia sta già a quel livello o
# sopra. È una misura per difetto — il sorpasso vero è avvenuto prima, in un punto fra due
# rilevazioni — e va bene così: un ritardo dichiarato più corto del vero non gonfia il
# claim. L'alternativa sarebbe interpolare l'incrocio, che qui non si fa.
anni_testo <- function(n) paste0(n, if (n == 1) " anno" else " anni")

ritardo <- serie |>
  filter(!is.na(valore)) |>
  summarise(
    livello = valore[territorio == "Bagheria" & anno == ULTIMO],
    raggiunto = min(anno[territorio == "Sicilia" & valore >= livello]),
    .by = c(metrica, metrica_label)
  ) |>
  mutate(anni = ULTIMO - raggiunto,
         sicilia = mapply(valore_di, metrica, "Sicilia", raggiunto))
stopifnot(nrow(ritardo) == length(METRICHE), all(ritardo$anni > 0),
          all(ritardo$sicilia >= ritardo$livello))

RIT <- setNames(ritardo$anni, ritardo$metrica)

pannello <- function(m) {
  d <- filter(serie, metrica == m)
  r <- filter(ritardo, metrica == m)
  p <- ggplot(d, aes(anno, valore, colour = territorio)) +
    # Il ritardo: il livello di Bagheria-oggi tirato indietro fino all'annata in cui la
    # Sicilia c'era già. Il trattino verticale chiude la lettura — dice che a quell'anno
    # la Sicilia stava sopra la riga, non sopra un punto qualsiasi.
    geom_segment(data = r, aes(x = raggiunto, xend = ULTIMO, y = livello, yend = livello),
                 inherit.aes = FALSE, linewidth = 0.45, linetype = "22", colour = "grey45") +
    geom_segment(data = r, aes(x = raggiunto, xend = raggiunto, y = livello, yend = sicilia),
                 inherit.aes = FALSE, linewidth = 0.4, colour = "grey65") +
    geom_text(data = r, aes(x = (raggiunto + ULTIMO) / 2, y = livello,
                            label = paste0("almeno ", anni_testo(anni), " di ritardo")),
              inherit.aes = FALSE, vjust = -0.8, size = 2.9, colour = "grey35") +
    geom_line(linewidth = 1.05, lineend = "round", na.rm = TRUE) +
    geom_point(size = 2.1, na.rm = TRUE) +
    geom_text(data = filter(d, anno == ULTIMO), aes(label = territorio), hjust = 0,
              nudge_x = 0.14, size = 3.5, fontface = "bold", show.legend = FALSE) +
    scale_colour_manual(values = COLORI_TERRITORIO[TERRITORI], guide = "none") +
    # Spazio a destra per il nome in fondo alla linea: senza, esce dal pannello.
    scale_x_continuous(breaks = PRIMO:ULTIMO, expand = expansion(mult = c(0.04, 0.20))) +
    # I break di default cadevano su 57,5 e 62,5 e l'etichetta a zero decimali li scriveva
    # "58%" e "62%": una griglia che dichiara un valore diverso da quello dove sta.
    # pretty() su questi intervalli (11 e 16 punti) restituisce passi interi.
    # ponytail: se una revisione stringerà il range sotto i ~5 punti pretty() tornerà a dare
    # mezzi punti e l'etichetta ricomincerà a mentire — allora servono i decimali.
    scale_y_continuous(breaks = function(l) pretty(l, 5),
                       labels = function(x) virgola(x, 0, "%")) +
    labs(subtitle = paste0(NOME[[m]], "\nnel ", ULTIMO, ": ",
                           virgola(valore_di(m, "Bagheria", ULTIMO), 1, "%"), " contro ",
                           virgola(valore_di(m, "Sicilia", ULTIMO), 1, "%")),
         x = NULL, y = NULL) +
    tema_datapolis()
  # La striscia per ultima: è opaca, e sopra non deve passare né la griglia né una riga di
  # riferimento — una riga tirata dritta sopra un buco dice che lì qualcosa c'è.
  if (m %in% buchi$metrica) {
    p <- p + striscia_mancante(2019.6, 2020.4,
                               y = mean(range(d$valore, na.rm = TRUE)), "2020 non rilevato")
  }
  p
}

figura <- wrap_plots(lapply(METRICHE, pannello), nrow = 1) +
  plot_annotation(
    title = paste0("Bagheria cresce su istruzione e lavoro, ma nel ", ULTIMO,
                   " è dove la Sicilia era già anni prima"),
    subtitle = sommario(paste0(
      "Due misure della stessa fascia 25-49, una per pannello, sullo stesso asse degli anni: il ",
      PRIMO, " di Bagheria e quello della Sicilia stanno sulla stessa verticale, e la distanza fra le due linee è il divario di quell'annata.\n",
      "Bagheria sale su tutte e due e il divario non si allarga, ma non aggancia mai: nel ", ULTIMO,
      " è al ", virgola(valore_di(METRICHE[[1]], "Bagheria", ULTIMO), 1, "%"),
      " di diplomati contro ", virgola(valore_di(METRICHE[[1]], "Sicilia", ULTIMO), 1, "%"),
      " e al ", virgola(valore_di(METRICHE[[2]], "Bagheria", ULTIMO), 1, "%"),
      " di occupati contro ", virgola(valore_di(METRICHE[[2]], "Sicilia", ULTIMO), 1, "%"), ".\n",
      "Il tratteggio porta il livello di Bagheria ", ULTIMO,
      " indietro fino all'annata in cui la Sicilia lo aveva già raggiunto: ",
      anni_testo(RIT[[METRICHE[[1]]]]), " sul diploma, ",
      anni_testo(RIT[[METRICHE[[2]]]]),
      " sull'occupazione. Il territorio non è fermo, è in ritardo."), LARGHEZZA),
    caption = didascalia_4b(
      mostra = paste0(
        "due misure della classe 25-49 anni a Bagheria e in Sicilia, una per pannello, sullo stesso asse degli anni, dal ",
        PRIMO, " al ", ULTIMO, ": a sinistra la quota con almeno il diploma, a destra il tasso di occupazione, entrambe in percentuale della popolazione della classe. ",
        "La figura dice se il territorio avanza su entrambe le dimensioni e quanto sia indietro rispetto alla Sicilia, non se sia lo stesso individuo a essere diplomato e occupato. ",
        "I due pannelli vengono infatti da due tavole aggregate distinte sulla stessa fascia d'età, e l'incrocio fra titolo di studio e condizione professionale non esiste nei dati comunali pubblici: questa non è l'occupazione dei diplomati."),
      base = paste0(
        "Due territori e ", ULTIMO - PRIMO + 1, " annate nominali. Nessun intervallo di confidenza: sono conteggi censuari e non stime campionarie. ",
        "Il ", buchi$anno, " esiste nella tavola istruzione e manca in quella lavoro: nel pannello destro la linea è interrotta e nessun valore è interpolato. ",
        "L'asse degli anni resta lineare in entrambi i pannelli perché il buco riguarda una sola delle due misure e i due pannelli devono restare allineati. ",
        "Il ritardo misurato dal tratteggio è letto sui punti osservati ed è una stima per difetto: il tratteggio parte dalla prima annata in cui la Sicilia sta già al livello che Bagheria raggiunge nel ",
        ULTIMO, ", quindi il sorpasso vero è avvenuto prima, in un punto fra due rilevazioni che qui non si stima. ",
        "La fascia 25-49 è quella dove le due tavole condividono l'età: è più larga del target 15-34 dell'hackathon e non va confusa con le serie 15-24 delle altre figure del thread."),
      lettura = paste0(
        "in ogni pannello le due linee sono Bagheria e la Sicilia sullo stesso asse degli anni, quindi la distanza verticale fra le due in un'annata è il divario di quell'annata. ",
        "La linea tratteggiata orizzontale porta il livello di Bagheria nel ", ULTIMO,
        " indietro nel tempo fino all'annata in cui la Sicilia lo aveva già raggiunto: la sua lunghezza è il ritardo in anni, ed è la quantità che il titolo enuncia. ",
        "I due pannelli hanno scale verticali proprie, perché misurano cose diverse: le altezze non vanno confrontate fra pannelli, solo le distanze dentro ciascuno."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola istruzione e tavola della condizione professionale, classe 25-49 anni, ",
        PRIMO, "-", ULTIMO, ". Elaborazione: pipeline/edu (thread educazione), data/processed/edu_gaps_vs_sicily.csv."),
      larghezza = LARGHEZZA),
    theme = tema_figura()
  )

salva(figura, "edu_fig05_forbice_25_49", larghezza = LARGHEZZA, altezza = 21)

# Figura 6b — dove sta Bagheria dentro la Sicilia, annata per annata. Una cresta per anno:
# la distribuzione del tasso di occupazione femminile nei 390 comuni siciliani, 2018-2024.
# Tutta la regione scivola a destra di quattro punti, Bagheria li guadagna anche lei, e
# resta comunque nel quinto più basso. Il muro non è un livello, è una posizione.
#
# Sostituisce la nuvola istruzione × occupazione che stava qui: con rho -0,24 su 390 punti
# mostrava un blob senza pendenza, e il percentile di Bagheria — il claim che regge —
# restava scritto in sottotitolo invece che visto. La stessa relazione sui quattro
# territori di confronto sta in fig06, che con quattro frecce la fa vedere davvero.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 24   # stessa misura del salvataggio: su questa il testo va a capo

creste <- read_csv(file.path(PROCESSED, "genere_creste_390.csv"),
                   col_types = cols(anno = "i", .default = "d"))
# Bagheria, mediana e percentile di ogni annata: la stessa tabella che alimenta fig04.
distrib <- read_csv(file.path(PROCESSED, "genere_distribuzione_390.csv"),
                    col_types = cols(anno = "i", fonte = "c", .default = "d")) |>
  filter(anno %in% creste$anno)

ANNI <- sort(unique(creste$anno))
# Una rilevazione sola in figura: se il 2011 di 8milaCensus arrivasse fin qui, lo scarto
# di definizione fra le due fonti si leggerebbe come movimento della distribuzione.
stopifnot(nrow(distrib) == length(ANNI), all(distrib$fonte == "censimento permanente"))

# 2018 in basso, 2024 in alto: dal basso verso l'alto si va avanti nel tempo, e lo
# scivolamento diventa una diagonale invece di sei profili da confrontare a memoria.
base_di <- setNames(seq_along(ANNI), ANNI)

# Le creste hanno tutte area 1 (verificato nel notebook), quindi le altezze si confrontano:
# una scala sola per tutte, mai una normalizzazione per cresta — con quella, un'annata più
# dispersa sembrerebbe alta come una concentrata.
#
# 1,3 su un passo di 1 è una sovrapposizione bassa per un joyplot, ed è deliberata: i gambi
# partono dalla linea di base, cioè esattamente dove la cresta davanti coprirebbe. Con la
# sovrapposizione larga il finding — i due gambi e il percentile a fianco — finirebbe sotto
# il riempimento dell'annata successiva.
ALTEZZA <- 1.3
SCALA <- ALTEZZA / max(creste$densita)

creste <- creste |>
  mutate(base = base_di[as.character(anno)],
         alto = base + densita * SCALA)

# Altezza della cresta di quell'anno nel punto x: serve a far arrivare il gambo fino al
# profilo, non a ricavare un dato. La curva è quella calcolata in Python, qui si legge.
altezza_a <- function(anno_, x_) {
  curva <- creste[creste$anno == anno_, ]
  approx(curva$x, curva$alto, xout = x_)$y
}

segni <- distrib |>
  mutate(base = base_di[as.character(anno)],
         y_bagheria = mapply(altezza_a, anno, bagheria),
         y_mediana = mapply(altezza_a, anno, mediana))

PRIMO <- filter(segni, anno == min(ANNI))
ULTIMO <- filter(segni, anno == max(ANNI))
PASSO_BAG <- ULTIMO$bagheria - PRIMO$bagheria
PASSO_MED <- ULTIMO$mediana - PRIMO$mediana
QUINTO <- 20  # il quinto più basso: la soglia che il titolo promette e che nessuna annata passa

# I due claim del titolo, verificati sul dato invece che ricopiati: Bagheria non passa mai
# il quinto più basso, e sei anni di crescita non le bastano a raggiungere dove stava la
# mediana regionale all'inizio. Se un giorno cadessero, titolo e tratteggio vanno riscritti
# insieme — non ristampati.
stopifnot(max(distrib$percentile) < QUINTO, ULTIMO$bagheria < PRIMO$mediana)

VERMIGLIO <- COLORI_TERRITORIO[["Bagheria"]]

# Un'annata alla volta, e dentro l'annata nell'ordine in cui va vista: il riempimento, i
# due gambi, il profilo che li chiude. Le annate vanno impilate dalla più lontana (2024, in
# fondo) alla più vicina (2018, davanti), così dove si sovrappongono è quella davanti a
# coprire. Con i layer globali — un geom_ribbon per tutte, poi un geom_segment per tutte —
# i gambi delle creste dietro finiscono disegnati sopra le creste davanti, e la pila si
# sfonda: si vedeva il gambo della mediana 2024 attraversare il 2023 e il 2022.
strato_annata <- function(a) {
  curva <- filter(creste, anno == a)
  segno <- filter(segni, anno == a)
  list(
    geom_ribbon(data = curva, aes(x = x, ymin = base, ymax = alto), fill = "grey94"),
    # Due gambi per cresta: la mediana regionale e Bagheria. Restano paralleli per sei
    # annate — è la distanza che non si chiude, ed è tutto il finding.
    geom_segment(data = segno, aes(x = mediana, xend = mediana, y = base, yend = y_mediana),
                 colour = "grey35", linewidth = 0.7),
    geom_segment(data = segno, aes(x = bagheria, xend = bagheria, y = base, yend = y_bagheria),
                 colour = VERMIGLIO, linewidth = 1.2),
    geom_line(data = curva, aes(x = x, y = alto), colour = "grey35", linewidth = 0.45),
    # Il percentile a fianco del gambo, annata per annata: è il "non esce mai dal quinto
    # più basso" del titolo, letto sulla figura invece che creduto sulla parola.
    geom_text(data = segno, aes(x = bagheria - 0.5, y = base + 0.08,
                                label = paste0(round(percentile), "°")),
              hjust = 1, vjust = 0, size = 3, colour = VERMIGLIO)
  )
}

figura <- ggplot() +
  Reduce(c, lapply(rev(ANNI), strato_annata)) +
  # Il tratteggio va per ultimo, sopra la pila: attraversandola tutta lascia vedere quanto
  # indietro sta il 2024 di Bagheria rispetto alla mediana del 2018, sei creste più in
  # basso. Messo per primo lo seppellivano i riempimenti, che sono opachi.
  geom_vline(xintercept = ULTIMO$bagheria, linetype = "dotted",
             colour = VERMIGLIO, linewidth = 0.45) +
  # Le due etichette stanno sulla cresta in cima, una volta sola: sotto, i gambi sono già
  # riconoscibili dal colore, e ripeterle sei volte aggiungerebbe inchiostro e non lettura.
  annotate("text", x = ULTIMO$bagheria - 0.8, y = ULTIMO$y_bagheria + 0.15,
           label = "Bagheria", hjust = 1, vjust = 0, size = 3.7, fontface = "bold",
           colour = VERMIGLIO) +
  annotate("text", x = ULTIMO$mediana + 0.8, y = ULTIMO$y_mediana,
           label = "mediana\nsiciliana", hjust = 0, vjust = 1, size = 3.4,
           lineheight = 0.95, fontface = "bold", colour = "grey35") +
  scale_x_continuous(breaks = seq(15, 40, by = 5), labels = function(v) paste0(v, "%"),
                     expand = expansion(mult = 0.01)) +
  scale_y_continuous(breaks = base_di, labels = ANNI,
                     expand = expansion(add = c(0.06, 0.8))) +
  labs(
    title = "Bagheria sale con tutta la Sicilia e non esce mai dal quinto più basso",
    subtitle = paste0(
      "Ogni cresta è la distribuzione dei 390 comuni siciliani in quell'anno. Il gambo scuro è la mediana regionale,\n",
      "quello vermiglio Bagheria, col suo percentile a fianco.\n",
      "In sei annate la mediana sale da ", virgola(PRIMO$mediana, 1, "%"), " a ", virgola(ULTIMO$mediana, 1, "%"),
      " e Bagheria da ", virgola(PRIMO$bagheria, 1, "%"), " a ", virgola(ULTIMO$bagheria, 1, "%"),
      ": guadagna più della mediana\n",
      "(+", virgola(PASSO_BAG, 1, taglia_zero = FALSE), " punti contro +", virgola(PASSO_MED, 1, taglia_zero = FALSE),
      ") e non supera mai il ", round(max(distrib$percentile)), "° percentile, cioè il quinto più basso della regione.\n",
      "Il tratteggio è il ", max(ANNI), " di Bagheria: cade ancora a sinistra della mediana siciliana del ", min(ANNI), "."),
    x = "tasso di occupazione femminile, 15 anni e più",
    y = NULL,
    caption = didascalia_4b(
      mostra = paste0(
        "distribuzione del tasso di occupazione femminile fra i comuni siciliani, una curva per anno, dal ", min(ANNI), " al ", max(ANNI),
        ". Ogni curva è una stima di densità sui comuni di quell'anno, non una serie storica: il tempo scorre dal basso verso l'alto, ",
        "e lo scivolamento verso destra è l'aumento generale dell'occupazione femminile in tutta la regione. ",
        "La stessa relazione sui quattro territori di confronto sta in fig06."),
      base = paste0(
        "N = 390 comuni siciliani per ciascuna delle ", length(ANNI), " annate disegnate. ",
        "Le curve sono stime di densità per nucleo con banda unica, scelta con la regola di Silverman sul pool delle annate: ",
        "così le differenze di forma sono del dato e non del lisciamento. Ogni curva ha area 1 e la scala verticale è comune, quindi anche le altezze si confrontano fra annate; ",
        "non c'è normalizzazione per singola curva, che farebbe sembrare alta un'annata dispersa quanto una concentrata. ",
        "Il 2020 manca alla fonte: le annate sono ", length(ANNI), " e non sette, e la curva di quell'anno semplicemente non esiste, senza interpolazione. ",
        "Il 2011 di 8milaCensus resta fuori perché è un'altra rilevazione, e una curva appaiata alle altre farebbe leggere lo scarto di definizione come movimento della distribuzione; ",
        "il confronto fra le due epoche sta in fig04 e fig04b, dove lo stacco è dichiarato. ",
        "Nessun intervallo di confidenza: la densità descrive i 390 comuni osservati, non stima una popolazione più ampia."),
      lettura = paste0(
        "ogni curva grigia è un'annata, etichettata sull'asse verticale, e le annate sono impilate dal ", min(ANNI), " in basso al ", max(ANNI), " in alto. ",
        "Dentro ogni curva ci sono due gambi verticali: quello scuro è la mediana regionale, quello vermiglio è Bagheria, con il suo percentile scritto a fianco. ",
        "La distanza fra i due gambi è il finding, e resta la stessa per tutte le annate. ",
        "La linea punteggiata verticale è il valore di Bagheria nel ", max(ANNI),
        " e attraversa tutta la pila: serve a vedere che cade ancora a sinistra della mediana siciliana del ", min(ANNI), ". ",
        "Le etichette «Bagheria» e «mediana siciliana» compaiono una volta sola, sulla curva in cima: sotto, i gambi si riconoscono dal colore."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, popolazione di 15 anni e più, 390 comuni siciliani, ",
        min(ANNI), "-", max(ANNI), ". Fascia e anni sono diversi dalle serie 15-24 del thread: è contesto regionale, non un termine di paragone. ",
        "Elaborazione: notebooks/genere.ipynb (data/processed/genere_creste_390.csv e genere_distribuzione_390.csv)."),
      larghezza = LARGHEZZA)) +
  tema_figura()

salva(figura, "fig06b_creste_390", larghezza = LARGHEZZA, altezza = 21)

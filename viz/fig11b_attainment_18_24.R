# Figura 11b — il controllo di robustezza sulla fascia in cui il diploma è raggiungibile.
# Il vantaggio femminile nel titolo di studio regge anche sul 18-24, dove chi non ha
# ancora finito la scuola non pesa più sul denominatore; il primato del 9-24 invece no —
# sul 18-24 Sicilia e Italia stanno sopra Bagheria.
# Serve a delimitare il claim: quello che distingue Bagheria non è il livello del diploma
# ma la conversione in lavoro (fig11, fig05).
#
# Era il pannello destro della fig11, che sta tutta sul 15-24. Due fasce nella stessa
# figura sono esattamente ciò che le convenzioni del thread vietano senza etichetta
# esplicita: separata, la fascia si dichiara nel titolo e non serve nessuna cautela.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 22   # stessa misura del salvataggio: su questa il testo va a capo

dati <- read_csv(file.path(PROCESSED, "genere_per_1000.csv"), show_col_types = FALSE)
anno_rif <- max(dati$anno)
dati <- filter(dati, anno == anno_rif)

ETICHETTA_VICINATO <- dati$nome_territorio[startsWith(dati$nome_territorio, "vicinato")][1]
LIVELLI <- c("Bagheria", ETICHETTA_VICINATO, "Palermo", "Sicilia", "Italia")
dati <- mutate(dati, nome_territorio = factor(nome_territorio, levels = rev(LIVELLI)))

QUOTA <- "almeno_diploma_18_24_bound_%"
v <- function(terr, gen) dati[[QUOTA]][dati$nome_territorio == terr & dati$genere == gen]
divario <- function(terr) v(terr, "F") - v(terr, "M")

# I due claim del titolo, letti dal dato: il vantaggio femminile c'è ovunque, ma sul
# 18-24 Bagheria non è più in testa. Se cambiassero, le frasi vanno riscritte.
# I denominatori della fascia disegnata: senza, cinque percentuali su territori di taglia
# diversissima non dicono su quante persone poggiano.
enne <- function(terr, gen) dati$pop_18_24[dati$nome_territorio == terr & dati$genere == gen]
N_TERRITORI <- paste(vapply(LIVELLI, function(t)
  paste0(t, " ", migliaia(round(enne(t, "F"))), " ragazze e ",
         migliaia(round(enne(t, "M"))), " ragazzi"), character(1)), collapse = "; ")

divari <- sapply(LIVELLI, divario)
sopra_bagheria <- LIVELLI[sapply(LIVELLI, \(t) v(t, "F")) > v("Bagheria", "F")]
stopifnot(all(divari > 0), length(sopra_bagheria) > 0)

figura <- ggplot(dati, aes(.data[[QUOTA]], nome_territorio)) +
  geom_line(aes(group = nome_territorio), colour = "grey75", linewidth = 1.8,
            lineend = "round") +
  geom_point(aes(colour = genere), size = 4.2) +
  # Stesso ancoraggio di fig08: hjust 0/1 più uno scostamento in unità di dato. Con un
  # hjust fuori scala (-0,45) il margine valeva una frazione della LUNGHEZZA del testo,
  # che qui è di due cifre: usciva più stretto del raggio del pallino e i numeri gli
  # finivano sopra.
  geom_text(aes(label = virgola(.data[[QUOTA]], 0),
                hjust = ifelse(genere == "F", 0, 1), colour = genere),
            nudge_x = ifelse(dati$genere == "F", 1.15, -1.15),
            size = 3.2, fontface = "bold", show.legend = FALSE) +
  scale_colour_manual(values = COLORI_GENERE, labels = ETICHETTE_GENERE, name = NULL) +
  scale_x_continuous(limits = c(58, 82), breaks = seq(60, 80, 5),
                     labels = \(x) virgola(x, 0, "%")) +
  labs(
    title = "Sul 18-24 il vantaggio delle ragazze regge,\nil primato di Bagheria passa ad altri",
    subtitle = sommario(paste0(
      "Quota di residenti di 18-24 anni con almeno il diploma, in percentuale dei coetanei della stessa fascia e dello stesso genere, ", anno_rif,
      ", su cinque territori: è la fascia in cui il titolo è già raggiungibile, quindi chi non ha ancora finito la scuola non pesa sul denominatore come accade sul 9-24. ",
      "Vale come controllo di robustezza del claim educativo.\n",
      "Il vantaggio femminile regge in tutti e cinque i territori, e a Bagheria vale +",
      virgola(divario("Bagheria")), " punti (", virgola(v("Bagheria", "F"), 0, "%"),
      " contro ", virgola(v("Bagheria", "M"), 0, "%"),
      "), il più ampio del panel. Ma sul livello passano avanti ",
      paste(sopra_bagheria, collapse = " e "),
      ". È il limite del claim educativo: a distinguere Bagheria è che il titolo resti fuori dal mercato del lavoro (fig11), più di quanto le ragazze studino."), LARGHEZZA),
    x = "% con almeno il diploma, 18-24 anni", y = NULL,
    caption = didascalia_2b(
      lettura = paste0(
        "ogni riga è un territorio e il segmento grigio unisce i due generi: la sua lunghezza è il divario. ",
        "Il pallino rosa è il valore femminile, quello blu il maschile, e la cifra accanto a ciascuno è il suo valore, stampata all'esterno per non coprire il pallino. ",
        "L'ordine delle righe è geografico, dal comune al paese, non per valore. ",
        "Il valore è un limite superiore e non una stima puntuale, perché qualche qualifica professionale si consegue a 17 anni: la quota vera è al più quella disegnata. ",
        "La fascia 18-24 è diversa sia dalla classe 15-24 su cui stanno le altre figure del thread sia dalla fascia 9-24 della serie storica di fig05b: le tre misure vanno lette una per volta. ",
        "Quante delle diplomate lavorino da qui non si ricava, perché l'incrocio fra titolo di studio e condizione professionale non è pubblicato a livello comunale. ",
        "Vicinato = i cinque comuni più vicini per distanza fra i centroidi: conteggi sommati e poi le quote, non media delle cinque quote."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola istruzione, anno ", anno_rif,
        ". Elaborazione: notebooks/genere.ipynb (data/processed/genere_per_1000.csv)."),
      larghezza = LARGHEZZA)) +
  tema_figura()

salva(figura, "fig11b_attainment_18_24", larghezza = LARGHEZZA, altezza = 18)

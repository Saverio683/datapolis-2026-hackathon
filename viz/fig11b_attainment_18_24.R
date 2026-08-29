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
    title = "Sul 18-24 il vantaggio delle ragazze resta,\nil primato di Bagheria no",
    subtitle = paste0(
      "Quota con almeno il diploma a 18-24 anni, ", anno_rif,
      ": la fascia in cui il titolo è raggiungibile, quindi chi non ha ancora\n",
      "finito la scuola non pesa sul denominatore. Il vantaggio femminile regge in tutti e cinque i territori — a Bagheria vale\n",
      "+", virgola(divario("Bagheria")), " punti (", virgola(v("Bagheria", "F"), 0, "%"),
      " contro ", virgola(v("Bagheria", "M"), 0, "%"),
      "), il più ampio del panel. Ma sul livello Bagheria non è più in testa:\n",
      paste(sopra_bagheria, collapse = " e "),
      " stanno sopra. È il limite del claim educativo: a distinguere Bagheria non è quanto\n",
      "le ragazze studiano, ma che il titolo non si converta in lavoro (fig11)."),
    x = "% con almeno il diploma, 18-24 anni", y = NULL,
    caption = paste0(
      "Fonte: ISTAT, Censimento permanente della popolazione - istruzione, anno ", anno_rif, ".\n",
      "Il 18-24 è un bound superiore: qualche qualifica IFP si ottiene a 17 anni, quindi la quota vera è al più questa (stessa logica dei bounds sulle casalinghe in fig02).\n",
      "Fascia diversa dal 15-24 su cui stanno le altre figure del thread e dal 9-24 della serie storica (fig05b): le tre misure non si sommano e non vanno lette in sequenza.\n",
      "L'incrocio titolo di studio × condizione professionale non è pubblicato a livello comunale: da qui non si ricava quante delle diplomate lavorino.\n",
      "Vicinato = i cinque comuni più vicini per distanza fra i centroidi: conteggi sommati e poi le quote, non media dei cinque valori.\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_per_1000.csv")) +
  tema_figura()

salva(figura, "fig11b_attainment_18_24", larghezza = 22, altezza = 14)

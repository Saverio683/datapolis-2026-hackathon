# Figura 5 — la forbice: più diplomate dei coetanei, eppure il tasso di occupazione più
# basso del panel. La congiunzione che dà il titolo si mostra come POSIZIONE — un
# quadrante con Bagheria da sola nell'angolo «più istruite, meno occupate» — invece che
# come due classifiche affiancate da unire a mente (la forma della prima versione).
# L'occupazione è in livello femminile, la scala che fig01 mostra reggere in ogni
# annata; il rapporto M/F resta in fig01, che è la figura delle scale.
# Il quadrante sta sulla STESSA fascia 15-24 (vantaggio calcolato nel notebook, export
# dedicato): cade la cautela «le due fasce non sono la stessa popolazione» sul claim
# principale. Su questa fascia il primato del vantaggio è un pareggio con la Sicilia
# (+4,8 contro +4,7): il claim è il distacco dal vicinato e la mancata conversione,
# non il primato assoluto — come da sintesi finale del notebook.
# La forbice nel tempo — Bagheria contro vicinato, appaiati nel 2018-19 e divisi dal
# 2021 — sta in fig05b: quella serie esiste solo sulla fascia 9-24, e affiancata al
# quadrante 15-24 costringeva a ripetere a ogni sguardo che le due misure non si sommano.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# --- i dati: la fotografia del quadrante, tutta sulla fascia 15-24 ----------------------
quadrante <- read_csv(file.path(PROCESSED, "genere_forbice_quadrante.csv"),
                      col_types = cols(territorio = "c", nome_territorio = "c", .default = "d"))

ETICHETTA_VICINATO <- grep("^vicinato", unique(quadrante$nome_territorio), value = TRUE)
stopifnot(length(ETICHETTA_VICINATO) == 1)
COLORI <- c(COLORI_TERRITORIO, setNames(COLORE_VICINATO, ETICHETTA_VICINATO))
ANNO <- max(quadrante$anno)

foto <- filter(quadrante, anno == ANNO)
valore <- function(terr, colonna) foto[[colonna]][foto$nome_territorio == terr]

# --- pannello A: il quadrante ----------------------------------------------------------
# Guide alla mediana dei cinque valori mostrati, come fig08 usa la mediana del gruppo:
# lettura dei valori disegnati, non un ricalcolo. Con cinque punti la mediana È il punto
# centrale, quindi due territori siedono esattamente sulle guide — corretto così.
MED_X <- median(foto$vantaggio_diploma_15_24_pp)
MED_Y <- median(foto$tasso_occupazione_F)

# Etichette dirette: nome + valori, in inchiostro e non nel colore della serie (l'ambra
# sul bianco non regge come testo); Bagheria in vermiglio bold perché è il soggetto,
# come le etichette di fig04 e fig10. Posizioni a mano: cinque punti, zero collisioni.
etichette_a <- foto |>
  mutate(
    testo = paste0(nome_territorio, "\n+", virgola(vantaggio_diploma_15_24_pp),
                   " pp · ", virgola(tasso_occupazione_F, 1, "%")),
    sopra = nome_territorio != ETICHETTA_VICINATO,   # solo il vicinato ha l'etichetta sotto
    y_testo = if_else(sopra, tasso_occupazione_F + 0.45, tasso_occupazione_F - 0.45),
    vjust = if_else(sopra, 0, 1),
    hjust = case_when(nome_territorio == "Bagheria" ~ 0.75,
                      nome_territorio == "Sicilia" ~ 0.75,
                      nome_territorio == ETICHETTA_VICINATO ~ 0.25,
                      nome_territorio == "Palermo" ~ 0.4,
                      .default = 0.5),
    colore = if_else(nome_territorio == "Bagheria", COLORI_TERRITORIO[["Bagheria"]], "grey25"),
    peso = if_else(nome_territorio == "Bagheria", "bold", "plain")
  )

pann_a <- ggplot(foto, aes(vantaggio_diploma_15_24_pp, tasso_occupazione_F,
                           colour = nome_territorio)) +
  geom_vline(xintercept = 0, linetype = "dashed", colour = "grey55", linewidth = 0.4) +
  annotate("text", x = 0, y = 7.4, label = "parità F = M", angle = 90, vjust = 1.35,
           size = 2.7, colour = "grey45") +
  geom_hline(yintercept = MED_Y, linetype = "dashed", colour = "grey70", linewidth = 0.35) +
  geom_vline(xintercept = MED_X, linetype = "dashed", colour = "grey70", linewidth = 0.35) +
  annotate("text", x = 5.55, y = MED_Y + 0.28, label = "mediana", hjust = 1,
           size = 2.6, colour = "grey50") +
  annotate("text", x = MED_X, y = 6.55, label = "mediana", angle = 90, vjust = -0.35,
           hjust = 0, size = 2.6, colour = "grey50") +
  annotate("text", x = 5.55, y = 6.75, hjust = 1, vjust = 1, lineheight = 0.95,
           label = "più istruite,\nmeno occupate", size = 3.1, colour = "grey45") +
  geom_point(aes(size = nome_territorio == "Bagheria")) +
  geom_text(data = etichette_a,
            aes(y = y_testo, label = testo, vjust = vjust, hjust = hjust),
            colour = etichette_a$colore, fontface = etichette_a$peso,
            size = 3.2, lineheight = 0.98) +
  scale_colour_manual(values = COLORI, guide = "none") +
  scale_size_manual(values = c(`TRUE` = 5, `FALSE` = 4.2), guide = "none") +
  scale_x_continuous(breaks = 0:5, limits = c(-0.15, 5.6),
                     expand = expansion(mult = c(0, 0.01))) +
  scale_y_continuous(breaks = seq(8, 18, 2), labels = function(x) virgola(x, 0, "%")) +
  coord_cartesian(ylim = c(6.2, 18.9), clip = "off") +
  labs(subtitle = paste0("Ogni punto un territorio; le guide tratteggiate ",
                         "sono le mediane del panel"),
       x = "vantaggio nel diploma delle ragazze (F − M, punti)",
       y = "tasso di occupazione femminile")

# --- composizione ----------------------------------------------------------------------
# La forbice nel tempo sta in fig05b: quella serie usa la fascia 9-24, l'unica disponibile
# dal 2018, mentre il quadrante sta tutto sulla 15-24. Affiancarle chiedeva al lettore di
# tenere a mente, a ogni sguardo, che le due misure non si sommano — e la caption doveva
# dirlo mentre spiegava anche il resto.
figura <- pann_a +
  plot_annotation(
    title = "Il capitale umano che Bagheria spreca di più è femminile",
    subtitle = paste0(
      "Anno ", ANNO, ", fascia 15-24: le ragazze di Bagheria superano i coetanei nel diploma (+",
      virgola(valore("Bagheria", "vantaggio_diploma_15_24_pp")), " punti) e hanno\n",
      "il tasso di occupazione più basso del panel (",
      virgola(valore("Bagheria", "tasso_occupazione_F"), 1, "%"),
      "). Il vicinato ha lo stesso mercato del lavoro (",
      virgola(valore(ETICHETTA_VICINATO, "tasso_occupazione_F"), 1, "%"), " di occupazione\n",
      "femminile) ma un vantaggio educativo di appena +",
      virgola(valore(ETICHETTA_VICINATO, "vantaggio_diploma_15_24_pp")),
      " punti: lo svantaggio occupazionale è di zona, la forbice è di Bagheria.\n",
      "Bagheria è sola nell'angolo in basso a destra — più istruite della mediana, meno occupate. Come ci sia arrivata sta in fig05b."),
    caption = paste0(
      "Fonte: ISTAT, Censimento permanente della popolazione — istruzione (9-24 anni), condizione professionale (15-24),\n",
      "demografia per età singola (denominatori), anno ", ANNO, ".\n",
      "Il quadrante sta sulla stessa popolazione 15-24: diplomate/i 15-24 = 9-24 per costruzione (nessun titolo sotto i 15;\n",
      "coerenza fra le tavole verificata nel notebook, scarto zero).\n",
      "La stessa forbice nel tempo sta in fig05b, ma sul vantaggio 9-24, l'unico disponibile dal 2018: le due misure non si\n",
      "sommano e non vanno lette in serie. Sulla fascia 15-24 il primato del vantaggio educativo è un pareggio con la Sicilia,\n",
      "e sul bound 18-24 non regge (fig11b): il claim è il distacco dal vicinato e la mancata conversione.\n",
      "Il rapporto M/F e le tre scale dell'occupazione stanno in fig01; qui l'occupazione è il livello femminile,\n",
      "la scala che regge in ogni annata.\n",
      "Vicinato = i cinque comuni più vicini per distanza fra i centroidi: conteggi sommati e poi i tassi, non media dei cinque\n",
      "tassi. Guide del quadrante: mediane dei cinque valori mostrati.\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_forbice_quadrante.csv (fotografia 15-24)"),
    theme = tema_figura()
  )

salva(figura, "fig05_forbice", larghezza = 22, altezza = 17)

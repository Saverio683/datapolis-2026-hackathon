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
LARGHEZZA <- 22   # stessa misura del salvataggio: su questa il testo va a capo

quadrante <- read_csv(file.path(PROCESSED, "genere_forbice_quadrante.csv"),
                      col_types = cols(territorio = "c", nome_territorio = "c", .default = "d"))

ETICHETTA_VICINATO <- grep("^vicinato", unique(quadrante$nome_territorio), value = TRUE)
stopifnot(length(ETICHETTA_VICINATO) == 1)
COLORI <- c(COLORI_TERRITORIO, setNames(COLORE_VICINATO, ETICHETTA_VICINATO))
ANNO <- max(quadrante$anno)

# I denominatori dei due assi: cinque punti su un piano non dicono su quante persone
# poggiano, e i cinque territori hanno taglie che vanno da migliaia a milioni.
basi <- read_csv(file.path(PROCESSED, "genere_per_1000.csv"), show_col_types = FALSE) |>
  filter(anno == ANNO)
enne <- function(terr, g) basi$pop_15_24[basi$nome_territorio == terr & basi$genere == g]

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
    # vicinato e Bagheria sotto: sopra Bagheria passa la mediana orizzontale e la taglierebbe
    sopra = !nome_territorio %in% c(ETICHETTA_VICINATO, "Bagheria"),
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
       x = "vantaggio nel diploma delle ragazze 15-24 (F − M, punti)",
       y = "tasso di occupazione femminile 15-24")

# --- composizione ----------------------------------------------------------------------
# La forbice nel tempo sta in fig05b: quella serie usa la fascia 9-24, l'unica disponibile
# dal 2018, mentre il quadrante sta tutto sulla 15-24. Affiancarle chiedeva al lettore di
# tenere a mente, a ogni sguardo, che le due misure non si sommano — e la caption doveva
# dirlo mentre spiegava anche il resto.
figura <- pann_a +
  plot_annotation(
    title = "Le ragazze di Bagheria superano i coetanei nel diploma\ne lavorano meno che in ogni altro territorio",
    subtitle = sommario(paste0(
      "Posizione dei cinque territori sul piano che incrocia istruzione e lavoro delle ragazze, anno ", ANNO,
      ", tutto sulla classe 15-24: sull'asse orizzontale il vantaggio educativo femminile, cioè quanti punti percentuali separano la quota di diplomate da quella dei diplomati, ",
      "sull'asse verticale il tasso di occupazione femminile in percentuale delle coetanee residenti. È la fotografia di un solo anno; la stessa forbice nel tempo sta in fig05b.\n",
      "Le ragazze di Bagheria superano i coetanei nel diploma (+",
      virgola(valore("Bagheria", "vantaggio_diploma_15_24_pp")), " punti) e hanno il tasso di occupazione più basso dei cinque territori (",
      virgola(valore("Bagheria", "tasso_occupazione_F"), 1, "%"),
      "). Il vicinato ha lo stesso mercato del lavoro (",
      virgola(valore(ETICHETTA_VICINATO, "tasso_occupazione_F"), 1, "%"), " di occupazione ",
      "femminile) ma un vantaggio educativo di appena +",
      virgola(valore(ETICHETTA_VICINATO, "vantaggio_diploma_15_24_pp")),
      " punti: lo svantaggio occupazionale è di zona, la forbice è di Bagheria.\n",
      "Bagheria sta nell'angolo in basso a destra: più istruite della mediana, meno occupate. Come ci sia arrivata sta in fig05b."), LARGHEZZA),
    caption = didascalia_2b(
      lettura = paste0(
        "ogni punto è un territorio, e Bagheria è il punto vermiglio più grande. ",
        "Le due linee tratteggiate chiare sono le mediane dei cinque valori disegnati, e dividono il piano in quadranti: l'angolo in basso a destra è «più istruite della mediana e meno occupate», ed è dove sta Bagheria. Con cinque territori e i loro errori campionari la posizione nel quadrante è una lettura, non un test: il confronto formale sul tasso femminile sta in fig01. ",
        "La linea tratteggiata verticale allo zero è la parità educativa fra ragazze e ragazzi: a destra di quella riga le ragazze sono più istruite dei coetanei. ",
        "Con cinque punti la mediana coincide con il punto centrale, quindi due territori siedono esattamente sulle guide. ",
        "L'etichetta accanto a ogni punto ripete i suoi due valori. Il rapporto fra tasso maschile e femminile non è su questo piano: le tre scale del divario stanno in fig01, e qui l'occupazione è il livello femminile, la scala che regge in ogni annata. ",
        "Sul vantaggio educativo Bagheria pareggia con la Sicilia, e sulla fascia 18-24 il primato passa ad altri (fig11b): ciò che la figura sostiene è il distacco dal vicinato e la mancata conversione, non il primato assoluto. ",
        "Vicinato = i cinque comuni più vicini per distanza fra i centroidi, con i conteggi sommati prima dei tassi: sono i tassi del blocco, non la media dei cinque tassi."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola istruzione, tavola della condizione professionale e demografia per età singola per i denominatori, anno ", ANNO, ". ",
        "Elaborazione: notebooks/genere.ipynb (data/processed/genere_forbice_quadrante.csv e genere_per_1000.csv per i denominatori)."),
      larghezza = LARGHEZZA),
    theme = tema_figura()
  )

salva(figura, "fig05_forbice", larghezza = LARGHEZZA, altezza = 22)

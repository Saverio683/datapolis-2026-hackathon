# Figura 4b — la fotografia del 2011 non è scaduta: la graduatoria di allora predice
# quella del 2024. Ogni punto è un comune siciliano, la diagonale è "stessa posizione
# nelle due annate". Il quadrato in basso a sinistra è il quintile più basso in entrambe:
# chi ci entra, tendenzialmente ci resta — e Bagheria ci sta in tutte e due le annate.
#
# Era il terzo pannello della fig04, schiacciato in un terzo di riga sotto la carta, con
# le annotazioni sopra la nuvola. È un'affermazione metodologica — perché un claim di
# posizionamento costruito sul censimento vecchio regge — e non geografica: la carta e
# l'istogramma rispondono a "dove sta Bagheria", questa a "quanto dura quel dove".

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 21   # stessa misura del salvataggio: su questa il testo va a capo

comuni <- read_csv(file.path(PROCESSED, "genere_mappa_2011_2024.csv"),
                   col_types = cols(territorio = "c", nome_comune = "c", ruolo = "c",
                                    .default = "d"))
distribuzione <- read_csv(file.path(PROCESSED, "genere_distribuzione_390.csv"),
                          col_types = cols(fonte = "c", .default = "d"))

ANNO <- max(distribuzione$anno)
BASE <- min(distribuzione$anno)
riga <- function(anno) distribuzione[distribuzione$anno == anno, ]
prima <- riga(BASE)

bagheria <- filter(comuni, ruolo == "Bagheria")
vicini <- filter(comuni, ruolo == "vicino") |> arrange(distanza_km)

# Il claim del titolo: la correlazione è alta e Bagheria resta nel quintile basso. Le due
# righe sono ciò che impedisce alla frase di sopravvivere a un dato che non la sostiene.
QUINTILE <- 20
stopifnot(prima$rho_vs_2024 > 0.8,
          bagheria$pct_2011 < QUINTILE, bagheria$pct_2024 < QUINTILE)

punto <- function(dati, colore, dimensione) {
  # alone bianco sotto: sul grigio dei 390 un punto pieno da solo non si stacca.
  list(geom_point(data = dati, colour = "white", size = dimensione + 1.4),
       geom_point(data = dati, colour = colore, size = dimensione))
}

# Bagheria non ha etichetta dentro il mucchio: sta nel quadrato insieme ai vicini e
# qualunque testo lì sopra coprirebbe altri comuni, quindi il richiamo esce a destra, alla
# stessa altezza del punto. Le altre annotazioni vivono negli angoli vuoti: in alto a
# sinistra chi è risalito molto, in basso a destra chi è crollato — entrambi rari.
# Niente coord_equal: forza il pannello a un quadrato e distribuisce il resto come margine,
# e titolo e caption finivano rientrati verso il centro. Il rapporto lo danno le dimensioni
# della figura, e la diagonale è comunque disegnata come retta di riferimento.
figura <- ggplot(comuni, aes(pct_2011, pct_2024)) +
  annotate("rect", xmin = 0, xmax = QUINTILE, ymin = 0, ymax = QUINTILE,
           fill = "grey92", colour = NA) +
  geom_abline(slope = 1, intercept = 0, colour = "grey60", linetype = "dashed",
              linewidth = 0.4) +
  geom_point(colour = "grey55", size = 1.4, alpha = 0.55) +
  punto(vicini, COLORE_VICINATO, 3.0) +
  punto(bagheria, COLORI_TERRITORIO[["Bagheria"]], 4.6) +
  annotate("text", x = 3, y = 97, hjust = 0, vjust = 1, size = 3, colour = "grey45",
           lineheight = 1.25,
           label = paste0("sopra la diagonale: chi \u00e8 risalito\nsotto: chi \u00e8 sceso\n",
                          "il quadrato \u00e8 il quintile pi\u00f9 basso\n",
                          "in verde i ", nrow(vicini), " comuni vicini a Bagheria")) +
  annotate("text", x = bagheria$pct_2011 + 4.5, y = bagheria$pct_2024, hjust = 0,
           size = 3.6, fontface = "bold", colour = COLORI_TERRITORIO[["Bagheria"]],
           label = paste0("Bagheria: ", virgola(bagheria$pct_2011, 0, "\u00b0"), " \u2192 ",
                          virgola(bagheria$pct_2024, 0, "\u00b0"))) +
  annotate("text", x = 98, y = 13, hjust = 1, size = 3.6, fontface = "bold", colour = "grey25",
           label = paste0("rho di Spearman ", virgola(prima$rho_vs_2024, 3))) +
  annotate("text", x = 98, y = 6, hjust = 1, size = 3, colour = "grey45",
           label = paste0("dentro il solo permanente (2018 contro ", ANNO, "): ",
                          virgola(riga(2018)$rho_vs_2024, 3))) +
  scale_x_continuous(limits = c(0, 100), breaks = seq(0, 100, 25)) +
  scale_y_continuous(limits = c(0, 100), breaks = seq(0, 100, 25)) +
  labs(
    title = paste0("La graduatoria del ", BASE, " predice quella del ", ANNO, ":\n",
                   "il posizionamento è una fotografia ancora valida"),
    subtitle = sommario(paste0(
      "Posizione di ogni comune siciliano nella graduatoria regionale del tasso di occupazione femminile, espressa in percentile: ",
      "nel ", BASE, " sull'asse orizzontale e nel ", ANNO, " sull'asse verticale. È un'affermazione di metodo e non di geografia, ",
      "perché dice quanto duri una posizione; dove stia Bagheria nella distribuzione siciliana, e come si sia mossa tutta l'isola, sta in fig04.\n",
      "Ogni punto è uno dei 390 comuni. Sulla diagonale stanno i comuni che in graduatoria hanno tenuto il posto: ",
      "la nuvola le sta stretta attorno (rho di Spearman ", virgola(prima$rho_vs_2024, 3), ").\n",
      "Nel quadrato in basso a sinistra il quintile più povero di lavoro femminile: ",
      virgola(prima$quintile_basso_ancora_tale_nel_2024_pct, 0, "%"), " di chi ci stava nel ", BASE,
      " ci sta ancora. Bagheria è fra quelli, dal ",
      virgola(bagheria$pct_2011, 0, "°"), " al ", virgola(bagheria$pct_2024, 0, "°"),
      " percentile: in tredici anni il livello è salito (fig04), la posizione ha tenuto."), LARGHEZZA),
    x = paste0("percentile ", BASE), y = paste0("percentile ", ANNO),
    caption = didascalia_2b(
      lettura = paste0(
        "ogni punto grigio è un comune. La retta tratteggiata è la diagonale, cioè «stessa posizione nelle due annate»: ",
        "sopra la diagonale stanno i comuni risaliti in graduatoria, sotto quelli scesi, e più un punto è lontano dalla retta più si è mosso. ",
        "Il quadrato grigio in basso a sinistra è il quintile più basso in entrambe le annate: ",
        virgola(prima$quintile_basso_ancora_tale_nel_2024_pct, 0, "%"), " di chi ci stava nel ", BASE, " ci sta ancora nel ", ANNO, ". ",
        "Bagheria è il punto vermiglio, i ", nrow(vicini), " comuni vicini sono in verde acqua, e stanno tutti dentro il quadrato: ",
        "il richiamo di Bagheria esce a destra perché un'etichetta dentro il mucchio coprirebbe altri comuni. ",
        "Gli assi non sono forzati a un quadrato: il rapporto lo danno le dimensioni della figura, e la diagonale resta comunque disegnata come retta di riferimento. ",
        "Gli assi portano percentili e non punti percentuali di proposito, perché le due rilevazioni hanno disegni diversi (universale a questionario la prima, campionaria sui registri la seconda): ",
        "il livello ne risente, il rango dentro l'anno molto meno, e i due valori di rho lo mostrano (", virgola(prima$rho_vs_2024, 3),
        " fra ", BASE, " e ", ANNO, ", ", virgola(riga(2018)$rho_vs_2024, 3), " dentro la sola rilevazione permanente). ",
        "Misiliscemi, istituito nel 2021 per distacco da Trapani, è l'unica esclusione dai ", migliaia(nrow(comuni)), " comuni disegnati."),
      fonte = paste0(
        "ISTAT, 8milaCensus, indicatore L11 (censimento ", BASE, ") e Censimento permanente della popolazione (", ANNO,
        "), tasso di occupazione femminile sulla popolazione di 15 anni e più. ",
        "Fascia e anni sono diversi dalle serie 15-24 del thread: è contesto di lungo periodo, non un termine di paragone. ",
        "Elaborazione: notebooks/genere.ipynb (data/processed/genere_mappa_2011_2024.csv e genere_distribuzione_390.csv)."),
      larghezza = LARGHEZZA)) +
  tema_figura()

salva(figura, "fig04b_persistenza", larghezza = LARGHEZZA, altezza = 24)

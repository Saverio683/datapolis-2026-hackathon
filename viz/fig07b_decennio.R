# Figura 7b — da quando si perde: la stessa coorte (15-19 anni all'inizio) seguita per
# dieci anni, due volte. Risponde all'obiezione ovvia alla fig07 — tre anni di dati non
# bastano a chiamare "fuga" una perdita. Nel decennio 2001-2011 Bagheria tratteneva la
# coorte meglio di Sicilia e Palermo; nel 2011-2021 ne perde più di Palermo sui maschi.
# La frattura è databile, ed è lo stesso decennio del muro di fig10.
#
# Era il pannello inferiore della fig07, che teneva insieme "dove" e "da quando" con una
# "e" nel titolo. Qui la fonte è un'altra (classi quinquennali di tre censimenti, non le
# età singole del permanente) e l'orizzonte è un altro: separata, la caption può spiegare
# la gamba mista del 2011-2021 senza doversi dividere con quella del profilo per età.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# Stessa coorte seguita per dieci anni, due volte. Le classi quinquennali permettono solo
# passi di cinque anni: il decennio è due classi avanti, ed è la scala più corta che copra
# sia il 2001-2011 sia il 2011-2021.
decennale <- read_csv(file.path(PROCESSED, "genere_ritenzione_decennale.csv"),
                      col_types = cols(territorio = "c", nome_territorio = "c",
                                       genere = "c", eta_da = "c", eta_a = "c",
                                       fonti_diverse = "c", .default = "d"))
COORTE <- "Y15-19"
decenni <- decennale |>
  filter(anni == 10, eta_da == COORTE) |>
  mutate(periodo = paste0(anno_da, "-", anno_a),
         nome_territorio = factor(nome_territorio, levels = ORDINE),
         genere = factor(ETICHETTE_GENERE[genere], levels = ETICHETTE_GENERE))
# Il vicinato non c'è: le classi quinquennali sono state scaricate solo per i quattro
# territori di confronto. Se un giorno ci fosse, questa riga lo farebbe notare invece di
# lasciarlo sparire dentro un factor con un livello in meno.
stopifnot(!anyNA(decenni$nome_territorio),
          setequal(levels(droplevels(decenni$nome_territorio)), ORDINE))

SPESSORI <- c(Bagheria = 1.2, Palermo = 0.55, Sicilia = 0.55, Italia = 0.55)

bagheria_decenni <- filter(decenni, nome_territorio == "Bagheria")
salto <- bagheria_decenni |>
  summarise(scarto = ritenzione_pct[anno_da == max(anno_da)] -
              ritenzione_pct[anno_da == min(anno_da)], .by = genere)
scarto_di <- function(g) abs(salto$scarto[salto$genere == g])
valore <- function(g, quando) {
  riga <- bagheria_decenni[bagheria_decenni$genere == g, ]
  riga$ritenzione_pct[if (quando == "prima") which.min(riga$anno_da) else which.max(riga$anno_da)]
}
# Il titolo dice che il primo decennio teneva e il secondo no: se il verso cambiasse, la
# frase andrebbe riscritta, non ristampata.
stopifnot(all(salto$scarto < 0))

figura <- ggplot(decenni, aes(periodo, ritenzione_pct, colour = nome_territorio,
                              group = nome_territorio)) +
  geom_hline(yintercept = 100, linetype = "dashed", colour = "grey55", linewidth = 0.4) +
  geom_line(aes(linewidth = nome_territorio)) +
  geom_point(size = 2.4) +
  # Solo Bagheria porta i valori: è il soggetto, e con quattro etichette per estremo il
  # pannello diventa illeggibile (nel 2011-2021 tre territori stanno in tre punti).
  geom_text(data = bagheria_decenni,
            aes(label = virgola(ritenzione_pct, 1, "%"),
                vjust = if_else(anno_da == min(anno_da), -1.2, 2.0)),
            size = 3.2, fontface = "bold", show.legend = FALSE) +
  geom_text(data = salto, inherit.aes = FALSE,
            aes(x = 1.5, y = 82, label = paste0(virgola(scarto), " punti in un decennio")),
            size = 3.2, fontface = "bold", colour = COLORI_TERRITORIO[["Bagheria"]]) +
  facet_wrap(~genere) +
  scale_colour_manual(values = COLORI_TERRITORIO, breaks = ORDINE) +
  # Bagheria è il soggetto: linea piena; i benchmark sono contesto, più sottili.
  scale_linewidth_manual(values = SPESSORI, guide = "none") +
  scale_x_discrete(expand = expansion(add = c(0.35, 0.45))) +
  scale_y_continuous(labels = function(x) virgola(x, 0, "%")) +
  coord_cartesian(ylim = c(78, 118)) +
  guides(colour = guide_legend(override.aes = list(linewidth = 1.1))) +
  labs(
    title = "La falla si è aperta nel decennio 2011-2021:\nprima Bagheria tratteneva la coorte meglio di Palermo e Sicilia",
    subtitle = paste0(
      "La stessa coorte — chi aveva 15-19 anni all'inizio — seguita per dieci anni, due volte. Il tratteggio a 100 è la coorte che si conserva.\n",
      "Tre anni di dati non basterebbero a chiamarla fuga (fig07), dieci sì. Nel 2001-2011 le ragazze di Bagheria arrivavano a ",
      virgola(valore("femmine", "prima"), 1, "%"), ", sopra\n",
      "Sicilia e Palermo; nel decennio successivo scendono a ", virgola(valore("femmine", "dopo"), 1, "%"), " — ",
      virgola(scarto_di("femmine")), " punti. Sui ragazzi il calo è di ", virgola(scarto_di("maschi")),
      " punti e li porta sotto Palermo.\n",
      "È lo stesso decennio in cui si alza il muro dell'occupazione femminile (fig10): la frattura è databile, e non si è richiusa da sola."),
    x = NULL, y = "coorte dopo dieci anni",
    caption = paste0(
      "Fonte: ISTAT - classi quinquennali dei censimenti 2001 e 2011 e del Censimento permanente 2021 (DF_DCSS_POP_DEMCITMIG_TV_1 le serve tutte e tre).\n",
      "Il decennio 2011-2021 ha una gamba per rilevazione: il 2011 è decennale, il 2021 permanente. La distorsione nota va nel verso prudente - il censimento 2011\n",
      "contò meno dell'anagrafe, quindi sta al denominatore del decennio che crolla e al numeratore di quello che tiene: il divario fra i due decenni è una stima per difetto.\n",
      "Controlli interni al solo permanente sulla stessa coorte a cinque anni (2018-2023 e 2019-2024): la perdita si concentra sulla transizione 20-24 → 25-29,\n",
      "femmine 92,8% e 93,3% a Bagheria contro ~102% in Italia. Tutti i periodi stanno in data/processed/genere_ritenzione_decennale.csv.\n",
      "Il vicinato non compare: le classi quinquennali sono state scaricate solo per i quattro territori di confronto. Per età singola sta invece in fig07.\n",
      "Palermo è il controfattuale dichiarato del disegno di valutazione (notebook, sezione «Trend paralleli»).\n",
      "Elaborazione: notebooks/genere.ipynb - data/processed/genere_ritenzione_decennale.csv")) +
  tema_figura()

salva(figura, "fig07b_decennio", larghezza = 26, altezza = 16)

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
LARGHEZZA <- 26   # stessa misura del salvataggio: su questa il testo va a capo

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

# Le numerosità delle coorti di partenza a Bagheria: sono il denominatore di ogni punto
# disegnato, e senza di loro la percentuale non dice su quante persone poggia.
N_COORTI <- decenni |>
  filter(nome_territorio == "Bagheria") |>
  select(periodo, genere, n_da) |>
  pivot_wider(names_from = genere, values_from = n_da) |>
  arrange(periodo) |>
  mutate(testo = paste0(periodo, ": ", migliaia(femmine), " ragazze e ",
                        migliaia(maschi), " ragazzi")) |>
  pull(testo) |> paste(collapse = "; ")

# Il controllo a cinque anni dentro la sola rilevazione permanente, letto dallo stesso file
# invece che ricopiato: se i dati cambiano, la didascalia cambia con loro.
cinque_anni <- function(terr) {
  r <- decennale[decennale$nome_territorio == terr & decennale$anni == 5 &
                   decennale$eta_da == "Y20-24" & decennale$genere == "F" &
                   decennale$anno_da %in% c(2018, 2019), ]
  r <- r[order(r$anno_da), ]
  list(periodi = paste0(r$anno_da, "-", r$anno_a, collapse = " e "),
       valori = paste(virgola(r$ritenzione_pct, 1, "%"), collapse = " e "))
}
CTRL_BAG <- cinque_anni("Bagheria")
CTRL_ITA <- cinque_anni("Italia")

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
    subtitle = sommario(paste0(
      "Residenti della coorte dieci anni dopo per 100 residenti iniziali, per genere e per quattro territori: ",
      "sempre la stessa classe d'età (15-19 anni all'inizio del decennio) seguita due volte, nel 2001-2011 e nel 2011-2021. ",
      "È una misura netta di saldo, che comprende sia chi parte sia chi arriva, e dice da quando si perde; a che età si perde lo dice fig07. Il tratteggio a 100 è la coorte che si conserva.\n",
      "Tre anni di dati non basterebbero a chiamarla fuga (fig07), dieci sì. Nel 2001-2011 le ragazze di Bagheria arrivavano a ",
      virgola(valore("femmine", "prima"), 1, "%"), ", sopra Sicilia e Palermo; nel decennio successivo scendono a ",
      virgola(valore("femmine", "dopo"), 1, "%"), " (", virgola(scarto_di("femmine")),
      " punti). Sui ragazzi il calo è di ", virgola(scarto_di("maschi")),
      " punti e li porta sotto Palermo.\n",
      "È il decennio successivo a quello in cui si alza il muro dell'occupazione femminile (fig10, 2001-2011): prima si apre il divario sul lavoro, poi quello sulla permanenza."), LARGHEZZA),
    x = NULL, y = "coorte dopo dieci anni",
    caption = didascalia_2b(
      lettura = paste0(
        "la riga tratteggiata orizzontale a 100% è la coorte che si conserva: sopra è cresciuta, sotto si è ridotta. ",
        "Ogni pannello è un genere e ogni linea un territorio, fra i due decenni: la pendenza della linea è il finding, non il livello. ",
        "Bagheria è in vermiglio a tratto pieno perché è il soggetto, i tre riferimenti sono a tratto sottile. ",
        "I valori in cifre sono stampati solo su Bagheria: con quattro etichette per estremo il pannello diventerebbe illeggibile. ",
        "Il decennio 2011-2021 ha una gamba per rilevazione, perché il 2011 è censimento decennale e il 2021 censimento permanente: la distorsione nota va nel verso prudente, ",
        "perché il censimento 2011 contò meno dell'anagrafe e sta quindi al denominatore del decennio che crolla e al numeratore di quello che tiene, e il divario fra i due decenni è una stima per difetto. ",
        "Il controllo dentro la sola rilevazione permanente, sulla stessa coorte a cinque anni (", CTRL_BAG$periodi,
        "), dà per le femmine di Bagheria ", CTRL_BAG$valori, " contro ", CTRL_ITA$valori,
        " dell'Italia: il verso regge anche senza mescolare le due rilevazioni. ",
        "Il vicinato non compare perché le classi quinquennali sono state scaricate solo per i quattro territori di confronto. ",
        "Palermo è il controfattuale dichiarato del disegno di valutazione (notebook, sezione «Trend paralleli»)."),
      fonte = paste0(
        "ISTAT, classi quinquennali dei censimenti 2001 e 2011 e del Censimento permanente 2021 (il dataflow DF_DCSS_POP_DEMCITMIG_TV_1 le serve tutte e tre). ",
        "Tutti i periodi disponibili, compresi quelli non disegnati, stanno in data/processed/genere_ritenzione_decennale.csv. ",
        "Elaborazione: notebooks/genere.ipynb (data/processed/genere_ritenzione_decennale.csv)."),
      larghezza = LARGHEZZA)) +
  tema_figura()

salva(figura, "fig07b_decennio", larghezza = LARGHEZZA, altezza = 20)

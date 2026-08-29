# Figura 13b — la stessa tavola della fig13, aperta per genere. Sta in una figura sua e
# non in un pannello in più: la fig13 confronta quattro territori a genere unito, qui i
# territori scendono a due perché la dimensione in più sono maschi e femmine, e otto linee
# per pannello non si leggono. La parentela la tiene la lettera, la fascia è la stessa.
#
# Il finding non è che il divario cresce con l'età — cresce ovunque, anche in Italia — ma
# che a Bagheria è il più profondo dei quattro territori in tutte e quattro le classi, e
# lo è già a 15-24, dove in punti sembra piccolo solo perché a quell'età lavorano in pochi.
# Per questo il divario si dice due volte: in punti nella testata, in rapporto nel testo.
#
# Il colore è il genere, il tratto è il territorio: sono due codifiche indipendenti, e
# quella del genere è la convenzione della cartella (blu/rosa, theme.R). Il rosa e il blu
# qui non stanno per un territorio — è la ragione per cui nessun territorio li usa altrove.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

LARGHEZZA <- 26   # stessa misura del salvataggio: su questa il testo va a capo

nomi <- read_csv(file.path(PROCESSED, "territori.csv"), col_types = cols(.default = "c"))

RIFERIMENTO <- "Sicilia"

dati <- read_csv(file.path(PROCESSED, "tasso_occupazione_eta.csv"),
                 col_types = cols(territorio = "c", eta = "c", classe = "c",
                                  genere = "c", .default = "d")) |>
  filter(genere != "T", eta != "Y_GE15") |>
  left_join(nomi[c("territorio", "nome_territorio")], by = "territorio") |>
  mutate(classe = factor(classe, levels = c("15-24", "25-49", "50-64", "65+")))

ANNO <- max(dati$anno)
PRIMO <- min(dati$anno)
ANCORE <- c(PRIMO, 2021, ANNO)

# Il quadro completo (quattro territori) serve al controllo e al testo, non al disegno:
# sul grafico restano Bagheria e la Sicilia, altrimenti sono sedici linee su quattro pannelli.
quadro <- dati |>
  filter(anno == ANNO) |>
  select(nome_territorio, classe, genere, tasso_occupazione) |>
  pivot_wider(names_from = genere, values_from = tasso_occupazione) |>
  mutate(gap_pp = M - F, rapporto = M / F)

# Il titolo dice "il più profondo a ogni età": se una sola classe lo smentisse, andrebbe
# riscritto. Il rapporto e non i punti, perché è la misura che non dipende dal livello
# generale della classe — a 15-24 lavorano in pochi ovunque, e in punti qualunque divario
# lì sembra piccolo.
peggiore <- quadro |>
  summarise(peggiore = nome_territorio[which.max(rapporto)], .by = classe)
stopifnot(all(peggiore$peggiore == "Bagheria"))

riga <- function(terr, cl) quadro[quadro$nome_territorio == terr & quadro$classe == cl, ]
GIOVANI <- riga("Bagheria", "15-24")
ANZIANI <- riga("Bagheria", "50-64")
GIOVANI_RIF <- riga(RIFERIMENTO, "15-24")

# I denominatori per classe e genere a Bagheria: sono la base di ogni tasso disegnato.
N_CLASSI <- dati |>
  filter(nome_territorio == "Bagheria", anno == ANNO) |>
  select(classe, genere, popolazione) |>
  pivot_wider(names_from = genere, values_from = popolazione) |>
  arrange(classe) |>
  mutate(testo = paste0(classe, " ", migliaia(round(F)), " donne e ",
                        migliaia(round(M)), " uomini")) |>
  pull(testo) |> paste(collapse = "; ")

testata <- quadro |>
  filter(nome_territorio == "Bagheria") |>
  transmute(classe, pannello = paste0(classe, "   ", virgola(gap_pp, 1), " pp fra M e F"))
LIVELLI <- testata$pannello[order(testata$classe)]

serie <- dati |>
  filter(nome_territorio %in% c("Bagheria", RIFERIMENTO)) |>
  select(classe, nome_territorio, genere, anno, tasso_occupazione) |>
  complete(classe, nome_territorio, genere, anno = full_seq(anno, 1)) |>
  left_join(testata, by = "classe") |>
  mutate(pannello = factor(pannello, levels = LIVELLI),
         nome_territorio = factor(nome_territorio, levels = c("Bagheria", RIFERIMENTO)))

figura <- ggplot(serie, aes(asse_2020(anno), tasso_occupazione,
                            colour = genere, linetype = nome_territorio)) +
  geom_line(aes(group = interaction(nome_territorio, genere),
                linewidth = nome_territorio == "Bagheria")) +
  geom_point(data = filter(serie, nome_territorio == "Bagheria"), size = 1.5) +
  facet_wrap(~ pannello, nrow = 1) +
  scale_colour_manual(values = COLORI_GENERE, labels = ETICHETTE_GENERE) +
  # Nomi su entrambi i valori: con il secondo senza nome la scala non lo appaia alla
  # Sicilia, le assegna NA e geom_line le scarta in silenzio — la figura esce con le
  # tratteggiate mancanti e nessun errore.
  scale_linetype_manual(values = setNames(c("solid", "22"), c("Bagheria", RIFERIMENTO))) +
  scale_linewidth_manual(values = c(`TRUE` = 1.3, `FALSE` = 0.7), guide = "none") +
  scale_x_continuous(breaks = asse_2020(ANCORE), labels = ANCORE,
                     expand = expansion(mult = c(0.06, 0.06))) +
  scale_y_continuous(limits = c(0, 80), breaks = seq(0, 75, 25),
                     labels = function(x) virgola(x, 0, "%")) +
  guides(colour = guide_legend(order = 1), linetype = guide_legend(order = 2)) +
  buco_2020(y = 40, serie$anno, serie$tasso_occupazione) +
  labs(
    title = "A Bagheria il tasso di occupazione maschile è il doppio di quello femminile\ngià a 15-24 anni",
    subtitle = paste0(
      "Quota di occupati sulla popolazione della classe, per genere, ", PRIMO, "-", ANNO,
      ". Bagheria a tratto pieno, ", RIFERIMENTO, " tratteggiata.\n",
      "In punti il divario cresce con l'età (da ", virgola(GIOVANI$gap_pp, 1),
      " pp sui 15-24 a ", virgola(ANZIANI$gap_pp, 1), " pp sui 50-64), ma cresce ovunque. ",
      "Quello che distingue Bagheria è il rapporto:\n",
      virgola(GIOVANI$rapporto, 2, "×", taglia_zero = FALSE), " già a 15-24 contro ",
      virgola(GIOVANI_RIF$rapporto, 2, "×", taglia_zero = FALSE), " in ", RIFERIMENTO,
      ", ed è il più alto dei quattro territori in tutte e quattro le classi. Il divario\n",
      "non si apre dopo i vent'anni: a vent'anni c'è già, e in punti sembra piccolo solo ",
      "perché a quell'età lavorano in pochi."),
    x = NULL, y = NULL, colour = NULL, linetype = NULL,
    caption = didascalia_4b(
      mostra = paste0(
        "tasso di occupazione per genere, cioè occupati in percentuale della popolazione della stessa classe d'età e dello stesso genere, dal ",
        PRIMO, " al ", ANNO, ", sulle quattro classi d'età pubblicate a livello comunale. ",
        "Sul grafico stanno due territori, Bagheria e ", RIFERIMENTO,
        ": con quattro territori le linee diventerebbero sedici e i pannelli illeggibili. ",
        "Il tasso è calcolato sulla popolazione della classe e non sulle sole forze di lavoro, quindi comprende studenti e inattivi, ",
        "e per questo la classe 15-24 sta strutturalmente bassa per entrambi i generi."),
      base = paste0(
        "Denominatori di Bagheria nel ", ANNO, " (", N_CLASSI,
        "). Nessun intervallo di confidenza: sono conteggi censuari e non stime campionarie, e nessun record è escluso. ",
        "Il divario è dichiarato su due scale perché dicono cose diverse: in punti percentuali nell'intestazione di ogni pannello, in rapporto fra i due tassi nel sottotitolo. ",
        "Il rapporto è la misura che non dipende dal livello generale della classe, ed è quella su cui Bagheria risulta il territorio più sbilanciato dei quattro in tutte e quattro le classi (verifica sui quattro territori nel notebook, non disegnata qui). ",
        "Il 2020 manca alla fonte: sulla classe 15-24 non esiste nessuna riga, sulle altre classi esiste solo il denominatore. La serie è interrotta e nessun valore è interpolato."),
      lettura = paste0(
        "ci sono due codifiche indipendenti e vanno lette insieme: il colore è il genere (rosa le femmine, blu i maschi) e il tratto è il territorio (pieno Bagheria, tratteggiato ",
        RIFERIMENTO, "). Il rosa e il blu qui non stanno per un territorio, ed è la ragione per cui nessun territorio li usa nelle altre figure. ",
        "Ogni pannello è una classe d'età, e la cifra nella sua intestazione è il divario fra maschi e femmine a Bagheria in punti percentuali nell'ultima annata. ",
        "La striscia grigia verticale fra il 2019 e il 2021 occupa l'annata mancante: dove c'è la striscia non c'è misura. ",
        "Sull'asse orizzontale sono etichettate solo la prima annata, il 2021 e l'ultima; le posizioni restano quelle di tutte le annate."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, ", PRIMO, "-", ANNO,
        ". Elaborazione: pipeline/build.py (data/processed/tasso_occupazione_eta.csv; fig13 è la stessa tavola a generi uniti)."),
      larghezza = LARGHEZZA)) +
  tema_figura() +
  theme(panel.spacing.x = unit(1.1, "lines"))

salva(figura, "fig13b_occupazione_eta_genere", larghezza = LARGHEZZA, altezza = 19)

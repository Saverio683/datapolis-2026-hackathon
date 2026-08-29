# Figura 1 — il divario di genere sull'occupazione 15-24 nelle tre scale.
# Il punto: punti, rapporto e livello femminile ordinano i territori in modo diverso, e
# solo una delle tre mette Bagheria in fondo in ogni annata. Il conteggio «in testa in N
# anni su M» sotto ogni pannello è la stessa lettura che fig05 fa sulla forbice: qui sta
# nella figura che parla delle scale, che è il posto dove la scelta va argomentata.
# La striscia di fig05 non ripete più il rapporto e il tasso femminile: erano queste due
# serie, disegnate una seconda volta e senza bande.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# Una costante sola per la larghezza: il testo va a capo esattamente sulla misura con cui
# la figura viene salvata, altrimenti il taglio si scopre guardando il PNG.
LARGHEZZA <- 34

# Il vicinato entra aggregato, come in tutte le altre figure: una serie sola con la sua
# banda, non cinque linee. Sui conteggi sommati dei cinque comuni l'intervallo si stringe
# abbastanza da reggere il confronto con Bagheria; le serie per singolo comune restano nel
# CSV e sono troppo rumorose per essere lette anno su anno.
gap_vicini <- read_csv(file.path(PROCESSED, "genere_gap_occupazione_ci_vicini.csv"),
                       col_types = cols(territorio = "c", nome_territorio = "c", .default = "d"))
vicinato <- filter(gap_vicini, territorio == "VICINI5")
ETICHETTA_VICINATO <- vicinato$nome_territorio[1]
COLORI <- c(COLORI_TERRITORIO, setNames(COLORE_VICINATO, ETICHETTA_VICINATO))

dati <- bind_rows(
    read_csv(file.path(PROCESSED, "genere_gap_occupazione_ci.csv"), show_col_types = FALSE),
    vicinato
  ) |>
  mutate(nome_territorio = factor(nome_territorio, levels = names(COLORI))) |>
  # Il 2020 manca alla fonte sulla classe 15-24: la riga vuota interrompe la linea invece
  # di farla passare dritta sopra il buco. Nessun valore inventato.
  complete(nome_territorio, anno = 2018:2024)

# I denominatori della classe 15-24, cioè l'N su cui poggiano tutti e tre i pannelli.
# Stessa base che il notebook usa per i tassi: qui si legge, non si ricalcola.
platea <- read_csv(file.path(PROCESSED, "genere_platea.csv"),
                   col_types = cols(territorio = "c", nome_territorio = "c",
                                    genere = "c", .default = "d"))
enne <- function(terr) {
  riga <- function(g) platea$platea_2024[platea$nome_territorio == terr & platea$genere == g]
  paste0(terr, " ", migliaia(riga("F")), " femmine e ", migliaia(riga("M")), " maschi")
}
N_TERRITORI <- paste(vapply(ORDINE, enne, character(1)), collapse = "; ")

ULTIMO_ANNO <- max(dati$anno[!is.na(dati$rapporto_M_F)])
valore_di <- function(territorio, colonna) {
  dati[[colonna]][dati$nome_territorio == territorio & dati$anno == ULTIMO_ANNO]
}
# Il comune più sbilanciato resta un fatto anche se non è disegnato: senza questa riga il
# sottotitolo lascerebbe credere che nessuno in zona superi Bagheria, e non è vero.
PEGGIORE_COMUNE <- gap_vicini |>
  filter(territorio != "VICINI5", anno == ULTIMO_ANNO) |>
  slice_max(rapporto_M_F, n = 1)

#' Quante annate mettono Bagheria all'estremo che definisce il problema su questa scala.
#' È una lettura dei valori già calcolati, non un ricalcolo; la resa a parole degli estremi
#' sta in `frase_annate()` (theme.R), condivisa con fig05.
quante_annate <- function(colonna, verso, frase) {
  per_anno <- dati |>
    filter(!is.na(.data[[colonna]])) |>
    summarise(testa = nome_territorio[if (verso == "max") which.max(.data[[colonna]])
                                      else which.min(.data[[colonna]])],
              .by = anno)
  frase_annate(sum(per_anno$testa == "Bagheria"), nrow(per_anno), frase)
}

# Il primato sul livello regge in ogni annata, ma in due c'è pochissimo. L'anno in cui ci
# passa più stretto va in caption: senza, «il minimo del panel» lascia credere a uno
# scarto ampio, e il vicinato è a un decimo di punto.
MARGINE <- dati |>
  filter(!is.na(tasso_F)) |>
  summarise(bagheria = tasso_F[nome_territorio == "Bagheria"],
            secondo = min(tasso_F[nome_territorio != "Bagheria"]), .by = anno) |>
  slice_min(secondo - bagheria, n = 1)

#' Il pannello dei punti si legge al rovescio degli altri due: qui la posizione di
#' Bagheria è quella buona, e dirlo come «non è mai all'estremo» costringe a leggere una
#' negazione. Il fatto è che sta sotto i due territori con l'occupazione più alta, ed è
#' quello che l'etichetta dice. Contato, non assunto: se un'annata smentisse, si vedrebbe.
sotto_riferimenti <- function(colonna, riferimenti) {
  per_anno <- dati |>
    filter(!is.na(.data[[colonna]])) |>
    summarise(sotto = .data[[colonna]][nome_territorio == "Bagheria"]
                      < min(.data[[colonna]][nome_territorio %in% riferimenti]),
              .by = anno)
  # A capo dentro la frase: per esteso su una riga sola l'etichetta invade il pannello
  # accanto, e i due riferimenti sono il punto di rottura naturale.
  frase_annate(sum(per_anno$sotto), nrow(per_anno),
               paste0("un gap più stretto\ndi ", paste(riferimenti, collapse = " e ")))
}

comune <- list(
  scale_colour_manual(values = COLORI, breaks = names(COLORI)),
  scala_2020(),
  labs(x = NULL)
)

# La striscia del 2020 (`buco_2020`) e la compressione dell'asse (`asse_2020`) stanno in
# theme.R: le usano anche fig05b e edu_fig06. L'asse porta le posizioni, non gli anni:
# il 2020 non ne ha una, e fra 2019 e 2021 resta solo la colonna vuota che la striscia riempie.

punti <- ggplot(dati, aes(asse_2020(anno), gap, colour = nome_territorio, fill = nome_territorio)) +
  geom_ribbon(aes(ymin = gap_lo, ymax = gap_hi), alpha = 0.15, colour = NA) +
  scale_fill_manual(values = COLORI) +
  geom_line(linewidth = 0.9) +
  geom_point(size = 1.7) +
  comune +
  # Il fill serve solo alle bande: senza questo la sua legenda resta distinta da quella
  # del colore e patchwork non riesce ad accorparle in una sola.
  guides(fill = "none") +
  buco_2020(y = 7.5, dati$anno, dati$gap) +
  labs(subtitle = paste0("In punti percentuali (M − F)\n",
                         sotto_riferimenti("gap", c("Sicilia", "Italia"))),
       y = "punti percentuali")

rapporto <- ggplot(dati, aes(asse_2020(anno), rapporto_M_F, colour = nome_territorio)) +
  geom_hline(yintercept = 1, linetype = "dashed", colour = "grey55", linewidth = 0.4) +
  annotate("text", x = asse_2020(2018), y = 1.04, label = "parità", hjust = 0,
           size = 3, colour = "grey45") +
  geom_line(linewidth = 0.9) +
  geom_point(size = 1.7) +
  comune +
  # coord_cartesian e non limits: taglia la vista, non le righe. Qualche vicino ha rapporti
  # fuori scala su conteggi minuscoli, la linea esce dal riquadro e non sparisce in silenzio.
  scale_y_continuous(labels = function(x) virgola(x, 1, taglia_zero = FALSE)) +
  coord_cartesian(ylim = c(0.95, max(dati$rapporto_M_F, na.rm = TRUE) + 0.05)) +
  buco_2020(y = 1.75, dati$anno, dati$rapporto_M_F) +
  labs(subtitle = paste0("In rapporto (tasso M / tasso F)\n",
                         quante_annate("rapporto_M_F", "max", "il rapporto più sbilanciato")),
       y = "quante volte")

# Terza scala: il livello, non più il divario. Senza banda perché l'intervallo esportato è
# quello di Newcombe sulla differenza, non il Wilson sui due tassi: disegnarne una qui
# vorrebbe dire ricalcolarla in R, e la trasformazione sta in Python.
livello <- ggplot(dati, aes(asse_2020(anno), tasso_F, colour = nome_territorio)) +
  geom_line(linewidth = 0.9) +
  geom_point(size = 1.7) +
  comune +
  # breaks espliciti: i default cadono sui mezzi punti e l'asse esce con 5%, 8%, 10%, 12%.
  scale_y_continuous(breaks = seq(0, 20, 5), labels = function(x) virgola(x, 0, "%")) +
  buco_2020(y = 11, dati$anno, dati$tasso_F) +
  labs(subtitle = paste0("In livello (tasso di occupazione femminile)\n",
                         quante_annate("tasso_F", "min", "il tasso più basso")),
       # corto: il titolo d'asse ruotato è alto quanto il testo, e per esteso finiva
       # addosso alla seconda riga del sottotitolo. Il denominatore resta dichiarato.
       y = "su 100 coetanee")

# La legenda in una riga tutta sua, in cima (come in fig07): `guide_area()` è il posto
# che patchwork dà ai guide raccolti, e come prima riga della composizione finisce sopra
# i titoli dei tre pannelli invece che incastrata fra i titoli e i grafici. Centrata
# sull'intera figura, non sul solo pannello che la produce.
figura <- guide_area() / (punti | rapporto | livello) +
  plot_layout(heights = c(0.08, 1), guides = "collect") +
  plot_annotation(
    title = "Delle tre scale del divario, solo il livello femminile mette Bagheria in fondo ogni anno",
    subtitle = paste0(
      "Tasso di occupazione 15-24 anni, 2018-2024. In punti il divario è più largo dove si lavora di più: l'Italia sta sopra Bagheria (",
      virgola(valore_di("Italia", "gap")), " contro ", virgola(valore_di("Bagheria", "gap")),
      " nel ", ULTIMO_ANNO, ") perché lì\n",
      "lavora il ", virgola(valore_di("Italia", "tasso_F"), 1, "%"), " delle ragazze contro l'",
      virgola(valore_di("Bagheria", "tasso_F"), 1, "%"),
      ". Su questa scala Bagheria non è mai la peggiore, e non è una buona notizia.\n",
      "In rapporto è il più sbilanciato del panel nella maggioranza delle annate: un ragazzo ha il doppio della probabilità di lavorare di una coetanea.\n",
      "Ma il vicinato lo segue a un soffio (",
      virgola(valore_di(ETICHETTA_VICINATO, "rapporto_M_F"), 2, "×", taglia_zero = FALSE),
      " contro ", virgola(valore_di("Bagheria", "rapporto_M_F"), 2, "×", taglia_zero = FALSE),
      ") e comune per comune ", PEGGIORE_COMUNE$nome_territorio, " arriva a ",
      virgola(PEGGIORE_COMUNE$rapporto_M_F, 2, "×", taglia_zero = FALSE),
      ": in rapporto il divario è un tratto di zona.\n",
      "A reggere ogni annata è la terza scala: il tasso femminile di Bagheria (",
      virgola(valore_di("Bagheria", "tasso_F"), 1, "%"),
      " nel ", ULTIMO_ANNO, ") è il minimo del panel in tutti gli anni misurati.\n",
      "È il livello, non il divario, il claim da portare nella proposal."),
    caption = didascalia_4b(
      mostra = paste0(
        "tasso di occupazione della classe 15-24 anni, letto su tre scale diverse della stessa disuguaglianza, dal 2018 al ",
        ULTIMO_ANNO, ", su cinque territori. A sinistra il divario in punti percentuali (tasso maschile meno tasso femminile), ",
        "al centro il rapporto fra i due tassi (quante volte il tasso maschile contiene quello femminile), a destra il livello femminile ",
        "(occupate ogni 100 coetanee residenti). Le tre scale misurano lo stesso fenomeno e ordinano i territori in modo diverso: non si sommano e non si convertono l'una nell'altra."),
      base = paste0(
        "Denominatori della classe 15-24 al ", ULTIMO_ANNO, ": ", N_TERRITORI,
        ". Per il vicinato i conteggi dei cinque comuni sono sommati prima del rapporto, così l'intervallo si stringe abbastanza da reggere il confronto con Bagheria. ",
        "Bande, solo sul primo pannello: intervallo di confidenza al 95% di Newcombe sulla differenza fra due proporzioni, costruito sui limiti di Wilson dei due tassi. ",
        "Sul secondo e sul terzo pannello non c'è banda, perché l'intervallo esportato è quello della differenza e non quello del rapporto o dei singoli tassi: ricalcolarlo in R sposterebbe una trasformazione fuori dalla pipeline. ",
        "Il 2020 manca alla fonte sulla classe 15-24 in tutti i territori: la serie è interrotta e nessun valore è interpolato. ",
        "I conteggi «in N annate su M» sotto ogni pannello sono contati sui valori disegnati, non stimati."),
      lettura = paste0(
        "la striscia grigia verticale fra il 2019 e il 2021 occupa l'annata mancante: dove c'è la striscia non c'è misura. ",
        "Nel pannello centrale la riga tratteggiata orizzontale a 1,0 è la parità fra i due tassi. ",
        "Bagheria è in vermiglio, Palermo in viola, la Sicilia in ambra, l'Italia in grigio, il vicinato in verde acqua; blu e rosa restano riservati a maschi e femmine nelle altre figure di questa cartella. ",
        "Il divario in punti è compresso dai livelli bassi: dove lavorano poche persone di entrambi i generi la differenza assoluta resta piccola anche a parità di svantaggio relativo, ed è la ragione per cui il primo pannello mette Bagheria in posizione apparentemente buona. ",
        "Sul livello Bagheria è ultima in ogni annata, ma per poco: nel ", MARGINE$anno, " sono ",
        virgola(MARGINE$bagheria, 1, "%", taglia_zero = FALSE), " contro ",
        virgola(MARGINE$secondo, 1, "%", taglia_zero = FALSE),
        ", quindi a distinguere Bagheria è il livello, non lo scarto in graduatoria. ",
        "Vicinato = i cinque comuni più vicini per distanza fra i centroidi; le serie dei singoli comuni stanno in genere_gap_occupazione_ci_vicini.csv, dove su 10-28 mila abitanti gli intervalli sono larghi il quintuplo."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, classe 15-24 anni, 2018-",
        ULTIMO_ANNO, ". Elaborazione: notebooks/genere.ipynb (data/processed/genere_gap_occupazione_ci.csv, genere_gap_occupazione_ci_vicini.csv e genere_platea.csv)."),
      larghezza = LARGHEZZA),
    theme = tema_figura()
  )

salva(figura, "fig01_gap_tre_scale", larghezza = LARGHEZZA, altezza = 19)

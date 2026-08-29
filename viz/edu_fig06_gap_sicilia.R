# Figura edu-06 — il gap con la Sicilia non si chiude (port R della fig06 del thread
# educazione). Dimostratore dell'assimilazione sul branch unison: dati da
# edu_gaps_vs_sicily.csv (pipeline/edu), tema e tipografia condivisi di theme.R.
# Dentro il glob di build_all.R: la numerazione del thread educazione è il prefisso
# `edu_fig` (edu-01..edu-08), separata da quella del thread genere.
#
# Palette: qui le serie sono metriche, non territori né generi, quindi i colori
# riservati (vermiglio Bagheria, blu/rosa genere, viola/ambra territori) non si
# applicano ai loro significati. Il vermiglio marca la metrica-problema (fuori da
# lavoro e studio); nero e sky restano neutre. Da rivedere col team se queste
# figure entrano nel deck accanto alle fig01-11.

source(file.path(if (dir.exists("viz")) "viz" else ".", "theme.R"))

# Stessa misura del salvataggio: su questa il testo va a capo.
LARGHEZZA <- 26

# I denominatori della classe, per la didascalia: una differenza in punti non dice
# quante persone ci siano sotto, e su due territori di taglia opposta è la prima domanda.
stati <- read_csv(file.path(PROCESSED, "edu_youth_states_2018_2024.csv"),
                  show_col_types = FALSE)
enne <- function(t) stati$popolazione[stati$territorio_nome == t &
                                        stati$anno == max(stati$anno)]
N_BAG <- enne("Bagheria")
N_SIC <- enne("Sicilia")

SPEC <- tibble::tibble(
  metrica = c("quota_fuori_lavoro_studio", "quota_inattivi_non_studenti", "quota_occupati"),
  nome = c("fuori da lavoro e studio", "inattivi non studenti", "occupazione"),
  colore = c("#D55E00", "#000000", "#56B4E9"))

serie <- read_csv(file.path(PROCESSED, "edu_gaps_vs_sicily.csv"), show_col_types = FALSE) |>
  filter(dominio == "giovani", metrica %in% SPEC$metrica) |>
  inner_join(SPEC, by = "metrica") |>
  # Il 2020 manca alla fonte: la riga vuota interrompe la linea invece di farla passare
  # sotto la striscia, dove il rettangolo opaco la nasconderebbe. Nessun valore inventato.
  # La chiave è `nome` perché è quella che porta il colore: completare per `metrica`
  # lascerebbe l'estetica vuota sulla riga nuova.
  complete(nome, anno = 2018:2024)

# Le righe del 2020 sono vuote per costruzione: fuori dalle etichette di fine linea.
ultimi <- serie |>
  filter(!is.na(gap_bagheria_sicilia_pp)) |>
  slice_max(anno, n = 1, by = nome)
gap_occ_18 <- serie$gap_bagheria_sicilia_pp[serie$metrica == "quota_occupati" & serie$anno == 2018]
gap_occ_24 <- serie$gap_bagheria_sicilia_pp[serie$metrica == "quota_occupati" & serie$anno == 2024]

figura <- ggplot(serie, aes(asse_2020(anno), gap_bagheria_sicilia_pp, colour = nome)) +
  geom_hline(yintercept = 0, linewidth = 0.5, colour = "grey30") +
  geom_line(linewidth = 1.05) +
  geom_point(size = 2) +
  geom_text(data = ultimi,
            aes(label = paste0(nome, "  ", virgola(gap_bagheria_sicilia_pp, 1, " p.p."))),
            hjust = 0, nudge_x = 0.12, size = 3.3, fontface = "bold", show.legend = FALSE) +
  scale_colour_manual(values = setNames(SPEC$colore, SPEC$nome), guide = "none") +
  # L'asse porta le posizioni, non gli anni: il 2020 non ne ha una (manca alla fonte) e
  # fra 2019 e 2021 resta solo la colonna vuota che la striscia grigia riempie.
  # Il margine a destra è per le etichette di fine linea.
  scala_2020(limits = c(asse_2020(2018), asse_2020(2024) + 2.6)) +
  scale_y_continuous(labels = function(x) virgola(x, 0)) +
  buco_2020(-2.2, serie$anno, serie$gap_bagheria_sicilia_pp) +
  labs(
    title = "Bagheria recupera, e il divario con la Sicilia resta dov'era",
    subtitle = sommario(paste0(
      "Differenza fra Bagheria e la Sicilia, in punti percentuali, su tre misure della classe 15-24 anni, dal 2018 al 2024: ",
      "tasso di occupazione, quota di inattivi non studenti e quota fuori da lavoro e studio. ",
      "La figura mostra i divari e non i livelli, ed è una scelta di misura: il confronto in differenze regge alla rottura di misura fra il 2019 e il 2021, comune a tutti i territori, mentre i livelli delle singole componenti no.\n",
      "L'occupazione resta ", virgola(abs(gap_occ_24), 1), " punti sotto (era ",
      virgola(abs(gap_occ_18), 1), " nel 2018); inattività e area fuori da lavoro e studio restano sopra."), LARGHEZZA),
    x = NULL, y = "Bagheria − Sicilia (punti percentuali)",
    caption = didascalia_2b(
      lettura = paste0(
        "la riga orizzontale allo zero è la parità con la Sicilia, e la distanza di ogni punto da quella riga è il divario di quell'annata. ",
        "Il verso favorevole cambia da misura a misura, e va letto insieme al nome: per l'occupazione un divario negativo è sfavorevole a Bagheria, mentre per gli inattivi non studenti e per l'area fuori da lavoro e studio è sfavorevole un divario positivo. ",
        "La striscia grigia verticale occupa l'annata mancante: dove c'è la striscia non c'è misura, e il 2020 non è interpolato. ",
        "Fra il 2019 e il 2021 il censimento permanente cambia la definizione di «in cerca di occupazione»: è la ragione per cui la figura si limita alle differenze."),
      fonte = paste0(
        "ISTAT, Censimento permanente della popolazione, tavola della condizione professionale, classe 15-24 anni, 2018-2024 (",
        migliaia(round(N_BAG)), " residenti a Bagheria e ", migliaia(round(N_SIC)), " in Sicilia nell'ultima annata). ",
        "Elaborazione: pipeline/edu (thread educazione), data/processed/edu_gaps_vs_sicily.csv (con edu_youth_states_2018_2024.csv per i denominatori)."),
      larghezza = LARGHEZZA)
  ) +
  tema_figura()

salva(figura, "edu_fig06_gap_sicilia", larghezza = LARGHEZZA, altezza = 19)
